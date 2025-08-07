#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
import traceback
import gzip
import io

from ..config import config

class EnhancedJSONFormatter(logging.Formatter):
    """支持结构化日志的JSON格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        """将日志记录转为JSON字符串"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
            "path": record.pathname,
            "process": record.process,
            "thread": record.threadName
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = traceback.format_exc()
        
        # 添加自定义字段
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data, ensure_ascii=False)

class LogRotator:
    """自定义日志轮转处理器"""
    
    def __init__(self, max_size: int = 10*1024*1024, backup_count: int = 30):
        self.max_size = max_size  # 10MB
        self.backup_count = backup_count
    
    def should_rollover(self, log_file: Path) -> bool:
        """检查是否需要轮转"""
        if not log_file.exists():
            return False
        return log_file.stat().st_size >= self.max_size
    
    def do_rollover(self, log_file: Path):
        """执行日志轮转"""
        for i in range(self.backup_count-1, 0, -1):
            src = log_file.with_suffix(f".{i}.gz")
            if src.exists():
                dst = log_file.with_suffix(f".{i+1}.gz")
                src.replace(dst)
        
        # 压缩当前日志
        with open(log_file, 'rb') as f_in:
            with gzip.open(log_file.with_suffix('.1.gz'), 'wb') as f_out:
                f_out.writelines(f_in)
        
        # 清空当前日志
        with open(log_file, 'w') as f:
            f.truncate()

class LoggerService:
    """高级日志服务"""
    service_name = "logger"
    
    def __init__(self):
        self.log_dir = config.data_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # 主日志配置
        self.main_logger = self._setup_logger(
            name="yimengqing",
            filename=self.log_dir / "main.log",
            level=logging.INFO
        )
        
        # 审计日志
        self.audit_logger = self._setup_logger(
            name="audit",
            filename=self.log_dir / "audit.log",
            level=logging.INFO,
            formatter=EnhancedJSONFormatter()
        )
        
        # 错误日志
        self.error_logger = self._setup_logger(
            name="error",
            filename=self.log_dir / "error.log",
            level=logging.ERROR,
            formatter=EnhancedJSONFormatter()
        )
        
        # 调试日志（仅在调试模式启用）
        if config.config.debug_mode:
            self.debug_logger = self._setup_logger(
                name="debug",
                filename=self.log_dir / "debug.log",
                level=logging.DEBUG
            )
    
    def _setup_logger(self, name: str, filename: Path, 
                     level: int, formatter: Optional[logging.Formatter] = None) -> logging.Logger:
        """配置日志记录器"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 文件处理器
        file_handler = logging.handlers.WatchedFileHandler(filename, encoding='utf-8')
        file_handler.setLevel(level)
        
        # 格式化器
        if formatter is None:
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d - %(message)s'
            )
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_operation(self, action: str, operator: int, 
                     target: Optional[int] = None, 
                     details: Optional[Dict] = None):
        """记录关键操作日志"""
        log_data = {
            "action": action,
            "operator": operator,
            "target": target,
            "timestamp": datetime.now().isoformat()
        }
        if details:
            log_data.update(details)
        
        self.audit_logger.info(
            "Operation Log", 
            extra={"log_data": log_data}
        )
    
    def log_command(self, user_id: int, group_id: int, 
                   command: str, result: str):
        """记录命令执行日志"""
        self.main_logger.info(
            f"Command executed - User:{user_id} Group:{group_id} "
            f"Command:'{command}' Result:'{result[:100]}'"
        )
    
    def log_error(self, error_type: str, context: str, 
                 exception: Optional[Exception] = None):
        """记录错误日志"""
        exc_info = traceback.format_exc() if exception else None
        self.error_logger.error(
            f"{error_type} error occurred",
            extra={
                "context": context,
                "exception": exc_info
            }
        )
        
        # 同时记录到主日志
        self.main_logger.error(
            f"{error_type} error: {context}",
            exc_info=exception
        )
    
    def log_debug(self, message: str, extra: Optional[Dict] = None):
        """记录调试日志"""
        if not config.config.debug_mode:
            return
        
        if extra:
            self.debug_logger.debug(message, extra=extra)
        else:
            self.debug_logger.debug(message)
    
    def get_recent_logs(self, log_type: str = "main", lines: int = 100) -> str:
        """获取最近的日志内容"""
        log_file = self.log_dir / f"{log_type}.log"
        if not log_file.exists():
            return f"No {log_type} logs found"
        
        # 处理gzip压缩的日志
        if log_type in ("audit", "error"):
            return self._read_json_logs(log_file, lines)
        else:
            return self._read_text_logs(log_file, lines)
    
    def _read_text_logs(self, file_path: Path, lines: int) -> str:
        """读取文本格式日志"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()[-lines:]
        return ''.join(content)
    
    def _read_json_logs(self, file_path: Path, lines: int) -> str:
        """读取JSON格式日志"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()[-lines:]
        
        try:
            logs = [json.loads(line) for line in content]
            return json.dumps(logs, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return ''.join(content)

# 服务实例
logger_service = LoggerService()

# 快捷访问方法
def log_command(user_id: int, group_id: int, command: str, result: str):
    logger_service.log_command(user_id, group_id, command, result)

def log_error(error_type: str, context: str, exception: Optional[Exception] = None):
    logger_service.log_error(error_type, context, exception)

def log_operation(action: str, operator: int, target: Optional[int] = None, details: Optional[Dict] = None):
    logger_service.log_operation(action, operator, target, details)