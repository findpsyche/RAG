"""
Wheel系统 API集成测试
验证所有端点的功能
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# API基础URL
BASE_URL = "http://localhost:8000"

class WheelAPITester:
    """API测试工具"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _print_result(self, method: str, endpoint: str, status_code: int, data: Any = None):
        """打印结果"""
        status = "✓" if 200 <= status_code < 300 else "✗"
        print(f"{status} {method} {endpoint} [{status_code}]")
        if data:
            print(f"  响应: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}")
    
    # ========== 系统健康检查 ==========
    
    def test_health_check(self):
        """健康检查"""
        print("\n【系统健康检查】")
        
        response = self.session.get(f"{self.base_url}/health")
        self._print_result("GET", "/health", response.status_code, response.json())
        return response.status_code == 200
    
    def test_root(self):
        """根路径"""
        print("\n【API根路径】")
        
        response = self.session.get(f"{self.base_url}/")
        self._print_result("GET", "/", response.status_code, response.json())
        return response.status_code == 200
    
    # ========== 查询功能 ==========
    
    def test_query(
        self,
        query: str = "什么是RAG系统?",
        top_k: int = 5,
        mode: str = "balanced"
    ):
        """执行查询"""
        print(f"\n【执行查询】 - {query}")
        
        payload = {
            "query": query,
            "top_k": top_k,
            "mode": mode,
            "explain": True
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/query",
            json=payload
        )
        
        self._print_result("POST", "/api/v1/query", response.status_code, response.json())
        return response.status_code == 200
    
    def test_query_stream(self, query: str = "测试查询"):
        """流式查询"""
        print(f"\n【流式查询】 - {query}")
        
        payload = {"query": query, "top_k": 5}
        
        response = self.session.post(
            f"{self.base_url}/api/v1/query/stream",
            json=payload,
            stream=True
        )
        
        self._print_result("POST", "/api/v1/query/stream", response.status_code)
        return response.status_code == 200
    
    # ========== 模式管理 ==========
    
    def test_get_modes(self):
        """获取所有模式"""
        print("\n【获取所有模式】")
        
        response = self.session.get(f"{self.base_url}/api/v1/modes")
        data = response.json()
        
        self._print_result("GET", "/api/v1/modes", response.status_code, data)
        print(f"  可用模式: {list(data.keys())}")
        return response.status_code == 200
    
    def test_get_current_mode(self):
        """获取当前模式"""
        print("\n【获取当前模式】")
        
        response = self.session.get(f"{self.base_url}/api/v1/mode/current")
        data = response.json()
        
        self._print_result("GET", "/api/v1/mode/current", response.status_code, data)
        return response.status_code == 200
    
    def test_switch_mode(self, target_mode: str = "precision"):
        """切换模式"""
        print(f"\n【切换模式】 -> {target_mode}")
        
        response = self.session.post(
            f"{self.base_url}/api/v1/mode/switch",
            json={"mode": target_mode}
        )
        
        self._print_result("POST", "/api/v1/mode/switch", response.status_code, response.json())
        return response.status_code == 200
    
    # ========== 文档处理 ==========
    
    def test_upload_document(self, file_path: str = "test.txt", mode: str = "balanced"):
        """上传文档"""
        print(f"\n【上传文档】 - {file_path}")
        
        # 创建测试文件
        with open("temp_test.txt", "w") as f:
            f.write("这是一个测试文档。\n" * 10)
        
        with open("temp_test.txt", "rb") as f:
            files = {"file": f}
            response = self.session.post(
                f"{self.base_url}/api/v1/documents/upload?mode={mode}",
                files=files
            )
        
        self._print_result("POST", "/api/v1/documents/upload", response.status_code, response.json())
        return response.status_code == 200
    
    # ========== 监控 ==========
    
    def test_get_metrics(self):
        """获取性能指标"""
        print("\n【获取性能指标】")
        
        response = self.session.get(f"{self.base_url}/api/v1/metrics")
        data = response.json()
        
        self._print_result("GET", "/api/v1/metrics", response.status_code)
        if data:
            print(f"  收集的指标: {list(data.keys())}")
        return response.status_code == 200
    
    def test_get_metrics_summary(self):
        """获取指标摘要"""
        print("\n【获取指标摘要】")
        
        response = self.session.get(f"{self.base_url}/api/v1/metrics/summary")
        self._print_result("GET", "/api/v1/metrics/summary", response.status_code, response.json())
        return response.status_code == 200
    
    # ========== 配置 ==========
    
    def test_get_config(self):
        """获取系统配置"""
        print("\n【获取系统配置】")
        
        response = self.session.get(f"{self.base_url}/api/v1/config")
        data = response.json()
        
        self._print_result("GET", "/api/v1/config", response.status_code, data)
        return response.status_code == 200
    
    # ========== 管理 ==========
    
    def test_clear_cache(self):
        """清除缓存"""
        print("\n【清除缓存】")
        
        response = self.session.post(f"{self.base_url}/api/v1/admin/clear-cache")
        self._print_result("POST", "/api/v1/admin/clear-cache", response.status_code, response.json())
        return response.status_code == 200
    
    def test_admin_stats(self):
        """获取管理统计"""
        print("\n【管理统计】")
        
        response = self.session.get(f"{self.base_url}/api/v1/admin/stats")
        data = response.json()
        
        self._print_result("GET", "/api/v1/admin/stats", response.status_code)
        if data:
            print(f"  统计项目: {list(data.keys())}")
        return response.status_code == 200
    
    # ========== 完整测试流程 ==========
    
    def run_full_test_suite(self):
        """运行完整测试套件"""
        print("\n" + "="*60)
        print("开始Wheel系统API完整测试")
        print("="*60)
        
        start_time = time.time()
        results = {}
        
        # 系统测试
        print("\n【1. 系统检查】")
        results['health'] = self.test_health_check()
        results['root'] = self.test_root()
        
        # 查询测试
        print("\n【2. 查询功能】")
        results['query_1'] = self.test_query("什么是机器学习?", mode="balanced")
        results['query_2'] = self.test_query("Vector database有哪些?", mode="efficiency")
        results['stream'] = self.test_query_stream()
        
        # 模式管理
        print("\n【3. 模式管理】")
        results['get_modes'] = self.test_get_modes()
        results['current_mode'] = self.test_get_current_mode()
        results['switch_mode'] = self.test_switch_mode("precision")
        
        # 文档处理
        print("\n【4. 文档处理】")
        results['upload'] = self.test_upload_document()
        
        # 监控
        print("\n【5. 性能监控】")
        results['metrics'] = self.test_get_metrics()
        results['metrics_summary'] = self.test_get_metrics_summary()
        
        # 配置
        print("\n【6. 配置管理】")
        results['config'] = self.test_get_config()
        
        # 管理
        print("\n【7. 系统管理】")
        results['clear_cache'] = self.test_clear_cache()
        results['admin_stats'] = self.test_admin_stats()
        
        # 总结
        duration = time.time() - start_time
        total_tests = len(results)
        passed = sum(1 for v in results.values() if v)
        
        print("\n" + "="*60)
        print("测试完成!")
        print("="*60)
        print(f"总耗时: {duration:.2f}s")
        print(f"测试结果: {passed}/{total_tests} 通过")
        print(f"成功率: {(passed/total_tests)*100:.1f}%")
        print("="*60 + "\n")
        
        # 详细结果
        print("详细结果:")
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {test_name}: {status}")
        
        return passed == total_tests


def main():
    """主函数"""
    
    tester = WheelAPITester()
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"错误: 无法连接到API服务器 ({BASE_URL})")
        print("请先运行: python wheel1.py")
        return
    
    # 运行测试
    success = tester.run_full_test_suite()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
