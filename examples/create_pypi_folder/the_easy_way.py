from firefox_bookmarks import *

fb = FirefoxBookmarks()
fb.connect(criterion=ProfileCriterion.LARGEST)

folder = fb.create(
    title="PyPI",
    entity_type=FirefoxEntity.FOLDER,
)

bookmark = fb.create(
    title="firefox-bookmarks · PyPI",
    entity_type=FirefoxEntity.FOLDER,
    parent=folder,
    url="https://pypi.org/project/firefox-bookmarks/",
)

fb.commit()

bookmarks = fb.select(where=Bookmark.title.contains("PyPI"))

for bookmark in bookmarks:
    print(f"Bookmark[{bookmark.id}] = {bookmark.path}")

print("!INFO: To undo these changes, run the revert.py file in this directory")

fb.disconnect()
