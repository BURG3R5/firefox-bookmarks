from peewee import fn

from firefox_bookmarks import *

fb = FirefoxBookmarks()
fb.connect(criterion=ProfileCriterion.LARGEST)

count_updated = fb.str_update(
    field=Bookmark.title,
    where=Bookmark.title.contains("Wikikipedia"),
    updated=fn.REPLACE(Bookmark.title, "Wikikipedia", "Wikipedia"),
)

fb.commit()

print(f"REVERTED!\nNumber of bookmarks updated: {count_updated}")

fb.disconnect()
