import io
import os
import unittest

import universal_hooks
from universal_hooks import _regex_from_dir, _make_dir_matchers, FileSystem, _run_dir, _run_pkg_dirs, \
    TransactionInfo, UniversalHooksPlugin

HOOK_NAMES = 'pre_config config resolved sack pre_transaction transaction'.split()


class TestHooks(unittest.TestCase):
    def test_suffix(self):
        m = _regex_from_dir('ea-__WILDCARD__')

        self.assertTrue(m.search('ea-'))
        self.assertTrue(m.search('ea-foo'))

    def test_prefix(self):
        m = _regex_from_dir('__WILDCARD__-devel')
        self.assertTrue(m.search('foo-devel'))

    def test_middle(self):
        m = _regex_from_dir('__WILDCARD__perl__WILDCARD__')
        self.assertTrue(m.search('perl'))
        self.assertTrue(m.search('preperlpost'))

    def test_make_dir_matchers(self):
        universal_hooks.fs = WildcardStub()
        dir_matchers = _make_dir_matchers('/unit/wildcard_root')

        self.assertEqual(2, len(dir_matchers))
        self.assertListEqual(['dir1', 'dir2__WILDCARD__'], sorted(dir_matchers.keys()))
        self.assertTrue(dir_matchers['dir1'].search('dir1'))
        self.assertTrue(dir_matchers['dir2__WILDCARD__'].search('dir2'))
        self.assertTrue(dir_matchers['dir2__WILDCARD__'].search('dir2-foo'))

    def test_run_dir(self):
        log_spy = LogSpy()
        universal_hooks.fs = ScriptStub()
        subproc_spy = SubprocSpy()
        universal_hooks.subprocess = subproc_spy
        _run_dir('/etc/dnf/universal-hooks/transaction', log_spy)

        self.assertListEqual([], log_spy.history)
        self.assertListEqual(
            ['/etc/dnf/universal-hooks/transaction/script1 ', '/etc/dnf/universal-hooks/transaction/script2 '],
            subproc_spy.history)

    def test_run_pkg_dirs(self):
        fs_stub = PkgDirsStub()
        temp_file_spy = TempFileSpy()
        fs_stub.temp_file = temp_file_spy
        universal_hooks.fs = fs_stub
        subproc_spy = SubprocSpy()
        universal_hooks.subprocess = subproc_spy
        log_spy = LogSpy()
        _run_pkg_dirs('/etc/dnf/universal-hooks', log_spy, 'transaction', TransactionStub())

        self.assertListEqual([], log_spy.history)
        self.assertListEqual(['/etc/dnf/universal-hooks/pkgs/unit-pkg1/transaction/unit-pkg1-script ',
                              '/etc/dnf/universal-hooks/multi_pkgs/transaction/unit-__WILDCARD__/unit-wildcard-script --pkg_list=/unit/tmp/unit-temp-file'],
                             subproc_spy.history)

        expected_file_content = '''unit-pkg1
unit-pkg2
'''
        self.assertEqual(expected_file_content, temp_file_spy.content.getvalue())

    def test_plugin(self):
        fs_stub = PkgDirsStub()
        temp_file_spy = TempFileSpy()
        fs_stub.temp_file = temp_file_spy
        universal_hooks.fs = fs_stub
        subproc_spy = SubprocSpy()
        universal_hooks.subprocess = subproc_spy

        p = UniversalHooksPlugin(DnfBaseStub(), None)
        for hook in HOOK_NAMES:
            method = getattr(p, hook)
            method()

        self.assertListEqual([
            '/etc/dnf/universal-hooks/pre_config/script ',
            '/etc/dnf/universal-hooks/config/script ',
            '/etc/dnf/universal-hooks/resolved/script ',
            '/etc/dnf/universal-hooks/sack/script ',
            '/etc/dnf/universal-hooks/pre_transaction/script ',
            '/etc/dnf/universal-hooks/pkgs/unit-pkg1/transaction/unit-pkg1-script ',
            '/etc/dnf/universal-hooks/multi_pkgs/transaction/unit-__WILDCARD__/unit-wildcard-script --pkg_list=/unit/tmp/unit-temp-file',
            '/etc/dnf/universal-hooks/transaction/script ',
        ], subproc_spy.history)


class WildcardStub(FileSystem):
    def glob(self, pathname):
        return [
            '/unit/wildcard_root/dir1',
            '/unit/wildcard_root/dir2__WILDCARD__',
        ]

    def isdir(self, pathname):
        return 'dir' in pathname

    def access(self, path, mode):
        pass

    def NamedTemporaryFile(self, mode, encoding):
        pass


class ScriptStub(FileSystem):

    def glob(self, pathname):
        return [
            '/etc/dnf/universal-hooks/transaction/script1',
            '/etc/dnf/universal-hooks/transaction/script2',
        ]

    def isdir(self, pathname):
        return '/etc/dnf/universal-hooks/transaction' == pathname

    def access(self, path, mode):
        return 'script' in path and os.X_OK & mode

    def NamedTemporaryFile(self, mode, encoding):
        pass


class LogSpy:

    def __init__(self) -> None:
        self.history = []

    def error(self, msg):
        self.history.append((self.error.__name__, msg))


class SubprocSpy(object):

    def __init__(self) -> None:
        self.history = []

    def run(self, args, shell=False):
        self.history.append(args)
        return GoodCompletionStub()


class GoodCompletionStub:
    @property
    def returncode(self):
        return 0


class TransactionStub(TransactionInfo):
    def getMembers(self):
        return [
            MemberStub('unit-pkg1'),
            MemberStub('unit-pkg2'),
        ]


class MemberStub:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class PkgDirsStub(FileSystem):

    def __init__(self) -> None:
        self.temp_file = None

    def glob(self, pathname):
        paths = {
            '/etc/dnf/universal-hooks/multi_pkgs/transaction/*': [
                '/etc/dnf/universal-hooks/multi_pkgs/transaction/unit-__WILDCARD__'
            ],
            '/etc/dnf/universal-hooks/multi_pkgs/transaction/unit-__WILDCARD__/*': [
                '/etc/dnf/universal-hooks/multi_pkgs/transaction/unit-__WILDCARD__/unit-wildcard-script'
            ],
            '/etc/dnf/universal-hooks/pkgs/unit-pkg1/transaction/*': [
                '/etc/dnf/universal-hooks/pkgs/unit-pkg1/transaction/unit-pkg1-script'
            ],
            '/etc/dnf/universal-hooks/pkgs/unit-pkg2/transaction/*': [],
            '/etc/dnf/universal-hooks/multi_pkgs/pre_transaction/*': [],
            '/etc/dnf/universal-hooks/pkgs/unit-pkg1/pre_transaction/*': [],
        }

        for hook in HOOK_NAMES:
            paths[f'/etc/dnf/universal-hooks/{hook}/*'] = [f'/etc/dnf/universal-hooks/{hook}/script']

        return paths[pathname]

    def isdir(self, pathname):
        return 'script' not in pathname

    def access(self, path, mode):
        return 'script' in path

    def NamedTemporaryFile(self, mode, encoding):
        return self.temp_file


class TempFileSpy:

    def __init__(self) -> None:
        self.content = io.StringIO()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def write(self, data):
        self.content.write(data)

    def flush(self):
        pass

    @property
    def name(self):
        return '/unit/tmp/unit-temp-file'


class DnfBaseStub:
    @property
    def transaction(self):
        return [MemberStub('unit-pkg1')]
