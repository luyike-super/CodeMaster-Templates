from enum import Enum, auto

class SearchEngineType(Enum):
    """搜索引擎类型枚举"""
    TAVILY = auto()  # Tavily搜索引擎
    GOOGLE = auto()  # Google搜索引擎
    BING = auto()    # Bing搜索引擎
    # 可以添加更多搜索引擎类型
    
    def __str__(self):
        return self.name.lower() 