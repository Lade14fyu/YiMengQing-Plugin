#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional
from datetime import datetime
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from ..config import config
from ..utils.time_utils import get_time_period, get_current_time

class ResponseTemplates:
    """响应消息模板库"""

    # 签到回复模板
    @staticmethod
    def checkin_response(user_id: int, days: int, horoscope: str) -> Message:
        """生成签到回复消息
        
        Args:
            user_id: 用户QQ号
            days: 累计签到天数
            horoscope: 今日黄历
            
        Returns:
            Message: 构造的回复消息
        """
        period = get_time_period()
        msg = Message()
        msg.append(MessageSegment.at(user_id))
        msg.append(MessageSegment.text(" "))

        if period == "morning":
            text = (
                f"嗯哼~又有顾客了，签到成功噢，{horoscope}\n"
                f"这位客官，你已经签到{days}天了呢，要不要占卜一下你的运势呀?"
            )
        elif period == "afternoon":
            text = (
                f"下午好啊客官~真是让我等着急了呢，签到成功噢~\n"
                f"这是您第{days}次光顾小店，祝您今日幸运~"
            )
        else:
            text = (
                "啊~(打哈欠)，还没睡呢客官?半夜来光顾我这荒山野岭的小店?\n"
                "真是有兴致……不能打卡了，早上五点再来吧……"
            )
        
        msg.append(MessageSegment.text(text))
        return msg

    # 占卜回复模板
    @staticmethod
    def divination_response(constellation: str, result: Dict) -> Message:
        """生成占卜回复消息
        
        Args:
            constellation: 星座名称
            result: 占卜结果，包含:
                - level: 运势等级
                - description: 运势描述
                - advice: 建议
                
        Returns:
            Message: 构造的回复消息
        """
        level_icons = {
            "大吉": "✨",
            "中吉": "⭐",
            "小吉": "🌙",
            "凶": "⚠️",
            "大凶": "💀"
        }
        
        icon = level_icons.get(result["level"], "🔮")
        
        return Message([
            MessageSegment.text(f"{icon} {constellation}今日运势 {icon}\n"),
            MessageSegment.text(f"「{result['level']}」\n\n"),
            MessageSegment.text(f"{result['description']}\n\n"),
            MessageSegment.text(f"📜 建议: {result['advice']}")
        ])

    # 通用回复模板
    @staticmethod
    def general_response(response_type: str, **kwargs) -> Message:
        """通用回复模板
        
        Args:
            response_type: 回复类型，支持:
                - "welcome": 新人欢迎
                - "help": 帮助信息
                - "error": 错误提示
                - "vip": VIP专属回复
            **kwargs: 模板参数
            
        Returns:
            Message: 构造的回复消息
        """
        templates = {
            "welcome": lambda: f"欢迎{kwargs.get('username', '新成员')}加入本群！",
            "help": lambda: (
                "可用命令:\n"
                "1. 怡怡签到 - 每日签到\n"
                "2. 占卜 [星座] - 星座运势\n"
                "3. 怡梦 - 随机对话"
            ),
            "error": lambda: (
                f"出错啦: {kwargs.get('error', '未知错误')}\n"
                f"时间: {get_current_time()}"
            ),
            "vip": lambda: (
                f"尊贵的VIP {kwargs.get('username')}，"
                f"您享有专属服务~"
            )
        }
        
        if response_type not in templates:
            return Message(f"未知回复类型: {response_type}")
        
        return Message(templates[response_type]())

    # 管理员操作回复模板
    @staticmethod
    def admin_response(action: str, success: bool, **kwargs) -> Message:
        """管理员操作回复
        
        Args:
            action: 操作类型，如"ban", "unban"
            success: 是否成功
            **kwargs: 额外参数
                - target: 操作目标
                - reason: 原因
                
        Returns:
            Message: 构造的回复消息
        """
        action_names = {
            "ban": "禁言",
            "unban": "解除禁言",
            "promote": "提升管理员",
            "demote": "撤销管理员"
        }
        
        action_name = action_names.get(action, action)
        
        if success:
            text = f"成功{action_name}用户 {kwargs.get('target')}"
            if "reason" in kwargs:
                text += f"，原因: {kwargs['reason']}"
        else:
            text = f"{action_name}操作失败: {kwargs.get('error', '未知错误')}"
        
        return Message(text)

    # 随机对话回复
    @staticmethod
    def random_chat_response(user_id: int, response_set: str = "normal") -> Message:
        """随机对话回复
        
        Args:
            user_id: 用户QQ号
            response_set: 回复集，可选:
                - "normal": 普通回复
                - "vip": VIP回复
                
        Returns:
            Message: 构造的回复消息
        """
        responses = {
            "normal": [
                "叫我做什么，莫非是被开水烫着了？安静一会儿，我头疼。",
                "哪个客官？某非是想着给小店增点热闹？站那干甚？只有不嫌本店破旧，原地坐下即可。",
                "没空，自己玩去。",
                "说吧，听着呢。",
                "嘘……请勿喧哗。",
                "吵吵闹闹的作甚？安静一点……"
            ],
            "vip": [
                "哎呦~你来啦?抱抱~想死你了。",
                "VIP客官驾到，小店蓬荜生辉~",
                "特意为您准备了上好的茶叶，请慢用~"
            ]
        }
        
        msg = Message()
        msg.append(MessageSegment.at(user_id))
        msg.append(MessageSegment.text(" "))
        
        if response_set == "vip" and user_id in config.config.vip_users:
            msg.append(MessageSegment.text(random.choice(responses["vip"])))
        else:
            msg.append(MessageSegment.text(random.choice(responses["normal"])))
        
        return msg

# 实例化模板类
response_templates = ResponseTemplates()

# 快捷访问方法
def get_checkin_response(user_id: int, days: int, horoscope: str) -> Message:
    return response_templates.checkin_response(user_id, days, horoscope)

def get_divination_response(constellation: str, result: Dict) -> Message:
    return response_templates.divination_response(constellation, result)

def get_random_chat_response(user_id: int, response_set: str = "normal") -> Message:
    return response_templates.random_chat_response(user_id, response_set)

# 导出接口
__all__ = [
    'response_templates',
    'get_checkin_response',
    'get_divination_response',
    'get_random_chat_response'
]