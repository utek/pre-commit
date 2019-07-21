import subprocess

import pre_commit.constants as C
from pre_commit.commands.init_templatedir import init_templatedir
from pre_commit.envcontext import envcontext
from pre_commit.util import cmd_output
from testing.fixtures import git_dir
from testing.fixtures import make_consuming_repo
from testing.util import cmd_output_mocked_pre_commit_home
from testing.util import cwd
from testing.util import git_commit


def test_init_templatedir(tmpdir, tempdir_factory, store, cap_out):
    target = str(tmpdir.join('tmpl'))
    init_templatedir(C.CONFIG_FILE, store, target, hook_type='pre-commit')
    lines = cap_out.get().splitlines()
    assert lines[0].startswith('pre-commit installed at ')
    assert lines[1] == (
        '[WARNING] `init.templateDir` not set to the target directory'
    )
    assert lines[2].startswith(
        '[WARNING] maybe `git config --global init.templateDir',
    )

    with envcontext([('GIT_TEMPLATE_DIR', target)]):
        path = make_consuming_repo(tempdir_factory, 'script_hooks_repo')

        with cwd(path):
            retcode, output, _ = git_commit(
                fn=cmd_output_mocked_pre_commit_home,
                tempdir_factory=tempdir_factory,
                # git commit puts pre-commit to stderr
                stderr=subprocess.STDOUT,
            )
            assert retcode == 0
            assert 'Bash hook....' in output


def test_init_templatedir_already_set(tmpdir, tempdir_factory, store, cap_out):
    target = str(tmpdir.join('tmpl'))
    tmp_git_dir = git_dir(tempdir_factory)
    with cwd(tmp_git_dir):
        cmd_output('git', 'config', 'init.templateDir', target)
        init_templatedir(C.CONFIG_FILE, store, target, hook_type='pre-commit')

    lines = cap_out.get().splitlines()
    assert len(lines) == 1
    assert lines[0].startswith('pre-commit installed at')
