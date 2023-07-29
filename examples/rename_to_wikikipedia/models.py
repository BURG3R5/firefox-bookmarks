from peewee import fn

from firefox_bookmarks.models import *

connect_firefox_models(criterion=ProfileCriterion.LARGEST)

count_updated = FirefoxBookmark \
    .update(title=fn.REPLACE(FirefoxBookmark.title, "Wikipedia", "Wikikipedia")) \
    .where(FirefoxBookmark.title.contains("Wikipedia")) \
    .execute()

bookmarks = FirefoxBookmark \
    .select(FirefoxBookmark.id, FirefoxBookmark.title) \
    .where(FirefoxBookmark.title.contains("Wikikipedia")) \
    .execute()

for bookmark in bookmarks:
    print(f"Bookmark[{bookmark.id}] = {bookmark.title}")

print(f"\nNumber of bookmarks updated: {count_updated}\n"
      "!INFO: To undo these changes, run the revert.py file in this directory")
