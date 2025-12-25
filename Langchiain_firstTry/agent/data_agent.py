"""
可复用的数据分析 Agent：
- 本地 LLM (llama-cpp) + 本地 embedding + Chroma。
- 支持文件夹批量入库（文本/CSV/PDF 简单示例），RAG 查询、引用返回、低置信度拒答。
"""

import argparse
import os
from pathlib import Path
from typing import List, Optional

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import LlamaCpp
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_csv_file(path: Path, limit: int = 2000) -> str:
    # 简化处理：截断前若干行
    return "\n".join(path.read_text(encoding="utf-8", errors="ignore").splitlines()[:limit])


def load_pdf_file(path: Path) -> str:
    try:
        import pypdf  # 仅在需要时导入
    except ImportError as e:
        raise RuntimeError("请先安装 pypdf 以解析 PDF") from e
    reader = pypdf.PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def gather_texts(data_dir: Path) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    docs: List[Document] = []
    for file in data_dir.rglob("*"):
        if not file.is_file():
            continue
        ext = file.suffix.lower()
        try:
            if ext in {".txt", ".md"}:
                raw = load_text_file(file)
            elif ext in {".csv"}:
                raw = load_csv_file(file)
            elif ext in {".pdf"}:
                raw = load_pdf_file(file)
            else:
                continue  # 忽略不支持的格式
        except Exception:
            continue  # 容错处理

        for i, chunk in enumerate(splitter.split_text(raw)):
            docs.append(Document(page_content=chunk, metadata={"source": str(file), "chunk_idx": i}))
    return docs


class DataAgent:
    def __init__(
        self,
        model_path: str,
        embed_path: str,
        persist_dir: str = "./storage/chroma_store",
        k: int = 3,
        similarity_threshold: float = 0.25,
        n_ctx: int = 4096,
        n_threads: int = 8,
        n_gpu_layers: int = 0,
    ):
        self.model_path = model_path
        self.embed_path = embed_path
        self.persist_dir = persist_dir
        self.k = k
        self.similarity_threshold = similarity_threshold
        self._llm = LlamaCpp(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )
        self._embed = HuggingFaceEmbeddings(
            model_name=embed_path,
            model_kwargs={"device": os.getenv("EMBED_DEVICE", "cpu")},
        )
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._vs = Chroma(persist_directory=persist_dir, embedding_function=self._embed)

    def ingest_dir(self, data_dir: Path):
        docs = gather_texts(data_dir)
        if not docs:
            print(f"[WARN] 未找到可解析文件: {data_dir}")
            return
        self._vs.add_documents(docs)
        self._vs.persist()
        print(f"[OK] 已入库文档数: {len(docs)}")

    def _prompt(self) -> PromptTemplate:
        template = (
            "你是企业内部助手，只能基于给定参考回答。\n"
            "若参考不足，请回答“未检索到足够依据”。\n\n"
            "问题：{question}\n"
            "参考：\n{context}\n"
            "回答（请简短并附引用编号）："
        )
        return PromptTemplate(template=template, input_variables=["context", "question"])

    def query(self, question: str, k: Optional[int] = None) -> str:
        k = k or self.k
        scored = self._vs.similarity_search_with_score(question, k=k)
        if not scored:
            return "未检索到足够依据。"
        # 兼容距离/相似度
        top_sim = scored[0][1]
        if top_sim > 1:
            top_sim = 1 / (1 + top_sim)
        if top_sim < self.similarity_threshold:
            return "未检索到足够依据。"

        retriever = self._vs.as_retriever(search_kwargs={"k": k})
        qa = RetrievalQA.from_chain_type(
            llm=self._llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self._prompt()},
        )
        result = qa({"query": question})
        answer = result.get("result", "").strip()
        sources = result.get("source_documents", [])
        if sources:
            refs = [f"[{i}] {s.metadata.get('source','?')}#{s.metadata.get('chunk_idx','?')}" for i, s in enumerate(sources, 1)]
            answer = f"{answer}\n参考：\n" + "\n".join(refs)
        return answer


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--ingest", type=str, help="待入库的数据目录")
    p.add_argument("--query", type=str, help="查询问题")
    p.add_argument("--k", type=int, default=3)
    return p.parse_args()


def main():
    model_path = os.getenv("LOCAL_LLM_PATH", "/models/qwen2-7b-instruct-q4_0.gguf")
    embed_path = os.getenv("LOCAL_EMBED_PATH", "/models/bge-base-zh-v1.5")
    persist_dir = os.getenv("CHROMA_DIR", "./storage/chroma_store")
    agent = DataAgent(
        model_path=model_path,
        embed_path=embed_path,
        persist_dir=persist_dir,
        n_gpu_layers=int(os.getenv("LLM_GPU_LAYERS", "0")),
    )
    args = parse_args()
    if args.ingest:
        agent.ingest_dir(Path(args.ingest))
    if args.query:
        print(agent.query(args.query, k=args.k))


if __name__ == "__main__":
    main()

