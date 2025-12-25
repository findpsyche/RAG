'''
    构建LLM模块
    首先我们需要实现 LLM 模块
    这是系统中最基本的模块，我们将利用大模型完成文档的清洗
    信息提取等工作，可以说 GraphRAG 的一部分精髓即为使用大模型预先处理文档信息
    方便后续进行检索，这里我们使用 zhipuai 的 api 来实现。
'''
from abc import ABC, abstractmethod
from typing import Any, Optional
class BaseLLM(ABC):
    """Interface for large language models.
    Args:
        model_name (str): The name of the language model.
        model_params (Optional[dict[str, Any]], optional): Additional parameters passed to the model when text is sent to it. Defaults to None.
        **kwargs (Any): Arguments passed to the model when for the class is initialised. Defaults to None.
    """
    def __init__(
        self,
        model_name: str,
        model_params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ):
        self.model_name = model_name
        self.model_params = model_params or {}
    @abstractmethod
    def predict(self, input: str) -> str:
        """Sends a text input to the LLM and retrieves a response.
        Args:
            input (str): Text sent to the LLM
        Returns:
            str: The response from the LLM.
        """
''' 
    继承上面LLM基类进行实现大模型的接口
'''
from zhipuai import ZhipuAI
from typing import Any, Optional
from .base import BaseLLM
class zhipuLLM(BaseLLM):
    """Implementation of the BaseLLM interface using zhipuai."""
    def __init__(
        self,
        model_name: str,
        api_key: str,
        model_params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ):
        super().__init__(model_name, model_params, **kwargs)
        self.client = ZhipuAI(api_key=api_key)
    def predict(self, input: str) -> str:
        """Sends a text input to the zhipuai model and retrieves a response.
        Args:
            input (str): Text sent to the zhipuai model
        Returns:
            str: The response from the zhipuai model.
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": input}],
        )
        return response.choices[0].message.content
'''检查'''
llm = zhipuLLM(model_name="....", api_key="...")
print(llm.predict("Hello, how are you?"))

'''
embedding模块
'''
from abc import ABC, abstractmethod
from typing import List, Any, Optional

class BaseEmb(ABC):
    def __init__(
        self,
        model_name: str,
        model_params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ):
        self.model_name = model_name
        self.model_params = model_params or {}

    @abstractmethod
    def get_emb(self, input: str) -> List[float]:
        """Sends a text input to the embedding model and retrieves the embedding.

        Args:
            input (str): Text sent to the embedding model

        Returns:
            List[float]: The embedding vector from the model.
        """
        pass

from zhipuai import ZhipuAI
from typing import List
from .base import BaseEmb

class zhipuEmb(BaseEmb):
    def __init__(self, model_name: str, api_key: str, **kwargs):
        super().__init__(model_name=model_name, **kwargs)
        self.client = ZhipuAI(api_key=api_key)

    def get_emb(self, text: str) -> List[float]:
        emb = self.client.embeddings.create(
            model=self.model_name,
            input=text,
        )
        return emb.data[0].embedding
'''测试emb模型'''
emb = zhipuEmb(model_name="....", api_key="...")
print(emb.get_emb("Hello, how are you?"))

'''
neo4j交互
'''
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
            url, auth=(username, password)
        )  # 创建Neo4j数据库驱动
with driver.session() as session:
    result = session.run("MATCH (n) RETURN n") # 查询图中的所有节点
    for record in result:
        print(record)


'''
数据预处理
'''
#open
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()
#分割片段
def split_text(self,file_path:str, segment_length=300, overlap_length=50) -> Dict:
        """
        将文本文件分割成多个片段，每个片段的长度为segment_length，相邻片段之间有overlap_length的重叠。

        参数:
        - file_path: 文本文件的路径
        - segment_length: 每个片段的长度，默认为300
        - overlap_length: 相邻片段之间的重叠长度，默认为50

        返回:
        - 包含片段ID和片段内容的字典
        """
        chunks = {}  # 用于存储片段的字典
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()  # 读取文件内容

        text_segments = []  # 用于存储分割后的文本片段
        start_index = 0  # 初始化起始索引

        # 循环分割文本，直到剩余文本长度不足以形成新的片段
        while start_index + segment_length <= len(content):
            text_segments.append(content[start_index : start_index + segment_length])
            start_index += segment_length - overlap_length  # 更新起始索引，考虑重叠长度

        # 处理剩余的文本，如果剩余文本长度小于segment_length但大于0
        if start_index < len(content):
            text_segments.append(content[start_index:])

        # 为每个片段生成唯一的ID，并将其存储在字典中
        for segment in text_segments:
            chunks.update({compute_mdhash_id(segement, prefix="chunk-"): segement})

        return chunks
'''
实体定义
'''
'''
class Entity:
    name: str
    desc: str
    chunks_id: list
    entity_id: str
    '''

'''
抽取实体提示词
GET_ENTITY = """
## Goal

You are an experienced machine learning teacher.
You need to identify the key concepts related to machine learning that the article requires students to master. For each concept, provide a brief description that explains its relevance and importance in the context of the article.

## Example

article:
"In the latest study, we explored the potential of using machine learning algorithms for disease prediction. We used support vector machines (SVM) and random forest algorithms to analyze medical data. The results showed that these models performed well in predicting disease risk through feature selection and cross-validation. In particular, the random forest model showed better performance in dealing with overfitting problems. In addition, we discussed the application of deep learning in medical image analysis."

response:
<concept>
    <name>Support Vector Machine (SVM)</name>
    <description>A supervised learning model used for classification and regression tasks, particularly effective in high-dimensional spaces.</description>
</concept>
<concept>
    <name>Random Forest Algorithm</name>
    <description>An ensemble learning method that builds multiple decision trees and merges them together to get a more accurate and stable prediction, often used to reduce overfitting.</description>
</concept>
<concept>
    <name>Feature Selection</name>
    <description>The process of selecting a subset of relevant features for use in model construction, crucial for improving model performance and reducing complexity.</description>
</concept>
<concept>
    <name>Overfitting</name>
    <description>A common issue where a model learns the details and noise in the training data to the extent that it negatively impacts the model's performance on new data.</description>
</concept>
<concept>
    <name>Deep Learning</name>
    <description>A subset of machine learning that uses neural networks with many layers to model complex patterns in large datasets, often applied in image and speech recognition tasks.</description>
</concept>

## Format

Wrap each concept in the HTML tag <concept>, and include the name of the concept in the <name> tag and its description in the <description> tag.

## Article

{text}

## Your response
"""


'''

'''
在上面的提示词中，我们要求 LLM 的回复格式为 HTML 格式
因此，我们需要提取指定标签内的内容，这一步我们使用正则表达式来实现
'''
def get_text_inside_tag(html_string: str, tag: str):
    # html_string 为待解析文本，tag为查找标签
    pattern = f"<{tag}>(.*?)<\/{tag}>"
    try:
        result = re.findall(pattern, html_string, re.DOTALL)
        return result
    except SyntaxError as e:
        raise ("Json Decode Error: {error}".format(error=e))

def get_entity(self, text: str, chunk_id: str) -> List[Dict]:
        """
        从给定的文本中提取实体，并为每个实体生成唯一的ID和描述。

        参数:
        - text: 输入的文本
        - chunk_id: 文本块的ID

        返回:
        - 包含提取的实体信息的列表
        """
        # 使用语言模型预测实体信息
        data = self.llm.predict(GET_ENTITY.format(text=text))
        concepts = []  # 用于存储提取的实体信息

        # 从预测结果中提取实体信息
        for concept_html in get_text_inside_tag(data, "concept"):
            concept = {}
            concept["name"] = get_text_inside_tag(concept_html, "name")[0].strip()
            concept["description"] = get_text_inside_tag(concept_html, "description")[
                0
            ].strip()
            concept["chunks id"] = [chunk_id]
            concept["entity id"] = compute_mdhash_id(
                concept["description"], prefix="entity-"
            )
            concepts.append(concept)

        return concepts

'''
实体抽取后
提示LLM三元组抽取
抽取三元组的提示词
'''
'''
GET_TRIPLETS = """
## Goal
Identify and extract all the relationships between the given concepts from the provided text.
Identify as many relationships between the concepts as possible.
The relationship in the triple should accurately reflect the interaction or connection between the two concepts.

## Guidelines:
1. **Subject:** The first entity from the given entities.
2. **Predicate:** The action or relationship linking the subject to the object.
3. **Object:** The second entity from the given entities.

## Example:
1. Article :
    "Gaussian Processes are used to model the objective function in Bayesian Optimization"
   Given entities:
   [{{"name": "Gaussian Processes", "entity id": "entity-1", "description":"..."}}, {{"name": "Bayesian Optimization", "entity id": "entity-2", "description":"..."}}]
   Output:
   <triplet><subject>Gaussian Processes</subject><subject_id>entity-1</subject_id><predicate>are used to model the objective function in</predicate><object>Bayesian Optimization</object><object_id>entity-2</object_id></triplet>

2. Article :
    "Hydrogen is a colorless, odorless, non-toxic gas and is the lightest and most abundant element in the universe. Oxygen is a gas that supports combustion and is widely present in the Earth's atmosphere. Water is a compound made up of hydrogen and oxygen, with the chemical formula H2O."
    Given entities:
    [{{"name": "Hydrogen", "entity id": "entity-3", "description":"..."}}, {{"name": "Oxygen", "entity id": "entity-4", "description":"..."}}, {{"name": "Water", "entity id": "entity-5", "description":"..."}}]
    Output:
    <triplet><subject>Hydrogen</subject><subject_id>entity-3</subject_id><predicate>is a component of</predicate><object>Water</object><object_id>entity-5</object_id></triplet>
3. Article :
    "John read a book on the weekend"
    Given entities:
    []
    Output:
    None

## Format:
For each identified triplet, provide:
**the entity should just from "Given Entities"**
<triplet><subject>[Entity]</subject><subject_id>[Entity ID]</subject_id><predicate>[The action or relationship]</predicate><object>[Entity]</object><object_id>[Entity ID]</object_id></triplet>

## Given Entities:
{entity}

### Article:
{text}

## Additional Instructions:
- Before giving your response, you should analyze and think about it sentence by sentence.
- Both the subject and object must be selected from the given entities and cannot change their content.
- If no relevant triplet involving both entities is found, no triplet should be extracted.
- If there are similar concepts, please rewrite them into a form that suits our requirements.

## Your response:
"""
'''
'''
使用正则表达式
提取指定标签内容
'''
def get_triplets(self, content, entity: list) -> List[Dict]:
        """
        从给定的内容中提取三元组（Triplet）信息
        并返回包含这些三元组信息的列表。
        参数:
        - content: 输入的内容
        - entity: 实体列表
        返回:
        - 包含提取的三元组信息的列表
        """
        try:
            # 使用语言模型预测三元组信息
            data = self.llm.predict(GET_TRIPLETS.format(text=content, entity=entity))
            data = get_text_inside_tag(data, "triplet")
        except Exception as e:
            print(f"Error predicting triplets: {e}")
            return []
        res = []  # 用于存储提取的三元组信息
        # 从预测结果中提取三元组信息
        for triplet_data in data:
            try:
                subject = get_text_inside_tag(triplet_data, "subject")[0]
                subject_id = get_text_inside_tag(triplet_data, "subject_id")[0]
                predicate = get_text_inside_tag(triplet_data, "predicate")[0]
                object = get_text_inside_tag(triplet_data, "object")[0]
                object_id = get_text_inside_tag(triplet_data, "object_id")[0]
                res.append(
                    {
                        "subject": subject,
                        "subject_id": subject_id,
                        "predicate": predicate,
                        "object": object,
                        "object_id": object_id,
                    }
                )
            except Exception as e:
                print(f"Error extracting triplet: {e}")
                continue
        return res


'''
实体消融 提示词
ENTITY_DISAMBIGUATION = """
## Goal
Given multiple entities with the same name, determine if they can be merged into a single entity. If merging is possible, provide the transformation from entity id to entity id.

## Guidelines
1. **Entities:** A list of entities with the same name.
2. **Merge:** Determine if the entities can be merged into a single entity.
3. **Transformation:** If merging is possible, provide the transformation from entity id to entity id.

## Example
1. Entities:
   [
       {"name": "Entity A", "entity id": "entity-1", "description":"..."},
       {"name": "Entity A", "entity id": "entity-2", "description":"..."},
       {"name": "Entity A", "entity id": "entity-3", "description":"..."}
   ]

Your response should be:

<transformation>{"entity-2": "entity-1", "entity-3": "entity-1"}</transformation>


2. Entities:
   [
       {"name": "Entity B", "entity id": "entity-4", "description":"..."},
       {"name": "Entity C", "entity id": "entity-5", "description":"..."},
       {"name": "Entity B", "entity id": "entity-6", "description":"..."}
   ]

Your response should be:

<transformation>None</transformation>

## Output Format
Provide the following information:
- Transformation: A dictionary mapping entity ids to the final entity id after merging.

## Given Entities
{entities}

## Your response
"""

'''
'''
将需要替换实体ID的ID更新被代替的ID
'''
entity_names = list(set(entity["name"] for entity in all_entities))

if use_llm_deambiguation:
    entity_id_mapping = {}
    for name in entity_names:
        same_name_entities = [
            entity for entity in all_entities if entity["name"] == name
        ]
        transform_text = self.llm.predict(
            ENTITY_DISAMBIGUATION.format(same_name_entities)
        )
        entity_id_mapping.update(
            get_text_inside_tag(transform_text, "transform")
        )
else:
    entity_id_mapping = {}
    for entity in all_entities:
        entity_name = entity["name"]
        if entity_name not in entity_id_mapping:
            entity_id_mapping[entity_name] = entity["entity id"]

for entity in all_entities:
    entity["entity id"] = entity_id_mapping.get(
        entity["name"], entity["entity id"]
    )

triplets_to_remove = [
    triplet
    for triplet in all_triplets
    if entity_id_mapping.get(triplet["subject"], triplet["subject_id"]) is None
    or entity_id_mapping.get(triplet["object"], triplet["object_id"]) is None
]

updated_triplets = [
    {
        **triplet,
        "subject_id": entity_id_mapping.get(
            triplet["subject"], triplet["subject_id"]
        ),
        "object_id": entity_id_mapping.get(
            triplet["object"], triplet["object_id"]
        ),
    }
    for triplet in all_triplets
    if triplet not in triplets_to_remove
]
all_triplets = updated_triplets

'''
实体消岐后，我们就可以开始合并同一实体的信息
'''
entity_map = {}

for entity in all_entities:
    entity_id = entity["entity id"]
    if entity_id not in entity_map:
        entity_map[entity_id] = {
            "name": entity["name"],
            "description": entity["description"],
            "chunks id": [],
            "entity id": entity_id,
        }
    else:
        entity_map[entity_id]["description"] += " " + entity["description"]

    entity_map[entity_id]["chunks id"].extend(entity["chunks id"])


'''
导入neo4j
'''
query = (
        "MERGE (a:Entity {name: $subject_name, description: $subject_desc, chunks_id: $subject_chunks_id, entity_id: $subject_entity_id}) "
        "MERGE (b:Entity {name: $object_name, description: $object_desc, chunks_id: $object_chunks_id, entity_id: $object_entity_id}) "
        "MERGE (a)-[r:Relationship {name: $predicate}]->(b) "
        "RETURN a, b, r"
    )
'''
提取上面三元组信息，到query
'''
def create_triplet(self, subject: dict, predicate, object: dict) -> None:
    """
    创建一个三元组（Triplet）并将其存储到Neo4j数据库中。

    参数:
    - subject: 主题实体的字典，包含名称、描述、块ID和实体ID
    - predicate: 关系名称
    - object: 对象实体的字典，包含名称、描述、块ID和实体ID

    返回:
    - 查询结果
    """
    # 定义Cypher查询语句，用于创建或合并实体节点和关系
    query = (
        "MERGE (a:Entity {name: $subject_name, description: $subject_desc, chunks_id: $subject_chunks_id, entity_id: $subject_entity_id}) "
        "MERGE (b:Entity {name: $object_name, description: $object_desc, chunks_id: $object_chunks_id, entity_id: $object_entity_id}) "
        "MERGE (a)-[r:Relationship {name: $predicate}]->(b) "
        "RETURN a, b, r"
    )

    # 使用数据库会话执行查询
    with self.driver.session() as session:
        result = session.run(
            query,
            subject_name=subject["name"],
            subject_desc=subject["description"],
            subject_chunks_id=subject["chunks id"],
            subject_entity_id=subject["entity id"],
            object_name=object["name"],
            object_desc=object["description"],
            object_chunks_id=object["chunks id"],
            object_entity_id=object["entity id"],
            predicate=predicate,
        )

    return

for triplet in all_triplets:
    subject_id = triplet["subject_id"]
    object_id = triplet["object_id"]

    subject = entity_map.get(subject_id)
    object = entity_map.get(object_id)
    if subject and object:
        self.create_triplet(subject, triplet["predicate"], object)

'''
社区检测
'''
def detect_communities(self) -> None:
    query = """
    CALL gds.graph.project(
        'graph_help',
        ['Entity'],
        {
            Relationship: {
                orientation: 'UNDIRECTED'
            }
        }
    )
    """
    with self.driver.session() as session:
        result = session.run(query)

    query = """
    CALL gds.leiden.write('graph_help', {
        writeProperty: 'communityIds',
        includeIntermediateCommunities: True,
        maxLevels: 10,
        tolerance: 0.0001,
        gamma: 1.0,
        theta: 0.01
    })
    YIELD communityCount, modularity, modularities
    """
    with self.driver.session() as session:
        result = session.run(query)
        for record in result:
            print(
                f"社区数量: {record['communityCount']}, 模块度: {record['modularity']}"
            )
        session.run("CALL gds.graph.drop('graph_help')")

'''
检测后生成schema
'''
def gen_community_schema(self) -> dict[str, dict]:
    results = defaultdict(
        lambda: dict(
            level=None,
            title=None,
            edges=set(),
            nodes=set(),
            chunk_ids=set(),
            sub_communities=[],
        )
    )

    with self.driver.session() as session:
        # Fetch community data
        result = session.run(
            f"""
            MATCH (n:Entity)
            WITH n, n.communityIds AS communityIds, [(n)-[]-(m:Entity) | m.entity_id] AS connected_nodes
            RETURN n.entity_id AS node_id,
                    communityIds AS cluster_key,
                    connected_nodes
            """
        )

        max_num_ids = 0
        for record in result:
            for index, c_id in enumerate(record["cluster_key"]):
                node_id = str(record["node_id"])
                level = index
                cluster_key = str(c_id)
                connected_nodes = record["connected_nodes"]

                results[cluster_key]["level"] = level
                results[cluster_key]["title"] = f"Cluster {cluster_key}"
                results[cluster_key]["nodes"].add(node_id)
                results[cluster_key]["edges"].update(
                    [
                        tuple(sorted([node_id, str(connected)]))
                        for connected in connected_nodes
                        if connected != node_id
                    ]
                )
        for k, v in results.items():
            v["edges"] = [list(e) for e in v["edges"]]
            v["nodes"] = list(v["nodes"])
            v["chunk_ids"] = list(v["chunk_ids"])
        for cluster in results.values():
            cluster["sub_communities"] = [
                sub_key
                for sub_key, sub_cluster in results.items()
                if sub_cluster["level"] > cluster["level"]
                and set(sub_cluster["nodes"]).issubset(set(cluster["nodes"]))
            ]

    return dict(results)
'''
社区摘要
'''
def generate_community_report(self):
    communities_schema = self.read_community_schema()
    for community_key, community in tqdm(
        communities_schema.items(), desc="generating community report"
    ):
        community["report"] = self.gen_single_community_report(community)
    with open(self.community_path, "w", encoding="utf-8") as file:
        json.dump(communities_schema, file, indent=4)
    print("All community report has been generated.")

def gen_single_community_report(self, community: dict):
    nodes = community["nodes"]
    edges = community["edges"]
    nodes_describe = []
    edges_describe = []
    for i in nodes:
        node = self.get_node_by_id(i)
        nodes_describe.append({"name": node["name"], "desc": node["description"]})
    for i in edges:
        edge = self.get_edges_by_id(i[0], i[1])
        edges_describe.append(
            {"source": edge["src"], "target": edge["tar"], "desc": edge["r"]}
        )
    nodes_csv = "entity,description\n"
    for node in nodes_describe:
        nodes_csv += f"{node['name']},{node['desc']}\n"
    edges_csv = "source,target,description\n"
    for edge in edges_describe:
        edges_csv += f"{edge['source']},{edge['target']},{edge['desc']}\n"
    data = f"""
    Text:
    -----Entities-----
    ```csv
    {nodes_csv}
    ```
    -----Relationships-----
    ```csv
    {edges_csv}
    ```
    """
    prompt = GEN_COMMUNITY_REPORT.format(input_text=data)
    report = self.llm.predict(prompt)
    return report