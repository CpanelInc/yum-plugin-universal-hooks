#!/usr/bin/python3.6

# Copyright (c) 2020, cPanel, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import abc
import glob
import logging
import os
from os import path
import re
import subprocess
import sys
import tempfile

from dnf import Plugin

# this logger is configured by the dnf CLI, but error() is not shown by default (but is with -v)
# LOG = logging.getLogger("dnf")

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.ERROR)
LOG.addHandler(logging.StreamHandler(sys.stderr))


class UniversalHooksPlugin(Plugin):
    name = 'universal-hooks'

    def __init__(self, base, cli):
        super().__init__(base, cli)
        self.hook_root = '/etc/dnf/universal-hooks'

    def pre_config(self):
        _run_dir(path.join(self.hook_root, self.pre_config.__name__), LOG)

    def config(self):
        _run_dir(path.join(self.hook_root, self.config.__name__), LOG)

    def resolved(self):
        _run_dir(path.join(self.hook_root, self.resolved.__name__), LOG)

    def sack(self):
        _run_dir(path.join(self.hook_root, self.sack.__name__), LOG)

    def pre_transaction(self):
        name = self.pre_transaction.__name__
        _run_pkg_dirs(self.hook_root, LOG, name, DnfTransactionInfo(self.base.transaction))
        _run_dir(path.join(self.hook_root, name), LOG)

    def transaction(self):
        name = self.transaction.__name__
        _run_pkg_dirs(self.hook_root, LOG, name, DnfTransactionInfo(self.base.transaction))
        _run_dir(path.join(self.hook_root, name), LOG)


class FileSystem(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def glob(self, pathname):
        pass

    @abc.abstractmethod
    def isdir(self, pathname):
        pass

    @abc.abstractmethod
    def access(self, path, mode):
        pass

    @abc.abstractmethod
    def NamedTemporaryFile(self, mode, encoding):
        pass


class RealFileSystem(FileSystem):
    def glob(self, pathname):
        return glob.glob(pathname)

    def isdir(self, pathname):
        return path.isdir(pathname)

    def access(self, path, mode):
        return os.access(path, mode)

    def NamedTemporaryFile(self, mode, encoding):
        return tempfile.NamedTemporaryFile(mode=mode, encoding=encoding)


fs = RealFileSystem()


def _run_dir(hook_dir, log, args=''):
    if not fs.isdir(hook_dir):
        return None

    for script in sorted(fs.glob(hook_dir + "/*")):
        if fs.access(script, os.X_OK):
            cmdline = f'{script} {args}'
            completed = subprocess.run(cmdline, shell=True)  # todo change args to a list, shell=False
            if 0 != completed.returncode:
                log.error("!!! %s did not exit cleanly: %d", cmdline, completed.returncode)
        else:
            log.error("!!! %s is not executable", script)


class TransactionInfo(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def getMembers(self):
        pass


class DnfTransactionInfo(TransactionInfo):
    def __init__(self, transaction) -> None:
        self.transaction = transaction

    def getMembers(self):
        return self.transaction


def _run_pkg_dirs(base_dir, log, slot, tinfo):
    """

    :param str base_dir:
    :param logging.Logger log:
    :param str slot:
    :param TransactionInfo tinfo:
    """

    wildcard_path = path.join(base_dir, 'multi_pkgs', slot)
    dir_matchers = _make_dir_matchers(wildcard_path)
    wildcard_to_run = {}

    with fs.NamedTemporaryFile(mode='w', encoding='utf-8') as temp_pkg_file:
        members_seen = {}
        members = tinfo.getMembers()
        for member in sorted(set(members), key=lambda m: m.name):
            pkg = member.name
            if pkg in members_seen:
                continue

            members_seen[pkg] = 1

            temp_pkg_file.write(pkg + "\n")

            _run_dir(path.join(base_dir, 'pkgs', pkg, slot), log)

            for wildcard_dir, matcher in dir_matchers.items():
                if matcher.search(pkg):
                    wildcard_to_run[wildcard_dir] = 1

        # the file may be used by a subprocess, so make sure it is flushed to kernel
        temp_pkg_file.flush()

        for wildcard_dir in wildcard_to_run:
            _run_dir(path.join(wildcard_path, wildcard_dir), log, "--pkg_list=" + temp_pkg_file.name)


def _make_dir_matchers(wc_slot_dir):
    dir_matchers = {}
    for pth in fs.glob(wc_slot_dir + "/*"):
        if fs.isdir(pth):
            pth = path.basename(path.normpath(pth))
            dir_matchers[pth] = _regex_from_dir(pth)
    return dir_matchers


def _regex_from_dir(path):
    expr = path.replace("__WILDCARD__", ".*")
    return re.compile("^" + expr + "$")
