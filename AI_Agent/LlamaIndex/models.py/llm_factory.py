from typing import Dict, Type, Optional, Any, Mapping
from abc import ABC, abstractmethod
from enum import Enum, auto
import os
from config.config_models import LLMConfig

class LLMProviderType(Enum):
    """LLM提供商类型枚举"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    QIANWENOPENAI = "qianwenopenai"
    QIANWENDASHSCOPE = "qianwendashscope"
    def __str__(self) -> str:
        return self.value 

class LLMProvider(ABC):
    """LLM提供商的抽象基类，定义所有LLM提供商必须实现的接口"""
    
    @abstractmethod
    def get_llm(self, **kwargs) -> Any:
        """返回配置好的LLM实例"""
        pass

class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        from llama_index.llms.deepseek import DeepSeek
        
        # 从配置类获取配置
        config = LLMConfig.get_deepseek_config()
        
        # 使用传入的参数覆盖默认配置
        config.update(kwargs)
        
        return DeepSeek(**config)

class QianWenProviderWithOpenAILike(LLMProvider):
    """OpenAI LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        from llama_index.llms.openai_like import OpenAILike
        
        # 从配置类获取配置
        config = LLMConfig.get_qianwen_openai_config()
        
        # 使用传入的参数覆盖默认配置
        if "model" in kwargs:
            config["model"] = kwargs.pop("model")
        if "api_base" in kwargs:
            config["api_base"] = kwargs.pop("api_base")
        if "api_key" in kwargs:
            config["api_key"] = kwargs.pop("api_key")
        if "is_chat_model" in kwargs:
            config["is_chat_model"] = kwargs.pop("is_chat_model")
            
        config.update(kwargs)
        
        return OpenAILike(**config)

class QianWenProviderWithDashScope(LLMProvider):
    """千问 LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        from llama_index.llms.dashscope import DashScope
        
        # 从配置类获取配置
        config = LLMConfig.get_qianwen_dashscope_config()
        
        # 使用传入的参数覆盖默认配置
        if "model_name" in kwargs:
            config["model_name"] = kwargs.pop("model_name")
        if "api_key" in kwargs:
            config["api_key"] = kwargs.pop("api_key")
            
        config.update(kwargs)
        
        return DashScope(**config)

class OpenAIProvider(LLMProvider):
    """OpenAI LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        from llama_index.llms.openai import OpenAI
        
        # 从配置类获取配置
        config = LLMConfig.get_openai_config()
        
        # 使用传入的参数覆盖默认配置
        config.update(kwargs)
        
        return OpenAI(**config)

class LLMFactory:
    """LLM工厂类，用于创建不同的LLM实例"""
    
    # 注册所有可用的LLM提供商
    _providers: Dict[LLMProviderType, Type[LLMProvider]] = {
        LLMProviderType.DEEPSEEK: DeepSeekProvider,
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.QIANWENOPENAI: QianWenProviderWithOpenAILike,
        LLMProviderType.QIANWENDASHSCOPE: QianWenProviderWithDashScope
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