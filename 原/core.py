#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any, Optional, Union
from datetime import datetime
from nonebot import on_message, on_notice, on_command, on_request
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
    NoticeEvent,
    RequestEvent,
    Message,
    MessageSegment
)
from nonebot.rule import Rule, to_me
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from .config import config
from .handlers import (
    chat_handler,
    checkin_handler,
    developer_handler,
    divination_handler,
    group_manage_handler
)
from .utils.time_utils import get_current_time, get_time_period
from .utils.message_utils import extract_command

# ---------------------------- 插件元信息 ----------------------------
__plugin_meta__ = PluginMetadata(
    name="怡梦卿",
    description="神秘的美男子古风占卜师",
    usage=(
        "1. 发送'怡怡签到' - 每日签到\n"
        "2. 发送'占卜 [星座]' - 星座运势占卜\n"
        "3. 发送'怡梦'或'怡怡' - 随机回复\n"
        "4. 发送'怡梦卿' - 自我介绍\n"
        "5. 发送'我该怎样说' - 使用说明"
    ),
    extra={
        "author": "怡境梦呓",
        "version": "3.1.3",
        "priority": 10
    }
)

# ---------------------------- 规则定义 ----------------------------
async def _is_group_event(event: MessageEvent) -> bool:
    """检查是否是群聊事件"""
    return isinstance(event, GroupMessageEvent)

async def _is_private_event(event: MessageEvent) -> bool:
    """检查是否是私聊事件"""
    return isinstance(event, PrivateMessageEvent)

async def _is_admin_event(event: MessageEvent) -> bool:
    """检查是否是管理员事件"""
    return config.is_admin(event.user_id)

group_rule = Rule(_is_group_event)
private_rule = Rule(_is_private_event)
admin_rule = Rule(_is_admin_event)

# ---------------------------- 命令注册 ----------------------------
checkin_cmd = on_command(
    "怡怡签到", 
    aliases={"怡签到"}, 
    rule=group_rule, 
    priority=10,
    block=True
)

divination_cmd = on_command(
    "占卜", 
    rule=group_rule, 
    priority=10,
    block=True
)

about_cmd = on_command(
    "怡梦卿", 
    aliases={"你好", "你是"}, 
    rule=group_rule, 
    priority=10,
    block=True
)

how_to_cmd = on_command(
    "我该怎样说", 
    aliases={"我该怎样说?"}, 
    rule=group_rule, 
    priority=10,
    block=True
)

chat_cmd1 = on_command(
    "怡梦", 
    aliases={"怡怡"}, 
    rule=group_rule, 
    priority=10,
    block=True
)

chat_cmd2 = on_command(
    "怡梦卿", 
    rule=group_rule, 
    priority=10,
    block=True
)

vip_cmd = on_command(
    "怡", 
    rule=group_rule, 
    priority=10,
    block=True
)

developer_cmd = on_command(
    "梦到什么了", 
    rule=private_rule & admin_rule, 
    priority=1,
    block=True
)

# ---------------------------- 事件处理器 ----------------------------
notice_handler = on_notice(rule=group_rule, priority=5)
request_handler = on_request(priority=5)
message_handler = on_message(rule=group_rule, priority=20)

# ---------------------------- 命令处理器 ----------------------------
@checkin_cmd.handle()
async def handle_checkin(bot: Bot, event: GroupMessageEvent):
    """处理签到命令"""
    user_id = event.user_id
    group_id = event.group_id
    await checkin_handler.handle_checkin(bot, user_id, group_id)

@divination_cmd.handle()
async def handle_divination(
    bot: Bot, 
    event: GroupMessageEvent, 
    args: Message = CommandArg()
):
    """处理占卜命令"""
    user_id = event.user_id
    group_id = event.group_id
    constellation = args.extract_plain_text().strip()
    await divination_handler.handle_divination(
        bot, user_id, group_id, constellation
    )

@about_cmd.handle()
async def handle_about(bot: Bot, event: GroupMessageEvent):
    """处理自我介绍"""
    group_id = event.group_id
    await chat_handler.handle_about(bot, group_id)

@how_to_cmd.handle()
async def handle_how_to(bot: Bot, event: GroupMessageEvent):
    """处理使用说明"""
    group_id = event.group_id
    await chat_handler.handle_how_to(bot, group_id)

@chat_cmd1.handle()
async def handle_chat1(bot: Bot, event: GroupMessageEvent):
    """处理普通对话1"""
    user_id = event.user_id
    group_id = event.group_id
    await chat_handler.handle_chat1(bot, user_id, group_id)

@chat_cmd2.handle()
async def handle_chat2(bot: Bot, event: GroupMessageEvent):
    """处理普通对话2"""
    user_id = event.user_id
    group_id = event.group_id
    await chat_handler.handle_chat2(bot, user_id, group_id)

@vip_cmd.handle()
async def handle_vip(bot: Bot, event: GroupMessageEvent):
    """处理VIP命令"""
    user_id = event.user_id
    group_id = event.group_id
    await chat_handler.handle_vip(bot, user_id, group_id)

@developer_cmd.handle()
async def handle_developer(bot: Bot, event: PrivateMessageEvent):
    """处理开发者命令"""
    user_id = event.user_id
    await developer_handler.handle_developer(bot, user_id)

# ---------------------------- 事件处理器 ----------------------------
@notice_handler.handle()
async def handle_notice(bot: Bot, event: NoticeEvent):
    """处理通知事件"""
    await group_manage_handler.handle_notice(bot, event)

@request_handler.handle()
async def handle_request(bot: Bot, event: RequestEvent):
    """处理请求事件"""
    await group_manage_handler.handle_request(bot, event)

@message_handler.handle()
async def handle_message(bot: Bot, event: GroupMessageEvent):
    """
    处理普通消息
    1. 检查开发者命令
    2. 检查屏蔽词
    3. 检查权限模式
    """
    user_id = event.user_id
    message = str(event.message)
    
    # 1. 检查开发者命令
    if await developer_handler.check_developer_commands(bot, event):
        return
    
    # 2. 检查屏蔽词
    if await group_manage_handler.check_blocked_words(bot, event):
        return
    
    # 3. 检查权限模式
    if (config.config.permission_mode and 
        not (config.is_admin(user_id) or config.is_vip(user_id))):
        await developer_handler.request_permission(bot, event)
        return

# ---------------------------- 辅助函数 ----------------------------
async def check_permission(
    bot: Bot, 
    event: MessageEvent, 
    matcher: Matcher, 
    state: T_State
) -> bool:
    """检查权限的通用函数"""
    user_id = event.user_id
    
    # 如果是主人或代理人，直接放行
    if config.is_admin(user_id):
        return True
    
    # 如果是VIP用户且不在权限模式下放行
    if config.is_vip(user_id) and not config.config.permission_mode:
        return True
    
    # 其他情况需要申请权限
    await matcher.finish("您没有权限执行此操作")
    return False

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
    "check_permission"
]