#!/bin/bash
# 音箱健康诊断脚本
# 用于监控音箱系统状态并记录日志

LOG_FILE="/var/log/speaker_health.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$(command -v python3 || command -v python)"
HOME_CONTROL_SCRIPT="$SCRIPT_DIR/home_control.py"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_speaker_connectivity() {
    log "=== 开始音箱健康检查 ==="

    # 检查 home_control 脚本是否存在
    if [ ! -f "$HOME_CONTROL_SCRIPT" ]; then
        log "❌ 错误: 找不到 home_control.py 脚本"
        return 1
    fi

    # 检查 Python 是否可用
    if [ -z "$PYTHON_BIN" ]; then
        log "❌ 错误: 找不到 Python 解释器"
        return 1
    fi

    # 检查 home control 服务器是否可达
    log "正在检查音箱控制服务器连接..."
    if command -v curl >/dev/null 2>&1; then
        CURL_OUTPUT=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:22222/ 2>&1)
        if [ "$CURL_OUTPUT" = "000" ]; then
            log "⚠️ 警告: 无法连接到音箱控制服务器 (127.0.0.1:22222)"
            log "提示: 请确保 home control 服务器正在运行"
        else
            log "✓ 音箱控制服务器连接正常 (HTTP $CURL_OUTPUT)"
        fi
    else
        log "⚠️ 警告: curl 命令不可用，跳过连接检查"
    fi

    # 检查音箱控制脚本是否能正常执行
    log "正在测试音箱控制脚本..."
    TEST_OUTPUT=$($PYTHON_BIN "$HOME_CONTROL_SCRIPT" speaker volume 0 2>&1)
    TEST_EXIT=$?

    if [ $TEST_EXIT -eq 0 ]; then
        log "✓ 音箱控制脚本工作正常"
    else
        log "⚠️ 警告: 音箱控制脚本执行可能存在问题"
        log "错误信息: $TEST_OUTPUT"
    fi

    # 系统资源检查
    log "检查系统资源..."
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f"), ($3/$2) * 100.0}')
    log "CPU 使用率: ${CPU_USAGE}% | 内存使用率: ${MEM_USAGE}%"

    if [ -n "$CPU_USAGE" ] && [ "$(echo "$CPU_USAGE > 80" | bc)" -eq 1 ]; then
        log "⚠️ 警告: CPU 使用率过高 (${CPU_USAGE}%)"
    fi

    if [ -n "$MEM_USAGE" ] && [ "$(echo "$MEM_USAGE > 80" | bc)" -eq 1 ]; then
        log "⚠️ 警告: 内存使用率过高 (${MEM_USAGE}%)"
    fi

    log "✓ 音箱健康检查完成"
    log "=== 音箱健康检查结束 ==="
    log ""
}

# 执行检查
check_speaker_connectivity

exit 0
