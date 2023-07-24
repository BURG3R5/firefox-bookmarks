from peewee import fn

from firefox_bookmarks.models import *

connect_firefox_models(criterion=ProfileCriterion.LARGEST)

count_updated = FirefoxBookmark \
    .update(title=fn.REPLACE(FirefoxBookmark.title, "Wikikipedia", "Wikipedia")) \
    .where(FirefoxBookmark.title.contains("Wikikipedia")) \
    .execute()

print(f"REVERTED!\nNumber of bookmarks updated: {count_updated}")
