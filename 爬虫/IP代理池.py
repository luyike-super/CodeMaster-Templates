
import time
import random
import requests
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('proxy_pool')

class ProxyPool:
    """代理池管理类，用于获取、管理和轮换HTTP代理"""
    
    def __init__(self, change_interval=60, use_proxy=True):
        """
        初始化代理池
        
        Args:
            change_interval: 更换代理的时间间隔（秒）
            use_proxy: 是否使用代理
        """
        # 免费代理API来源
        self.free_proxy_apis = [
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
        ]
        
        # 手动代理列表
        self.manual_proxy_list = []
        
        # 当前可用的代理列表
        self.available_proxies = []
        
        # 当前正在使用的代理
        self.current_proxy = None
        
        # 上次更换代理的时间
        self.last_change_time = 0
        
        # 更换代理的时间间隔（秒）
        self.change_interval = change_interval
        
        # 是否使用代理
        self.use_proxy = use_proxy
    
    def add_manual_proxy(self, proxy):
        """
        添加手动代理到代理池
        
        Args:
            proxy: 代理URL，格式为 "http://ip:port" 或 "http://username:password@ip:port"
        """
        if not proxy.startswith('http'):
            proxy = f"http://{proxy}"
        self.manual_proxy_list.append(proxy)
        logger.info(f"已添加手动代理: {proxy}")
    
    def clear_manual_proxies(self):
        """清空手动代理列表"""
        self.manual_proxy_list = []
        logger.info("已清空手动代理列表")
    
    def get_proxy_list(self):
        """
        从多个来源获取代理列表
        
        Returns:
            list: 代理列表
        """
        proxy_list = []
        
        # 首先添加手动代理列表
        proxy_list.extend(self.manual_proxy_list)
        
        # 如果不使用代理，直接返回空列表
        if not self.use_proxy:
            return proxy_list
        
        # 然后尝试从API获取代理
        for api_url in self.free_proxy_apis:
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    # 解析代理列表（假设每行一个代理）
                    api_proxies = response.text.strip().split('\n')
                    valid_proxies = []
                    for proxy in api_proxies:
                        if proxy and ':' in proxy:  # 确保代理格式正确
                            # 如果代理没有协议前缀，添加http://
                            if not proxy.startswith('http'):
                                proxy = f"http://{proxy}"
                            valid_proxies.append(proxy)
                    proxy_list.extend(valid_proxies)
                    logger.info(f"从 {api_url} 获取了 {len(valid_proxies)} 个代理")
            except Exception as e:
                logger.error(f"从 {api_url} 获取代理失败: {e}")
        
        # 更新可用代理列表
        self.available_proxies = proxy_list
        logger.info(f"代理池中共有 {len(proxy_list)} 个代理")
        return proxy_list
    
    def select_random_proxy(self):
        """
        从代理列表中随机选择一个
        
        Returns:
            str: 选择的代理URL
        """
        if not self.available_proxies:
            # 如果没有可用代理，尝试重新获取
            self.available_proxies = self.get_proxy_list()
        
        if not self.available_proxies:
            logger.warning("代理列表为空，无法选择代理")
            return None
        
        proxy = random.choice(self.available_proxies)
        logger.info(f"选择代理: {proxy}")
        return proxy
    
    def get_current_proxy(self):
        """
        获取当前代理
        
        Returns:
            str: 当前使用的代理URL
        """
        return self.current_proxy
    
    def change_proxy_if_needed(self):
        """
        检查是否需要更换代理
        
        Returns:
            str: 当前代理URL，如果更换了代理则返回新代理
        """
        if not self.use_proxy:
            return None
        
        current_time = time.time()
        
        # 如果是首次使用代理或者已经超过更换间隔
        if self.current_proxy is None or (current_time - self.last_change_time) >= self.change_interval:
            proxy_list = self.get_proxy_list()
            if proxy_list:
                self.current_proxy = self.select_random_proxy()
                self.last_change_time = current_time
                logger.info(f"代理已更换为: {self.current_proxy}")
            else:
                logger.warning("无法获取代理列表，将不使用代理")
                self.current_proxy = None
        
        return self.current_proxy
    
    def get_playwright_proxy_config(self, proxy):
        """
        将代理URL转换为Playwright的代理配置格式
        
        Args:
            proxy: 代理URL，格式为 "http://ip:port" 或 "http://username:password@ip:port"
            
        Returns:
            dict: Playwright的代理配置
        """
        if not proxy:
            return None
        
        proxy_url = proxy.replace("http://", "")
        
        if "@" in proxy_url:
            # 处理有用户名密码的代理
            auth, address = proxy_url.split("@", 1)
            username, password = auth.split(":", 1)
            return {
                "server": f"http://{address}",
                "username": username,
                "password": password
            }
        else:
            # 处理没有用户名密码的代理
            return {
                "server": f"http://{proxy_url}"
            }
    
    def test_proxy(self, proxy, test_url="https://www.google.com", timeout=5):
        """
        测试代理是否可用
        
        Args:
            proxy: 代理URL
            test_url: 测试URL
            timeout: 超时时间（秒）
            
        Returns:
            bool: 代理是否可用
        """
        try:
            response = requests.get(
                test_url, 
                proxies={"http": proxy, "https": proxy}, 
                timeout=timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"代理 {proxy} 测试失败: {e}")
            return False
    
    def remove_proxy(self, proxy):
        """
        从可用代理列表中移除指定代理
        
        Args:
            proxy: 要移除的代理URL
        """
        if proxy in self.available_proxies:
            self.available_proxies.remove(proxy)
            logger.info(f"已从代理池中移除代理: {proxy}")
            
            # 如果移除的是当前代理，则更新当前代理
            if proxy == self.current_proxy:
                self.current_proxy = None
                self.last_change_time = 0  # 重置时间，以便下次立即更换