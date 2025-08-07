#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import random
import secrets
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from nonebot import Bot
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
    Message,
    MessageSegment
)

from ..config import config
from ..utils.time_utils import get_current_time

class DeveloperHandler:
    def __init__(self):
        self.permission_requests: Dict[str, Dict] = {}
        self.shutdown_codes: Dict[str, str] = {}
        self.approve_rules: Dict[str, List[int]] = {
            "level_blacklist": [],
            "level_whitelist": []
        }
        self._load_approve_rules()

    def _load_approve_rules(self):
        """加载审核规则"""
        rules_file = config.data_dir / "approve_rules.json"
        if rules_file.exists():
            with open(rules_file, "r", encoding="utf-8") as f:
                self.approve_rules.update(json.load(f))

    def _save_approve_rules(self):
        """保存审核规则"""
        rules_file = config.data_dir / "approve_rules.json"
        with open(rules_file, "w", encoding="utf-8") as f:
            json.dump(self.approve_rules, f, ensure_ascii=False, indent=4)

    async def handle_developer(self, bot: Bot, user_id: int):
        """处理开发者菜单"""
        if not config.is_admin(user_id):
            return

        msg = [
            "小生……做噩梦了",
            "1.代理人设置☞参谋[QQ号]",
            "2.删除代理人☞变卦[QQ号]",
            "3.接管入群申请☞观星",
            "4.停止接管☞合眼",
            "5.设置审核条件☞挪盘",
            "6.禁言☞襟声[QQ号] [时长分钟]",
            "7.私信☞窃语[群号]#[QQ号]#[内容]",
            "8.黑名单☞山海经[QQ号]",
            "9.白名单☞封神榜[QQ号]",
            "10.开启权限审核☞修炼",
            "11.关闭权限审核☞修行",
            "12.屏蔽词☞定声[词汇]",
            "13.解除屏蔽☞诵经[词汇]",
            "14.关闭机器人☞闭关"
        ]
        await bot.send_private_msg(user_id=user_id, message="\n".join(msg))

    async def check_developer_commands(self, bot: Bot, event: MessageEvent) -> bool:
        """检查并处理开发者命令"""
        if not isinstance(event, (GroupMessageEvent, PrivateMessageEvent)):
            return False

        user_id = event.user_id
        if not config.is_admin(user_id):
            return False

        msg = str(event.message).strip()
        
        # 代理人管理
        if msg.startswith("参谋"):
            return await self._handle_agent_add(bot, event, msg[2:].strip())
        elif msg.startswith("变卦"):
            return await self._handle_agent_remove(bot, event, msg[2:].strip())
        
        # 入群审核
        elif msg == "观星":
            config.config.group_approve_mode = True
            config.save_config()
            await bot.send(event, "知道了，小生眼观六路，耳听八方。")
            return True
        elif msg == "合眼":
            config.config.group_approve_mode = False
            config.save_config()
            await bot.send(event, "已停止审核入群申请")
            return True
        
        # 其他命令处理...
        # 此处省略部分代码，实际实现需要完整处理所有命令

        return False

    async def _handle_agent_add(self, bot: Bot, event: MessageEvent, qq_str: str) -> bool:
        """添加代理人"""
        if not qq_str.isdigit():
            return False

        qq = int(qq_str)
        if len(config.config.agents) >= 2:
            await bot.send(event, "代理人已满两位，无法再添加")
        else:
            config.config.agents.append(qq)
            config.save_config()
            await bot.send(event, "啊……副店长么?小生记住了。")
        return True

    async def _handle_agent_remove(self, bot: Bot, event: MessageEvent, qq_str: str) -> bool:
        """移除代理人"""
        if not qq_str.isdigit():
            return False

        qq = int(qq_str)
        if qq in config.config.agents:
            config.config.agents.remove(qq)
            config.save_config()
            await bot.send(event, "副店长走了?来日方长，定可再见的。")
        else:
            await bot.send(event, "这位并非代理人呢")
        return True

    async def request_permission(self, bot: Bot, event: GroupMessageEvent):
        """权限申请处理"""
        if not config.config.permission_mode:
            return

        request_id = f"{event.time}_{event.user_id}_{event.group_id}"
        self.permission_requests[request_id] = {
            "user_id": event.user_id,
            "group_id": event.group_id,
            "user_name": event.sender.card or event.sender.nickname,
            "time": get_current_time(),
            "message": str(event.message),
            "responded": False
        }

        # 通知所有管理员
        admins = [config.config.master_qq] + config.config.agents
        for admin_id in admins:
            msg = (
                f"⚠️ 权限申请通知 ⚠️\n"
                f"群号: {event.group_id}\n"
                f"用户: {event.user_id}({event.sender.nickname})\n"
                f"时间: {get_current_time()}\n"
                f"内容: {event.message}\n"
                f"请回复: 同意{request_id} 或 拒绝{request_id}"
            )
            await bot.send_private_msg(user_id=admin_id, message=msg)

    async def handle_shutdown(self, bot: Bot, event: PrivateMessageEvent):
        """处理关闭机器人请求"""
        if not config.is_admin(event.user_id):
            return

        code = secrets.token_hex(4)
        self.shutdown_codes[code] = str(event.user_id)
        
        # 发送给主人
        await bot.send_private_msg(
            user_id=config.config.master_qq,
            message=f"关闭验证码: {code} (有效期10分钟)"
        )
        
        # 回复操作者
        await bot.send(
            event,
            "已给主人发送关闭码，输入正确即可关闭本bot\n"
            f"请输入: {code}"
        )

    async def verify_shutdown(self, bot: Bot, event: PrivateMessageEvent, code: str) -> bool:
        """验证关闭码"""
        if code in self.shutdown_codes:
            if self.shutdown_codes[code] == str(event.user_id):
                await bot.send(event, "已闭关，有缘再见")
                return True
        await bot.send(event, "验证失败，关闭码错误或已过期")
        return False

    async def handle_mute(self, bot: Bot, event: GroupMessageEvent, qq_str: str, duration: str = "30"):
        """处理禁言命令"""
        if not (qq_str.isdigit() and duration.isdigit()):
            return False

        qq = int(qq_str)
        minutes = int(duration)
        
        try:
            await bot.set_group_ban(
                group_id=event.group_id,
                user_id=qq,
                duration=minutes * 60
            )
            await bot.send(event, f"安静一会儿哦，{qq}这位客官")
            return True
        except Exception as e:
            await bot.send(event, f"禁言失败: {str(e)}")
            return False

# 实例化开发者处理器
developer_handler = DeveloperHandler()