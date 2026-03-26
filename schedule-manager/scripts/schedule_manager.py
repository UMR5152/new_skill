#!/usr/bin/env python3
"""
Schedule Manager Script
Manage reminders, alarms, timers, and memos.

Usage:
    python schedule_manager.py <command> [options]

Commands:
    add/add       - Add a new schedule item
    reminder/提醒 - Add a quick reminder
    alarm/闹钟    - Set an alarm
    timer/定时    - Set a countdown timer
    memo/备忘     - Add a memo/note
    list/列表     - List all schedules
    today/今天    - Show today's schedules
    delete/删除   - Delete a schedule item
    clear/清空    - Clear all schedules
    search/搜索   - Search schedules
    complete/完成 - Mark as completed
"""

import argparse
import sys
import json
import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Data storage path
DATA_DIR = os.path.expanduser("~/.schedule_manager")
DATA_FILE = os.path.join(DATA_DIR, "schedules.json")

# Command aliases
COMMAND_ALIASES = {
    "add": "add",
    "添加": "add",
    "new": "add",
    "reminder": "reminder",
    "提醒": "reminder",
    "remind": "reminder",
    "alarm": "alarm",
    "闹钟": "alarm",
    "timer": "timer",
    "定时": "timer",
    "countdown": "timer",
    "memo": "memo",
    "备忘": "memo",
    "note": "memo",
    "记事": "memo",
    "list": "list",
    "列表": "list",
    "ls": "list",
    "today": "today",
    "今天": "today",
    "delete": "delete",
    "删除": "delete",
    "remove": "delete",
    "rm": "delete",
    "clear": "clear",
    "清空": "clear",
    "reset": "clear",
    "search": "search",
    "搜索": "search",
    "find": "search",
    "complete": "complete",
    "完成": "complete",
    "done": "complete",
    "finish": "complete",
}

# Type aliases
TYPE_ALIASES = {
    "reminder": "reminder",
    "提醒": "reminder",
    "alarm": "alarm",
    "闹钟": "alarm",
    "timer": "timer",
    "定时": "timer",
    "memo": "memo",
    "备忘": "memo",
    "note": "memo",
}

# Repeat options
REPEAT_OPTIONS = ["once", "daily", "weekly", "monthly"]

# Type display names
TYPE_NAMES = {
    "reminder": "提醒",
    "alarm": "闹钟",
    "timer": "定时器",
    "memo": "备忘录",
}

# Status display names
STATUS_NAMES = {
    "pending": "待处理",
    "completed": "已完成",
    "expired": "已过期",
}


def ensure_data_dir():
    """Ensure data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_data() -> Dict[str, Any]:
    """Load schedule data from file."""
    ensure_data_dir()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"schedules": [], "next_id": 1}
    return {"schedules": [], "next_id": 1}


def save_data(data: Dict[str, Any]):
    """Save schedule data to file."""
    ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_time(time_str: str) -> Optional[datetime]:
    """Parse time string to datetime."""
    now = datetime.now()
    time_str = time_str.strip().lower()

    # Relative time: +30m, +2h
    match = re.match(r"^\+(\d+)(m|h)$", time_str)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit == "m":
            return now + timedelta(minutes=value)
        elif unit == "h":
            return now + timedelta(hours=value)

    # Keywords: today, tomorrow
    if time_str.startswith("today "):
        time_part = time_str[6:].strip()
        try:
            t = datetime.strptime(time_part, "%H:%M")
            return now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        except ValueError:
            pass

    if time_str.startswith("tomorrow "):
        time_part = time_str[9:].strip()
        try:
            t = datetime.strptime(time_part, "%H:%M")
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        except ValueError:
            pass

    # 今天/明天
    if time_str.startswith("今天 "):
        time_part = time_str[3:].strip()
        try:
            t = datetime.strptime(time_part, "%H:%M")
            return now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        except ValueError:
            pass

    if time_str.startswith("明天 "):
        time_part = time_str[3:].strip()
        try:
            t = datetime.strptime(time_part, "%H:%M")
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        except ValueError:
            pass

    # Full datetime: YYYY-MM-DD HH:MM
    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    # Date only: YYYY-MM-DD
    try:
        d = datetime.strptime(time_str, "%Y-%m-%d")
        return d.replace(hour=9, minute=0)  # Default to 9:00 AM
    except ValueError:
        pass

    # Time only: HH:MM
    try:
        t = datetime.strptime(time_str, "%H:%M")
        result = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        # If time has passed, assume tomorrow
        if result < now:
            result += timedelta(days=1)
        return result
    except ValueError:
        pass

    return None


def parse_duration(duration_str: str) -> Optional[timedelta]:
    """Parse duration string to timedelta."""
    duration_str = duration_str.strip().lower()

    match = re.match(r"^(\d+)(m|h|d)$", duration_str)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)

    return None


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    now = datetime.now()

    if dt.date() == now.date():
        return f"今天 {dt.strftime('%H:%M')}"
    elif dt.date() == (now + timedelta(days=1)).date():
        return f"明天 {dt.strftime('%H:%M')}"
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


def get_status(schedule: Dict[str, Any]) -> str:
    """Get schedule status."""
    if schedule.get("status") == "completed":
        return "completed"

    if schedule["type"] in ["reminder", "alarm", "timer"]:
        trigger_time = datetime.fromisoformat(schedule["time"])
        if trigger_time < datetime.now():
            return "expired"

    return "pending"


def add_schedule(schedule_type: str, message: str, time_str: Optional[str] = None,
                 repeat: str = "once", category: str = None) -> Dict[str, Any]:
    """Add a new schedule item."""
    data = load_data()

    schedule = {
        "id": data["next_id"],
        "type": schedule_type,
        "message": message,
        "repeat": repeat,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    if category:
        schedule["category"] = category

    if time_str:
        parsed_time = parse_time(time_str)
        if not parsed_time:
            print(f"错误: 无法解析时间 '{time_str}'")
            sys.exit(1)
        schedule["time"] = parsed_time.isoformat()

    if schedule_type == "timer" and not time_str:
        # Timer requires duration
        print("错误: 定时器需要指定时长 (例如: 30m, 1h)")
        sys.exit(1)

    data["schedules"].append(schedule)
    data["next_id"] += 1
    save_data(data)

    return schedule


def add_timer(duration_str: str, message: str) -> Dict[str, Any]:
    """Add a timer schedule."""
    duration = parse_duration(duration_str)
    if not duration:
        print(f"错误: 无法解析时长 '{duration_str}'")
        sys.exit(1)

    trigger_time = datetime.now() + duration

    # Create schedule directly to avoid parse_time
    data = load_data()
    schedule = {
        "id": data["next_id"],
        "type": "timer",
        "message": message,
        "time": trigger_time.isoformat(),
        "duration": duration_str,
        "repeat": "once",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    data["schedules"].append(schedule)
    data["next_id"] += 1
    save_data(data)

    return schedule


def list_schedules(show_all: bool = False, schedule_type: str = None) -> List[Dict[str, Any]]:
    """List all schedules."""
    data = load_data()

    schedules = []
    for s in data["schedules"]:
        # Update status
        s["status"] = get_status(s)

        # Filter by type
        if schedule_type and s["type"] != schedule_type:
            continue

        # Filter by status
        if not show_all and s["status"] in ["completed", "expired"]:
            continue

        schedules.append(s)

    # Sort by time
    def sort_key(s):
        if s["type"] == "memo":
            return datetime.max.isoformat()
        return s.get("time", datetime.max.isoformat())

    schedules.sort(key=sort_key)

    # Save updated statuses
    save_data(data)

    return schedules


def get_today_schedules() -> List[Dict[str, Any]]:
    """Get today's schedules."""
    data = load_data()
    today = datetime.now().date()

    schedules = []
    for s in data["schedules"]:
        s["status"] = get_status(s)

        if s["type"] == "memo":
            continue

        if s.get("time"):
            schedule_date = datetime.fromisoformat(s["time"]).date()
            if schedule_date == today and s["status"] == "pending":
                schedules.append(s)

    schedules.sort(key=lambda s: s.get("time", ""))

    return schedules


def delete_schedule(schedule_id: int) -> bool:
    """Delete a schedule by ID."""
    data = load_data()

    for i, s in enumerate(data["schedules"]):
        if s["id"] == schedule_id:
            data["schedules"].pop(i)
            save_data(data)
            return True

    return False


def complete_schedule(schedule_id: int) -> bool:
    """Mark a schedule as completed."""
    data = load_data()

    for s in data["schedules"]:
        if s["id"] == schedule_id:
            s["status"] = "completed"
            s["completed_at"] = datetime.now().isoformat()
            save_data(data)
            return True

    return False


def clear_schedules(schedule_type: str = None) -> int:
    """Clear all schedules or by type."""
    data = load_data()

    if schedule_type:
        original_count = len(data["schedules"])
        data["schedules"] = [s for s in data["schedules"] if s["type"] != schedule_type]
        removed = original_count - len(data["schedules"])
    else:
        removed = len(data["schedules"])
        data["schedules"] = []

    save_data(data)
    return removed


def search_schedules(keyword: str) -> List[Dict[str, Any]]:
    """Search schedules by keyword."""
    data = load_data()

    keyword = keyword.lower()
    results = []

    for s in data["schedules"]:
        s["status"] = get_status(s)
        if keyword in s.get("message", "").lower():
            results.append(s)
        elif keyword in s.get("category", "").lower():
            results.append(s)

    save_data(data)
    return results


def print_schedule_list(schedules: List[Dict[str, Any]], title: str = "日程列表"):
    """Print formatted schedule list."""
    if not schedules:
        print(f"\n📭 {title}: 暂无日程\n")
        return

    print(f"\n📋 {title}")
    print("━" * 50)

    for s in schedules:
        schedule_id = s["id"]
        schedule_type = TYPE_NAMES.get(s["type"], s["type"])
        status = STATUS_NAMES.get(s["status"], s["status"])
        message = s.get("message", "")
        repeat = s["repeat"]

        # Status icon
        status_icon = "⏳" if s["status"] == "pending" else "✅" if s["status"] == "completed" else "⌛"

        # Type icon
        type_icons = {"reminder": "🔔", "alarm": "⏰", "timer": "⏱️", "memo": "📝"}
        type_icon = type_icons.get(s["type"], "📌")

        # Time display
        time_display = ""
        if s["type"] != "memo" and s.get("time"):
            dt = datetime.fromisoformat(s["time"])
            time_display = format_datetime(dt)

        # Repeat display
        repeat_display = ""
        if repeat != "once":
            repeat_names = {"daily": "每天", "weekly": "每周", "monthly": "每月"}
            repeat_display = f" [{repeat_names.get(repeat, repeat)}]"

        # Category display
        category_display = f" [{s['category']}]" if s.get("category") else ""

        print(f"\n{status_icon} #{schedule_id} {type_icon} {schedule_type}")
        print(f"   📌 {message}")
        if time_display:
            print(f"   🕐 {time_display}{repeat_display}")
        if category_display:
            print(f"   📂 {s['category']}")
        print(f"   状态: {status}")

    print("\n" + "━" * 50)


def print_success(message: str, schedule: Dict[str, Any] = None):
    """Print success message."""
    print(f"\n✅ {message}")

    if schedule:
        schedule_type = TYPE_NAMES.get(schedule["type"], schedule["type"])
        type_icons = {"reminder": "🔔", "alarm": "⏰", "timer": "⏱️", "memo": "📝"}
        type_icon = type_icons.get(schedule["type"], "📌")

        print(f"   ID: {schedule['id']}")
        print(f"   类型: {type_icon} {schedule_type}")
        print(f"   内容: {schedule['message']}")

        if schedule.get("time"):
            dt = datetime.fromisoformat(schedule["time"])
            print(f"   时间: {format_datetime(dt)}")

        if schedule["repeat"] != "once":
            repeat_names = {"daily": "每天", "weekly": "每周", "monthly": "每月"}
            print(f"   重复: {repeat_names.get(schedule['repeat'], schedule['repeat'])}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="日程管理 - 提醒、闹钟、定时器、备忘录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s reminder "14:30" "开会"           # 设置提醒
  %(prog)s 提醒 "明天 09:00" "面试"          # 设置提醒
  %(prog)s alarm "07:00"                     # 设置闹钟
  %(prog)s timer 30m "休息一下"              # 30分钟定时器
  %(prog)s memo "记得买礼物"                 # 添加备忘
  %(prog)s list                              # 查看所有日程
  %(prog)s today                             # 今天的日程
  %(prog)s delete 1                          # 删除ID为1的日程
  %(prog)s complete 1                        # 标记完成
  %(prog)s search "开会"                     # 搜索
        """,
    )

    parser.add_argument(
        "command",
        help="命令: add/添加, reminder/提醒, alarm/闹钟, timer/定时, memo/备忘, "
             "list/列表, today/今天, delete/删除, clear/清空, search/搜索, complete/完成",
    )

    parser.add_argument(
        "args",
        nargs="*",
        help="命令参数",
    )

    parser.add_argument(
        "--type", "-t",
        help="类型: reminder/alarm/timer/memo",
    )

    parser.add_argument(
        "--time",
        help="时间 (格式: HH:MM 或 YYYY-MM-DD HH:MM)",
    )

    parser.add_argument(
        "--date",
        help="日期 (格式: YYYY-MM-DD 或 today/tomorrow)",
    )

    parser.add_argument(
        "--repeat",
        choices=REPEAT_OPTIONS,
        default="once",
        help="重复: once/daily/weekly/monthly",
    )

    parser.add_argument(
        "--message", "-m",
        help="消息/描述",
    )

    parser.add_argument(
        "--category", "-c",
        help="分类 (用于备忘录)",
    )

    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="显示所有（包括已完成）",
    )

    parser.add_argument(
        "--id",
        type=int,
        help="日程ID",
    )

    args = parser.parse_args()

    # Map command
    command = COMMAND_ALIASES.get(args.command.lower())
    if not command:
        print(f"错误: 未知命令 '{args.command}'")
        print(f"支持的命令: {', '.join(set(COMMAND_ALIASES.keys()))}")
        sys.exit(1)

    # Execute command
    if command == "add":
        # Generic add command
        schedule_type = TYPE_ALIASES.get(args.type.lower() if args.type else "reminder", "reminder")
        message = args.message or (args.args[0] if args.args else "")
        time_str = args.time or (args.args[1] if len(args.args) > 1 else None)

        if not message:
            print("错误: 请提供消息内容")
            sys.exit(1)

        schedule = add_schedule(schedule_type, message, time_str, args.repeat, args.category)
        print_success("日程已添加", schedule)

    elif command == "reminder":
        # Quick reminder: reminder "time" "message"
        time_str = args.args[0] if args.args else args.time
        message = args.args[1] if len(args.args) > 1 else args.message

        if not time_str:
            print("错误: 请提供时间")
            sys.exit(1)
        if not message:
            print("错误: 请提供提醒内容")
            sys.exit(1)

        schedule = add_schedule("reminder", message, time_str, args.repeat)
        print_success("提醒已设置", schedule)

    elif command == "alarm":
        # Quick alarm: alarm "time" [message]
        time_str = args.args[0] if args.args else args.time
        message = args.args[1] if len(args.args) > 1 else args.message or "闹钟"

        if not time_str:
            print("错误: 请提供时间")
            sys.exit(1)

        schedule = add_schedule("alarm", message, time_str, args.repeat)
        print_success("闹钟已设置", schedule)

    elif command == "timer":
        # Timer: timer "duration" [message]
        duration_str = args.args[0] if args.args else None
        message = args.args[1] if len(args.args) > 1 else args.message or "定时器"

        if not duration_str:
            print("错误: 请提供时长 (例如: 30m, 1h)")
            sys.exit(1)

        schedule = add_timer(duration_str, message)
        print_success("定时器已设置", schedule)

    elif command == "memo":
        # Memo: memo "message"
        message = args.args[0] if args.args else args.message

        if not message:
            print("错误: 请提供备忘内容")
            sys.exit(1)

        schedule = add_schedule("memo", message, category=args.category)
        print_success("备忘已添加", schedule)

    elif command == "list":
        # List schedules
        schedule_type = TYPE_ALIASES.get(args.type.lower() if args.type else None)
        schedules = list_schedules(show_all=args.all, schedule_type=schedule_type)
        print_schedule_list(schedules, "所有日程" if args.all else "待处理日程")

    elif command == "today":
        # Today's schedules
        schedules = get_today_schedules()
        print_schedule_list(schedules, "今日日程")

    elif command == "delete":
        # Delete schedule
        schedule_id = args.id or (int(args.args[0]) if args.args else None)

        if not schedule_id:
            print("错误: 请提供日程ID")
            sys.exit(1)

        if delete_schedule(schedule_id):
            print_success(f"日程 #{schedule_id} 已删除")
        else:
            print(f"错误: 找不到日程 #{schedule_id}")
            sys.exit(1)

    elif command == "complete":
        # Mark complete
        schedule_id = args.id or (int(args.args[0]) if args.args else None)

        if not schedule_id:
            print("错误: 请提供日程ID")
            sys.exit(1)

        if complete_schedule(schedule_id):
            print_success(f"日程 #{schedule_id} 已完成")
        else:
            print(f"错误: 找不到日程 #{schedule_id}")
            sys.exit(1)

    elif command == "clear":
        # Clear schedules
        schedule_type = TYPE_ALIASES.get(args.type.lower() if args.type else None)
        removed = clear_schedules(schedule_type)

        if schedule_type:
            type_name = TYPE_NAMES.get(schedule_type, schedule_type)
            print_success(f"已清空 {removed} 个{type_name}")
        else:
            print_success(f"已清空所有日程 (共 {removed} 个)")

    elif command == "search":
        # Search schedules
        keyword = args.args[0] if args.args else None

        if not keyword:
            print("错误: 请提供搜索关键词")
            sys.exit(1)

        schedules = search_schedules(keyword)
        print_schedule_list(schedules, f"搜索结果: \"{keyword}\"")


if __name__ == "__main__":
    main()
