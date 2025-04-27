#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import asyncio
from playwright.async_api import async_playwright

class BrowserLoginCache:
    """浏览器登录状态缓存管理类"""
    
    def __init__(self, config_path="browser_config.json", home_url=None):
        """初始化浏览器登录缓存管理器
        
        Args:
            config_path: 配置文件路径，用于存储登录信息和配置
            home_url: 首页URL，用于检查登录状态
        """
        self.config_path = config_path
        self.home_url = home_url
        self.config = self._load_config()
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
    
    def _load_config(self):
        """加载配置文件，如果不存在则创建默认配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            default_config = {
                "storage_state": None,  # 用于存储登录状态
                "show_browser": True,   # 是否显示浏览器
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            return default_config
    
    def _save_config(self):
        """保存配置到本地"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    async def init_browser(self):
        """初始化浏览器"""
        self.playwright = await async_playwright().start()
        # 根据配置决定是否显示浏览器
        browser_options = {
            "headless": not self.config.get("show_browser", True)
        }
        
        self.browser = await self.playwright.chromium.launch(**browser_options)
        
        # 如果有登录状态，则加载它
        context_options = {}
        storage_state = self.config.get("storage_state")
        
        if storage_state:
            print("检测到已保存的登录状态，尝试使用...")
            # 将存储状态写入临时文件
            temp_state_path = "temp_state.json"
            with open(temp_state_path, "w", encoding="utf-8") as f:
                json.dump(storage_state, f)
            
            # 使用文件路径加载状态
            context_options["storage_state"] = temp_state_path
        
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        # 删除临时文件
        if storage_state and os.path.exists("temp_state.json"):
            os.remove("temp_state.json")
    
    async def close_browser(self):
        """关闭浏览器和相关资源"""
        if self.page:
            await self.page.close()
            self.page = None
            
        if self.context:
            await self.context.close()
            self.context = None
            
        if self.browser:
            await self.browser.close()
            self.browser = None
            
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    async def save_login_state(self):
        """保存登录状态"""
        if self.context:
            try:
                # 获取当前的storage_state并保存到配置中
                storage_path = "login_state.json"
                await self.context.storage_state(path=storage_path)
                
                # 读取保存的状态并存入配置
                with open(storage_path, "r", encoding="utf-8") as f:
                    storage = json.load(f)
                
                self.config["storage_state"] = storage
                self._save_config()
                print(f"登录状态已保存到 {self.config_path}")
                
                # 清理临时文件
                if os.path.exists(storage_path):
                    os.remove(storage_path)
                    
                return True
            except Exception as e:
                print(f"保存登录状态时出错: {e}")
                return False
    
    async def check_login(self, login_selector=None):
        """检查是否已经登录
        
        Args:
            login_selector: 用于检查登录状态的选择器或XPath
            
        Returns:
            bool: 是否已登录
        """
        if not login_selector:
            return False
            
        try:
            # 使用提供的选择器检查登录状态
            login_element = await self.page.is_visible(login_selector)
            return login_element
        except Exception as e:
            print(f"检查登录状态时出错: {e}")
            return False
    
    async def wait_for_login(self, login_selector, login_url=None, check_interval=2, timeout=300):
        """等待用户登录完成
        
        Args:
            login_selector: 用于检查登录状态的选择器或XPath
            login_url: 登录页面URL
            check_interval: 检查登录状态的时间间隔(秒)
            timeout: 超时时间(秒)，超过此时间将退出等待
        
        Returns:
            bool: 是否成功登录
        """
        # 如果提供了登录URL，则导航到登录页面
        if login_url:
            await self.page.goto(login_url)
            
        print("等待用户登录...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self.check_login(login_selector):
                print("登录成功！")
                # 保存登录状态
                await self.save_login_state()
                return True
            
            print(f"未检测到登录，{check_interval}秒后重试...")
            await asyncio.sleep(check_interval)
        
        print(f"登录等待超时（{timeout}秒）")
        return False
    
    async def login_with_cache(self, home_url=None, login_url=None, login_selector=None):
        """使用缓存登录
        
        如果有保存的登录状态，会尝试使用它；否则会打开登录页面等待用户手动登录
        
        Args:
            home_url: 首页URL，不提供则使用初始化时设置的home_url
            login_url: 登录页面URL
            login_selector: 用于检查登录状态的选择器或XPath
            
        Returns:
            bool: 是否成功登录
        """
        if not self.page:
            await self.init_browser()
        
        # 设置home_url
        if home_url:
            self.home_url = home_url
        
        if not self.home_url:
            raise ValueError("未设置首页URL")
        
        # 先访问首页，再检查登录状态
        await self.page.goto(self.home_url)
        
        # 检查是否已经登录
        if await self.check_login(login_selector):
            print("已使用保存的登录状态成功登录")
            return True
            
        # 如果没有登录成功，则前往登录页面
        print("保存的登录状态已失效或不存在，前往登录页面...")
        
        return await self.wait_for_login(
            login_selector=login_selector,
            login_url=login_url,
            check_interval=2,
            timeout=300
        )

# 使用示例
async def example_usage():
    """示例使用方法"""
    import time
    # 创建缓存管理器实例
    cache_manager = BrowserLoginCache(
        config_path="browser_config.json",
        home_url="https://example.com/"
    )
    
    try:
        # 初始化浏览器
        await cache_manager.init_browser()
        
        # 使用缓存登录
        login_success = await cache_manager.login_with_cache(
            login_url="https://example.com/login",
            login_selector="xpath=//div[contains(@class, 'user-info')]"
        )
        
        if login_success:
            print("登录成功，执行后续操作...")
            # 这里可以执行需要登录后才能进行的操作
            await asyncio.sleep(5)  # 示例：等待5秒
        else:
            print("登录失败")
            
    finally:
        # 确保关闭浏览器
        await cache_manager.close_browser()

if __name__ == "__main__":
    # 使用示例
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(example_usage())
    finally:
        loop.close() 