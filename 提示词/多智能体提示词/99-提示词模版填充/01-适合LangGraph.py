# 导入必要的库
from enum import Enum  # 用于创建枚举类
import os  # 用于处理文件路径
import re  # 用于正则表达式操作
from datetime import datetime  # 用于获取当前时间
from typing import List, Dict, Any, Optional
from pathlib import Path

# 导入LangChain和LangGraph相关组件
from langchain_core.prompts import PromptTemplate  # 用于创建提示模板
from langgraph.prebuilt.chat_agent_executor import AgentState  # 用于管理代理状态


class PromptType(Enum):
    """提示词模板类型枚举"""
    SUPERVISOR = "supervisor"
    JOB_FIND_AGENT = "job_find_agent"

# 获取提示词模板函数
def get_prompt_template(prompt_type: PromptType, encoding: str = 'utf-8') -> str:
    """从文件中读取提示词模板并进行必要的格式转换
    Args:
        prompt_type: 提示词模板类型（PromptType枚举）
        encoding: 文件编码格式，默认为 utf-8
        
    Returns:
        格式化后的提示词模板字符串
        
    Raises:
        FileNotFoundError: 当模板文件不存在时
        UnicodeDecodeError: 当文件编码不匹配时
    """
    template_path = Path(os.path.dirname(__file__)) / f"{prompt_type.value}.md"
    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在：{template_path}")
        
    try:
        with open(template_path, 'r', encoding=encoding) as f:
            template = f.read()
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"模板文件编码错误，请确保文件为 {encoding} 编码：{e}")
        
    template = template.replace("{", "{{").replace("}", "}}")
    template = re.sub(r"<<([^>>]+)>>", r"{\1}", template)
    return template


# 应用提示词模板函数
def apply_prompt_template(
    prompt_type: PromptType,
    state: AgentState,
    time_format: str = "%a %b %d %Y %H:%M:%S %z",
    additional_vars: Optional[Dict[str, Any]] = None
) -> List[Dict[str, str]]:
    """将提示词模板应用到当前状态，生成系统提示消息
    
    Args:
        prompt_type: 提示词模板类型（PromptType枚举）
        state: 代理状态对象，包含消息历史等信息
        time_format: 时间格式字符串，默认为 "%a %b %d %Y %H:%M:%S %z"
        additional_vars: 额外的模板变量，可选
        
    Returns:
        包含系统提示和历史消息的列表
        
    Raises:
        KeyError: 当必要的状态变量缺失时
        ValueError: 当模板变量格式不正确时
    """
    try:
        # 准备模板变量
        template_vars = {
            "CURRENT_TIME": datetime.now().strftime(time_format),
            **state,
            **(additional_vars or {})
        }
        
        # 创建系统提示
        # 模板中某个没有的变量没有被成功填充，会报错，需要处理
        system_prompt = PromptTemplate(
            template=get_prompt_template(prompt_type),
            input_variables=list(template_vars.keys())
        ).format(**template_vars)
        
        # 验证消息格式
        if not isinstance(state["messages"], list):
            raise ValueError("state['messages'] 必须是列表类型")
            
        return [{"role": "system", "content": system_prompt}] + state["messages"]
        
    except KeyError as e:
        raise KeyError(f"缺少必要的状态变量：{e}")
    except Exception as e:
        raise ValueError(f"模板应用失败：{e}")


