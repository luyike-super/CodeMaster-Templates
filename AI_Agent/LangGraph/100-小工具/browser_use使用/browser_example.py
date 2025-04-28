import asyncio
import logging
import os

from browser_use import Browser, BrowserConfig, Agent as BrowserAgent
from app.llm import LLMFactory, LLMProviderType

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 使用DeepSeek模型
llm_deepseek = LLMFactory.create_llm(LLMProviderType.DEEPSEEK)

async def main():
    # 创建浏览器实例
    browser = Browser(config=BrowserConfig(headless=False))  # headless=False 会显示浏览器界面
    
    print("浏览器实例创建成功，准备启动浏览器代理...")
    
    prompt = """
                访问boss直聘， 搜索 `AI Agent`, 开始重复的简历投递工作：
                    1. 点击html 名 <div class=card-area"> 的标签的第一个标签 ,  右侧选择`立即沟通` ，
                        会弹出弹窗， 请选择`继续沟通`， 页面切换到聊天界面， 发送消息`你好，我正在使用Agent自动工作，有兴趣可以联系我`。
                         发送完。回退浏览器一次。回到原来的里面
                    2. 稍微向下滚动一点， 选择第二个标签... 一直循环下去 
                    3. 如果你执行过程中， 偏离了预期的循环操作， 就从头开始
            """

    # 创建浏览器代理
    agent = BrowserAgent(
        task=prompt,  # 任务描述
        llm=llm_deepseek,  # 使用DeepSeek模型
        browser=browser,  # 浏览器实例
    )
    
    try:
        print("开始执行浏览器任务...")
        # 运行代理
        result = await agent.run()
        print(f"浏览器任务执行结果: {result}")
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
    finally:
        # 确保浏览器关闭
        await browser.close()
        print("浏览器已关闭")

if __name__ == "__main__":
  
    # 运行异步主函数
    asyncio.run(main()) 