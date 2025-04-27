import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 大模型配置
    OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # 文件上传配置
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    
    # 确保上传目录存在
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    # 允许的文件类型
    ALLOWED_EXTENSIONS = {'.csv', '.xlsx'}
    
    # 文件大小限制（100MB）
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    
    # 会话配置
    SESSION_TIMEOUT = 1800  # 30分钟
    
    # 重试配置
    MAX_RETRIES = 5

settings = Settings() 