from typing import Dict, Type, Any
from abc import ABC, abstractmethod
from config.config_models import LLMConfig


class EmbeddingProviderType:
    DASHSCOPE = "dashscope"
    # 未来可扩展更多类型

class EmbeddingProvider(ABC):
    """Embedding 提供商的抽象基类，定义所有 Embedding 提供商必须实现的接口"""
    @abstractmethod
    def get_embedding(self, **kwargs) -> Any:
        """返回配置好的 Embedding 实例"""
        pass

class DashScopeEmbeddingProvider(EmbeddingProvider):
    """DashScope Embedding 提供商实现"""
    def get_embedding(self, **kwargs) -> Any:
        from llama_index.embeddings.dashscope import DashScopeEmbedding
        
        # 从配置类获取配置
        config = LLMConfig.get_dashscope_embedding_config()
        
        # 使用传入的参数覆盖默认配置
        if "model_name" in kwargs:
            config["model_name"] = kwargs.pop("model_name")
        if "api_key" in kwargs:
            config["api_key"] = kwargs.pop("api_key")
        
        config.update(kwargs)
        
        return DashScopeEmbedding(**config)



class EmbeddingFactory:
    """Embedding 工厂类，用于创建不同的 Embedding 实例"""
    _providers: Dict[str, Type[EmbeddingProvider]] = {
        EmbeddingProviderType.DASHSCOPE: DashScopeEmbeddingProvider
    }

    @classmethod
    def register_provider(cls, provider_type: str, provider_class: Type[EmbeddingProvider]) -> None:
        cls._providers[provider_type] = provider_class

    @classmethod
    def create_embedding(cls, provider_type: str, **kwargs) -> Any:
        if provider_type not in cls._providers:
            raise ValueError(f"不支持的Embedding提供商: {provider_type}")
        provider = cls._providers[provider_type]()
        return provider.get_embedding(**kwargs)

    @classmethod
    def get_available_providers(cls) -> list:
        return list(cls._providers.keys()) 