from typing import Dict, Any
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMConfig:
    """LLM配置类，用于存储和管理所有LLM相关的配置"""
    
    # DeepSeek配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
    
    # DashScope配置 (千问)
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    QIANWEN_MODEL = os.getenv("QIANWEN_MODEL", "qwen-plus")
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # 千问OpenAI兼容模式配置
    QIANWEN_OPENAI_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 嵌入模型配置
    DASHSCOPE_EMBEDDING_MODEL = os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v2")
    
    @classmethod
    def get_deepseek_config(cls, **kwargs) -> Dict[str, Any]:
        """获取DeepSeek配置"""
        config = {
            "api_key": cls.DEEPSEEK_API_KEY,
            "model": cls.DEEPSEEK_MODEL,
            "temperature": 0.2,
        }
        config.update(kwargs)
        return config
    
    @classmethod
    def get_qianwen_openai_config(cls, **kwargs) -> Dict[str, Any]:
        """获取千问OpenAI兼容模式配置"""
        config = {
            "model": cls.QIANWEN_MODEL,
            "api_base": cls.QIANWEN_OPENAI_BASE,
            "api_key": cls.DASHSCOPE_API_KEY,
            "is_chat_model": True,
        }
        config.update(kwargs)
        return config
    
    @classmethod
    def get_qianwen_dashscope_config(cls, **kwargs) -> Dict[str, Any]:
        """获取千问DashScope配置"""
        config = {
            "model_name": cls.QIANWEN_MODEL,
            "api_key": cls.DASHSCOPE_API_KEY,
        }
        config.update(kwargs)
        return config
        
    @classmethod
    def get_openai_config(cls, **kwargs) -> Dict[str, Any]:
        """获取OpenAI配置"""
        config = {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
        }
        config.update(kwargs)
        return config
        
    @classmethod
    def get_dashscope_embedding_config(cls, **kwargs) -> Dict[str, Any]:
        """获取DashScope嵌入模型配置"""
        config = {
            "model_name": cls.DASHSCOPE_EMBEDDING_MODEL,
            "api_key": cls.DASHSCOPE_API_KEY,
        }
        config.update(kwargs)
        return config
