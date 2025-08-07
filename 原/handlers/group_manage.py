#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path

from nonebot import Bot
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    GroupMessageEvent,
    NoticeEvent,
    RequestEvent,
    Message,
    MessageSegment
)

from ..config import config
from ..utils.time_utils import get_current_time

class GroupManageHandler:
    def __init__(self):
        self.data_path = config.data_dir
        self._ensure_data_files()
        self.group_settings: Dict[str, Dict] = {}  # 群设置缓存
        self._load_group_settings()

    def _ensure_data_files(self):
        """确保数据文件存在"""
        files = {
            "group_settings.json": {},
            "welcome_messages.json": {
                "default": "欢迎新人入群！请查看群公告~"
            }
        }
        
        for filename, default in files.items():
            path = self.data_path / filename
            if not path.exists():
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default, f, ensure_ascii=False, indent=4)

    def _load_group_settings(self):
        """加载群设置"""
        path = self.data_path / "group_settings.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.group_settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.group_settings = {}

    def _save_group_settings(self):
        """保存群设置"""
        path = self.data_path / "group_settings.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.group_settings, f, ensure_ascii=False, indent=4)

    async def handle_notice(self, bot: Bot, event: NoticeEvent):
        """处理通知事件"""
        if event.notice_type == "group_decrease":
            # 成员退群通知
            await self._handle_member_leave(bot, event)
        elif event.notice_type == "group_increase":
            # 新人入群通知
            await self._handle_member_join(bot, event)

    async def _handle_member_leave(self, bot: Bot, event: NoticeEvent):
        """处理成员退群"""
        user_id = event.user_id
        group_id = event.group_id
        operator_id = event.operator_id

        # 获取用户信息
        user_info = await bot.get_group_member_info(
            group_id=group_id,
            user_id=user_id,
            no_cache=True
        )
        user_name = user_info.get("card") or user_info.get("nickname") or "未知用户"

        # 构建消息
        msg = (
            f"哎……听说又走了一位 {user_name}({user_id})\n"
            f"最后活跃: {datetime.fromtimestamp(user_info.get('last_sent_time', 0))}"
        )
        
        # 添加操作者信息（如果是被踢）
        if operator_id and operator_id != user_id:
            operator_info = await bot.get_group_member_info(
                group_id=group_id,
                user_id=operator_id,
                no_cache=True
            )
            operator_name = operator_info.get("card") or operator_info.get("nickname")
            msg += f"\n操作者: {operator_name}({operator_id})"

        await bot.send_group_msg(group_id=group_id, message=msg)

    async def _handle_member_join(self, bot: Bot, event: NoticeEvent):
        """处理新人入群"""
        group_id = event.group_id
        user_id = event.user_id

        # 读取欢迎消息配置
        welcome_path = self.data_path / "welcome_messages.json"
        with open(welcome_path, "r", encoding="utf-8") as f:
            welcome_data = json.load(f)
        
        # 获取群专属欢迎语或使用默认
        welcome_msg = welcome_data.get(str(group_id)) or welcome_data["default"]
        
        # 获取用户信息
        try:
            user_info = await bot.get_group_member_info(
                group_id=group_id,
                user_id=user_id,
                no_cache=True
            )
            user_name = user_info.get("card") or user_info.get("nickname") or "新伙伴"
        except:
            user_name = "新伙伴"

        # 构建@消息
        msg = Message([
            MessageSegment.at(user_id),
            MessageSegment.text(f" {user_name}，{welcome_msg}\n"),
            MessageSegment.text("入群时间: " + get_current_time())
        ])

        await bot.send_group_msg(group_id=group_id, message=msg)

    async def handle_request(self, bot: Bot, event: RequestEvent):
        """处理加群请求"""
        if event.request_type != "group" or event.sub_type != "add":
            return

        if not config.config.group_approve_mode:
            return

        user_id = event.user_id
        group_id = event.group_id
        comment = event.comment or "无附加信息"

        # 检查黑名单
        if config.is_blacklisted(user_id):
            await bot.set_group_add_request(
                flag=event.flag,
                sub_type=event.sub_type,
                approve=False,
                reason="您在本群的黑名单中"
            )
            return

        # 检查白名单
        if config.is_whitelisted(user_id):
            await bot.set_group_add_request(
                flag=event.flag,
                sub_type=event.sub_type,
                approve=True,
                reason="欢迎加入"
            )
            return

        # 自动审核逻辑
        if await self._auto_approve_check(bot, event, user_id, comment):
            await bot.set_group_add_request(
                flag=event.flag,
                sub_type=event.sub_type,
                approve=True,
                reason="自动审核通过"
            )
        else:
            # 转发给管理员审核
            await self._forward_to_admins(bot, event, user_id, group_id, comment)

    async def _auto_approve_check(self, bot: Bot, event: RequestEvent, 
                                user_id: int, comment: str) -> bool:
        """自动审核逻辑"""
        # 1. 检查QQ等级
        try:
            user_level = await self._get_user_level(bot, user_id)
            if user_level in config.approve_rules.get("level_blacklist", []):
                return False
            if user_level in config.approve_rules.get("level_whitelist", []):
                return True
        except:
            pass

        # 2. 检查申请内容关键词
        keywords = config.approve_rules.get("keyword_rules", [])
        for kw in keywords:
            if kw in comment:
                return True

        return False

    async def _get_user_level(self, bot: Bot, user_id: int) -> int:
        """获取用户QQ等级（模拟实现）"""
        # 实际实现可能需要调用外部API
        return random.randint(1, 100)  # 模拟返回

    async def _forward_to_admins(self, bot: Bot, event: RequestEvent,
                               user_id: int, group_id: int, comment: str):
        """转发给管理员审核"""
        admins = [config.config.master_qq] + config.config.agents
        for admin_id in admins:
            msg = (
                f"📨 加群申请通知\n"
                f"群号: {group_id}\n"
                f"申请人: {user_id}\n"
                f"申请内容: {comment}\n"
                f"处理命令: 同意 {event.flag} 或 拒绝 {event.flag}"
            )
            await bot.send_private_msg(user_id=admin_id, message=msg)

    async def check_blocked_words(self, bot: Bot, event: GroupMessageEvent) -> bool:
        """检查屏蔽词"""
        message = str(event.message)
        user_id = event.user_id

        # 管理员豁免
        if config.is_admin(user_id):
            return False

        # 检查精确屏蔽词
        for word in config.blocked_words.get("words", []):
            if word.lower() in message.lower():
                await self._handle_blocked_word(bot, event, word)
                return True

        # 检查正则模式
        for pattern in config.blocked_words.get("regex_patterns", []):
            if re.search(pattern, message, re.IGNORECASE):
                await self._handle_blocked_word(bot, event, pattern)
                return True

        return False

    async def _handle_blocked_word(self, bot: Bot, event: GroupMessageEvent, word: str):
        """处理屏蔽词违规"""
        try:
            # 尝试撤回消息
            await bot.delete_msg(message_id=event.message_id)
        except Exception as e:
            pass

        # 发送警告
        warning = (
            f"检测到违规内容，已自动处理\n"
            f"违规用户: {event.sender.nickname}\n"
            f"违规内容: {word[:20]}...\n"
            f"请遵守群规，文明交流"
        )
        await bot.send_group_msg(group_id=event.group_id, message=warning)

        # 记录违规
        self._log_violation(event.user_id, event.group_id, word)

    def _log_violation(self, user_id: int, group_id: int, word: str):
        """记录违规日志"""
        log_path = self.data_path / "violation_log.json"
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []

        logs.append({
            "user_id": user_id,
            "group_id": group_id,
            "word": word,
            "time": get_current_time()
        })

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)

# 实例化群管理处理器
group_manage_handler = GroupManageHandler()