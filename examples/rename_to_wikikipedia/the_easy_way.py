from peewee import fn

from firefox_bookmarks import *

fb = FirefoxBookmarks()
fb.connect(criterion=ProfileCriterion.LARGEST)

count_updated = fb.update(
    query=Bookmark.title.contains("Wikipedia"),
    data={
        Bookmark.title: fn.REPLACE(Bookmark.title, "Wikipedia", "Wikikipedia"),
    },
)

fb.commit()

bookmarks = fb.bookmarks(
    fields=(Bookmark.id, Bookmark.title),
    query=Bookmark.title.contains("Wikikipedia"),
)

for bookmark in bookmarks:
    print(f"Bookmark[{bookmark.id}] = {bookmark.title}")

print(f"\nNumber of bookmarks updated: {count_updated}\n"
      "!INFO: To undo these changes, run the revert.py file in this directory")

fb.disconnect()
