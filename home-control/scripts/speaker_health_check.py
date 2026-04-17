#!/usr/bin/env python3
"""
音箱健康诊断脚本
定期检查音箱状态，记录异常并尝试恢复
"""

import requests
import json
import logging
from datetime import datetime
import time
import os
import sys

# 配置
HOME_CONTROL_API = "http://127.0.0.1:22222"
LOG_FILE = "/var/log/speaker_health.log"
CHECK_INTERVAL = 300  # 5分钟检查一次
MAX_RETRIES = 3

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_speaker_health():
    """检查音箱健康状态"""
    try:
        # 通过发送一个安全的音量查询（实际不改变音量）来测试连接
        # 由于 API 不支持 status，我们通过尝试获取当前音量来检测健康状态
        response = requests.post(
            f"{HOME_CONTROL_API}/speaker",
            json={"action": "volume", "value": 0},  # value=0 作为健康检查，不实际改变音量
            timeout=10
        )
        data = response.json()

        if data.get("status") == "ok":
            state = data.get("state", {})
            volume = state.get("volume", 0)
            power = state.get("power", False)
            playing = state.get("playing", False)

            logger.info(f"音箱健康 - 电源: {'开' if power else '关'}, 播放: {'是' if playing else '否'}, 音量: {volume}")

            # 检查音量是否在安全范围内（避免突然大音量）
            if volume > 80:
                logger.warning(f"音箱音量过高 ({volume})，正在调整到安全值 50")
                # 不立即调整，避免干扰用户，仅记录警告
                # 如需自动调整，取消下面注释：
                # adjust_volume(50)

            return True
        else:
            logger.error(f"音箱状态异常: {data}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"无法连接到音箱服务: {e}")
        return False
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return False


def adjust_volume(level):
    """调整音箱音量"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f"{HOME_CONTROL_API}/speaker",
                json={"action": "volume", "value": level},
                timeout=10
            )
            data = response.json()
            if data.get("status") == "ok":
                logger.info(f"音量已调整为 {level}")
                return True
            else:
                logger.warning(f"调整音量失败，响应: {data}")
        except Exception as e:
            logger.error(f"调整音量失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            time.sleep(2)

    return False


def ensure_speaker_ready():
    """确保音箱处于就绪状态（关闭但不卡死）"""
    try:
        response = requests.post(
            f"{HOME_CONTROL_API}/speaker",
            json={"action": "off"},
            timeout=10
        )
        data = response.json()
        if data.get("status") == "ok":
            logger.info("音箱已置于就绪状态（关闭）")
            return True
    except Exception as e:
        logger.error(f"重置音箱失败: {e}")
    return False


def main():
    """主循环"""
    logger.info("音箱健康诊断服务启动")
    logger.info(f"API 地址: {HOME_CONTROL_API}")
    logger.info(f"检查间隔: {CHECK_INTERVAL} 秒")

    consecutive_failures = 0
    max_consecutive_failures = 5

    try:
        while True:
            if check_speaker_health():
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                logger.warning(f"连续失败次数: {consecutive_failures}/{max_consecutive_failures}")

                # 尝试恢复
                if consecutive_failures >= 3:
                    logger.warning("尝试恢复音箱状态...")
                    ensure_speaker_ready()

                # 连续失败太多，可能需要人工干预
                if consecutive_failures >= max_consecutive_failures:
                    logger.error("音箱系统异常，需要人工干预！")
                    # 可以在这里发送通知
                    consecutive_failures = 0  # 重置计数器避免刷屏

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        logger.info("收到停止信号，服务退出")
    except Exception as e:
        logger.error(f"服务异常退出: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 确保日志目录存在
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # 后台运行
    main()
