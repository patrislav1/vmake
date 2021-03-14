#!/usr/bin/env python3

import subprocess
import sys
import re

re_gcc_file_loc = [
    re.compile(r'^(.*):(\d+):(\d+): ' + msg + ':(.*)$')
    for msg in (
        'error',
        'warning',
        'note',
        'undefined reference'
    )
]
# TODO: also handle messages w/o column value

def shell_hyperlink(url, txt):
    result = '\x1b]8;;'
    result += url
    result += '\x1b\\'
    result += txt
    result += '\x1b]8;;\x1b\\'
    return result

def vscode_link_msg(orig_msg, f_path, f_row, f_col):
    f_desc = f'{f_path}:{f_row}:{f_col}'
    vsc_url = f'vscode://file/{f_desc}'
    n = len(f_desc)
    orig_msg = orig_msg[:n], orig_msg[n:]
    l = shell_hyperlink(vsc_url, orig_msg[0])
    sys.stderr.write(l + orig_msg[1] + '\n')

process = subprocess.Popen('make', stdout=sys.stdout, stderr=subprocess.PIPE)
for line in process.stderr:
    line = line.decode('utf-8')
    m = list(filter(None, [r.match(line) for r in re_gcc_file_loc]))
    if len(m):
        m = m[0]
        orig_msg, f_path, f_row, f_col = [m.group(i) for i in (0, 1, 2, 3)]
        vscode_link_msg(orig_msg, f_path, f_row, f_col)
    else:
        sys.stderr.write(line)

process.wait()
sys.exit(process.returncode)
