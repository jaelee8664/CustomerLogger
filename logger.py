import functools
import inspect
import logging
import sys
import os
import time
import traceback
from typing import Optional

class CustomerLogger:
    
    _logger_list = {} # Dictionary to store different types of loggers
    _instance = None # Class variable to hold the singleton instance
    
    def __new__(cls, logger_name:list[str], console:bool = False):
        # Use the Singleton pattern to ensure only one instance is created
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            # Create a folder named 'log' if it doesn't already exist
            if not os.path.exists("log"):
                os.makedirs("log")
            
            # Set up the log formatter
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            
            # Create loggers
            for name in logger_name:
                logger = logging.getLogger(name)
                cls._logger_list.update({name: logger})
                
                file_handler = logging.FileHandler(f"log/{name}_info.log")
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                
                # Add error level file handler
                error_file_handler = logging.FileHandler(f"log/{name}_error.log")
                error_file_handler.setLevel(logging.ERROR)
                error_file_handler.setFormatter(formatter)
                logger.addHandler(error_file_handler)
                
                # Add console handler if specified
                if console:
                    console_handler = logging.StreamHandler(sys.stdout)
                    console_handler.setLevel(logging.DEBUG)
                    console_handler.setFormatter(formatter)
                    logger.addHandler(console_handler)

        return cls._instance
    
    @classmethod
    def trace_call(cls, logger_name:str, to_log: Optional[str] = None):
        
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Get the logger instance for the specified logger name
                logger = cls._logger_list.get(logger_name)
                logger.setLevel(logging.INFO)
                
                # Get the names and values of the arguments
                bound_args = inspect.signature(func).bind(*args, **kwargs)
                bound_args.apply_defaults()
                func_args = bound_args.arguments

                try:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    
                    # Log the current function name
                    logger.info(f"Calling function: {func.__name__} | Execution time: {time.time() - start_time:.4f} seconds")
                    
                    # Log arguments
                    logger.info("Arguments:")
                    for arg_name, arg_value in func_args.items():
                        logger.info(f"{arg_name}: {arg_value}")
                        
                    logger.info(f"Result: {result}")
                    
                    logger.info(f"Additinal message: {to_log}") if to_log else None
                except Exception as e:
                    # Log the exception if one occurs
                    logger.setLevel(logging.ERROR)
                    logger.error(f"Calling function: {func.__name__}")
                    logger.error(f"Exception: {e}")
                    logger.error("Arguments:")
                    for arg_name, arg_value in func_args.items():
                        logger.error(f"{arg_name}: {arg_value}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise e
                
                return result
            return wrapper
        return decorator

if __name__ == "__main__":
    """
    TEST CODE
    """
    # Create the CustomerLogger singleton instance
    CustomerLogger(logger_name = ["test1", "test2"], console=True)
    
    @CustomerLogger.trace_call(logger_name="test1", to_log="This a test info log")
    def test_info_function(a, b, list_):
        c = a + b
        return c
    
    @CustomerLogger.trace_call(logger_name="test2", to_log="This a test error log")
    def test_error_function(a, b, list_ = None):
        c = a + b # This will raise a TypeError
        return c
    
    test_info_function(1, 2, [1, 2, 3])
    test_error_function(a = 1, b = "2")
