# playwright 版本

def continuous_scroll():
    try:
        # 初始化浏览器连接
        init_success = init_browser_sync()
        if not init_success:
            print("浏览器初始化失败，无法继续操作")
            return
            
        print("开始测试元素滚动功能 (按Ctrl+C中断)...")
        
        # 指定的XPath元素
        xpath_selector = '/html/body/div[1]/div[2]/div[3]/div/div/div[1]'
        print(f"将使用XPath: {xpath_selector}")
        
        scroll_count = 0
        # 循环测试滚动，直到程序被中断
        while True:
            try:
                scroll_count += 1
                print(f"======== 执行第{scroll_count}次滚动 ========")
                
                # 使用XPath定位元素并滚动
                print(f"尝试使用XPath滚动元素")
                element_exists = page.evaluate(f"""() => {{
                    const element = document.evaluate('{xpath_selector}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (element) {{
                        console.log('找到目标元素，尝试滚动');
                        element.scrollBy(0, 300);
                        return true;
                    }}
                    return false;
                }}""")
                
                if element_exists:
                    print("成功找到并滚动目标元素")
                else:
                    print("未找到目标元素，尝试其他方法")
                    
                    # 尝试滚动整个页面作为备选方案
                    print("尝试滚动整个页面")
                    page.evaluate("() => { window.scrollBy(0, 300); }")
                
                # 随机延时1-3秒
                delay = random.uniform(1, 3)
                print(f"等待 {delay:.2f} 秒...")
                time.sleep(delay)
                
                # 打印分隔线
                print("-" * 50)
                
            except Exception as loop_error:
                print(f"单次滚动过程中出现错误: {str(loop_error)}")
                # 短暂等待后继续
                time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
    except Exception as e:
        print(f"操作过程中出现错误: {str(e)}")
    finally:
        # 关闭浏览器连接
        close_browser_sync()