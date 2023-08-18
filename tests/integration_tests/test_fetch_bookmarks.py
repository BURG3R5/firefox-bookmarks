import pytest

from firefox_bookmarks import *


def test_fetch_bookmarks(golden_file):
    fb = FirefoxBookmarks()
    fb.connect()
    bookmarks = fb.bookmarks(where=Bookmark.url.contains("mozilla.org"))
    bookmark_reprs = set(repr(bkmk) for bkmk in bookmarks)
    fb.disconnect()

    assert bookmark_reprs == set(golden_file.splitlines())


# region FIXTURES


@pytest.fixture
def golden_file():
    with open(
            "tests/integration_tests/data/"
            "test_fetch_bookmarks.txt",
            "r",
    ) as golden_file:
        yield golden_file.read()


# endregion
