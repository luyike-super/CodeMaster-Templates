from abc import ABC, abstractmethod
from typing import List, Dict, Any
import asyncio
from tavily import TavilyClient
from dotenv import load_dotenv
import os
import requests
import json

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

# Jina搜索引擎实现
class JinaSearchEngine(SearchEngine):
    def __init__(self, api_key: str):
        """初始化Jina搜索引擎
        
        Args:
            api_key: Jina API密钥
        """
        self.api_key = api_key
        self.search_url = "https://s.jina.ai/"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-No-Cache": "true"
        }
    
    def search(self, query: str, options: str = "Default") -> Dict[str, Any]:
        """执行Jina搜索查询
        
        Args:
            query: 搜索查询字符串
            options: 输出格式选项 ("Default", "Markdown", "HTML", "Text", "Screenshot", "Pageshot")
            
        Returns:
            搜索结果字典
        """
        try:
            payload = {
                "q": query,
                "options": options
            }
            
            response = requests.post(
                self.search_url, 
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Jina搜索出错: {e}")
            return {"error": str(e)}
    
    def search_with_site(self, query: str, site: str, options: str = "Default") -> Dict[str, Any]:
        """在指定网站内执行Jina搜索查询
        
        Args:
            query: 搜索查询字符串
            site: 限制搜索的网站域名
            options: 输出格式选项
            
        Returns:
            搜索结果字典
        """
        try:
            headers = self.headers.copy()
            headers["X-Site"] = site
            
            payload = {
                "q": query,
                "options": options
            }
            
            response = requests.post(
                self.search_url, 
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Jina站内搜索出错: {e}")
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
                result = self.search(query)
                results.append(result)
            except Exception as e:
                print(f"Jina子查询 '{query}' 搜索出错: {e}")
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
                result = await loop.run_in_executor(None, lambda: self.search(query))
                return result
            except Exception as e:
                print(f"Jina异步查询 '{query}' 搜索出错: {e}")
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
        
    def read_webpage(self, url: str, options: str = "Default") -> Dict[str, Any]:
        """使用Jina Reader API获取网页内容
        
        Args:
            url: 要读取的网页URL
            options: 输出格式选项 ("Default", "Markdown", "HTML", "Text", "Screenshot", "Pageshot")
            
        Returns:
            网页内容字典
        """
        try:
            reader_url = "https://r.jina.ai/"
            payload = {
                "url": url,
                "options": options
            }
            
            headers = self.headers.copy()
            headers["X-With-Links-Summary"] = "true"
            headers["X-With-Images-Summary"] = "true"
            
            response = requests.post(
                reader_url, 
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Jina网页读取出错: {e}")
            return {"error": str(e)}
            
    def rerank(self, query: str, documents: List[str], model: str = "jina-reranker-v2-base-multilingual", top_n: int = None) -> Dict[str, Any]:
        """使用Jina重排序API对搜索结果进行重排序
        
        Args:
            query: 搜索查询
            documents: 要重排序的文档列表
            model: 使用的模型名称
            top_n: 返回的结果数量
            
        Returns:
            重排序结果字典
        """
        try:
            rerank_url = "https://api.jina.ai/v1/rerank"
            payload = {
                "model": model,
                "query": query,
                "documents": documents,
            }
            
            if top_n:
                payload["top_n"] = top_n
                
            response = requests.post(
                rerank_url, 
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Jina重排序出错: {e}")
            return {"error": str(e)}
            
    def deep_search(self, query: str, options: str = "Markdown", rerank: bool = True, model: str = "jina-reranker-v2-base-multilingual", top_n: int = 3) -> Dict[str, Any]:
        """执行深度搜索: 搜索 + 重排序
        
        Args:
            query: 搜索查询
            options: 输出格式选项
            rerank: 是否进行重排序
            model: 重排序使用的模型
            top_n: 返回的结果数量
            
        Returns:
            深度搜索结果
        """
        try:
            # 执行初步搜索
            search_results = self.search(query, options)
            
            if "error" in search_results:
                return search_results
                
            # 如果不需要重排序，直接返回搜索结果
            if not rerank:
                return search_results
            
            # 从搜索结果中提取文档内容
            documents = []
            for item in search_results.get("data", []):
                documents.append(item.get("content", ""))
            
            # 如果没有文档内容，返回原始搜索结果
            if not documents:
                return search_results
            
            # 执行重排序
            rerank_results = self.rerank(query, documents, model, top_n)
            
            # 如果重排序出错，返回原始搜索结果
            if "error" in rerank_results:
                return search_results
            
            # 构建最终结果
            final_results = {
                "original_search": search_results,
                "reranked_results": rerank_results,
                "top_results": []
            }
            
            # 根据重排序结果排列文档
            for result in rerank_results.get("results", []):
                idx = result.get("index")
                if idx is not None and idx < len(search_results.get("data", [])):
                    original_doc = search_results["data"][idx]
                    final_results["top_results"].append({
                        "document": original_doc,
                        "relevance_score": result.get("relevance_score")
                    })
            
            return final_results
        
        except Exception as e:
            print(f"Jina深度搜索出错: {e}")
            return {"error": str(e)}

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