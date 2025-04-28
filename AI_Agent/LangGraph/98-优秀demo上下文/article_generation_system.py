"""
LangGraph自主代理演示
展示如何使用LangGraph构建具有多个代理角色的自主代理系统

作者: Claude
"""

# 导入必要的库
import os
from typing import Annotated, List, Dict, Literal, TypedDict, Any, Optional, cast
from dotenv import load_dotenv

# 导入LangGraph相关库
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# 导入LangChain相关库
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, FunctionMessage
from langchain_core.tools import tool, BaseTool, StructuredTool

# 导入自定义LLM和搜索工具
from app.llm import LLMFactory, LLMProviderType
from app.utils.search import SearchEngineFactory, SearchEngineType

# 加载环境变量
load_dotenv()

# 创建LLM和搜索引擎
llm_deepseek = LLMFactory.create_llm(LLMProviderType.DEEPSEEK)
search_tavily = SearchEngineFactory.create_engine(SearchEngineType.TAVILY)

# ============================
# 第1部分: 定义工具和状态类型
# ============================

# 定义搜索工具
@tool
def search_internet(query: str) -> str:
    """使用Tavily搜索引擎搜索互联网获取最新信息。"""
    results = search_tavily.search(query)
    return str(results)

# 定义写作工具
@tool
def write_to_file(filename: str, content: str) -> str:
    """将内容写入文件。"""
    try:
        # 创建输出目录
        os.makedirs("output_articles", exist_ok=True)
        # 写入文件
        with open(f"output_articles/{filename}", "w", encoding="utf-8") as f:
            f.write(content)
        return f"内容已成功写入到 output_articles/{filename}"
    except Exception as e:
        return f"写入文件时发生错误: {str(e)}"

# 定义工具列表
tools = [search_internet, write_to_file]
llm_with_tools = llm_deepseek.bind_tools(tools)

# 定义代理角色类型
class AgentRole(TypedDict):
    name: str
    description: str
    goal: str
    tools: List[str]

# 定义代理状态类型
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    agent_scratchpad: str  # 代理的思考和计划区域
    current_step: str  # 当前执行步骤
    task: str  # 当前任务
    search_results: List[Dict[str, Any]]  # 搜索结果
    research_summary: str  # 研究总结
    plan: List[str]  # 执行计划
    draft: str  # 初稿
    final_output: str  # 最终输出
    error: Optional[str]  # 错误信息
    active_agent: str  # 当前活动的代理

# ============================
# 第2部分: 创建代理角色
# ============================

def create_agent_roles() -> Dict[str, AgentRole]:
    """创建代理角色配置"""
    return {
        "controller": {
            "name": "控制代理",
            "description": "负责任务规划、分配和监督整个系统执行流程的核心代理",
            "goal": "确保任务完成，协调其他代理的工作，解决冲突，跟踪进度",
            "tools": []
        },
        "researcher": {
            "name": "研究代理",
            "description": "负责信息收集和分析的代理",
            "goal": "收集与任务相关的全面、准确的信息，分析和综合这些信息",
            "tools": ["search_internet"]
        },
        "writer": {
            "name": "写作代理",
            "description": "负责内容创作的代理",
            "goal": "基于研究结果创作高质量、连贯、符合要求的内容",
            "tools": ["write_to_file"]
        },
        "reviewer": {
            "name": "审核代理",
            "description": "负责内容质量审核的代理",
            "goal": "确保内容质量、准确性、原创性和一致性",
            "tools": []
        }
    }

# ============================
# 第3部分: 创建主图
# ============================

def create_agent_graph():
    """创建自主代理系统的主图"""
    # 初始化代理状态图
    agent_graph = StateGraph(AgentState)
    
    # 获取代理角色
    agent_roles = create_agent_roles()
    
    # 定义节点函数
    
    # 错误处理节点 - 处理执行过程中出现的错误
    def error_handler(state: AgentState) -> Dict[str, Any]:
        """处理执行过程中的错误并尝试恢复"""
        error = state.get("error", "未知错误")
        current_step = state.get("current_step", "")
        active_agent = state.get("active_agent", "")
        
        print(f"错误处理器启动: 当前步骤={current_step}, 代理={active_agent}, 错误={error}")
        
        # 根据错误和当前状态确定恢复策略
        if "研究" in current_step or "search" in error.lower():
            # 搜索或研究相关错误，直接进入写作阶段
            print("研究阶段出错，跳过到写作阶段")
            return {
                "error": None,  # 清除错误
                "research_summary": state.get("research_summary", "") or "由于技术原因无法获取完整研究数据，但我们将基于现有信息继续写作。",
                "current_step": "writing",
                "active_agent": "writer"
            }
        elif "写作" in current_step or "write" in error.lower() or "file" in error.lower():
            # 写作相关错误，直接进入审核阶段
            print("写作阶段出错，跳过到审核阶段")
            return {
                "error": None,
                "draft": state.get("draft", "") or "由于技术原因无法生成完整草稿，但我们将继续进行审核。",
                "current_step": "review_draft",
                "active_agent": "controller"
            }
        elif "审核" in current_step or "review" in error.lower():
            # 审核相关错误，直接完成任务
            print("审核阶段出错，直接完成任务")
            final_output = state.get("draft", "") or "由于技术原因无法完成完整的文档生成，这是一个部分结果。"
            
            # 保存最终输出
            try:
                task = state.get("task", "未知任务")
                filename = f"{task.replace(' ', '_')}_final.txt"
                os.makedirs("output_articles", exist_ok=True)
                with open(f"output_articles/{filename}", "w", encoding="utf-8") as f:
                    f.write(final_output)
                print(f"最终结果已保存至: output_articles/{filename}")
            except Exception as e:
                print(f"保存最终结果出错: {e}")
                
            return {
                "error": None,
                "final_output": final_output,
                "current_step": "complete",
                "active_agent": "controller"
            }
        else:
            # 其他错误，重置到初始计划阶段
            print("遇到未识别错误，重置到计划阶段")
            return {
                "error": None,
                "current_step": "planning",
                "active_agent": "controller"
            }
    
    # 控制器节点 - 规划和任务分配
    def controller_node(state: AgentState) -> AgentState:
        messages = state["messages"]
        current_step = state.get("current_step", "init")
        
        # 构建提示
        role_description = agent_roles["controller"]["description"]
        goal = agent_roles["controller"]["goal"]
        
        if current_step == "init":
            # 初始化阶段 - 分析任务并创建计划
            task = messages[-1].content if isinstance(messages[-1], HumanMessage) else "无任务"
            
            prompt = f"""你是{role_description}，你的目标是{goal}。
            
            当前任务: {task}
            
            请执行以下操作:
            1. 分析任务的需求和范围
            2. 创建详细的执行计划，包含研究、写作和审核阶段
            3. 确定任务优先级
            
            请以JSON格式返回你的分析和计划。"""
            
            response = llm_deepseek.invoke(prompt)
            
            # 更新状态
            return {
                "agent_scratchpad": response.content,
                "current_step": "planning",
                "task": task,
                "active_agent": "controller",
                "plan": []
            }
        
        elif current_step == "planning":
            # 规划阶段 - 创建详细计划
            task = state["task"]
            agent_scratchpad = state["agent_scratchpad"]
            
            prompt = f"""你是{role_description}，你的目标是{goal}。
            
            当前任务: {task}
            初步分析: {agent_scratchpad}
            
            现在，请创建一个详细的、按步骤执行的计划，包括:
            1. 需要研究的具体问题和搜索查询
            2. 内容结构和大纲
            3. 质量检查标准
            
            返回一个包含明确步骤的计划列表。"""
            
            response = llm_deepseek.invoke(prompt)
            
            # 提取计划步骤
            plan_text = response.content
            plan_lines = [line.strip() for line in plan_text.split('\n') if line.strip()]
            
            # 更新状态
            return {
                "agent_scratchpad": state["agent_scratchpad"] + "\n\n详细计划:\n" + plan_text,
                "current_step": "research",
                "plan": plan_lines,
                "active_agent": "researcher"
            }
        
        elif current_step == "review_research":
            # 审核研究结果
            research_summary = state.get("research_summary", "")
            
            prompt = f"""你是{role_description}，你的目标是{goal}。
            
            请审核以下研究结果，并决定是否有足够的信息继续进行写作阶段:
            
            研究结果:
            {research_summary}
            
            如果信息不足，请指出还需要研究哪些问题，否则批准进入写作阶段。"""
            
            response = llm_deepseek.invoke(prompt)
            
            # 更新状态
            return {
                "agent_scratchpad": state["agent_scratchpad"] + "\n\n研究审核:\n" + response.content,
                "current_step": "writing",
                "active_agent": "writer"
            }
        
        elif current_step == "review_draft":
            # 审核初稿
            draft = state.get("draft", "")
            
            prompt = f"""你是{role_description}，你的目标是{goal}。
            
            请审核以下初稿，并提供反馈:
            
            初稿:
            {draft}
            
            请指出任何需要改进的地方，例如内容质量、准确性、结构等。"""
            
            response = llm_deepseek.invoke(prompt)
            
            # 更新状态
            return {
                "agent_scratchpad": state["agent_scratchpad"] + "\n\n初稿审核:\n" + response.content,
                "current_step": "final_review",
                "active_agent": "reviewer"
            }
        
        else:
            # 默认行为
            return {
                "current_step": "init",
                "active_agent": "controller"
            }
    
    # 研究员节点 - 信息收集和分析
    def researcher_node(state: AgentState) -> Dict[str, Any]:
        try:
            task = state["task"]
            plan = state["plan"]
            
            # 构建提示
            role_description = agent_roles["researcher"]["description"]
            goal = agent_roles["researcher"]["goal"]
            
            # 直接创建搜索查询而不使用工具调用
            search_query = f"{task} 研究资料"
            print(f"执行搜索: {search_query}")
            
            # 直接调用搜索函数
            try:
                # 创建输出目录
                os.makedirs("output_articles", exist_ok=True)
                
                # 执行搜索
                search_results = []
                result = str(search_tavily.search(search_query))
                search_results.append({"query": search_query, "result": result})
                
                # 如果第一次搜索不够详细，尝试更具体的查询
                if len(result) < 200:
                    specific_query = f"{task} 详细分析与评价"
                    result2 = str(search_tavily.search(specific_query))
                    search_results.append({"query": specific_query, "result": result2})
                
                # 保存搜索结果
                with open(f"output_articles/{task.replace(' ', '_')}_搜索结果.txt", "w", encoding="utf-8") as f:
                    f.write(str(search_results))
                    
            except Exception as e:
                print(f"搜索过程中出错: {str(e)}")
                search_results = [{"query": search_query, "result": f"搜索过程中出错: {str(e)}，但我们将继续进行研究。"}]
            
            # 生成总结
            summary_prompt = f"""基于以下信息，创建一个关于"{task}"的全面研究总结:
            
            搜索结果:
            {search_results}
            
            请确保总结:
            1. 涵盖所有重要信息
            2. 有逻辑地组织信息
            3. 突出关键发现
            4. 指出任何不确定或矛盾的信息"""
            
            # 调用LLM生成总结
            try:
                summary_response = llm_deepseek.invoke(summary_prompt)
                summary = summary_response.content
                
                # 保存研究总结
                with open(f"output_articles/{task.replace(' ', '_')}_研究总结.txt", "w", encoding="utf-8") as f:
                    f.write(summary)
                    
                print(f"研究总结已保存至: output_articles/{task.replace(' ', '_')}_研究总结.txt")
                
            except Exception as e:
                print(f"生成总结时出错: {str(e)}")
                summary = f"无法生成完整总结，但已收集到相关信息。错误: {str(e)}"
            
            # 更新状态
            return {
                "search_results": search_results,
                "research_summary": summary,
                "current_step": "review_research",
                "active_agent": "controller"
            }
        except Exception as e:
            # 捕获异常并设置错误状态
            error_message = f"研究过程中发生错误: {str(e)}"
            print(error_message)
            
            # 确保返回一些结果
            return {
                "error": error_message,
                "research_summary": "研究过程中遇到了技术问题，但我们将继续完成任务。",
                "current_step": "review_research",
                "active_agent": "controller"
            }
    
    # 写作员节点 - 内容创作
    def writer_node(state: AgentState) -> Dict[str, Any]:
        try:
            task = state["task"]
            research_summary = state["research_summary"]
            
            # 构建提示
            role_description = agent_roles["writer"]["description"]
            goal = agent_roles["writer"]["goal"]
            
            prompt = f"""你是{role_description}，你的目标是{goal}。
            
            当前任务: {task}
            研究总结: {research_summary}
            
            请使用提供的研究信息创建一篇高质量的文章。确保:
            1. 内容清晰、连贯且有吸引力
            2. 准确反映研究结果
            3. 结构良好，段落之间过渡自然
            4. 没有语法或拼写错误"""
            
            # 使用普通的LLM生成内容
            response = llm_deepseek.invoke(
                [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"请基于研究结果写一篇关于'{task}'的文章"}
                ]
            )
            
            # 提取文章内容
            draft = response.content
            
            # 手动保存文件
            filename = f"{task.replace(' ', '_')}.txt"
            try:
                # 创建输出目录
                os.makedirs("output_articles", exist_ok=True)
                # 写入文件
                with open(f"output_articles/{filename}", "w", encoding="utf-8") as f:
                    f.write(draft)
                print(f"内容已保存到文件: output_articles/{filename}")
            except Exception as e:
                print(f"保存文件时出错: {str(e)}")
            
            # 更新状态
            return {
                "draft": draft,
                "current_step": "review_draft",
                "active_agent": "controller"
            }
        except Exception as e:
            # 捕获异常并设置错误状态
            error_message = f"写作过程中发生错误: {str(e)}"
            print(error_message)
            
            # 尝试返回部分结果
            return {
                "error": error_message,
                "draft": state.get("draft", "无法生成草稿"),
                "current_step": "review_draft",  # 继续进行审核
                "active_agent": "controller"
            }
    
    # 审核员节点 - 质量审核
    def reviewer_node(state: AgentState) -> Dict[str, Any]:
        try:
            task = state["task"]
            draft = state["draft"]
            research_summary = state["research_summary"]
            
            # 构建提示
            role_description = agent_roles["reviewer"]["description"]
            goal = agent_roles["reviewer"]["goal"]
            
            prompt = f"""你是{role_description}，你的目标是{goal}。
            
            当前任务: {task}
            研究总结: {research_summary}
            文章草稿: {draft}
            
            请全面审核这篇文章，评估:
            1. 内容准确性 - 内容是否与研究结果一致
            2. 质量 - 文章是否清晰、连贯且有吸引力
            3. 完整性 - 是否涵盖了所有重要信息
            4. 语法和拼写 - 是否有语言错误
            
            提供详细的反馈和任何需要改进的建议。如果文章令人满意，请批准发布。"""
            
            response = llm_deepseek.invoke(prompt)
            
            # 决定是否需要修改
            feedback = response.content
            
            # 保存审核意见
            try:
                filename = f"{task.replace(' ', '_')}_审核意见.txt"
                os.makedirs("output_articles", exist_ok=True)
                with open(f"output_articles/{filename}", "w", encoding="utf-8") as f:
                    f.write(feedback)
                print(f"审核意见已保存至: output_articles/{filename}")
            except Exception as e:
                print(f"保存审核意见出错: {str(e)}")
            
            # 检查是否需要修改
            needs_revision = "需要修改" in feedback or "需要改进" in feedback or "不够" in feedback
            
            if needs_revision and len(draft) > 100:  # 确保有足够的内容可以修改
                # 需要修改
                print("审核结果: 需要修改")
                return {
                    "current_step": "writing",
                    "active_agent": "writer",
                    "agent_scratchpad": state.get("agent_scratchpad", "") + "\n\n审核反馈:\n" + feedback
                }
            else:
                # 最终版本
                final_document = draft
                
                # 保存最终版本
                try:
                    filename = f"{task.replace(' ', '_')}_final.txt"
                    os.makedirs("output_articles", exist_ok=True)
                    with open(f"output_articles/{filename}", "w", encoding="utf-8") as f:
                        f.write(final_document)
                    print(f"最终文档已保存至: output_articles/{filename}")
                except Exception as e:
                    print(f"保存最终文档出错: {str(e)}")
                
                print("审核结果: 批准发布")
                return {
                    "final_output": final_document,
                    "current_step": "complete",
                    "active_agent": "controller"
                }
        except Exception as e:
            error_message = f"审核过程中发生错误: {str(e)}"
            print(error_message)
            
            # 即使出错也完成任务
            final_document = state.get("draft", "由于技术原因无法完成最终版本")
            return {
                "error": error_message,
                "final_output": final_document,
                "current_step": "complete",
                "active_agent": "controller"
            }
    
    # 路由器节点 - 根据当前状态决定下一步
    def router(state: AgentState) -> Literal["controller", "researcher", "writer", "reviewer", "error_handler"]:
        """根据状态决定下一个节点"""
        # 首先检查是否有错误
        if state.get("error"):
            return "error_handler"
        
        current_step = state.get("current_step", "init")
        active_agent = state.get("active_agent", "controller")
        
        # 如果任务完成了，则直接返回END（使用return END）
        if current_step == "complete":
            return END
        
        return active_agent
    
    # 添加节点
    agent_graph.add_node("controller", controller_node)
    agent_graph.add_node("researcher", researcher_node)
    agent_graph.add_node("writer", writer_node)
    agent_graph.add_node("reviewer", reviewer_node)
    agent_graph.add_node("error_handler", error_handler)
    
    # 添加边
    agent_graph.add_conditional_edges("__start__", router)
    agent_graph.add_conditional_edges("controller", router)
    agent_graph.add_conditional_edges("researcher", router)
    agent_graph.add_conditional_edges("writer", router)
    agent_graph.add_conditional_edges("reviewer", router)
    agent_graph.add_conditional_edges("error_handler", router)
    
    # 创建检查点保存器（用于时间旅行功能）
    memory = MemorySaver()
    
    # 编译图
    return agent_graph.compile(checkpointer=memory)

# ============================
# 第4部分: 实用函数
# ============================

def get_state_history(agent_graph, config=None):
    """获取代理图的状态历史"""
    config = config or {}
    try:
        return agent_graph.get_state_history(config)
    except Exception as e:
        print(f"获取状态历史时出错: {e}")
        return []

def replay_from_checkpoint(agent_graph, checkpoint, config=None):
    """从检查点重放代理执行"""
    config = config or {}
    try:
        return agent_graph.restore_from_checkpoint(checkpoint, config)
    except Exception as e:
        print(f"从检查点恢复时出错: {e}")
        return None

def visualize_execution_flow(agent_graph, config=None):
    """可视化代理执行流程
    
    通过分析状态历史，生成一个可视化的执行流程图，展示代理之间的交互和状态变化。
    """
    try:
        # 获取状态历史
        history = list(get_state_history(agent_graph, config or {}))
        
        if not history:
            print("没有可用的执行历史记录")
            return
        
        # 打印执行流程表格
        print("\n===== 执行流程可视化 =====")
        print("步骤\t代理\t\t阶段\t\t操作\t\t状态")
        print("-" * 80)
        
        for i, state in enumerate(history):
            active_agent = state.values.get("active_agent", "未知")
            current_step = state.values.get("current_step", "未知")
            
            # 确定当前状态的操作
            action = "初始化"
            if i > 0:
                prev_state = history[i-1]
                prev_step = prev_state.values.get("current_step", "")
                
                if current_step != prev_step:
                    if current_step == "planning":
                        action = "分析任务"
                    elif current_step == "research":
                        action = "开始研究"
                    elif current_step == "review_research":
                        action = "审核研究结果"
                    elif current_step == "writing":
                        action = "撰写内容"
                    elif current_step == "review_draft":
                        action = "审核初稿"
                    elif current_step == "final_review":
                        action = "最终审核"
                    elif current_step == "complete":
                        action = "任务完成"
                else:
                    action = "处理中"
            
            # 获取状态信息
            status = ""
            if "error" in state.values and state.values["error"]:
                status = f"错误: {state.values['error'][:30]}..."
            elif current_step == "research" and "search_results" in state.values:
                results_count = len(state.values.get("search_results", []))
                status = f"搜索结果: {results_count}项"
            elif current_step == "review_research" and "research_summary" in state.values:
                summary_len = len(state.values.get("research_summary", ""))
                status = f"研究总结: {summary_len}字符"
            elif current_step == "writing" and "draft" in state.values:
                draft_len = len(state.values.get("draft", ""))
                status = f"草稿: {draft_len}字符"
            elif current_step == "complete" and "final_output" in state.values:
                output_len = len(state.values.get("final_output", ""))
                status = f"最终输出: {output_len}字符"
            
            print(f"{i}\t{active_agent}\t\t{current_step}\t\t{action}\t\t{status}")
        
        print("-" * 80)
        
        # 打印状态转换图
        print("\n代理交互图:")
        transitions = []
        for i in range(1, len(history)):
            prev = history[i-1].values.get("active_agent", "开始")
            curr = history[i].values.get("active_agent", "结束")
            if prev != curr:
                transitions.append(f"{prev} -> {curr}")
        
        if transitions:
            print(" | ".join(transitions))
        else:
            print("没有代理交互")
        
        # 打印处理的文件
        print("\n生成的文件:")
        try:
            if os.path.exists("output_articles"):
                files = os.listdir("output_articles")
                if files:
                    for f in files:
                        file_size = os.path.getsize(os.path.join("output_articles", f))
                        print(f"- {f} ({file_size} 字节)")
                else:
                    print("没有生成任何文件")
        except Exception as e:
            print(f"无法列出文件: {e}")
            
    except Exception as e:
        print(f"可视化执行流程时出错: {e}")

# ============================
# 第6部分: 主程序
# ============================

def run_autonomous_agent():
    """运行自主代理系统"""
    print("=== LangGraph自主代理演示 ===")
    print("这个系统使用多个协作代理来完成复杂任务。")
    print("系统包含控制、研究、写作和审核代理，并支持时间旅行检查点。")
    print()
    
    # 创建代理图
    agent_graph = create_agent_graph()
    
    # 获取用户输入
    user_task = input("请输入您的任务 (例如: '为我研究并编写一篇关于人工智能最新发展的文章'): ")
    
    # 初始化会话配置 - 使用thread_id而非session_id
    config = {"configurable": {"thread_id": "demo_thread"}}
    
    # 创建初始状态
    initial_state = {
        "messages": [HumanMessage(content=user_task)],
        "agent_scratchpad": "",
        "current_step": "init",
        "task": "",
        "search_results": [],
        "research_summary": "",
        "plan": [],
        "draft": "",
        "final_output": "",
        "error": None,
        "active_agent": "controller"
    }
    
    print("\n开始执行任务...")
    
    # 获取流式输出
    try:
        events = agent_graph.stream(
            initial_state,
            config,
            stream_mode="values"
        )
        
        # 跟踪每个节点的执行
        for i, event in enumerate(events):
            active_agent = event.get("active_agent", "未知")
            current_step = event.get("current_step", "未知")
            
            print(f"\n[步骤 {i+1}] 当前代理: {active_agent}, 阶段: {current_step}")
            
            if "research_summary" in event and event["research_summary"] and "research_summary" not in initial_state:
                print(f"\n--- 研究摘要 ---\n{event['research_summary'][:200]}...(已截断)")
                initial_state["research_summary"] = event["research_summary"]
            
            if "draft" in event and event["draft"] and "draft" not in initial_state:
                print(f"\n--- 文章草稿 ---\n{event['draft'][:200]}...(已截断)")
                initial_state["draft"] = event["draft"]
            
            if "final_output" in event and event["final_output"]:
                print(f"\n--- 最终输出 ---\n{event['final_output'][:200]}...(已截断)")
                print(f"\n完整内容已保存到output_articles目录")
    
    except Exception as e:
        print(f"执行出错: {e}")
    
    print("\n=== 执行完成 ===")
    
    # 显示时间旅行选项
    print("\n时间旅行功能:")
    print("1. 查看执行历史")
    print("2. 从特定检查点恢复")
    print("3. 可视化执行流程")
    print("4. 退出")
    
    choice = input("\n请选择 (1-4): ")
    
    if choice == "1":
        # 查看执行历史
        try:
            print("\n执行历史:")
            history = list(get_state_history(agent_graph, config))
            if not history:
                print("没有可用的执行历史记录")
                return
                
            for i, state in enumerate(history):
                print(f"检查点 {i}: 代理 = {state.values.get('active_agent', '未知')}, 阶段 = {state.values.get('current_step', '未知')}")
        except Exception as e:
            print(f"查看执行历史时出错: {e}")
    
    elif choice == "2":
        # 从检查点恢复
        try:
            checkpoint_id_input = input("请输入检查点ID: ")
            if not checkpoint_id_input.strip():
                print("未提供有效的检查点ID")
                return
                
            checkpoint_id = int(checkpoint_id_input)
            history = list(get_state_history(agent_graph, config))
            
            if not history:
                print("没有可用的执行历史记录")
                return
                
            if 0 <= checkpoint_id < len(history):
                checkpoint = history[checkpoint_id]
                print(f"\n从检查点 {checkpoint_id} 恢复 (代理: {checkpoint.values.get('active_agent', '未知')}, 阶段: {checkpoint.values.get('current_step', '未知')})")
                
                # 恢复执行
                new_task = input("请输入新的任务说明 (留空使用原任务): ")
                
                if new_task:
                    checkpoint.values["messages"].append(HumanMessage(content=new_task))
                
                # 从检查点恢复
                restored_state = replay_from_checkpoint(agent_graph, checkpoint, config)
                if restored_state:
                    print("\n已成功从检查点恢复!")
            else:
                print("无效的检查点ID")
        except ValueError:
            print("请输入有效的数字作为检查点ID")
        except Exception as e:
            print(f"从检查点恢复时出错: {e}")
    
    elif choice == "3":
        # 可视化执行流程
        try:
            visualize_execution_flow(agent_graph, config)
        except Exception as e:
            print(f"可视化执行流程时出错: {e}")
            
    elif choice == "4":
        print("退出程序")
    
    else:
        print("无效的选择")

if __name__ == "__main__":
    run_autonomous_agent() 