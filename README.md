# polycephaly

Programs for maintaining user forks within a GitHub Organisation

## Overview

While git and GitHub(R) are great tools, the complexity of having local copies of
personal forks to maintain, along with master branches that need to be
synchronized across them, can cause non-technical users to find the maintenance
burdonsome.

The programs in this repo aim to make the upkeep of an organization's many repos
and forks easy for their git Administrator.

## Configuration File Format

```ini
[Repo 1 Title]
url = <ssh url of upstream repository for Repo 1>

[Repo 2 Title]
url = <ssh url of upstream repository for Repo 2>
```

**NOTE 1:** The title for each repo will be displayed in the GUI Title

**NOTE 2:** The url is the *common* upstream for all the clones in the
directory

## Current Functionality

1. Given a directory of cloned forks for a repository, allow easy
   synchronization of all master branches. This allows non-technical users to
   simply 'Sync' in their GH Client to bring their master branch up to date.

## Prerequisites

1. Programs use Python 3 and Tkinter for GUI generation.
1. git needs to be installed.

## Future Plans

1. Automatic cloning of all forks of a given repository instead of relying on
   manual creation.
