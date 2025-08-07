#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Union
from datetime import datetime
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from ..config import config
from ..utils.time_utils import get_current_time, humanize_time

class SystemMessages:
    """系统消息模板库"""

    @staticmethod
    def group_welcome(group_name: str, rules: List[str]) -> Message:
        """群欢迎消息模板
        
        Args:
            group_name: 群名称
            rules: 群规则列表
            
        Returns:
            Message: 欢迎消息
        """
        rules_text = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(rules))
        
        return Message([
            MessageSegment.text(f"✨ 欢迎来到「{group_name}」✨\n\n"),
            MessageSegment.text("请务必阅读以下群规：\n"),
            MessageSegment.text(rules_text),
            MessageSegment.text("\n\n祝您交流愉快~")
        ])

    @staticmethod
    def member_join(username: str) -> Message:
        """新成员加入通知
        
        Args:
            username: 新成员昵称
            
        Returns:
            Message: 欢迎消息
        """
        return Message([
            MessageSegment.text(f"👋 欢迎 {username} 加入本群！\n"),
            MessageSegment.text(f"入群时间: {get_current_time()}\n"),
            MessageSegment.text("发送「帮助」查看可用功能")
        ])

    @staticmethod
    def member_leave(username: str, last_active: datetime) -> Message:
        """成员退群通知
        
        Args:
            username: 成员昵称
            last_active: 最后活跃时间
            
        Returns:
            Message: 告别消息
        """
        return Message([
            MessageSegment.text(f"😢 成员 {username} 已离开\n"),
            MessageSegment.text(f"最后活跃: {humanize_time(last_active)}\n"),
            MessageSegment.text("有缘再见~")
        ])

    @staticmethod
    def admin_operation(action: str, operator: str, target: str, 
                       success: bool = True, reason: Optional[str] = None) -> Message:
        """管理员操作通知
        
        Args:
            action: 操作类型 (ban/unban/promote等)
            operator: 操作者
            target: 目标用户
            success: 是否成功
            reason: 操作原因
            
        Returns:
            Message: 操作通知
        """
        action_names = {
            "ban": "禁言",
            "unban": "解除禁言",
            "promote": "提升管理",
            "demote": "撤销管理",
            "kick": "移出群聊"
        }
        
        action_name = action_names.get(action, action)
        status = "成功" if success else "失败"
        
        msg = Message([
            MessageSegment.text(f"⚡ 管理员操作通知 ⚡\n"),
            MessageSegment.text(f"操作: {action_name} {target}\n"),
            MessageSegment.text(f"状态: {status}\n"),
            MessageSegment.text(f"操作者: {operator}")
        ])
        
        if reason:
            msg.append(MessageSegment.text(f"\n原因: {reason}"))
            
        return msg

    @staticmethod
    def group_notice(title: str, content: str, 
                    publisher: str, important: bool = False) -> Message:
        """群公告模板
        
        Args:
            title: 公告标题
            content: 公告内容
            publisher: 发布者
            important: 是否重要公告
            
        Returns:
            Message: 公告消息
        """
        decorator = "📢" if important else "📌"
        return Message([
            MessageSegment.text(f"{decorator} 【{title}】 {decorator}\n\n"),
            MessageSegment.text(f"{content}\n\n"),
            MessageSegment.text(f"发布者: {publisher}\n"),
            MessageSegment.text(f"发布时间: {get_current_time()}")
        ])

    @staticmethod
    def error_message(error_type: str, detail: str, 
                     suggestion: str = "") -> Message:
        """错误消息模板
        
        Args:
            error_type: 错误类型
            detail: 错误详情
            suggestion: 解决建议
            
        Returns:
            Message: 错误消息
        """
        msg = Message([
            MessageSegment.text("⚠️ 发生错误 ⚠️\n"),
            MessageSegment.text(f"类型: {error_type}\n"),
            MessageSegment.text(f"详情: {detail}")
        ])
        
        if suggestion:
            msg.append(MessageSegment.text(f"\n建议: {suggestion}"))
            
        return msg

    @staticmethod
    def debug_info(title: str, data: Union[Dict, List, str]) -> Message:
        """调试信息模板
        
        Args:
            title: 调试标题
            data: 调试数据
            
        Returns:
            Message: 调试消息
        """
        if isinstance(data, (dict, list)):
            from json import dumps
            content = dumps(data, indent=2, ensure_ascii=False)
        else:
            content = str(data)
            
        return Message([
            MessageSegment.text(f"🐛 {title} 🐛\n\n"),
            MessageSegment.text(content)
        ])

    @staticmethod
    def permission_request(action: str, requester: str, 
                          target: Optional[str] = None) -> Message:
        """权限申请通知
        
        Args:
            action: 请求的操作
            requester: 请求者
            target: 操作目标
            
        Returns:
            Message: 申请消息
        """
        msg = Message([
            MessageSegment.text("🔒 权限申请通知 🔒\n"),
            MessageSegment.text(f"操作: {action}\n"),
            MessageSegment.text(f"请求者: {requester}")
        ])
        
        if target:
            msg.append(MessageSegment.text(f"\n目标: {target}"))
            
        msg.append(MessageSegment.text("\n请回复「同意」或「拒绝」"))
        return msg

# 实例化消息模板
system_messages = SystemMessages()

# 快捷访问方法
def get_group_welcome(group_name: str, rules: List[str]) -> Message:
    return system_messages.group_welcome(group_name, rules)

def get_member_join(username: str) -> Message:
    return system_messages.member_join(username)

def get_error_message(error_type: str, detail: str, suggestion: str = "") -> Message:
    return system_messages.error_message(error_type, detail, suggestion)

# 导出接口
__all__ = [
    'system_messages',
    'get_group_welcome',
    'get_member_join',
    'get_error_message'
]