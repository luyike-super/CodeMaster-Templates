# 导入必要的库
import os  # 用于处理文件路径
import re  # 用于正则表达式操作
from datetime import datetime  # 用于获取当前时间

# 导入LangChain和LangGraph相关组件
from langchain_core.prompts import PromptTemplate  # 用于创建提示模板
from langgraph.prebuilt.chat_agent_executor import AgentState  # 用于管理代理状态


# 获取提示词模板函数
def get_prompt_template(prompt_name: str) -> str:
    """从文件中读取提示词模板并进行必要的格式转换
    
    Args:
        prompt_name: 提示词模板文件名（不含扩展名）
        
    Returns:
        格式化后的提示词模板字符串
    """
    # 从当前文件所在目录读取对应的提示词模板文件
    template = open(os.path.join(os.path.dirname(__file__), f"{prompt_name}.md")).read()
    # 使用反斜杠转义花括号
    template = template.replace("{", "{{").replace("}", "}}")
    # 将 `<<VAR>>` 替换为 `{VAR}`
    template = re.sub(r"<<([^>>]+)>>", r"{\1}", template)
    return template


# 应用提示词模板函数
def apply_prompt_template(prompt_name: str, state: AgentState) -> list:
    """将提示词模板应用到当前状态，生成系统提示消息
    
    Args:
        prompt_name: 提示词模板文件名（不含扩展名）
        state: 代理状态对象，包含消息历史等信息
        
    Returns:
        包含系统提示和历史消息的列表
    """
    # 创建系统提示，填充当前时间和状态变量
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],  # 定义模板中可用的变量
        template=get_prompt_template(prompt_name),  # 获取提示词模板
    ).format(CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"), **state)  # 填充当前时间和状态变量
    # 返回系统提示和历史消息的组合
    # 系统提示作为第一条消息，角色为system，后面跟着状态中的历史消息
    return [{"role": "system", "content": system_prompt}] + state["messages"]


print("======================使用方法提示===============================================")
# 高级版本
research_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["researcher"]),
    tools=[tavily_tool, crawl_tool],
    prompt=lambda state: apply_prompt_template("researcher", state),
)

# 简单版本
messages = apply_prompt_template("supervisor", state)