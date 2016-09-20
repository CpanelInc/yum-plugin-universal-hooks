# Overview

This plugin allows us to run scripts at various entry points in the yum process (yum calls these “slots” [*]).

Assuming you have a yum repo that contains this plugin:

1.  `yum install yum-plugin-universal-hooks` # install a plugin called 'universal-hooks'
    *   when you run yum you should see something like: 
        *   Loaded plugins: universal-hooks, fastestmirror, …

2.  add scripts to the appropriate place in `/etc/yum/universal-hooks/` (manually, via an RPM installation, etc)
    *   script output is not hindered
    *   if it exits non-zero it will have a warning to that effect
    *   if it is not executable it will have a warning to that effect
    *   there is currently one argument passed to the script, --pkg_list=/path/to/randomlynamefile that has a list of packages being operated on, one per line of the file
    *   there are a number of TODOs/YAGNIs noted in the source code
3.  Like any yum plugin it can be disabled via its config or via the command line.
4.  `/etc/yum/universal-hooks/` will remain if you `yum remove yum-plugin-universal-hooks` so that any scripts will be available when re-installed.

# /etc/yum/universal-hooks/ structure

This path can be changed by the plugin’s config file, but don’t  ;)

The main directory can have the following directories:

*   A directory for arbitrary scripts to go in named after each yum “slot” [*].
    *   e.g. `/etc/yum/universal-hooks/posttrans/whatever.sh`
*   A directory called “pkgs” that will organize package specific scripts.
    *   That directory contains directories named after the package in question, for example “perl”.
        *   Those directories can contain directories, for arbitrary scripts to go in, named after each yum “slot” [*].
            *   Currently only “pretrans” and “posttrans” are package specific.
        *   e.g. `/etc/yum/universal-hooks/pkgs/perl/posttrans/whatever.sh`
            
*   A directory called “multi_pkgs” that will contains scripts for multiple packages.
    *   Contains a directory named after each yum “slot” [*].
        *   Currently only “pretrans” and “posttrans” are package specific.
        *   Those directories can contain “wildcard” directories, for arbitrary scripts to go in.
            *   a “wildcard” directory is a directory whose name contains `__WILDCARD__` to stand for .* in Regexp parlance
            *   If you want to match `^ea-.*$` you’d name this directory `ea-__WILDCARD__`
            *   If you want to match `^.*-devel$` you’d name this directory `__WILDCARD__-devel`
            *   If you want to match `perl` anywhere in the string: `__WILDCARD__perl__WILDCARD__`
            *   If you want to match every package ever involved in a transaction, name it `__WILDCARD__`
                *   This would be sort of weird though since you can get the same thing from `/etc/yum/universal-hooks/posttrans`
            *   e.g. `/etc/yum/universal-hooks/multi_pkgs/posttrans/ea-__WILDCARD__/whatever.sh`
                *   That script would run once at the end of a transaction is one or more packages that started with ea- were involved in the transaction.

# Script Execution Order

The scripts are run in the order that your system `glob()` returns. While technically arbitrary it is typically lexicographically. That being the case we will prefix scripts with 3 digits and a hyphen, underscore, or period (e.g. 042-foo). If a script is not installed/updated/removed via an RPM we should do the same number prefix but extend that with a cp- prefix (e.g. 042-cp-foo). Leaving a numeric gap between names will allow 3rdparties to do things in the spot they want.


* * *


*Footnote: The slot names and their descriptions are at http://yum.baseurl.org/wiki/WritingYumPlugins#SlotsandHooks under “The following slots exist”.

At the time this was written that info was:

```
config
    Called first as plugins are initialised. Plugins that need to extend Yum's
    configuration files or command line options should do so during this slot.

postconfig
    Called immediately after Yum's config object is initialised. Useful for 
    extending variables or modifying items in the config, for example the 
    $ variables that are used in repo configuration. 
    Note: Only available in yum 3.1.7 or later

init
    Called early in Yum's initialisation. May be used for general plugin
    related initialisation.

predownload
    Called just before Yum starts downloads of packages. Plugins may access
    information about the packages to be downloaded here.

postdownload
    Called just after Yum finishes package downloads. Plugins may access
    error information about the packages just downloaded.

prereposetup
    Called just before Yum initialises its repository information.

postreposetup
    Called just after Yum initialises its repository information.

exclude
    Called after package inclusion and exclusions are processed. Plugins
    may modify package exclusions here.

preresolve
    Called before Yum begins package resolution.

postresolve
    Called just after Yum finishes package resolution.

pretrans
    Called before Yum begins the RPM update transation.

posttrans
    Called just after Yum has finished the RPM update transation.

close
    Called as Yum is performing a normal exit. Plugins may wish to
    perform cleanup functions here.

clean
    Called during Yum's cleanup.  This slot will be executed when Yum 
    is run with the parameters 'clean all' or 'clean plugins'.
```
