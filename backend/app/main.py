from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import chat, file, analysis, example
from app.core.config import settings
from app.services.dependencies import close_llm_service
import traceback

app = FastAPI(
    title="智能数据分析对话机器人",
    description="基于大模型的智能数据分析对话平台",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(file.router, prefix="/api/file", tags=["file"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(example.router, prefix="/api", tags=["examples"])

# 注册启动和关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的操作"""
    await close_llm_service()

@app.get("/")
async def root():
    return {"message": "欢迎使用智能数据分析对话机器人API"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "detail": traceback.format_exc()
        }
    ) 