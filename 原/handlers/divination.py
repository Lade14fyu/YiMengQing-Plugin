#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from typing import Dict, List, Tuple
from nonebot import Bot
from nonebot.adapters.onebot.v11 import Message, MessageSegment

class DivinationHandler:
    def __init__(self):
        self.constellations = {
            "白羊座": (3, 21, 4, 19),
            "金牛座": (4, 20, 5, 20),
            "双子座": (5, 21, 6, 21),
            "巨蟹座": (6, 22, 7, 22),
            "狮子座": (7, 23, 8, 22),
            "处女座": (8, 23, 9, 22),
            "天秤座": (9, 23, 10, 23),
            "天蝎座": (10, 24, 11, 22),
            "射手座": (11, 23, 12, 21),
            "摩羯座": (12, 22, 1, 19),
            "水瓶座": (1, 20, 2, 18),
            "双鱼座": (2, 19, 3, 20)
        }
        
        self.lucky_data = self._load_lucky_data()
        self.history = {}  # 用户占卜记录缓存

    def _load_lucky_data(self) -> Dict[str, List[str]]:
        """加载运势数据"""
        return {
            "大吉": [
                "今天鸿运当头，宜大胆行动",
                "贵人相助，事业学业双丰收",
                "感情运势极佳，单身者有望邂逅良缘"
            ],
            "中吉": [
                "整体运势不错，可尝试新事物",
                "财运平稳，适合小额投资",
                "人际关系和谐，易得他人帮助"
            ],
            "小吉": [
                "运势平稳，按部就班即可",
                "注意细节处理，避免小失误",
                "健康运良好，适合锻炼身体"
            ],
            "凶": [
                "今日易遇波折，重要决策需谨慎",
                "注意口舌是非，谨言慎行为上",
                "财运不佳，避免大额消费"
            ],
            "大凶": [
                "诸事不宜，建议低调行事",
                "健康预警，注意休息调养",
                "易遇小人，重要文件需备份"
            ]
        }

    async def handle_divination(self, bot: Bot, user_id: int, group_id: int, constellation: str):
        """处理占卜请求"""
        # 验证星座有效性
        if constellation not in self.constellations:
            await bot.send_group_msg(
                group_id=group_id,
                message=self._get_invalid_constellation_msg()
            )
            return

        # 获取运势结果
        lucky_level, detail = self._generate_luck(constellation)
        
        # 构建回复消息
        msg = self._build_message(user_id, constellation, lucky_level, detail)
        
        # 发送结果
        await bot.send_group_msg(group_id=group_id, message=msg)
        
        # 记录占卜历史
        self._record_history(user_id, constellation, lucky_level)

    def _get_invalid_constellation_msg(self) -> str:
        """无效星座提示"""
        return (
            "请指定正确的星座名称，例如：\n"
            "占卜白羊座\n"
            "可用星座：\n" + 
            " ".join(self.constellations.keys())
        )

    def _generate_luck(self, constellation: str) -> Tuple[str, str]:
        """生成运势结果"""
        # 基础概率分布
        weights = {
            "大吉": 0.15,
            "中吉": 0.25,
            "小吉": 0.35,
            "凶": 0.2,
            "大凶": 0.05
        }
        
        # 根据星座微调概率
        adjustments = {
            "白羊座": {"大吉": +0.05, "凶": -0.03},
            "摩羯座": {"中吉": +0.1, "大凶": -0.05},
            "双鱼座": {"小吉": +0.07, "凶": +0.03}
        }
        
        # 应用调整
        final_weights = weights.copy()
        if constellation in adjustments:
            for k, v in adjustments[constellation].items():
                final_weights[k] += v
        
        # 确保概率合法
        total = sum(final_weights.values())
        for k in final_weights:
            final_weights[k] /= total
        
        # 随机选择运势
        levels = list(final_weights.keys())
        probs = list(final_weights.values())
        lucky_level = random.choices(levels, weights=probs, k=1)[0]
        
        # 选择详细描述
        detail = random.choice(self.lucky_data[lucky_level])
        
        return lucky_level, detail

    def _build_message(self, user_id: int, constellation: str, 
                      lucky_level: str, detail: str) -> Message:
        """构建消息内容"""
        # 基础消息
        msg = [
            MessageSegment.text(f"✨ {constellation}今日运势 ✨\n"),
            MessageSegment.text(f"「{lucky_level}」\n"),
            MessageSegment.text(detail)
        ]
        
        # 添加运势图标
        icon_map = {
            "大吉": "🎉",
            "中吉": "✨",
            "小吉": "⭐",
            "凶": "⚠️",
            "大凶": "💀"
        }
        msg.insert(1, MessageSegment.text(icon_map[lucky_level] + " "))
        
        # 添加个性化建议
        advice = self._get_personal_advice(user_id, constellation, lucky_level)
        if advice:
            msg.append(MessageSegment.text("\n\n💡 专属建议: " + advice))
        
        # VIP用户特殊待遇
        if user_id == 1055411737:  # 指定VIP用户
            msg.append(MessageSegment.text("\n\n🎁 您是我们的贵宾，今日可享专属优惠！"))
        
        return Message(msg)

    def _get_personal_advice(self, user_id: int, 
                           constellation: str, 
                           lucky_level: str) -> str:
        """生成个性化建议"""
        # 这里可以实现基于用户历史的建议
        # 示例实现简单随机建议
        advices = {
            "大吉": [
                "趁势而为，大胆推进计划",
                "适合开展新项目或表白心意"
            ],
            "中吉": [
                "保持现状会有不错收获",
                "可以尝试小幅度创新"
            ],
            "凶": [
                "重要决定请三思而后行",
                "今日不宜签署重要文件"
            ]
        }
        
        if lucky_level in advices:
            return random.choice(advices[lucky_level])
        return ""

    def _record_history(self, user_id: int, 
                       constellation: str, 
                       lucky_level: str):
        """记录占卜历史"""
        if user_id not in self.history:
            self.history[user_id] = []
        
        self.history[user_id].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "constellation": constellation,
            "result": lucky_level
        })

# 实例化占卜处理器
divination_handler = DivinationHandler()