# Overview

This package provides a universal hook plugin for yum based systems (e.g. CentOS 7) and dnf based systems (e.g. CentOS 8).

This plugin allows us to run scripts at various entry points in the yum or dnf process.

**If you install scripts for this plugin to run you must install them in the correct locations on yum systems and the correct locations on dnf systems.** The details are documented in each system’s Plugin Documentation below.

* [Design Doc](DESIGN.md)
* [DNF Plugin Documentation](DNF.md)
* [YUM Plugin Documentation](YUM.md)

Note: On dnf based systems it requires Python 3.6 and also `Provides: dnf-plugin-universal-hooks`.

## Testing

Note:

* [install-zsh-test-hooks.sh](./install-test-zsh-hooks.sh) will create some dummy hook scripts for `zsh` RPM.
* on `dnf` systems you can use the `dnf` command instead of `yum` if you like

1. `yum install yum-plugin-universal-hooks`
2. cd into repo
3. `./install-test-zsh-hooks.sh`
4. Do a transaction involving zsh
   * e.g. if you already have zsh: `yum reinstall -y zsh`
   * e.g. if you do not already have zsh: `yum install -y zsh`
5. Note the output shows that they were executed properly. For example, on a `dnf` machine it will look like this:
```
Universal Hook Fired: “/etc/dnf/universal-hooks/pkgs/zsh/transaction/test-hook.sh” with args:
 … done (/etc/dnf/universal-hooks/pkgs/zsh/transaction/test-hook.sh)

Universal Hook Fired: “/etc/dnf/universal-hooks/multi_pkgs/transaction/zs__WILDCARD__/test-hook.sh” with args: --pkg_list=/tmp/tmp4wd9fnyl
pkg_list:
zsh
 … done (/etc/dnf/universal-hooks/multi_pkgs/transaction/zs__WILDCARD__/test-hook.sh)

Universal Hook Fired: “/etc/dnf/universal-hooks/transaction/test-hook.sh” with args:
 … done (/etc/dnf/universal-hooks/transaction/test-hook.sh)
```

