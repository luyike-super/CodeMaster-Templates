from abc import ABC, abstractmethod
from typing import List, Dict, Any
import asyncio
from tavily import TavilyClient
from dotenv import load_dotenv
import os

# 抽象搜索引擎接口
class SearchEngine(ABC):
    @abstractmethod
    def search(self, query: str) -> Dict[str, Any]:
        """执行搜索查询"""
        pass
    
    @abstractmethod
    def search_with_subqueries(self, subqueries: List[str]) -> List[Dict[str, Any]]:
        """执行子查询搜索"""
        pass
    
    @abstractmethod
    async def search_async(self, queries: List[str], max_concurrency: int = 5) -> List[Dict[str, Any]]:
        """执行异步搜索"""
        pass

# Tavily搜索引擎实现
class TavilySearchEngine(SearchEngine):
    def __init__(self, api_key: str):
        """初始化Tavily搜索引擎
        
        Args:
            api_key: Tavily API密钥
        """
        self.client = TavilyClient(api_key=api_key)
    
    def search(self, query: str) -> Dict[str, Any]:
        """常规搜索方法
        
        Args:
            query: 搜索查询字符串
            
        Returns:
            搜索结果字典
        """
        try:
            response = self.client.search(query)
            return response
        except Exception as e:
            print(f"搜索出错: {e}")
            return {"error": str(e)}
    
    def search_with_subqueries(self, subqueries: List[str]) -> List[Dict[str, Any]]:
        """将查询拆分为较小的子查询进行搜索
        
        Args:
            subqueries: 子查询列表
            
        Returns:
            搜索结果列表
        """
        results = []
        for query in subqueries:
            try:
                result = self.client.search(query)
                results.append(result)
            except Exception as e:
                print(f"子查询 '{query}' 搜索出错: {e}")
                results.append({"query": query, "error": str(e)})
        return results
    
    async def search_async(self, queries: List[str], max_concurrency: int = 5) -> List[Dict[str, Any]]:
        """异步搜索多个查询
        
        Args:
            queries: 查询列表
            max_concurrency: 最大并发请求数
            
        Returns:
            搜索结果列表
        """
        async def _search_one(query: str) -> Dict[str, Any]:
            try:
                loop = asyncio.get_event_loop()
                # 在异步环境中调用同步方法
                result = await loop.run_in_executor(None, lambda: self.client.search(query))
                return result
            except Exception as e:
                print(f"异步查询 '{query}' 搜索出错: {e}")
                return {"query": query, "error": str(e)}
        
        # 限制并发请求数
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def _search_with_limit(query: str) -> Dict[str, Any]:
            async with semaphore:
                return await _search_one(query)
        
        # 并发执行所有查询
        tasks = [_search_with_limit(query) for query in queries]
        results = await asyncio.gather(*tasks)
        return results

# 可以在此添加其他搜索引擎实现
# class GoogleSearchEngine(SearchEngine):
#     def __init__(self, api_key: str):
#         """初始化Google搜索引擎"""
#         self.api_key = api_key
#         # 初始化Google搜索客户端
#     
#     def search(self, query: str) -> Dict[str, Any]:
#         """实现Google搜索逻辑"""
#         pass
#     
#     def search_with_subqueries(self, subqueries: List[str]) -> List[Dict[str, Any]]:
#         """实现Google子查询搜索逻辑"""
#         pass
#     
#     async def search_async(self, queries: List[str], max_concurrency: int = 5) -> List[Dict[str, Any]]:
#         """实现Google异步搜索逻辑"""
#         pass 