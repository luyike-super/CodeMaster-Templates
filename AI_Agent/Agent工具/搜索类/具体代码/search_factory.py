from app.utils.search.search_engine import SearchEngine, TavilySearchEngine
from app.utils.search.search_engine_type import SearchEngineType
from dotenv import load_dotenv
import os

class SearchEngineFactory:
    """搜索引擎工厂类，负责创建不同类型的搜索引擎实例"""
    
    @staticmethod
    def create_engine(engine_type: SearchEngineType, **kwargs) -> SearchEngine:
        """创建搜索引擎实例
        
        Args:
            engine_type: 搜索引擎类型（枚举）
            **kwargs: 搜索引擎配置参数
            
        Returns:
            搜索引擎实例
        
        Raises:
            ValueError: 当指定的搜索引擎类型不受支持时
        """
        if engine_type == SearchEngineType.TAVILY:
            api_key = kwargs.get("api_key")
            if not api_key:
                load_dotenv()
                api_key = os.getenv("TAVILY_API_KEY")
            return TavilySearchEngine(api_key=api_key)
        # 可以在此添加其他搜索引擎的支持
        # elif engine_type == SearchEngineType.GOOGLE:
        #     return GoogleSearchEngine(**kwargs)
        # elif engine_type == SearchEngineType.BING:
        #     return BingSearchEngine(**kwargs)
        else:
            raise ValueError(f"不支持的搜索引擎类型: {engine_type}") 