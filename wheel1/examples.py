"""
Wheel系统使用示例
展示如何在不同场景下使用系统
"""

import asyncio
from wheel1 import WheelSystem, WheelSystemConfig
from core.modes import ProcessingMode, ModeConfig
from agents.mcp_integration import create_default_skills


# ============ 示例1: 基础使用 ============

def example_basic_usage():
    """基础使用示例"""
    print("="*60)
    print("示例1: 基础使用")
    print("="*60)
    
    # 创建系统实例
    system = WheelSystem()
    
    # 查询示例
    result = system.query("什么是RAG系统?", top_k=5)
    print(f"\n查询结果: {result}")
    
    # 获取指标
    metrics = system.get_metrics()
    print(f"\n性能指标: {metrics}")


# ============ 示例2: 模式切换 ============

def example_mode_switching():
    """模式切换示例"""
    print("\n" + "="*60)
    print("示例2: 处理模式切换")
    print("="*60)
    
    system = WheelSystem()
    
    # 显示所有模式
    ModeConfig.print_comparison()
    
    # 尝试三种模式
    for mode in [ProcessingMode.EFFICIENCY, ProcessingMode.BALANCED, ProcessingMode.PRECISION]:
        print(f"\n切换到{mode.value}模式...")
        system.switch_mode(mode)
        
        result = system.query("示例查询", top_k=3)
        print(f"延迟: {result.get('latency_ms')}ms")
        print(f"结果数: {result.get('count')}")


# ============ 示例3: 文档处理 ============

def example_document_processing():
    """文档处理示例"""
    print("\n" + "="*60)
    print("示例3: 文档处理")
    print("="*60)
    
    system = WheelSystem()
    
    # 处理不同类型的文件
    test_files = [
        "sample.pdf",
        "sample.docx",
        "sample.txt",
        "sample.jpg"
    ]
    
    for file_path in test_files:
        try:
            print(f"\n处理文件: {file_path}")
            result = system.process_document(
                file_path,
                metadata={"source": "example"}
            )
            print(f"状态: {result.get('status')}")
            print(f"Chunks数: {result.get('chunks_count')}")
            print(f"耗时: {result.get('duration'):.2f}s")
        except Exception as e:
            print(f"处理失败: {e}")


# ============ 示例4: MCP和Skills ============

async def example_mcp_skills():
    """MCP和Skills系统示例"""
    print("\n" + "="*60)
    print("示例4: MCP集成和Skills")
    print("="*60)
    
    system = WheelSystem()
    
    # 创建技能注册表
    from agents.mcp_integration import MCPServer
    
    skill_registry = create_default_skills(system)
    mcp_server = MCPServer(skill_registry)
    
    # 列出所有技能
    print("\n可用技能:")
    for skill_def in skill_registry.list_skills():
        print(f"  - {skill_def.name}: {skill_def.description}")
    
    # 执行技能示例
    print("\n执行'模式切换'技能...")
    result = await mcp_server.handle_tool_call(
        "Mode Switch",
        {"target_mode": "precision"}
    )
    print(f"结果: {result}")
    
    # 获取OpenAI格式的工具
    openai_tools = mcp_server.to_openai_tools()
    print(f"\nOpenAI Tools数量: {len(openai_tools)}")
    
    # 获取Claude格式的工具
    claude_tools = mcp_server.to_claude_tools()
    print(f"Claude Tools数量: {len(claude_tools)}")


# ============ 示例5: A/B测试 ============

def example_ab_testing():
    """A/B测试示例"""
    print("\n" + "="*60)
    print("示例5: A/B测试框架")
    print("="*60)
    
    from monitoring.metrics import ABTestFramework
    from datetime import timedelta
    
    framework = ABTestFramework()
    
    # 创建实验
    exp_id = framework.create_experiment(
        name="高效vs中效模式对比",
        control_config={"mode": "efficiency"},
        treatment_config={"mode": "balanced"},
        duration=timedelta(hours=1)
    )
    print(f"\n创建实验: {exp_id}")
    
    # 记录模拟结果
    for i in range(100):
        framework.record_result(
            exp_id,
            "control",
            {
                "latency_ms": 150 + (i % 50),
                "recall": 0.55,
                "cost": 0.001
            }
        )
        
        framework.record_result(
            exp_id,
            "treatment",
            {
                "latency_ms": 800 + (i % 200),
                "recall": 0.75,
                "cost": 0.01
            }
        )
    
    # 获取结果
    results = framework.get_results(exp_id)
    print(f"\n实验结果:")
    print(f"对照组样本: {results['control_samples']}")
    print(f"处理组样本: {results['treatment_samples']}")
    print(f"指标对比: {results['metrics_comparison']}")


# ============ 示例6: 性能基准 ============

def example_performance_benchmark():
    """性能基准测试示例"""
    print("\n" + "="*60)
    print("示例6: 性能基准测试")
    print("="*60)
    
    import time
    
    system = WheelSystem()
    queries = [
        "什么是机器学习?",
        "如何构建RAG系统?",
        "Vector database有哪些?",
        "Embedding模型的选择?",
        "LLM微调最佳实践"
    ]
    
    print(f"\n在三种模式上执行查询基准测试...")
    print(f"查询数量: {len(queries)}\n")
    
    for mode in [ProcessingMode.EFFICIENCY, ProcessingMode.BALANCED, ProcessingMode.PRECISION]:
        system.switch_mode(mode)
        
        latencies = []
        start_time = time.time()
        
        for query in queries:
            result = system.query(query, top_k=5)
            latencies.append(result.get('latency_ms', 0))
        
        total_time = time.time() - start_time
        
        print(f"{mode.value.upper()}模式:")
        print(f"  平均延迟: {sum(latencies)/len(latencies):.1f}ms")
        print(f"  总耗时: {total_time:.2f}s")
        print(f"  吞吐量: {len(queries)/total_time:.1f} req/s\n")


# ============ 示例7: 自定义配置 ============

def example_custom_config():
    """自定义配置示例"""
    print("\n" + "="*60)
    print("示例7: 自定义系统配置")
    print("="*60)
    
    config = WheelSystemConfig(
        mode=ProcessingMode.BALANCED,
        
        # 数据库配置
        db_host="localhost",
        db_port=5432,
        db_name="wheel_db",
        
        # Redis配置
        redis_host="localhost",
        redis_port=6379,
        redis_ttl=7200,  # 2小时TTL
        
        # LLM配置
        llm_provider="openai",
        llm_model="gpt-4-turbo",
        embedding_model="text-embedding-3-small",
        
        # 系统配置
        batch_size=64,
        max_workers=8,
        enable_monitoring=True,
        enable_cache=True
    )
    
    system = WheelSystem(config)
    
    print(f"\n系统配置:")
    print(f"  模式: {system.config.mode.value}")
    print(f"  数据库: {system.config.db_host}:{system.config.db_port}")
    print(f"  Redis: {system.config.redis_host}:{system.config.redis_port}")
    print(f"  LLM: {system.config.llm_provider}/{system.config.llm_model}")
    print(f"  缓存: {'启用' if system.config.enable_cache else '禁用'}")
    print(f"  监控: {'启用' if system.config.enable_monitoring else '禁用'}")


# ============ 示例8: 错误处理 ============

def example_error_handling():
    """错误处理示例"""
    print("\n" + "="*60)
    print("示例8: 错误处理")
    print("="*60)
    
    system = WheelSystem()
    
    # 测试不存在的文件
    try:
        result = system.process_document("nonexistent.pdf")
        print(f"结果: {result}")
    except Exception as e:
        print(f"捕获异常: {type(e).__name__}: {e}")
    
    # 空查询
    try:
        result = system.query("")
        print(f"空查询结果: {result}")
    except Exception as e:
        print(f"捕获异常: {e}")
    
    # 健康检查
    is_healthy, details = system.health_check()
    print(f"\n系统健康状态: {'正常' if is_healthy else '部分异常'}")
    for component, status in details.items():
        print(f"  {component}: {'✓' if status else '✗'}")


# ============ 主函数 ============

def main():
    """运行所有示例"""
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " Wheel系统 - 完整使用示例 ".center(58) + "║")
    print("╚" + "═"*58 + "╝")
    
    examples = [
        ("基础使用", example_basic_usage),
        ("模式切换", example_mode_switching),
        ("文档处理", example_document_processing),
        ("性能基准", example_performance_benchmark),
        ("自定义配置", example_custom_config),
        ("错误处理", example_error_handling),
    ]
    
    async_examples = [
        ("MCP和Skills", example_mcp_skills),
        ("A/B测试", example_ab_testing),
    ]
    
    # 运行同步示例
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n示例'{name}'执行异常: {e}")
    
    # 运行异步示例
    for name, func in async_examples:
        try:
            asyncio.run(func())
        except Exception as e:
            print(f"\n示例'{name}'执行异常: {e}")
    
    print("\n" + "="*60)
    print("所有示例执行完成!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
