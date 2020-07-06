# Overview

This package provides a universal hook plugin for yum based systems (e.g. CentOS 7) and dnf based systems (e.g. CentOS 8).

This plugin allows us to run scripts at various entry points in the yum or dnf process.

*If you install scripts for this plugin to run you must install them in the correct locations on yum systems and the correct locations on dnf systems.* The details are documented in each system’s Plugin Documentation below.

* [Design Doc](DESIGN.md)
* [YUM Plugin Documentation](README.yum.md)
* [DNF Plugin Documentation](README.dnf.md)

Note: On dnf based systems it requires Python 3.6 and also `Provides: dnf-plugin-universal-hooks`.
