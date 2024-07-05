![README banner for firefox-bookmarks](https://i.imgur.com/oZ2vyCx.png)

![CI Status](https://img.shields.io/github/actions/workflow/status/BURG3R5/firefox-bookmarks/integration_tests.yml?branch=main&style=flat-square) ![PyPI](https://img.shields.io/badge/pypi-1.2.0-blue?style=flat-square) ![License - AGPL v3 or later](https://img.shields.io/pypi/l/firefox-bookmarks?style=flat-square) ![Code style: YAPF](https://img.shields.io/badge/code%20style-yapf-blue?style=flat-square) ![Code style: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square)

# firefox-bookmarks

Manage your Firefox bookmarks with ease

## installation

```shell
pip install firefox-bookmarks
```

## usage

Import and initialize:

```python
from firefox_bookmarks import *

fb = FirefoxBookmarks()

# You can pass a `ProfileCriterion` to choose from multiple profiles
fb.connect(criterion=ProfileCriterion.LARGEST)
```

Query as you would in peewee (or Django or SQLAlchemy)

```python
github_bookmarks = fb.bookmarks(
    where=Bookmark.url.contains("https://github.com"),
)

for bookmark in github_bookmarks:
    print(f"Title: {bookmark.title}\nURL: {bookmark.url}\n")
```

## examples

See [the examples directory](https://github.com/BURG3R5/firefox-bookmarks/tree/main/examples)

## contributing

Want to fix a bug, add a feature, or improve documentation? Awesome! Read up on our [guidelines for contributing](https://github.com/BURG3R5/firefox-bookmarks/blob/main/.github/CONTRIBUTING.md) and then visit our [/contribute page](https://github.com/BURG3R5/firefox-bookmarks/contribute) to find good first issues! Pull requests are always welcome!

## license

Copyright (C) 2023 Aditya Rajput & other contributors

This software is licensed under the **Affero GPL v3**. You should have received [a copy](https://github.com/BURG3R5/firefox-bookmarks/blob/main/LICENSE) of the Affero GPL v3 along with this program. If not, you can visit the original [here](https://www.gnu.org/licenses/agpl-3.0.html#license-text).
