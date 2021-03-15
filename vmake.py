#!/usr/bin/env python3

import subprocess
import sys
import os
import re
import time

# Match file path and file location (row:column) from GCC error message
re_gcc_file_loc = [
    re.compile(r'^(?P<f_path>.*):(?P<f_loc>\d+:?\d*): ' + msg + '.+$')
    for msg in (
        'error',
        'warning',
        'note',
        'undefined reference',
    )
]

# Pass through wrapper for tmux to send escape sequence to terminal emulator
def tmux_wrap(msg):
    if not tmux_mode:
        return msg
    sys.stdout.flush()
    time.sleep(0.2)
    return '\x1bPtmux;\x1b' + msg + '\x1b\\'

# Create shell hyperlink
# https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
def shell_hyperlink(url, txt):
    HL_OSC8 = '\x1b]8;;'
    HL_ST = '\x07'

    sys.stdout.write(tmux_wrap(HL_OSC8 + url + HL_ST))
    sys.stdout.write(txt)
    sys.stdout.write(tmux_wrap(HL_OSC8 + HL_ST))

# Display hyperlink for VSCode URL handler
# https://code.visualstudio.com/docs/editor/command-line#_opening-vs-code-with-urls
def vscode_link_msg(orig_msg, m):
    f_desc = m['f_path'] + ':' + m['f_loc']
    vsc_url = f'vscode://file/{f_desc}'
    n = len(f_desc)
    orig_msg = orig_msg[:n], orig_msg[n:]
    shell_hyperlink(vsc_url, orig_msg[0])
    sys.stdout.write(orig_msg[1] + '\n')

tmux_mode = os.environ.get('TMUX') is not None

process = subprocess.Popen('make', stdout=sys.stdout, stderr=subprocess.PIPE)
for line in process.stderr:
    line = line.decode('utf-8')
    m = list(filter(None, [r.match(line) for r in re_gcc_file_loc]))
    if len(m):
        m = m[0]
        vscode_link_msg(m[0], m.groupdict())
    else:
        sys.stderr.write(line)

process.wait()
sys.exit(process.returncode)
