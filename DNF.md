# Overview

This plugin allows us to run scripts at various hook points in the dnf process (yum calls these “slots” [*]).

Assuming you have a yum repo that contains this plugin:

1.  `dnf install yum-plugin-universal-hooks` # install a plugin called 'universal-hooks'
    *   when you run dnf you should see something like:
        *   Loaded plugins: universal-hooks, fastestmirror, …
    * it is also known as `dnf-plugin-universal-hooks` as `yum-plugin-universal-hooks` “Provides” `dnf-plugin-universal-hooks`
2.  add scripts to the appropriate place in `/etc/dnf/universal-hooks/` (manually, via an RPM installation, etc)
    *   script output is not hindered
    *   if it exits non-zero it will have a warning to that effect
    *   if it is not executable it will have a warning to that effect
    *   for wildcard matches there is currently one argument passed to the script, --pkg_list=/path/to/randomlynamefile that has a list of packages being operated on, one per line of the file
        * non-wildcard matches will have no arguments
3.  Like any dnf plugin it can be disabled via its config or via the command line.
4.  `/etc/dnf/universal-hooks/` will remain if you `dnf remove yum-plugin-universal-hooks` so that any scripts will be available when re-installed.

# /etc/dnf/universal-hooks/ structure

This path can be changed by the plugin’s config file, but don’t  ;)

The main directory can have the following directories:

*   A directory for arbitrary scripts to go in named after each dnf hook point [*].
    *   e.g. `/etc/dnf/universal-hooks/transaction/whatever.sh`
*   A directory called “pkgs” that will organize package specific scripts.
    *   That directory contains directories named after the package in question, for example “perl”.
        *   Those directories can contain directories, for arbitrary scripts to go in, named after each dnf hook point [*].
            *   Currently only “pre_transaction” and “transaction” are package specific.
        *   e.g. `/etc/dnf/universal-hooks/pkgs/perl/transaction/whatever.sh`

*   A directory called “multi_pkgs” that will contains scripts for multiple packages.
    *   Contains a directory named after each snf hook point [*].
        *   Currently only “pre_transaction” and “transaction” are package specific.
        *   Those directories can contain “wildcard” directories, for arbitrary scripts to go in.
            *   a “wildcard” directory is a directory whose name contains `__WILDCARD__` to stand for .* in Regexp parlance
            *   If you want to match `^ea-.*$` you’d name this directory `ea-__WILDCARD__`
            *   If you want to match `^.*-devel$` you’d name this directory `__WILDCARD__-devel`
            *   If you want to match `perl` anywhere in the string: `__WILDCARD__perl__WILDCARD__`
            *   If you want to match every package ever involved in a transaction, name it `__WILDCARD__`
                *   This would be sort of weird though since you can get the same thing from `/etc/dnf/universal-hooks/transaction`
            *   e.g. `/etc/dnf/universal-hooks/multi_pkgs/transaction/ea-__WILDCARD__/whatever.sh`
                *   That script would run once at the end of a transaction is one or more packages that started with ea- were involved in the transaction.

# Script Execution Order

The scripts are run in the order that your system `glob()` returns. While technically arbitrary it is typically lexicographically. That being the case we will prefix scripts with 3 digits and a hyphen, underscore, or period (e.g. 042-foo). If a script is not installed/updated/removed via an RPM we should do the same number prefix but extend that with a cp- prefix (e.g. 042-cp-foo). Leaving a numeric gap between names will allow 3rdparties to do things in the spot they want.


* * *


*Footnote: The hook point names and their descriptions are at documented starting here: https://dnf.readthedocs.io/en/latest/api_plugins.html#dnf.Plugin.pre_config

At the time this was written that info was:

```
pre_config()
    This hook is called before configuring the repos.

config()
    This hook is called immediately after the CLI/extension is finished configuring DNF. The plugin can use this to tweak the global configuration or the repository configuration.

resolved()
    This hook is called immediately after the CLI has finished resolving a transaction. The plugin can use this to inspect the resolved but not yet executed Base.transaction.

sack()
    This hook is called immediately after Base.sack is initialized with data from all the enabled repos.

pre_transaction()
    This hook is called just before transaction execution. This means after a successful transaction test. RPMDB is locked during that time.

transaction()
    This hook is called immediately after a successful transaction. Plugins that were removed or obsoleted by the transaction will not run the transaction hook.
```

**Note:** From YUM to DNF plugins [there is not always a one-to-one mapping of the YUM slot to the DNF hook point](https://dnf.readthedocs.io/en/latest/api_vs_yum.html#changes-in-the-dnf-hook-api-compared-to-yum).
