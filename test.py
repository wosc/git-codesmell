# coding: utf8
import pytest
import shutil
import subprocess
import sys


def cmd(cmd):
    process = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # XXX This simply assumes utf8 -- is that feasible?
    return stdout.strip().decode('utf8'), process.returncode


@pytest.fixture(scope='session')
def gitconfig(request):
    config = cmd('git config --global --get-regexp codesmell')
    if not config:
        return

    cmd('git config --global --rename-section codesmell codesmellpytest')

    def teardown():
        cmd('git config --global --rename-section codesmellpytest codesmell')
    request.addfinalizer(teardown)

    config = cmd('git config --global --get commit.gpgsign')
    if not config:
        return
    cmd('git config --global --rename-section commit commitpytest')

    def teardown():
        cmd('git config --global --rename-section commitpytest commit')
    request.addfinalizer(teardown)


@pytest.fixture
def repository(request, gitconfig, tmpdir):
    cmd('cd {dir}; git init'.format(dir=tmpdir))
    cmd('cd {dir}; git config user.name pytest;'
        'git config user.email pytest@localhost'.format(dir=tmpdir))
    hook = '%s/.git/hooks/pre-commit' % tmpdir
    shutil.copy('detectcodesmells.py', hook)
    cmd('sed -i -e "s+/usr/bin/env python+{}+" {}'.format(
        sys.executable, hook))
    return str(tmpdir)


def test_no_patterns_configured_has_no_effect(repository):
    output, status = cmd(
        'cd {dir}; echo "qux" > bar;'
        'git add .; git commit -m "foo"'.format(dir=repository))
    assert status == 0
    assert '1 file changed' in output


def test_pattern_matches_aborts_commit(repository):
    cmd('cd {dir}; git config codesmell.all-files qux'.format(dir=repository))
    output, status = cmd(
        'cd {dir}; echo "qux" > bar;'
        'git add .; git commit -m "foo"'.format(dir=repository))
    assert status == 1
    assert '+qux' in output


def test_patterns_for_wrong_extension_has_no_effect(repository):
    cmd('cd {dir}; git config codesmell.txt qux'.format(dir=repository))
    output, status = cmd(
        'cd {dir}; echo "qux" > bar.html;'
        'git add .; git commit -m "foo"'.format(dir=repository))
    assert status == 0
    assert '1 file changed' in output
