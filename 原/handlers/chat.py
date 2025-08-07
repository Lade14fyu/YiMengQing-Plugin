#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from datetime import datetime
from nonebot import Bot
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from typing import Dict, Any, Optional

from ..config import config
from ..utils.time_utils import get_time_period, get_current_time

class ChatHandler:
    def __init__(self):
        self.responses = {
            "work_say_1": [
                "叫我做什么，莫非是被开水烫着了？安静一会儿，我头疼。",
                "哪个客官？某非是想着给小店增点热闹？站那干甚？只要不嫌本店破旧，原地坐下即可。",
                "没空，自己玩去。",
                "说吧，听着呢。",
                "嘘……请勿喧哗。",
                "吵吵闹闹的作甚？安静一点……"
            ],
            "work_say_2": [
                "哎！在这呢，在这呢。",
                "什么事?",
                "您除了叫嚷就没别的本事了嘛?",
                "在这呢，要占卜么?"
            ],
            "vip_response": "哎呦~你来啦?抱抱~想死你了。"
        }

    async def handle_about(self, bot: Bot, group_id: int):
        """处理自我介绍 (对应about_yimengqing)"""
        msg = (
            "客官们好啊，我叫怡梦卿，小生来这里开了一家占卜店，"
            "有钱的捧个钱场，没钱的捧个人场。"
            "要问我怎么进店?问我'我该怎样说'，就可知咯。"
        )
        await bot.send_group_msg(group_id=group_id, message=msg)

    async def handle_how_to(self, bot: Bot, group_id: int):
        """处理使用说明 (对应about_say)"""
        msg = (
            "1.怡怡签到☞用于每天签到，不同时间段有不同回答噢。\n"
            "2.怡梦☞不同效果噢。\n"
            "3.占卜【你的星座】☞占卜星座，但有时不准噢。"
        )
        await bot.send_group_msg(group_id=group_id, message=msg)

    async def handle_chat1(self, bot: Bot, user_id: int, group_id: int):
        """处理普通对话1 (对应work_say_1)"""
        msg = random.choice(self.responses["work_say_1"])
        await bot.send_group_msg(group_id=group_id, message=msg)

    async def handle_chat2(self, bot: Bot, user_id: int, group_id: int):
        """处理普通对话2 (对应work_say_2)"""
        msg = random.choice(self.responses["work_say_2"])
        await bot.send_group_msg(group_id=group_id, message=msg)

    async def handle_vip(self, bot: Bot, user_id: int, group_id: int):
        """处理VIP对话 (对应vip_work_say_3_1)"""
        if user_id in config.config.vip_users:
            msg = self.responses["vip_response"]
            await bot.send_group_msg(group_id=group_id, message=msg)

    async def handle_passive_response(self, bot: Bot, event: Dict[str, Any]):
        """处理被动响应 (对应passive_say1_refund)"""
        if event.get('notice_type') == 'group_decrease':
            user_name = event.get('user_name', '未知用户')
            user_id = event.get('user_id', 0)
            msg = f"哎……听说又走了一位 {user_name}({user_id})"
            await bot.send_group_msg(
                group_id=event['group_id'],
                message=msg
            )

# 实例化处理器
chat_handler = ChatHandler()