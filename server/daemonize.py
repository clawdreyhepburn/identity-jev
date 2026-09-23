#!/usr/bin/env python3
"""Double-fork a command into a true daemon detached from the launching shell.

Usage:
  python server/daemonize.py <pidfile> <logfile> -- <cmd> [args...]
"""
import os
import sys


def main():
    if "--" not in sys.argv:
        print("usage: daemonize.py <pidfile> <logfile> -- <cmd> [args...]")
        sys.exit(2)
    sep = sys.argv.index("--")
    pidfile = sys.argv[1]
    logfile = sys.argv[2]
    cmd = sys.argv[sep + 1:]
    if not cmd:
        print("no command")
        sys.exit(2)

    # first fork
    if os.fork() > 0:
        sys.exit(0)
    os.setsid()
    # second fork
    if os.fork() > 0:
        sys.exit(0)

    # fully detached grandchild
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(os.devnull, "r") as devnull:
        os.dup2(devnull.fileno(), 0)
    logfd = os.open(logfile, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    os.dup2(logfd, 1)
    os.dup2(logfd, 2)

    with open(pidfile, "w") as f:
        f.write(str(os.getpid()))

    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
