# firefox-bookmarks

Manage your Firefox bookmarks with ease

## installation

```shell
pip install firefox-bookmarks
```

## usage

Import and initialize models:

```python
from firefox_bookmarks.models import *

# You can pass a `ProfileCriterion` to choose from multiple profiles
connect_firefox_models(criterion=ProfileCriterion.LARGEST)
```

Query as you would in peewee (or Django or SQLAlchemy)

```python
github_bookmarks = FirefoxPlace \
    .select() \
    .join(FirefoxBookmark) \
    .where(FirefoxPlace.url.contains("https://github.com")) \
    .execute()

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
