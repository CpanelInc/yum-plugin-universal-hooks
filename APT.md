# Overview

This plugin allows us to run scripts at various hook points in the apt process (yum calls these “slots” [*]).

Assuming you have an apt repo that contains this plugin:

1.  `apt install apt-plugin-universal-hooks` # install a plugin called 'universal-hooks'
    * it is also known as `yum-plugin-universal-hooks` for convenience
2.  add scripts to the appropriate place in `/etc/apt/universal-hooks/` (manually, via a `deb` installation, etc)
    *   script output is not hindered
    *   if it exits non-zero it will have a warning to that effect
    *   if it is not executable it will have a warning to that effect
    *   for wildcard matches there is currently one argument passed to the script, --pkg_list=/path/to/randomlynamefile that has a list of packages being operated on, one per line of the file
        * non-wildcard matches will have no arguments
3.  There is no mechanism in apt to disable this besides editing the configuration `/etc/apt/apt.conf.d/apt-universal-hooks.conf`.
4.  `/etc/apt/universal-hooks/` will remain if you `apt remove apt-plugin-universal-hooks` so that any scripts will be available when re-installed.

# /etc/apt/universal-hooks/ structure

The main directory can have the following directories:

*   A directory for arbitrary scripts to go in named after each apt hook point [*].
    *   e.g. `/etc/apt/universal-hooks/Post-Invoke/whatever.sh`
*   A directory called “pkgs” that will organize package specific scripts.
    *   That directory contains directories named after the package in question, for example “perl”.
        *   Those directories can contain directories, for arbitrary scripts to go in, named after each apt hook point [*].
            *   Currently only “Pre-Install-Pkgs” and “Post-Invoke” are package specific.
        *   e.g. `/etc/apt/universal-hooks/pkgs/perl/Post-Invoke/whatever.sh`

*   A directory called “multi_pkgs” that will contains scripts for multiple packages.
    *   Contains a directory named after each apt hook point [*].
        *   Currently only “Pre-Install-Pkgs” and “Post-Invoke” are package specific.
        *   Those directories can contain “wildcard” directories, for arbitrary scripts to go in.
            *   a “wildcard” directory is a directory whose name contains `__WILDCARD__` to stand for .* in Regexp parlance
            *   If you want to match `^ea-.*$` you’d name this directory `ea-__WILDCARD__`
            *   If you want to match `^.*-devel$` you’d name this directory `__WILDCARD__-devel`
            *   If you want to match `perl` anywhere in the string: `__WILDCARD__perl__WILDCARD__`
            *   If you want to match every package ever involved in a transaction, name it `__WILDCARD__`
                *   This would be sort of weird though since you can get the same thing from `/etc/apt/universal-hooks/Post-Invoke`
            *   e.g. `/etc/apt/universal-hooks/multi_pkgs/Post-Invoke/ea-__WILDCARD__/whatever.sh`
                *   That script would run once at the end of a transaction if one or more packages that started with ea- were involved in the transaction.

# Script Execution Order

The scripts are run in the order that your system `glob()` returns. While technically arbitrary it is typically lexicographically. That being the case we will prefix scripts with 3 digits and a hyphen, underscore, or period (e.g. 042-foo). If a script is not installed/updated/removed via a `deb` we should do the same number prefix but extend that with a cp- prefix (e.g. 042-cp-foo). Leaving a numeric gap between names will allow 3rdparties to do things in the spot they want.


* * *


*Footnote: The hook point names and their descriptions are documented in `man apt.conf` under “HOW APT CALLS DPKG”.

At the time this was written that info was:

```
       Pre-Invoke, Post-Invoke
           … run before/after invoking dpkg(1).

       Pre-Install-Pkgs
           … run before invoking dpkg(1).
```

**Note**: There are similar `APT::Update` hook points too but those are not for install/upgrade/remove operations whcih is what universal-hooks is targeting.
