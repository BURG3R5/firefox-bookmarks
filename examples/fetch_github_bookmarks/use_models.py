from firefox_bookmarks.models import (
    FirefoxBookmark,
    FirefoxPlace,
    ProfileCriterion,
    connect_firefox_models,
)

connect_firefox_models(criterion=ProfileCriterion.LARGEST)

bookmarks = FirefoxBookmark \
    .select(
    FirefoxBookmark.title,
    FirefoxPlace.title,
    FirefoxPlace.url,
) \
    .join(FirefoxPlace) \
    .where((FirefoxBookmark.type == 1) & (FirefoxBookmark.place.url.startswith("https://github.com"))) \
    .execute()

for bookmark in bookmarks:
    print(f"Title: {bookmark.place.title or bookmark.title}\n"
          f"URL: {bookmark.place.url}\n")
