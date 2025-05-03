import os
import sys
import logging
import functools
from datetime import datetime
from typing import Optional, Union, Callable, Any, Dict, Type, TypeVar

# 默认日志格式
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
# 默认日期格式
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
# 默认日志级别
DEFAULT_LOG_LEVEL = logging.INFO

# 创建TypeVar用于泛型类型
T = TypeVar("T")

class LlamaKBLogger:
    """
    LlamaKB项目的日志记录器类
    提供统一的日志配置和记录功能
    """
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(LlamaKBLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, 
                 name: str = "llamakb",
                 level: Union[int, str] = DEFAULT_LOG_LEVEL,
                 log_file: Optional[str] = None,
                 log_format: str = DEFAULT_LOG_FORMAT,
                 date_format: str = DEFAULT_DATE_FORMAT,
                 console_output: bool = True):
        """
        初始化日志记录器
        
        参数:
            name: 日志记录器名称
            level: 日志级别，可以是int类型(如logging.DEBUG)或字符串类型(如'DEBUG')
            log_file: 日志文件路径，如果为None则不输出到文件
            log_format: 日志格式
            date_format: 日期格式
            console_output: 是否输出到控制台
        """
        # 避免重复初始化
        if self._initialized:
            return
            
        self.name = name
        # 处理日志级别
        if isinstance(level, str):
            self.level = getattr(logging, level.upper(), DEFAULT_LOG_LEVEL)
        else:
            self.level = level
            
        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        self.logger.propagate = False  # 避免日志传播到根记录器
        
        # 清除已有的handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
            
        # 设置日志格式
        formatter = logging.Formatter(log_format, date_format)
        
        # 添加控制台输出
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
        # 添加文件输出
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        self._initialized = True
        
    def get_logger(self):
        """获取日志记录器实例"""
        return self.logger
        
    # 提供各种日志级别的快捷方法
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)
        
    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
        
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
        
    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
        
    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
        
    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)


# 创建默认日志记录器实例
def setup_logger(name: str = "llamakb", 
                level: Union[int, str] = DEFAULT_LOG_LEVEL,
                log_file: Optional[str] = None, 
                log_format: str = DEFAULT_LOG_FORMAT,
                date_format: str = DEFAULT_DATE_FORMAT,
                console_output: bool = True) -> LlamaKBLogger:
    """
    设置并返回日志记录器
    
    参数:
        name: 日志记录器名称
        level: 日志级别，可以是int(如logging.DEBUG)或str(如'DEBUG')
        log_file: 日志文件路径，如果为None则不输出到文件
        log_format: 日志格式
        date_format: 日期格式
        console_output: 是否输出到控制台
        
    返回:
        配置好的LlamaKBLogger实例
    """
    return LlamaKBLogger(
        name=name,
        level=level,
        log_file=log_file,
        log_format=log_format,
        date_format=date_format,
        console_output=console_output
    )


# 装饰器：记录函数的输入和输出
def log_function(level: Union[int, str] = logging.DEBUG, 
                logger_name: Optional[str] = None, 
                show_args: bool = True,
                show_return: bool = True) -> Callable:
    """
    记录函数调用的装饰器
    
    参数:
        level: 日志级别
        logger_name: 使用的日志记录器名称，如果为None则使用被装饰函数的模块名
        show_args: 是否显示函数参数
        show_return: 是否显示返回值
        
    返回:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 确定使用哪个日志记录器
            if logger_name:
                logger = logging.getLogger(logger_name)
            else:
                logger = logging.getLogger(func.__module__)
                
            # 解析日志级别
            if isinstance(level, str):
                log_level = getattr(logging, level.upper(), logging.DEBUG)
            else:
                log_level = level
            
            # 记录函数调用
            func_name = func.__name__
            if show_args:
                params = ", ".join(
                    [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
                )
                logger.log(log_level, f"函数 {func_name} 被调用，参数: {params}")
            else:
                logger.log(log_level, f"函数 {func_name} 被调用")
                
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 记录返回值
                if show_return:
                    logger.log(log_level, f"函数 {func_name} 返回值: {result}")
                else:
                    logger.log(log_level, f"函数 {func_name} 执行完成")
                    
                return result
            except Exception as e:
                logger.exception(f"函数 {func_name} 执行出错: {str(e)}")
                raise
                
        return wrapper
    
    return decorator


# 为了向后兼容原有的log_func装饰器
def log_func(func: Callable = None, *, level: Union[int, str] = logging.DEBUG) -> Callable:
    """
    一个装饰器，用于记录工具函数的输入参数和输出。
    
    参数:
        func: 要被装饰的工具函数
        level: 日志级别，可以是int类型(如logging.DEBUG)或字符串类型(如'DEBUG')，默认为DEBUG级别
        
    返回:
        带有输入/输出日志记录的包装函数
    """
    # 使用新的log_function实现
    decorator = log_function(level=level)
    
    # 支持直接装饰和带参数装饰两种方式
    if func is None:
        return decorator
    else:
        return decorator(func)


# 创建默认的日志记录器
default_logger = setup_logger(
    log_file="logs/llamakb.log",  # 默认日志文件
    level=logging.INFO  # 默认日志级别
)

# 获取默认日志记录器的logger实例
logger = default_logger.get_logger()


# 以下是工具类的日志记录功能
class LoggedToolMixin:
    """一个为任何工具添加日志功能的混入类。"""

    def _log_operation(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """记录工具操作的辅助方法。"""
        tool_name = self.__class__.__name__.replace("Logged", "")
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.debug(f"Tool {tool_name}.{method_name} called with parameters: {params}")

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """重写_run方法以添加日志记录。"""
        self._log_operation("_run", *args, **kwargs)
        result = super()._run(*args, **kwargs)
        logger.debug(
            f"Tool {self.__class__.__name__.replace('Logged', '')} returned: {result}"
        )
        return result


def create_logged_tool(base_tool_class: Type[T]) -> Type[T]:
    """
    用于创建任何工具类的带日志版本的工厂函数。

    参数:
        base_tool_class: 需要增强日志功能的原始工具类

    返回:
        一个同时继承自 LoggedToolMixin 和基础工具类的新类
    """

    class LoggedTool(LoggedToolMixin, base_tool_class):
        pass

    # 为类设置一个更具描述性的名称
    LoggedTool.__name__ = f"Logged{base_tool_class.__name__}"
    return LoggedTool


# 文档转换日志记录器
transform_logger = setup_logger(
    log_file="logs/transform.log",  # 默认日志文件
    level=logging.INFO  # 默认日志级别
) 