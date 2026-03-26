# Schedule Manager (schedule-manager)

## Description

A comprehensive schedule management tool for setting reminders, alarms, timers, and memos. This skill helps you organize your daily tasks and never forget important events.

## Usage

```bash
python scripts/schedule_manager.py <command> [options]
```

### Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `add` | `添加` | Add a new schedule item |
| `reminder` | `提醒` | Add a quick reminder |
| `alarm` | `闹钟` | Set an alarm |
| `timer` | `定时` | Set a countdown timer |
| `memo` | `备忘` | Add a memo/note |
| `list` | `列表` | List all schedules |
| `today` | `今天` | Show today's schedules |
| `delete` | `删除` | Delete a schedule item |
| `clear` | `清空` | Clear all schedules |
| `search` | `搜索` | Search schedules |

### Options

| Option | Description |
|--------|-------------|
| `--type`, `-t` | Schedule type: reminder/alarm/timer/memo |
| `--time` | Time (format: HH:MM or YYYY-MM-DD HH:MM) |
| `--date` | Date (format: YYYY-MM-DD or today/tomorrow) |
| `--repeat` | Repeat: once/daily/weekly/monthly |
| `--message`, `-m` | Message/description |
| `--duration`, `-d` | Duration for timer (e.g., 30m, 1h) |
| `--id` | Schedule ID for deletion |
| `--all`, `-a` | Show all including completed |

## Schedule Types

### 1. Reminder (提醒)
Set reminders for specific times with custom messages.

### 2. Alarm (闹钟)
Simple alarms that ring at specified times.

### 3. Timer (定时器)
Countdown timers for short-term tasks.

### 4. Memo (备忘录)
Notes and things to remember without specific time.

## Examples

```bash
# === 提醒 ===

# 添加提醒
python scripts/schedule_manager.py add --type reminder --time "14:30" --message "开会"
python scripts/schedule_manager.py 添加 提醒 --time "2024-03-20 09:00" --message "项目截止"

# 快速提醒
python scripts/schedule_manager.py reminder "18:00" "下班记得买菜"
python scripts/schedule_manager.py 提醒 "明天 10:00" "参加面试"

# 重复提醒
python scripts/schedule_manager.py add -t reminder --time "09:00" --repeat daily -m "晨会"

# === 闹钟 ===

# 设置闹钟
python scripts/schedule_manager.py alarm "07:00"
python scripts/schedule_manager.py 闹钟 "07:30" --message "起床"

# 重复闹钟
python scripts/schedule_manager.py alarm "08:00" --repeat daily

# === 定时器 ===

# 设置定时器（30分钟后提醒）
python scripts/schedule_manager.py timer 30m "休息一下"
python scripts/schedule_manager.py 定时 1h "代码写完了"

# === 备忘录 ===

# 添加备忘
python scripts/schedule_manager.py memo "记得买生日礼物"
python scripts/schedule_manager.py 备忘 "WiFi密码: abc123"

# 带分类的备忘
python scripts/schedule_manager.py memo "银行卡号: 6222..." --category "重要"

# === 查询 ===

# 查看所有日程
python scripts/schedule_manager.py list
python scripts/schedule_manager.py 列表

# 查看今天的日程
python scripts/schedule_manager.py today
python scripts/schedule_manager.py 今天

# 查看所有（包括已完成）
python scripts/schedule_manager.py list --all

# 搜索
python scripts/schedule_manager.py search "开会"
python scripts/schedule_manager.py 搜索 "生日"

# === 管理 ===

# 删除日程
python scripts/schedule_manager.py delete 1
python scripts/schedule_manager.py 删除 2

# 清空所有
python scripts/schedule_manager.py clear
python scripts/schedule_manager.py 清空

# 标记完成
python scripts/schedule_manager.py complete 1
python scripts/schedule_manager.py 完成 2
```

## Data Storage

Schedule data is stored in:
```
~/.schedule_manager/schedules.json
```

### Data Structure

```json
{
  "schedules": [
    {
      "id": 1,
      "type": "reminder",
      "message": "开会",
      "time": "2024-03-20T14:30:00",
      "repeat": "once",
      "status": "pending",
      "created_at": "2024-03-19T10:00:00"
    }
  ]
}
```

## Features

- **Multiple Types**: Reminders, alarms, timers, and memos
- **Repeat Options**: Once, daily, weekly, monthly
- **Natural Time**: Support "today", "tomorrow", relative time
- **Search**: Quick search through all schedules
- **Categories**: Organize memos by category
- **Status Tracking**: Track pending/completed items

## Time Format Support

| Format | Example | Description |
|--------|---------|-------------|
| `HH:MM` | `14:30` | Time today |
| `YYYY-MM-DD HH:MM` | `2024-03-20 09:00` | Full datetime |
| `today HH:MM` | `today 15:00` | Today at time |
| `tomorrow HH:MM` | `tomorrow 09:00` | Tomorrow at time |
| `+Nm` | `+30m` | N minutes from now |
| `+Nh` | `+2h` | N hours from now |
| `Nd` | `3d` | N days (for timer) |

## Requirements

- Python 3.8+

## Installation

No additional dependencies required. Uses Python standard library.

## Workflow

1. Parse command and options
2. Validate input parameters
3. Create/update schedule in local storage
4. Display confirmation or list results
