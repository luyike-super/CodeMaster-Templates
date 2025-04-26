from typing import Dict, Type, Optional, Any, Mapping
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os
from .llm_providers import LLMProviderType

load_dotenv()

class LLMProvider(ABC):
    """LLM提供商的抽象基类，定义所有LLM提供商必须实现的接口"""
    
    @abstractmethod
    def get_llm(self, **kwargs) -> Any:
        """返回配置好的LLM实例"""
        pass

class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        from langchain_deepseek import ChatDeepSeek
        
        # 默认配置
        config = {
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "api_base": os.getenv("DEEPSEEK_API_BASE"),
            "model": os.getenv("DEEPSEEK_MODEL"),
            "temperature": 0,
            "max_tokens": None,
            "timeout": 120,
            "max_retries": 5,
            "default_headers": {"Connection": "keep-alive"}
        }
        
        # 使用传入的参数覆盖默认配置
        config.update(kwargs)
        
        return ChatDeepSeek(**config)

class OpenAIProvider(LLMProvider):
    """OpenAI LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        pass

class QianWenProvider(LLMProvider):
    """千问 LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        pass


class LLMFactory:
    """LLM工厂类，用于创建不同的LLM实例"""
    
    # 注册所有可用的LLM提供商
    _providers: Dict[LLMProviderType, Type[LLMProvider]] = {
        LLMProviderType.DEEPSEEK: DeepSeekProvider,
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.QIANWEN: QianWenProvider
    }
    
    @classmethod
    def register_provider(cls, provider_type: LLMProviderType, provider_class: Type[LLMProvider]) -> None:
        """注册新的LLM提供商"""
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def create_llm(cls, provider_type: LLMProviderType, **kwargs) -> Any:
        """
        根据提供商类型创建对应的LLM实例
        
        Args:
            provider_type: LLM提供商类型枚举
            **kwargs: 可选的配置参数，会覆盖默认配置
                - temperature: 温度参数，控制生成文本的随机性
                - model: 模型名称
                - max_tokens: 最大生成token数
                - 其他特定LLM提供商的参数
        
        Returns:
            配置好的LLM实例
        """
        if provider_type not in cls._providers:
            raise ValueError(f"不支持的LLM提供商: {provider_type}")
        
        provider = cls._providers[provider_type]()
        return provider.get_llm(**kwargs)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取所有可用的LLM提供商列表"""
        return list(cls._providers.keys()) 