#!/usr/bin/env python
#
# git hook that checks for common mistakes that you usually do not want to
# commit (such as "debugger" statements).
#
# Copyright (c) 2015, Wolfgang Schnerring
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import collections
import fnmatch
import re
import subprocess
import sys


__version__ = '1.1.dev0'


def main():
    PATTERNS = read_config()

    to_commit = cmd('git diff --no-color --staged')
    lines = to_commit.splitlines(True)

    # Taken from <https://bitbucket.org/birkenfeld/hgcodesmell>
    filestart = 0
    hunkstart = 0
    smell_count = 0
    for i, line in enumerate(lines):
        if line.startswith('diff'):
            filestart = i
            filename = line.split()[-1]
            smells = []
            for extension, pattern in PATTERNS.items():
                if not fnmatch.fnmatch(filename, extension):
                    continue
                smells.extend(pattern)
        elif line.startswith('@@'):
            hunkstart = i
        elif line.startswith('+'):
            for regex in smells:
                if regex.search(line):
                    diff = (lines[filestart:filestart + 3] +
                            lines[hunkstart:i + 4])
                    print(''.join(diff))
                    smell_count += 1
                    break
    if smell_count:
        print('\nCommit aborted, found {} smelly changes. '
              '(Use git commit --no-verify to commit anyway)'.format(
                  smell_count))
        sys.exit(1)


_pattern_re = re.compile(r'^codesmell.*?\.(.+) (.+)$')


def read_config():
    patterns = collections.defaultdict(list)
    config = cmd('git config --get-regexp codesmell')
    for line in config.splitlines():
        match = _pattern_re.search(line)
        extension = match.group(1)
        if extension == 'all-files':
            extension = '*'
        else:
            extension = '*.%s' % extension
        pattern = match.group(2)
        pattern = pattern.replace('\\', '\\\\')
        patterns[extension].append(re.compile(pattern))
    return patterns


def cmd(cmd):
    process = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # XXX This simply assumes utf8 -- is that feasible?
    return stdout.strip().decode('utf8')


if __name__ == '__main__':
    main()
