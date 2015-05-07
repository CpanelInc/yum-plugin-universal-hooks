#!/usr/bin/python

# Copyright (c) 2015, cPanel, Inc.
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

import os, glob, re
from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE

requires_api_version = '2.3'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)

def_base_dir = '/etc/yum/universal-hooks';

# conduit object info http://sourcecodebrowser.com/yum/2.4.0/namespaceyum_1_1plugins.html

# TODO: help/docs the way yum plugins do them

def _run_dir(dir, conduit, args = ''):

    dir.rstrip('*');
    dir.rstrip('/');

    if not os.path.isdir(dir):
        return None

    # TODO/YAGNI?: if yum called w/ --quiet: hide output from system() && do not call conduit.info()
    # TODO/YAGNI?: if yum called w/ --verbose also output pre/post "running $cmd" region markers
    # TODO: under dry run do nto run scripts just note that they would have been

    for script in glob.glob(dir + "/*"):
        if (os.access(script, os.X_OK)):

            # TODO/YAGNI?: if exit is ??? raise PluginYumExit("!!!! " + script + " said it was time to stop");
            if (len(args)):
                exit = os.system(script + ' ' + args)
                if(exit != 0):
                    conduit.info(2, "!!!! \"" + script + ' ' + args + "\" did not exit cleanly: " + str(exit))
            else:
                exit = os.system(script)
                if(exit != 0):
                    conduit.info(2, "!!!! " + script + " did not exit cleanly: " + str(exit))
        else:
            conduit.info(2, "!!!! " + script + ' is not executable')

def _run_pkg_dirs(base_dir, conduit, slot):
    ts = conduit.getTsInfo()

    # setup __WILDCARD__ data for the slot
    wc_slot_dir = base_dir + "/multi_pkgs/" + slot
    wildcard_list = {};
    for path in glob.glob(wc_slot_dir + "/*"):
        if os.path.isdir(path):
            path = os.path.basename(os.path.normpath(path))
            regx = path;
            regx = regx.replace("__WILDCARD__",".*")
            regx = re.compile("^" + regx + "$")
            wildcard_list[path] = regx
    wildcard_to_run = {};

    for member in ts.getMembers():

        # TODO/YAGNI?: set state to a normalized 'not_installed' 'updatable' 'installed' and pass as third arg to _run_dir()
        #    This is helpful so scripts don't have to decifer the meaning of obtuse values.
        #    It is also very tricky as the various state values (member.current_state, member.output_state, member.po.state, member.ts_state) are crazy, e.g.:
        #       Doing a reinstall member.current_state was 70 which means not installed per http://yum.baseurl.org/api/yum-3.2.26/yum.constants-module.html (which can be brought in via 'from yum.constants import *').

        pkg = member.name
        _run_dir(base_dir + "/pkgs/" + pkg + "/" + slot, conduit);

        # note any __WILDCARD__ that need to run for pkg
        for wc in wildcard_list:
            if wildcard_list[wc].search(pkg):
                wildcard_to_run[wc] = 1

    # call _run_dir on any __WILDCARD__ paths that match the pkg
    for wc_dir in wildcard_to_run:
        _run_dir(wc_slot_dir + "/" + wc_dir, conduit)

def config_hook(conduit):
    """
    Called first as plugins are initialised. Plugins that need to extend Yum's
    configuration files or command line options should do so during this slot.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/config", conduit)


def postconfig_hook(conduit):
    """
    Called immediately after Yum's config object is initialised. Useful for
    extending variables or modifying items in the config, for example the
    $ variables that are used in repo configuration.
    Note: Only available in yum 3.1.7 or later
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/postconfig", conduit)

def init_hook(conduit):
    """
    Called early in Yum's initialisation. May be used for general plugin
    related initialisation.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/init", conduit)

def predownload_hook(conduit):
    """
    Called just before Yum starts downloads of packages. Plugins may access
    information about the packages to be downloaded here.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/predownload", conduit)

def postdownload_hook(conduit):
    """
    Called just after Yum finishes package downloads. Plugins may access
    error information about the packages just downloaded.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/postdownload", conduit)

def prereposetup_hook(conduit):
    """
    Called just before Yum initialises its repository information.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/prereposetup", conduit)

def postreposetup_hook(conduit):
    """
    Called just after Yum initialises its repository information.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/postreposetup", conduit);

def exclude_hook(conduit):
    """
    Called after package inclusion and exclusions are processed. Plugins
    may modify package exclusions here.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/exclude", conduit);

def preresolve_hook(conduit):
    """
    Called before Yum begins package resolution.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/preresolve", conduit);

def postresolve_hook(conduit):
    """
    Called just after Yum finishes package resolution.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/postresolve", conduit);

def pretrans_hook(conduit):
    """
    Called before Yum begins the RPM update transation.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)

    _run_pkg_dirs(base_dir, conduit, 'pretrans');
    _run_dir(base_dir + "/pretrans", conduit);

def posttrans_hook(conduit):
    """
    Called just after Yum has finished the RPM update transation.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)

    _run_pkg_dirs(base_dir, conduit, 'posttrans')
    _run_dir(base_dir + "/posttrans", conduit)

def close_hook(conduit):
    """
    Called as Yum is performing a normal exit. Plugins may wish to
    perform cleanup functions here.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/close", conduit);

def clean_hook(conduit):
    """
    Called during Yum's cleanup.  This slot will be executed when Yum
    is run with the parameters 'clean all' or 'clean plugins'.
    """

    base_dir = conduit.confString('main','base_dir',def_base_dir)
    _run_dir(base_dir + "/clean", conduit);

