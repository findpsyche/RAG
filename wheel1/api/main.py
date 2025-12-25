"""
FastAPI应用主程序
提供RESTful API接口
"""

import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import tempfile
import asyncio

from core.modes import ProcessingMode

logger = logging.getLogger(__name__)


# ============ 数据模型 ============

class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="文档元数据")
    mode: ProcessingMode = Field(default=ProcessingMode.BALANCED, description="处理模式")


class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="查询文本")
    top_k: int = Field(default=5, ge=1, le=50, description="返回结果数")
    mode: Optional[ProcessingMode] = Field(default=None, description="处理模式（可覆盖系统默认）")
    use_reranking: Optional[bool] = Field(default=None, description="是否使用重排")
    explain: bool = Field(default=False, description="是否返回推理过程")


class QueryResponse(BaseModel):
    """查询响应"""
    query: str
    results: List[Dict[str, Any]]
    count: int
    latency_ms: float
    mode: str
    from_cache: bool = False
    explanation: Optional[str] = None


class ModeConfig(BaseModel):
    """模式配置"""
    mode: ProcessingMode
    description: str
    use_cases: List[str]
    metrics: Dict[str, Any]


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    components: Dict[str, bool]
    timestamp: datetime


# ============ 创建FastAPI应用 ============

def create_app(wheel_system: Any) -> FastAPI:
    """创建FastAPI应用"""
    
    app = FastAPI(
        title="Wheel系统 - 企业级RAG平台",
        description="支持多模态数据处理和知识检索的企业级AI系统",
        version="1.0.0"
    )
    
    # ============ 健康检查端点 ============
    
    @app.get("/health", response_model=HealthResponse, tags=["System"])
    async def health_check():
        """系统健康检查"""
        is_healthy, components = wheel_system.health_check()
        
        return HealthResponse(
            status="healthy" if is_healthy else "degraded",
            components=components,
            timestamp=datetime.now()
        )
    
    # ============ 文档处理端点 ============
    
    @app.post("/api/v1/documents/upload", tags=["Documents"])
    async def upload_document(
        file: UploadFile = File(...),
        mode: ProcessingMode = Query(ProcessingMode.BALANCED),
        background_tasks: BackgroundTasks = None
    ):
        """
        上传和处理文档
        
        支持格式: PDF, DOCX, TXT, 图像(JPG/PNG), 视频(MP4/AVI)
        """
        try:
            # 保存临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            # 切换模式（如需要）
            if mode != wheel_system.mode:
                wheel_system.switch_mode(mode)
            
            # 异步处理文档
            if background_tasks:
                background_tasks.add_task(
                    wheel_system.process_document,
                    tmp_path,
                    {"filename": file.filename, "uploaded_at": datetime.now().isoformat()}
                )
            else:
                result = wheel_system.process_document(
                    tmp_path,
                    {"filename": file.filename}
                )
            
            return {
                "status": "processing" if background_tasks else result.get("status"),
                "document_id": result.get("document_id") if not background_tasks else None,
                "message": "文档已上传并开始处理"
            }
        
        except Exception as e:
            logger.error(f"文档上传失败: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # ============ 查询端点 ============
    
    @app.post("/api/v1/query", response_model=QueryResponse, tags=["Query"])
    async def query(request: QueryRequest):
        """
        执行查询
        
        支持三种处理模式:
        - efficiency: 快速模式 (100-300ms)
        - balanced: 平衡模式 (500ms-2s)  
        - precision: 精确模式 (2-10s)
        """
        try:
            # 切换模式（如指定）
            if request.mode and request.mode != wheel_system.mode:
                wheel_system.switch_mode(request.mode)
            
            # 执行查询
            result = wheel_system.query(
                query_text=request.query,
                top_k=request.top_k,
                use_reranking=request.use_reranking,
                explain=request.explain
            )
            
            return QueryResponse(**result)
        
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/query/stream", tags=["Query"])
    async def query_stream(request: QueryRequest):
        """流式查询响应"""
        async def stream_results():
            try:
                result = wheel_system.query(
                    query_text=request.query,
                    top_k=request.top_k,
                    explain=request.explain
                )
                
                # 流式返回结果
                yield f"data: {result}\n\n"
            
            except Exception as e:
                yield f"error: {str(e)}\n\n"
        
        return StreamingResponse(stream_results(), media_type="text/event-stream")
    
    # ============ 模式管理端点 ============
    
    @app.get("/api/v1/modes", tags=["Modes"])
    async def get_modes():
        """获取所有可用模式"""
        from core.modes import ModeConfig
        
        modes = {}
        for mode in ProcessingMode:
            config = ModeConfig.get_config(mode)
            modes[mode.value] = {
                "name": config['name'],
                "description": config['description'],
                "use_cases": config['target_use_cases'],
                "metrics": config['metrics']
            }
        
        return modes
    
    @app.post("/api/v1/mode/switch", tags=["Modes"])
    async def switch_mode(mode: ProcessingMode):
        """切换处理模式"""
        try:
            wheel_system.switch_mode(mode)
            return {
                "status": "success",
                "current_mode": mode.value,
                "message": f"已切换到 {mode.value} 模式"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/v1/mode/current", tags=["Modes"])
    async def get_current_mode():
        """获取当前模式"""
        return {
            "current_mode": wheel_system.mode.value,
            "config": {
                k: v for k, v in vars(wheel_system.config).items()
                if k != 'mode_configs'
            }
        }
    
    # ============ 监控端点 ============
    
    @app.get("/api/v1/metrics", tags=["Monitoring"])
    async def get_metrics():
        """获取系统性能指标"""
        return wheel_system.get_metrics()
    
    @app.get("/api/v1/metrics/summary", tags=["Monitoring"])
    async def get_metrics_summary():
        """获取指标摘要"""
        metrics = wheel_system.get_metrics()
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": metrics
        }
    
    # ============ 配置端点 ============
    
    @app.get("/api/v1/config", tags=["Config"])
    async def get_config():
        """获取系统配置"""
        return {
            "mode": wheel_system.mode.value,
            "llm_provider": wheel_system.config.llm_provider,
            "llm_model": wheel_system.config.llm_model,
            "vector_db": wheel_system.config.vector_db_type,
            "cache_enabled": wheel_system.config.enable_cache,
            "monitoring_enabled": wheel_system.config.enable_monitoring
        }
    
    # ============ 管理端点 ============
    
    @app.post("/api/v1/admin/clear-cache", tags=["Admin"])
    async def clear_cache():
        """清除缓存"""
        try:
            wheel_system.cache.client.flushdb() if wheel_system.cache.client else None
            return {"status": "success", "message": "缓存已清除"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/admin/stats", tags=["Admin"])
    async def get_stats():
        """获取系统统计信息"""
        return {
            "mode": wheel_system.mode.value,
            "health": wheel_system.health_check(),
            "metrics": wheel_system.get_metrics(),
            "timestamp": datetime.now().isoformat()
        }
    
    # ============ 根端点 ============
    
    @app.get("/", tags=["System"])
    async def root():
        """系统信息"""
        return {
            "name": "Wheel系统",
            "version": "1.0.0",
            "status": "running",
            "current_mode": wheel_system.mode.value,
            "docs": "/docs",
            "api_base": "/api/v1"
        }
    
    return app
