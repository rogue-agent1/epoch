#!/usr/bin/env python3
"""epoch - Unix timestamp converter and time calculator.

Single-file, zero-dependency CLI.
"""

import sys
import argparse
import time
import calendar
from datetime import datetime, timezone, timedelta


def cmd_now(args):
    """Show current time in all formats."""
    now = datetime.now(timezone.utc)
    ts = now.timestamp()
    local = datetime.now()
    print(f"  Unix:    {int(ts)}")
    print(f"  Millis:  {int(ts * 1000)}")
    print(f"  UTC:     {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  Local:   {local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  ISO:     {now.isoformat()}")
    print(f"  RFC2822: {now.strftime('%a, %d %b %Y %H:%M:%S +0000')}")


def cmd_convert(args):
    """Convert timestamp to human-readable."""
    ts = float(args.timestamp)
    # Auto-detect millis
    if ts > 1e12:
        ts /= 1000
    dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
    dt_local = datetime.fromtimestamp(ts)
    now = time.time()
    delta = now - ts
    if abs(delta) < 60:
        ago = f"{abs(delta):.0f}s {'ago' if delta > 0 else 'from now'}"
    elif abs(delta) < 3600:
        ago = f"{abs(delta)/60:.0f}m {'ago' if delta > 0 else 'from now'}"
    elif abs(delta) < 86400:
        ago = f"{abs(delta)/3600:.1f}h {'ago' if delta > 0 else 'from now'}"
    else:
        ago = f"{abs(delta)/86400:.1f}d {'ago' if delta > 0 else 'from now'}"
    print(f"  Unix:  {int(ts)}")
    print(f"  UTC:   {dt_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  Local: {dt_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  Rel:   {ago}")


def cmd_parse(args):
    """Parse date string to timestamp."""
    text = " ".join(args.date)
    fmts = [
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%m/%d/%Y",
        "%b %d %Y", "%B %d, %Y", "%Y%m%d",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(text, fmt)
            ts = dt.replace(tzinfo=timezone.utc).timestamp()
            print(f"  Parsed: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Unix:   {int(ts)}")
            print(f"  Format: {fmt}")
            return
        except ValueError:
            continue
    print(f"  Could not parse: {text}")
    return 1


def cmd_diff(args):
    """Difference between two timestamps."""
    a, b = float(args.a), float(args.b)
    if a > 1e12: a /= 1000
    if b > 1e12: b /= 1000
    diff = abs(b - a)
    days = int(diff // 86400)
    hours = int((diff % 86400) // 3600)
    mins = int((diff % 3600) // 60)
    secs = int(diff % 60)
    print(f"  Difference: {days}d {hours}h {mins}m {secs}s")
    print(f"  Seconds:    {diff:.0f}")
    print(f"  Minutes:    {diff/60:.1f}")
    print(f"  Hours:      {diff/3600:.2f}")
    print(f"  Days:       {diff/86400:.3f}")


def main():
    p = argparse.ArgumentParser(prog="epoch", description="Unix timestamp converter")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("now", help="Current time in all formats")
    s = sub.add_parser("convert", aliases=["c"], help="Timestamp to date")
    s.add_argument("timestamp")
    s = sub.add_parser("parse", aliases=["p"], help="Date string to timestamp")
    s.add_argument("date", nargs="+")
    s = sub.add_parser("diff", help="Diff two timestamps")
    s.add_argument("a"); s.add_argument("b")
    args = p.parse_args()
    if not args.cmd:
        p.print_help(); return 1
    cmds = {"now": cmd_now, "convert": cmd_convert, "c": cmd_convert,
            "parse": cmd_parse, "p": cmd_parse, "diff": cmd_diff}
    return cmds[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
