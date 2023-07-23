from firefox_bookmarks import ProfileCriterion, connect_to_places_db

database = connect_to_places_db(criterion=ProfileCriterion.LARGEST)

query = ("SELECT moz_places.title, moz_bookmarks.title, moz_places.url "
         "FROM moz_bookmarks "
         "JOIN moz_places ON moz_bookmarks.fk = moz_places.id "
         "WHERE moz_bookmarks.type = 1 "
         "AND moz_places.url LIKE 'https://github.com%';")

result = database.execute_sql(query)
bookmarks = result.fetchall()

for bookmark in bookmarks:
    print(f"Title: {bookmark[0] or bookmark[1]}\nURL: {bookmark[2]}\n")
