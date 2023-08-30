from peewee import SQL, ForeignKeyField, IntegerField, Model, SqliteDatabase, TextField

from .constants import FirefoxEntity

database_obj = SqliteDatabase(None)


class Bookmark(Model):
    """Represents an entry in the `bookmark` table"""

    id = IntegerField(primary_key=True)
    title = TextField(null=True)
    url = TextField(null=True)
    description = TextField(null=True)
    type = IntegerField(null=True)
    parent = ForeignKeyField(model='self', null=True)
    place_id = IntegerField(null=True)
    origin_id = IntegerField(null=True)

    date_added = IntegerField(index=True, null=True)
    folder_type = TextField(null=True)
    foreign_count = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    guid = TextField(null=True, unique=True)
    hidden = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    keyword_id = IntegerField(null=True)
    last_modified = IntegerField(null=True)
    last_visit_date = IntegerField(index=True, null=True)
    last_visit_date = IntegerField(index=True, null=True)
    origin_alt_frecency = IntegerField(null=True)
    origin_frecency = IntegerField(null=True)
    origin_host = TextField(null=True)
    origin_prefix = TextField(null=True)
    origin_recalc_alt_frecency = IntegerField(
        constraints=[SQL("DEFAULT 0")],
        null=True,
    )
    origin_recalc_frecency = IntegerField(
        constraints=[SQL("DEFAULT 0")],
        null=True,
    )
    place_alt_frecency = IntegerField(index=True, null=True)
    place_frecency = IntegerField(
        constraints=[SQL("DEFAULT -1")],
        index=True,
        null=True,
    )
    place_guid = TextField(null=True)
    place_recalc_alt_frecency = IntegerField(
        constraints=[SQL("DEFAULT 0")],
        null=True,
    )
    place_recalc_frecency = IntegerField(
        constraints=[SQL("DEFAULT 0")],
        null=True,
    )
    preview_image_url = TextField(null=True)
    position = IntegerField(null=True)
    rev_host = TextField(index=True, null=True)
    site_name = TextField(null=True)
    sync_change_counter = IntegerField(constraints=[SQL("DEFAULT 1")])
    sync_status = IntegerField(constraints=[SQL("DEFAULT 0")])
    typed = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    url_hash = IntegerField(
        constraints=[SQL("DEFAULT 0")],
        index=True,
        null=True,
    )
    visit_count = IntegerField(
        constraints=[SQL("DEFAULT 0")],
        index=True,
        null=True,
    )

    class Meta:
        database = database_obj
        table_name = 'bookmark'
        indexes = (
            (('place_id', 'last_modified'), False),
            (('place_id', 'type'), False),
            (('parent', 'position'), False),
            (('origin_prefix', 'origin_host'), False),
        )

    @property
    def is_bookmark(self) -> bool:
        """Returns whether the object represents a bookmark"""
        return self.type == FirefoxEntity.BOOKMARK

    @property
    def is_folder(self) -> bool:
        """Returns whether the object represents a folder"""
        return self.type == FirefoxEntity.FOLDER

    def __str__(self) -> str:
        return str(self.title or ".")

    def __repr__(self) -> str:
        if self.is_bookmark:
            return f"[{self.title}]({self.url})"
        elif self.is_folder:
            return f"{self.title}/"
        return f"<Bookmark {self.id}, {self.type}, {self.title}>"

    @property
    def path(self) -> str:
        """Generates the 'path' of the object, which is a string resembling a *nix path leading thru parents back to the root

        Returns:
            str: The 'path' of the bookmark/folder
        """
        curr: Bookmark = self
        path = ""

        while curr.parent_id != 0 and curr.parent_id is not None:  # type: ignore
            path = repr(curr) + path
            curr = curr.parent  # type: ignore

        return "/" + path


def connect_bookmark_model(*, db_path: str) -> SqliteDatabase:
    """Connects the `Bookmark` model to the database at the given path

    Args:
        db_path: Path of the database to connect to.
    """

    database_obj.init(db_path)
    database_obj.connect(reuse_if_open=True)
    database_obj.create_tables([Bookmark])

    return database_obj


__all__ = [
    'Bookmark',
    'connect_bookmark_model',
]
