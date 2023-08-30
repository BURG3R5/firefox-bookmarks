# `firefox_bookmarks` Examples

This directory contains demonstrative scripts that showcase the package capabilities. It is recommended that you work through the examples in a specific order:

- `fetch_github_bookmarks/` - Fetch titles and URLs of all GitHub bookmarks in the profile with the largest places.sqlite

  - `execute_sql` - Use low-level API to connect to the db, and then execute a SQL query string
  - `models` - Use mid-level API to connect `peewee` models to the db, then use the ORM
  - `the_easy_way` - Use high-level API to connect to the db, then simply use the `.bookmarks` method

- `rename_to_wikikipedia/` - Replace "Wikipedia" in bookmark titles to "Wikikipedia"

  - `execute_sql` - Use low-level API to connect to the db, and then execute a SQL query string
  - `models` - Use mid-level API to connect `peewee` models to the db, then use the ORM
  - `the_easy_way` - Use high-level API to connect to the db, then simply use the `.str_update` method
  - `revert` - Revert the changes made by the above three scripts
