#!/usr/bin/env python3
"""epoch - Convert between unix timestamps and human dates.

Usage:
    epoch.py                        Current time in all formats
    epoch.py 1741836720             Timestamp → human
    epoch.py "2026-03-15 04:00"     Human → timestamp
    epoch.py diff 1741836720 now    Time difference
    epoch.py add 1741836720 2h30m   Add duration to timestamp
"""

import sys, time, re
from datetime import datetime, timezone, timedelta

def parse_duration(s: str) -> timedelta:
    """Parse durations like 2h30m, 45s, 1d12h."""
    total = timedelta()
    for val, unit in re.findall(r'(\d+)\s*([dhms])', s.lower()):
        val = int(val)
        if unit == 'd': total += timedelta(days=val)
        elif unit == 'h': total += timedelta(hours=val)
        elif unit == 'm': total += timedelta(minutes=val)
        elif unit == 's': total += timedelta(seconds=val)
    return total

def ts_to_human(ts: float) -> dict:
    utc = datetime.fromtimestamp(ts, tz=timezone.utc)
    local = datetime.fromtimestamp(ts)
    return {
        "unix": int(ts),
        "unix_ms": int(ts * 1000),
        "utc": utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "local": local.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "iso": utc.isoformat(),
        "relative": relative_time(ts),
    }

def human_to_ts(s: str) -> float:
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
        try:
            return datetime.strptime(s, fmt).timestamp()
        except ValueError:
            continue
    raise ValueError(f"Can't parse date: {s}")

def relative_time(ts: float) -> str:
    diff = time.time() - ts
    ago = diff > 0
    diff = abs(diff)
    if diff < 60: return f"{int(diff)}s {'ago' if ago else 'from now'}"
    if diff < 3600: return f"{int(diff/60)}m {'ago' if ago else 'from now'}"
    if diff < 86400: return f"{diff/3600:.1f}h {'ago' if ago else 'from now'}"
    return f"{diff/86400:.1f}d {'ago' if ago else 'from now'}"

def resolve_ts(s: str) -> float:
    if s == "now": return time.time()
    try: return float(s)
    except: return human_to_ts(s)

def print_info(ts: float):
    info = ts_to_human(ts)
    for k, v in info.items():
        print(f"  {k:10s}: {v}")

def main():
    args = sys.argv[1:]
    if not args:
        print("Now:")
        print_info(time.time())
        return

    if args[0] == "diff" and len(args) >= 3:
        t1, t2 = resolve_ts(args[1]), resolve_ts(args[2])
        diff = abs(t2 - t1)
        days, rem = divmod(int(diff), 86400)
        hours, rem = divmod(rem, 3600)
        mins, secs = divmod(rem, 60)
        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        if mins: parts.append(f"{mins}m")
        if secs: parts.append(f"{secs}s")
        print(f"Difference: {' '.join(parts)} ({int(diff)}s)")
        return

    if args[0] == "add" and len(args) >= 3:
        ts = resolve_ts(args[1])
        dur = parse_duration(args[2])
        result = ts + dur.total_seconds()
        print(f"Result:")
        print_info(result)
        return

    # Single argument: detect timestamp vs date string
    arg = " ".join(args)
    try:
        ts = float(arg)
        # Could be seconds or milliseconds
        if ts > 1e12: ts /= 1000  # ms → s
        print(f"Timestamp {int(ts)}:")
        print_info(ts)
    except ValueError:
        ts = human_to_ts(arg)
        print(f"Date → timestamp:")
        print_info(ts)

if __name__ == "__main__":
    main()
