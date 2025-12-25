"""
多 Agent 编排示例（LangGraph）：
- Planner：拆解用户需求。
- Executor：检索 + 生成回答（调用本地 RAG 工具）。
- Verifier：复核答案，若不足则提示无依据。
全程使用本地 LLM，适合复杂任务/多步骤指令。
"""

import os
import argparse
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate

from agent.data_agent import DataAgent


def build_llm():
    return LlamaCpp(
        model_path=os.getenv("LOCAL_LLM_PATH", "/models/qwen2-7b-instruct-q4_0.gguf"),
        n_ctx=int(os.getenv("LLM_CTX", "4096")),
        n_threads=int(os.getenv("LLM_THREADS", "8")),
        n_gpu_layers=int(os.getenv("LLM_GPU_LAYERS", "0")),
        verbose=False,
    )


def planner(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = build_llm()
    prompt = PromptTemplate.from_template(
        "你是任务规划器，请将用户需求拆解为 2-4 个步骤，简洁列出：\n需求：{query}\n步骤："
    )
    steps = llm(prompt.format(query=state["query"]))
    return {"plan": steps}


def executor(state: Dict[str, Any]) -> Dict[str, Any]:
    agent = DataAgent(
        model_path=os.getenv("LOCAL_LLM_PATH", "/models/qwen2-7b-instruct-q4_0.gguf"),
        embed_path=os.getenv("LOCAL_EMBED_PATH", "/models/bge-base-zh-v1.5"),
        persist_dir=os.getenv("CHROMA_DIR", "./storage/chroma_store"),
        n_gpu_layers=int(os.getenv("LLM_GPU_LAYERS", "0")),
    )
    answer = agent.query(state["query"], k=int(os.getenv("TOP_K", "4")))
    return {"answer": answer}


def verifier(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = build_llm()
    prompt = PromptTemplate.from_template(
        "你是审核员，检查回答是否基于引用且可信。如缺依据，回复“依据不足”。\n"
        "问题：{query}\n回答：{answer}\n审核结论："
    )
    verdict = llm(prompt.format(query=state["query"], answer=state.get("answer", "")))
    return {"verdict": verdict}


def build_graph():
    graph = StateGraph(dict)
    graph.add_node("planner", planner)
    graph.add_node("executor", executor)
    graph.add_node("verifier", verifier)
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "verifier")
    graph.add_edge("verifier", END)
    graph.set_entry_point("planner")
    return graph.compile()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, type=str, help="用户需求")
    args = ap.parse_args()
    workflow = build_graph()
    result = workflow.invoke({"query": args.query})
    print("规划:\n", result.get("plan", ""))
    print("\n回答:\n", result.get("answer", ""))
    print("\n审核:\n", result.get("verdict", ""))


if __name__ == "__main__":
    main()

