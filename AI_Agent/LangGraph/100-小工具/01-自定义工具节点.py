
# 定义 BasicToolNode，用于执行工具请求
class BasicToolNode:
    """一个在最后一条 AIMessage 中执行工具请求的节点。
    
    该节点会检查最后一条 AI 消息中的工具调用请求，并依次执行这些工具调用。
    """

    def __init__(self, tools: list) -> None:
        # tools 是一个包含所有可用工具的列表，我们将其转化为字典，
        # 通过工具名称（tool.name）来访问具体的工具
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        """执行工具调用
        
        参数:
        inputs: 包含 "messages" 键的字典，"messages" 是对话消息的列表，
                其中最后一条消息可能包含工具调用的请求。
        
        返回:
        包含工具调用结果的消息列表
        """
        # 获取消息列表中的最后一条消息，判断是否包含工具调用请求
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("输入中未找到消息")

        # 用于保存工具调用的结果
        outputs = []

        # 遍历工具调用请求，执行工具并将结果返回
        for tool_call in message.tool_calls:
            # 根据工具名称找到相应的工具，并调用工具的 invoke 方法执行工具
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            # 将工具调用结果作为 ToolMessage 保存下来
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),  # 工具调用的结果以 JSON 格式保存
                    name=tool_call["name"],  # 工具的名称
                    tool_call_id=tool_call["id"],  # 工具调用的唯一标识符
                )
            )
        # 返回包含工具调用结果的消息
        return {"messages": outputs}


"""
=========================================================================

完整案例


=========================================================================
"""
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
import json
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from app.llm import llm_deepseek
# 定义工具
@tool
def search_knowledge_base(query: str) -> str:
    """搜索知识库以回答用户的问题"""
    # 简单模拟知识库搜索
    knowledge = {
        "人工智能": "人工智能是计算机科学的一个分支，致力于创造能够模拟人类智能的系统。",
        "机器学习": "机器学习是人工智能的一个子领域，专注于开发能够从数据中学习的算法。",
        "深度学习": "深度学习是机器学习的一种方法，使用神经网络进行学习。"
    }
    
    for key, value in knowledge.items():
        if key in query:
            return value
    
    return "抱歉，我没有找到相关信息。"

# 创建工具列表
tools = [search_knowledge_base]

# 定义状态
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 定义 BasicToolNode，用于执行工具请求
class BasicToolNode:
    """一个在最后一条 AIMessage 中执行工具请求的节点。
    
    该节点会检查最后一条 AI 消息中的工具调用请求，并依次执行这些工具调用。
    """

    def __init__(self, tools: list) -> None:
        # tools 是一个包含所有可用工具的列表，我们将其转化为字典，
        # 通过工具名称（tool.name）来访问具体的工具
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        """执行工具调用
        
        参数:
        inputs: 包含 "messages" 键的字典，"messages" 是对话消息的列表，
                其中最后一条消息可能包含工具调用的请求。
        
        返回:
        包含工具调用结果的消息列表
        """
        # 获取消息列表中的最后一条消息，判断是否包含工具调用请求
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("输入中未找到消息")

        # 用于保存工具调用的结果
        outputs = []

        # 遍历工具调用请求，执行工具并将结果返回
        for tool_call in message.tool_calls:
            # 根据工具名称找到相应的工具，并调用工具的 invoke 方法执行工具
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            # 将工具调用结果作为 ToolMessage 保存下来
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),  # 工具调用的结果以 JSON 格式保存
                    name=tool_call["name"],  # 工具的名称
                    tool_call_id=tool_call["id"],  # 工具调用的唯一标识符
                )
            )
        # 返回包含工具调用结果的消息
        return {"messages": outputs}

# 定义路由函数，检查工具调用
def route_tools(state: State) -> Literal["tools", "__end__"]:
    """
    使用条件边来检查最后一条消息中  是否有工具调用。
    
    参数:
    state: 状态字典或消息列表，用于存储当前对话的状态和消息。
    
    返回:
    如果最后一条消息包含工具调用，返回 "tools" 节点，表示需要执行工具调用；
    否则返回 "__end__"，表示直接结束流程。
    """
    # 检查状态是否是列表类型（即消息列表），取最后一条 AI 消息
    if isinstance(state, list):
        ai_message = state[-1]
    # 否则从状态字典中获取 "messages" 键，取最后一条消息
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    # 如果没有找到消息，则抛出异常
    else:
        raise ValueError(f"输入状态中未找到消息: {state}")

    # 检查最后一条消息是否有工具调用请求
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"  # 如果有工具调用请求，返回 "tools" 节点
    return "__end__"  # 否则返回 "__end__"，流程结束

# 更新聊天机器人节点函数，支持工具调用
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 构建图
def build_graph():
    # 初始化图构建器
    graph_builder = StateGraph(State)
    
    # 初始化 LLM 并绑定搜索工具
    chat_model = llm_deepseek
    global llm_with_tools
    llm_with_tools = chat_model.bind_tools(tools)
    
    # 将节点添加到状态图中
    graph_builder.add_node("chatbot", chatbot)
    
    # 将 BasicToolNode 添加到状态图中
    tool_node = BasicToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    
    # 添加条件边，判断是否需要调用工具
    graph_builder.add_conditional_edges(
        "chatbot",  # 从聊天机器人节点开始
        route_tools,  # 路由函数，决定下一个节点
        {
            "tools": "tools", 
            "__end__": "__end__"
        },  # 定义条件的输出，工具调用走 "tools"，否则走 "__end__"
    )
    
    # 当工具调用完成后，返回到聊天机器人节点以继续对话
    graph_builder.add_edge("tools", "chatbot")
    
    # 指定从 START 节点开始，进入聊天机器人节点
    graph_builder.add_edge(START, "chatbot")
    
    # 编译状态图，生成可执行的流程图
    return graph_builder.compile()

# 创建可执行的图
graph = build_graph()

# 可视化图（如果在IPython环境中）
def visualize_graph():
    from IPython.display import Image, display
    graph2 = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(graph2)

# 运行对话
def run_conversation(user_input: str):
    from langchain_core.messages import HumanMessage
    # 创建一个包含用户输入的初始状态
    inputs = {"messages": [HumanMessage(content=user_input)]}
    
    # 运行图并返回结果
    return graph.invoke(inputs)

# 如果是主程序，执行可视化
if __name__ == "__main__":
    visualize_graph()

    result = run_conversation("什么是人工智能?")
    print(result["messages"][-1].content)
