"""
MCP (Model Context Protocol) 集成
支持OpenAI Tools和Claude Tools
以及自定义Skills系统
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


# ============ Skills系统 ============

class SkillCategory(str, Enum):
    """技能分类"""
    DATA_PROCESSING = "data_processing"
    RETRIEVAL = "retrieval"
    REASONING = "reasoning"
    KNOWLEDGE_MANAGEMENT = "knowledge_management"
    INTEGRATION = "integration"


@dataclass
class SkillDefinition:
    """技能定义"""
    name: str
    description: str
    category: SkillCategory
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    version: str = "1.0.0"
    enabled: bool = True


class Skill(ABC):
    """技能基类"""
    
    def __init__(self, definition: SkillDefinition, executor: Callable):
        """
        初始化技能
        
        Args:
            definition: 技能定义
            executor: 执行函数
        """
        self.definition = definition
        self.executor = executor
    
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """获取技能schema（用于MCP）"""
        return {
            "name": self.definition.name,
            "description": self.definition.description,
            "inputSchema": self.definition.input_schema,
            "outputSchema": self.definition.output_schema
        }


class BasicSkill(Skill):
    """基础技能实现"""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能"""
        try:
            result = await self.executor(inputs)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"技能执行失败: {self.definition.name} - {e}")
            return {
                "success": False,
                "error": str(e)
            }


class SkillRegistry:
    """技能注册表"""
    
    def __init__(self):
        """初始化技能注册表"""
        self.skills: Dict[str, Skill] = {}
        self.categories: Dict[SkillCategory, List[str]] = {}
        
        logger.info("初始化技能注册表")
    
    def register(self, skill: Skill) -> str:
        """
        注册技能
        
        Args:
            skill: 技能实例
        
        Returns:
            技能ID
        """
        skill_id = skill.definition.name.lower().replace(" ", "_")
        
        self.skills[skill_id] = skill
        
        # 按分类索引
        category = skill.definition.category
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(skill_id)
        
        logger.info(f"注册技能: {skill_id} ({category.value})")
        return skill_id
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(skill_id)
    
    def list_skills(self, category: Optional[SkillCategory] = None) -> List[SkillDefinition]:
        """列出技能"""
        if category:
            skill_ids = self.categories.get(category, [])
            return [self.skills[sid].definition for sid in skill_ids if sid in self.skills]
        
        return [skill.definition for skill in self.skills.values()]
    
    async def execute_skill(self, skill_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能"""
        skill = self.get_skill(skill_id)
        if not skill:
            return {"success": False, "error": f"技能不存在: {skill_id}"}
        
        return await skill.execute(inputs)
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """获取MCP工具定义"""
        return [skill.get_schema() for skill in self.skills.values()]


# ============ 预定义Skills ============

def create_default_skills(wheel_system: Any) -> SkillRegistry:
    """创建默认技能"""
    
    registry = SkillRegistry()
    
    # 1. 文档摄入技能
    document_ingestion_def = SkillDefinition(
        name="Document Ingestion",
        description="从文件摄入多模态文档（PDF、Word、图像等）",
        category=SkillCategory.DATA_PROCESSING,
        input_schema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "文件路径"},
                "mode": {"type": "string", "enum": ["efficiency", "balanced", "precision"]},
                "metadata": {"type": "object"}
            },
            "required": ["file_path"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "document_id": {"type": "string"},
                "chunks_count": {"type": "integer"},
                "status": {"type": "string"}
            }
        }
    )
    
    async def document_ingestion_executor(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """文档摄入执行器"""
        file_path = inputs.get('file_path')
        mode = inputs.get('mode', 'balanced')
        metadata = inputs.get('metadata', {})
        
        result = wheel_system.process_document(file_path, metadata)
        return result
    
    registry.register(BasicSkill(document_ingestion_def, document_ingestion_executor))
    
    # 2. 语义搜索技能
    semantic_search_def = SkillDefinition(
        name="Semantic Search",
        description="执行语义相似度搜索，返回最相关的文档",
        category=SkillCategory.RETRIEVAL,
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "查询文本"},
                "top_k": {"type": "integer", "default": 5},
                "threshold": {"type": "number"}
            },
            "required": ["query"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "results": {"type": "array"},
                "count": {"type": "integer"}
            }
        }
    )
    
    async def semantic_search_executor(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """语义搜索执行器"""
        query = inputs.get('query')
        top_k = inputs.get('top_k', 5)
        
        result = wheel_system.query(query, top_k=top_k)
        return result
    
    registry.register(BasicSkill(semantic_search_def, semantic_search_executor))
    
    # 3. 文本提取技能
    text_extraction_def = SkillDefinition(
        name="Text Extraction",
        description="从各种格式文件提取文本",
        category=SkillCategory.DATA_PROCESSING,
        input_schema={
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "format": {"type": "string"}
            },
            "required": ["file_path"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "length": {"type": "integer"}
            }
        }
    )
    
    async def text_extraction_executor(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """文本提取执行器"""
        file_path = inputs.get('file_path')
        text = wheel_system.doc_processor.extract_text(file_path)
        
        return {
            "text": text,
            "length": len(text)
        }
    
    registry.register(BasicSkill(text_extraction_def, text_extraction_executor))
    
    # 4. 图像理解技能
    image_understanding_def = SkillDefinition(
        name="Image Understanding",
        description="理解和分析图像内容，提取文本和语义信息",
        category=SkillCategory.DATA_PROCESSING,
        input_schema={
            "type": "object",
            "properties": {
                "image_path": {"type": "string"},
                "analysis_type": {"type": "string", "enum": ["ocr", "scene", "object_detection"]}
            },
            "required": ["image_path"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "objects": {"type": "array"},
                "analysis": {"type": "object"}
            }
        }
    )
    
    async def image_understanding_executor(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """图像理解执行器"""
        image_path = inputs.get('image_path')
        analysis_type = inputs.get('analysis_type', 'ocr')
        
        # 使用文档处理器中的OCR功能
        text = wheel_system.doc_processor.extract_text(image_path)
        
        return {
            "text": text,
            "analysis_type": analysis_type
        }
    
    registry.register(BasicSkill(image_understanding_def, image_understanding_executor))
    
    # 5. 知识图谱构建技能
    kg_building_def = SkillDefinition(
        name="Knowledge Graph Building",
        description="从文本构建知识图谱（实体、关系提取）",
        category=SkillCategory.KNOWLEDGE_MANAGEMENT,
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "domain": {"type": "string"}
            },
            "required": ["text"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "entities": {"type": "array"},
                "relationships": {"type": "array"}
            }
        }
    )
    
    async def kg_building_executor(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """知识图谱构建执行器"""
        text = inputs.get('text', '')
        
        # 简化实现：返回placeholder
        return {
            "entities": [],
            "relationships": [],
            "status": "knowledge_graph_feature_pending"
        }
    
    registry.register(BasicSkill(kg_building_def, kg_building_executor))
    
    # 6. 多模式切换技能
    mode_switch_def = SkillDefinition(
        name="Mode Switch",
        description="在三种处理模式之间动态切换（高效/中效/低效）",
        category=SkillCategory.INTEGRATION,
        input_schema={
            "type": "object",
            "properties": {
                "target_mode": {"type": "string", "enum": ["efficiency", "balanced", "precision"]}
            },
            "required": ["target_mode"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "previous_mode": {"type": "string"},
                "current_mode": {"type": "string"}
            }
        }
    )
    
    async def mode_switch_executor(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """模式切换执行器"""
        from core.modes import ProcessingMode
        
        target_mode = inputs.get('target_mode')
        previous_mode = wheel_system.mode.value
        
        wheel_system.switch_mode(ProcessingMode(target_mode))
        
        return {
            "previous_mode": previous_mode,
            "current_mode": wheel_system.mode.value
        }
    
    registry.register(BasicSkill(mode_switch_def, mode_switch_executor))
    
    logger.info(f"已加载 {len(registry.skills)} 个默认技能")
    return registry


# ============ MCP集成 ============

class MCPServer:
    """MCP服务器"""
    
    def __init__(self, skill_registry: SkillRegistry):
        """
        初始化MCP服务器
        
        Args:
            skill_registry: 技能注册表
        """
        self.skill_registry = skill_registry
        logger.info("初始化MCP服务器")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """获取所有可用工具（MCP格式）"""
        return self.skill_registry.get_mcp_tools()
    
    async def handle_tool_call(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理工具调用
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入
        
        Returns:
            执行结果
        """
        skill_id = tool_name.lower().replace(" ", "_")
        return await self.skill_registry.execute_skill(skill_id, tool_input)
    
    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """转换为OpenAI Tools格式"""
        tools = []
        
        for tool_def in self.get_tools():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_def['name'].lower().replace(" ", "_"),
                    "description": tool_def['description'],
                    "parameters": {
                        "type": "object",
                        "properties": tool_def['inputSchema'].get('properties', {}),
                        "required": tool_def['inputSchema'].get('required', [])
                    }
                }
            })
        
        return tools
    
    def to_claude_tools(self) -> List[Dict[str, Any]]:
        """转换为Claude Tools格式"""
        tools = []
        
        for tool_def in self.get_tools():
            tools.append({
                "name": tool_def['name'].lower().replace(" ", "_"),
                "description": tool_def['description'],
                "input_schema": {
                    "type": "object",
                    "properties": tool_def['inputSchema'].get('properties', {}),
                    "required": tool_def['inputSchema'].get('required', [])
                }
            })
        
        return tools
