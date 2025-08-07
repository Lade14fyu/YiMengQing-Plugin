#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .chat import chat_handler
from .checkin import checkin_handler
from .developer import developer_handler
from .divination import divination_handler
from .group_manage import group_manage_handler

__all__ = [
    'chat_handler',
    'checkin_handler',
    'developer_handler', 
    'divination_handler',
    'group_manage_handler'
]

# 版本兼容性检查
def _check_version():
    import sys
    if sys.version_info < (3, 8):
        raise RuntimeError("怡梦卿插件需要Python 3.8或更高版本")

_check_version()

# 初始化日志
import logging
logger = logging.getLogger('怡梦卿.handlers')
logger.info('所有处理器模块已加载完毕')