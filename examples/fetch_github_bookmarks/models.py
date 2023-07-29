from firefox_bookmarks.models import *

connect_firefox_models(criterion=ProfileCriterion.LARGEST)

bookmarks = FirefoxPlace \
    .select() \
    .join(FirefoxBookmark) \
    .where(FirefoxPlace.url.contains("https://github.com")) \
    .execute()

for bookmark in bookmarks:
    print(f"Title: {bookmark.title}\nURL: {bookmark.url}\n")
