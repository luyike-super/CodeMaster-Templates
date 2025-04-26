from enum import Enum, auto

class LLMProviderType(Enum):
    """LLM提供商类型枚举"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    QIANWEN = "qianwen"
    
    def __str__(self) -> str:
        return self.value 