from firefox_bookmarks import connect_to_places_db

database = connect_to_places_db()

query = ("UPDATE moz_bookmarks SET title = "
         "REPLACE(moz_bookmarks.title, 'Wikipedia', 'Wikikipedia') "
         "WHERE (moz_bookmarks.title LIKE '%Wikipedia%');")

database.execute_sql(query)

query = ("SELECT moz_bookmarks.id, moz_bookmarks.title "
         "FROM moz_bookmarks "
         "WHERE (moz_bookmarks.title LIKE '%Wikikipedia%');")

result = database.execute_sql(query)
bookmarks = result.fetchall()

for bookmark in bookmarks:
    print(f"Bookmark[{bookmark[0]}] = {bookmark[1]}")

print("\n!INFO: To undo these changes, "
      "run the revert.py file in this directory")
