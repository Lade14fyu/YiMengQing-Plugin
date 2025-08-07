#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
怡梦卿(YiMengQing) - TRSS-Yunzai 占卜机器人插件
神秘的美男子古风占卜师机器人
"""

from nonebot.plugin import PluginMetadata
from nonebot import get_driver, require

from .config import Config
from .core import __plugin_meta__

# 声明插件依赖
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_datastore")

# 获取全局配置
driver = get_driver()
plugin_config = Config.parse_obj(driver.config)

# 插件元信息
__plugin_meta__ = PluginMetadata(
    name="怡梦卿",
    description="神秘的美男子古风占卜师QQ机器人插件",
    usage=(
        "1. 怡怡签到 - 每日签到\n"
        "2. 占卜 [星座] - 星座运势占卜\n"
        "3. 怡梦/怡怡 - 随机回复\n"
        "4. 怡梦卿 - 自我介绍\n"
        "5. 我该怎样说 - 使用说明"
    ),
    type="application",
    homepage="https://github.com/your-repo/yimengqing-plugin",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={
        "author": "怡境梦呓",
        "version": "3.1.3",
        "priority": 10,
    },
)

# 初始化插件
async def init_plugin():
    from pathlib import Path
    import json
    
    # 确保数据目录存在
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # 初始化默认配置文件
    config_file = data_dir / "config.json"
    if not config_file.exists():
        default_config = {
            "master_qq": 0,
            "agents": [],
            "vip_users": [1055411737],
            "debug_mode": False,
            "permission_mode": False,
            "group_approve_mode": False,
            "shutdown_code": None
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
    
    # 初始化其他数据文件
    data_files = {
        "blacklist.json": {"users": [], "words": []},
        "whitelist.json": {"users": []},
        "checkin_data.json": {},
        "blocked_words.json": []
    }
    
    for filename, content in data_files.items():
        file_path = data_dir / filename
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=4)

# 在机器人启动时初始化
driver.on_startup(init_plugin)

# 导入核心功能
from .core import (
    checkin_cmd,
    divination_cmd,
    about_cmd,
    how_to_cmd,
    chat_cmd1,
    chat_cmd2,
    vip_cmd,
    developer_cmd,
    notice_handler,
    request_handler,
    message_handler
)

# 导出插件功能
__all__ = [
    "__plugin_meta__",
    "checkin_cmd",
    "divination_cmd",
    "about_cmd",
    "how_to_cmd",
    "chat_cmd1",
    "chat_cmd2",
    "vip_cmd",
    "developer_cmd",
    "notice_handler",
    "request_handler",
    "message_handler",
    "plugin_config"
]