import pytest
from peewee import fn

from firefox_bookmarks import *


def test_update_bookmarks(golden_file):
    fb = FirefoxBookmarks()
    fb.connect()
    count_updated = fb.update(
        where=Bookmark.url.contains("mozilla.org"),
        data={
            Bookmark.title: "<updated> " + Bookmark.title,
            Bookmark.url: fn.TRIM(Bookmark.url, "/"),
        },
    )
    fb.commit()
    fb.disconnect()

    fb.connect()
    bookmarks = fb.bookmarks(where=Bookmark.url.contains("mozilla.org"))
    bookmark_reprs = set(repr(bkmk) for bkmk in bookmarks)
    fb.restore_backup()
    fb.disconnect()

    assert count_updated == 5
    assert bookmark_reprs == set(golden_file.splitlines())


# region FIXTURES


@pytest.fixture
def golden_file():
    with open(
            "tests/integration_tests/data/"
            "update_bookmarks.txt",
            "r",
    ) as golden_file:
        yield golden_file.read()


# endregion
