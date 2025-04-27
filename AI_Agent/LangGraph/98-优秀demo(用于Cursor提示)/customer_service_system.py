import operator
from typing import Annotated, List, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.graph.message import add_messages
from app.llm import LLMFactory, LLMProviderType
# 定义状态结构
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    next_agent: str
    customer_info: dict
    issue_solved: bool

# 定义工具
@tool
def get_customer_info(customer_id: str) -> dict:
    """根据客户ID获取客户基本信息"""
    # 模拟数据库查询
    return {
        "name": "张三",
        "id": customer_id,
        "membership_level": "VIP",
        "last_purchase": "2024-12-15"
    }

@tool
def check_order_status(order_id: str) -> str:
    """检查订单状态"""
    # 模拟订单查询
    return f"订单 {order_id} 状态：配送中，预计明天送达"

@tool
def refund_order(order_id: str, amount: float) -> str:
    """处理退款请求"""
    return f"已成功为订单 {order_id} 退款 {amount} 元"

# 创建两个Agent
class CustomerServiceSystem:
    def __init__(self):
        # 初始化模型
        self.model = LLMFactory.create_llm(LLMProviderType.DEEPSEEK)
        
        # 信息收集Agent使用的工具
        self.info_tools = [get_customer_info]
        self.info_tool_node = ToolNode(self.info_tools)
        
        # 问题解决Agent使用的工具
        self.solution_tools = [check_order_status, refund_order]
        self.solution_tool_node = ToolNode(self.solution_tools)
        
        # 绑定工具到模型
        self.info_model = self.model.bind_tools(self.info_tools)
        self.solution_model = self.model.bind_tools(self.solution_tools)
    
    def build_graph(self):
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("info_agent", self.info_agent)
        workflow.add_node("info_tools", self.info_tool_node)
        workflow.add_node("solution_agent", self.solution_agent)
        workflow.add_node("solution_tools", self.solution_tool_node)
        
        # 添加边
        workflow.set_entry_point("info_agent")
        
        # 信息收集Agent的路由逻辑
        workflow.add_conditional_edges(
            "info_agent",
            self.info_agent_router,
            {
                "tools": "info_tools",
                "solution": "solution_agent",
                "end": END
            }
        )
        
        # 工具节点回到对应的Agent
        workflow.add_edge("info_tools", "info_agent")
        
        # 问题解决Agent的路由逻辑
        workflow.add_conditional_edges(
            "solution_agent",
            self.solution_agent_router,
            {
                "tools": "solution_tools",
                "end": END
            }
        )
        
        workflow.add_edge("solution_tools", "solution_agent")
        
        return workflow.compile()
    
    def info_agent(self, state: AgentState):
        """信息收集Agent"""
        messages = state["messages"]
        response = self.info_model.invoke(messages)
        
        # 如果收集到足够信息，转到解决方案Agent
        if "已收集客户信息" in response.content:
            state["next_agent"] = "solution"
        
        return {"messages": [response]}
    
    def solution_agent(self, state: AgentState):
        """问题解决Agent"""
        messages = state["messages"]
        response = self.solution_model.invoke(messages)
        
        # 检查是否解决问题
        if "问题已解决" in response.content:
            state["issue_solved"] = True
        
        return {"messages": [response]}
    
    def info_agent_router(self, state: AgentState):
        """信息收集Agent的路由逻辑"""
        last_message = state["messages"][-1]
        
        # 如果最后一条消息有工具调用
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        # 如果需要转到解决方案Agent
        elif state.get("next_agent") == "solution":
            return "solution"
        # 如果完成了所有任务
        else:
            return "end"
    
    def solution_agent_router(self, state: AgentState):
        """问题解决Agent的路由逻辑"""
        last_message = state["messages"][-1]
        
        # 如果最后一条消息有工具调用
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        # 如果问题已解决
        elif state.get("issue_solved", False):
            return "end"
        else:
            return "end"

# 使用示例
def run_customer_service():
    # 创建系统
    system = CustomerServiceSystem()
    graph = system.build_graph()
    
    # 初始状态
    initial_state = {
        "messages": [HumanMessage(content="你好，我是客户ID12345，我的订单789有问题，能帮我查看吗？")],
        "next_agent": "",
        "customer_info": {},
        "issue_solved": False
    }
    
    # 运行图
    for output in graph.stream(initial_state):
        for key, value in output.items():
            print(f"节点: {key}")
            if "messages" in value:
                for msg in value["messages"]:
                    if isinstance(msg, AIMessage):
                        print(f"AI: {msg.content}")
                    elif isinstance(msg, ToolMessage):
                        print(f"工具: {msg.content}")
                    elif isinstance(msg, HumanMessage):
                        print(f"人类: {msg.content}")
            print("---")

# 运行示例
if __name__ == "__main__":
    run_customer_service()