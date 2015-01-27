git-codesmell
=============

This is a git hook that checks for common mistakes that you usually
do not want to commit (such as "debugger" statements).
It is inspired by the mercurial extension
[hgcodesmell](https://bitbucket.org/birkenfeld/hgcodesmell).

The hook is written in Python and requires at least Python 2.7 or Python
3.3.

To install it, copy `detectcodesmells.py` to `.git/hooks/pre-commit` in your
git repository (make sure the file is executable). If you want it to be added
to reposiories automatically, you need to use a
[template directory](https://coderwall.com/p/jp7d5q/create-a-global-git-commit-hook):

    $ mkdir -p ~/.git-templates/hooks
    $ cp detectcodesmells.py ~/.git-templates/hooks/pre-commit
    $ chmod +x ~/.git-templates/hooks/pre-commit
    $ git config --global init.templatedir '~/.git-templates'

You can configure the code smell patterns according to filename extension in
your `~/.gitconfig` as follows (note that backslashes need to be escaped due to
git config parsing):

    [codesmell]
    py = \\bpdb\\.set_trace\\(\\)
    py = ^\\+\\s*print\\b
    js = ^\\+\\s*debugger;
    all-files = ^(>>>>>>>|<<<<<<<)

The key is the filename extension this pattern applies to (there can be
multiple ones for the same extension). The special key `all-files` applies to
all files.

The values will be passed through `re.compile`, with backslashes escaped one
more time (so they behave like raw strings, e.g. `r'\bpdb\.set_trace\(\)'`) and
then applied with `re.search` (i.e. if you want to match from the beginning of
a line, you'll need to explicitly start the pattern with "`^`").
