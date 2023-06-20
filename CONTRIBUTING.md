# Contributing to PhysLight

Thank you for your interest in contributing to the PhysLight
project. This document will cover our contribution process and
procedures.

* [Getting Information](#Getting-Information)
* [Legal Requirements](#Legal-Requirements)
* [Development Workflow](#Development-Workflow)
* [Coding Style](#Coding-Style)


## Getting Information

There primary way to connect with the PhysLight project:

* [GitHub Issues](https://github.com/wetadigital/physlight/issues): GitHub
  Issues are used both to track bugs and to discuss feature requests.

### How to Ask for Help

If you have trouble installing, building, or using the code
components, we do not yet have a mailing list set up, so do feel free
to post an issue.

### How to Report a Bug

PhysLight use GitHub's issue tracking system for bugs and enhancements:
https://github.com/wetadigital/physlight/issues

If you are submitting a bug report, please be sure to check on the
latest main branch of PhysLight, on what platform (OS/version), which
compiler you used, and any special build flags or environment
employed. In the report, please include:

* what you expected
* what happened
* what you tried

with enough detail that others can reproduce the problem.

### How to Request a Change

Open a GitHub issue: https://github.com/wetadigital/physlight/issues.

Describe the situation and the objective in as much detail as
possible. Feature requests will almost certainly spawn a discussion
among the project community.

### How to Contribute a Bug Fix or Change

To contribute code to the project, you will need:

* Knowledge of git.

* A fork of the GitHub repo.

* An understanding of the project's development workflow.

## Legal Requirements

PhysLight is a project of WētāFX and Wētā Digital and follows the
open source software best practice policies of the Linux Foundation.


### License

PhysLight is licensed under the [Apache 2.0](LICENSE)
license. Contributions to the library should abide by that standard
license.

### Commit Sign-Off

Every commit must be signed off.  That is, every commit log message
must include a “`Signed-off-by`” line (generated, for example, with
“`git commit --signoff`” or “`git commit -s`” for short). This
indicates that the committer wrote the code and has the right to
release it under the [Apache 2.0](LICENSE) license. See the followin
documentation included in the Academy Software Foundation project
processes
https://github.com/AcademySoftwareFoundation/tac/blob/main/process/contributing.md#contribution-sign-off
for more information on this requirement.

## Development Workflow

### Basics

The USD schema portions of this project use cmake, and uses the
*USDPluginExamples* project
https://github.com/wetadigital/USDPluginExamples as a basis for
defining the USD schema portion of the build. If you are unfamiliar
with cmake, that project provides a framework for working with USD
plugins, and provides examples for the various flavors of extensions
to USD which are possible.

In general, a linux build should be as easy as

    cmake -B dbg_build -DCMAKE_BUILD_TYPE=Debug -S usd
    make -C dbg_build

Although one may need to set USD_ROOT, TBB_ROOT, BOOST_ROOT,
USE_PYTHON_3 depending on your environment. Of course, you may
customize the build folder and use an appropriate build generator for
your platform.

Optionally, you can enable testing with `-DBUILD_TESTING=ON` when
running cmake

### Documentation

Currently, the tex code is a work in progress extracting it from an
internal build system. Once that is cleaned up, more will be written
here about contributing to the documentation effort.

### Repository Structure and Commit Policy

The PhysLight repository uses a simple branching and merging strategy.

All development work is done directly on the ``main`` branch. The ``main``
branch represents the current state of the project. At some point,
there may be official releases, at which point, more structure and
policy will be put into place.

Any contribution should be submitted as a Github pull request. See
[Creating a pull
request](https://help.github.com/articles/creating-a-pull-request/) if
you are unfamiliar with how this process works.

## Coding Style

### Formatting

When modifying existing code, follow the surrounding formatting
conventions so that new or modified code blends in with the current
code.

### Copyright Notices

All new source files should begin with a copyright and license stating:

    //
    // SPDX-License-Identifier: Apache-2.0
    // Copyright (c) Contributors to the PhysLight Project. 
    //
    
The particular comment delimiter is language-specific, but all source
files and support / build files (python, c++, tex, shell, etc) should
contain this style of comment.

### Third-party libraries

Prefer C++11 `std` over boost where possible.  Use boost classes you
already see in the code base, but check with the project leadership
before adding new boost usage.
