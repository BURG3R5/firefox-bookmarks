from firefox_bookmarks import *

fb = FirefoxBookmarks()
fb.connect(criterion=ProfileCriterion.LARGEST)

bookmarks = fb.bookmarks(where=Bookmark.url.contains("https://github.com"))

for bookmark in bookmarks:
    print(f"Title: {bookmark.title}\nURL: {bookmark.url}\n")

fb.disconnect()
