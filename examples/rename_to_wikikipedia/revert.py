from peewee import fn

from firefox_bookmarks import *

fb = FirefoxBookmarks()
fb.connect(criterion=ProfileCriterion.LARGEST)

count_updated = fb.update(
    where=Bookmark.title.contains("Wikikipedia"),
    data={
        Bookmark.title: fn.REPLACE(Bookmark.title, "Wikikipedia", "Wikipedia"),
    },
)

fb.commit()

print(f"REVERTED!\nNumber of bookmarks updated: {count_updated}")

fb.disconnect()
