from firefox_bookmarks import *

fb = FirefoxBookmarks()
fb.connect(criterion=ProfileCriterion.LARGEST)

medium_query = Bookmark.url.contains("medium.com")

for bookmark in fb.bookmarks(where=medium_query):
    print(bookmark.guid, "\t", bookmark.path)

new_folder = fb.create(
    type=FirefoxEntity.FOLDER,
    title="ME-dium",
    parent=None,
)

count_updated = fb.move(
    bookmarks=Bookmark.url.contains("medium.com"),
    destination=(Bookmark.title == "ME-dium"),
)

# fb.commit()

for bookmark in fb.bookmarks(where=medium_query):
    print(bookmark.path)

print(f"\nNumber of bookmarks updated: {count_updated}\n"
      "!INFO: To undo these changes, run the revert.py file in this directory")

fb.disconnect()
