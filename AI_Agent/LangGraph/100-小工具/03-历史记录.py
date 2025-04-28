
# 时间旅行功能抽取

# 导入必要的库
from langgraph.checkpoint.memory import MemorySaver
import os

class TimeTravel:
    """时间旅行功能类，用于管理LangGraph的检查点和历史状态"""

    def __init__(self, agent_graph):
        """初始化时间旅行工具
        
        Args:
            agent_graph: 已编译的LangGraph图实例
        """
        self.agent_graph = agent_graph
    
    def get_state_history(self, config=None):
        """获取代理图的状态历史
        
        Args:
            config: 配置参数字典，包含thread_id等
            
        Returns:
            状态历史列表
        """
        config = config or {}
        try:
            return self.agent_graph.get_state_history(config)
        except Exception as e:
            print(f"获取状态历史时出错: {e}")
            return []

    def replay_from_checkpoint(self, checkpoint, config=None):
        """从检查点重放代理执行
        
        Args:
            checkpoint: 要恢复的检查点
            config: 配置参数字典
            
        Returns:
            恢复后的状态
        """
        config = config or {}
        try:
            return self.agent_graph.restore_from_checkpoint(checkpoint, config)
        except Exception as e:
            print(f"从检查点恢复时出错: {e}")
            return None

    def visualize_execution_flow(self, config=None):
        """可视化代理执行流程
        
        通过分析状态历史，生成一个可视化的执行流程图，展示代理之间的交互和状态变化。
        
        Args:
            config: 配置参数字典
        """
        try:
            # 获取状态历史
            history = list(self.get_state_history(config or {}))
            
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
                output_dir = "output_articles"  # 可配置
                if os.path.exists(output_dir):
                    files = os.listdir(output_dir)
                    if files:
                        for f in files:
                            file_size = os.path.getsize(os.path.join(output_dir, f))
                            print(f"- {f} ({file_size} 字节)")
                    else:
                        print("没有生成任何文件")
            except Exception as e:
                print(f"无法列出文件: {e}")
                
        except Exception as e:
            print(f"可视化执行流程时出错: {e}")

    def show_interactive_menu(self, config=None):
        """显示交互式时间旅行菜单
        
        Args:
            config: 配置参数字典
        """
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
                history = list(self.get_state_history(config))
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
                history = list(self.get_state_history(config))
                
                if not history:
                    print("没有可用的执行历史记录")
                    return
                    
                if 0 <= checkpoint_id < len(history):
                    checkpoint = history[checkpoint_id]
                    print(f"\n从检查点 {checkpoint_id} 恢复 (代理: {checkpoint.values.get('active_agent', '未知')}, 阶段: {checkpoint.values.get('current_step', '未知')})")
                    
                    # 询问新任务
                    from langchain_core.messages import HumanMessage
                    new_task = input("请输入新的任务说明 (留空使用原任务): ")
                    
                    if new_task:
                        checkpoint.values["messages"].append(HumanMessage(content=new_task))
                    
                    # 从检查点恢复
                    restored_state = self.replay_from_checkpoint(checkpoint, config)
                    if restored_state:
                        print("\n已成功从检查点恢复!")
                    return restored_state
                else:
                    print("无效的检查点ID")
            except ValueError:
                print("请输入有效的数字作为检查点ID")
            except Exception as e:
                print(f"从检查点恢复时出错: {e}")
        
        elif choice == "3":
            # 可视化执行流程
            try:
                self.visualize_execution_flow(config)
            except Exception as e:
                print(f"可视化执行流程时出错: {e}")
                
        elif choice == "4":
            print("退出时间旅行功能")
        
        else:
            print("无效的选择")


# 如何创建支持时间旅行的图（示例）
def create_graph_with_timetravel(state_type, nodes, edges):
    """创建支持时间旅行功能的LangGraph图
    
    Args:
        state_type: 状态类型
        nodes: 图节点
        edges: 图边缘
        
    Returns:
        编译好的图实例
    """
    # 创建状态图
    graph = StateGraph(state_type)
    
    # 添加节点和边缘
    for name, func in nodes.items():
        graph.add_node(name, func)
    
    # 添加边缘（示例中简化处理）
    for edge in edges:
        if isinstance(edge, tuple) and len(edge) == 2:
            graph.add_edge(edge[0], edge[1])
    
    # 创建检查点保存器（用于时间旅行功能）
    memory = MemorySaver()
    
    # 编译图
    return graph.compile(checkpointer=memory)


# 使用示例
"""
# 初始化图
agent_graph = create_graph_with_timetravel(...)

# 创建时间旅行工具
time_travel = TimeTravel(agent_graph)

# 运行图
config = {"configurable": {"thread_id": "demo_thread"}}
result = agent_graph.invoke(initial_state, config)

# 显示时间旅行菜单
time_travel.show_interactive_menu(config)

# 或者单独使用功能
history = time_travel.get_state_history(config)
time_travel.visualize_execution_flow(config)
"""
