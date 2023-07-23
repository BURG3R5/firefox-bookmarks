from peewee import SQL, ForeignKeyField, IntegerField, Model, SqliteDatabase, TextField

from .constants import ProfileCriterion

database_obj = SqliteDatabase(None)


class _BaseModel(Model):

    class Meta:
        database = database_obj


class FirefoxOrigin(_BaseModel):
    """Represents an entry in the `moz_origins` table"""

    alt_frecency = IntegerField(null=True)
    frecency = IntegerField()
    host = TextField()
    prefix = TextField()
    recalc_alt_frecency = IntegerField(constraints=[SQL("DEFAULT 0")])
    recalc_frecency = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'moz_origins'
        indexes = ((('prefix', 'host'), True), )


class FirefoxPlace(_BaseModel):
    """Represents an entry in the `moz_places` table"""

    alt_frecency = IntegerField(index=True, null=True)
    description = TextField(null=True)
    foreign_count = IntegerField(constraints=[SQL("DEFAULT 0")])
    frecency = IntegerField(constraints=[SQL("DEFAULT -1")], index=True)
    guid = TextField(null=True, unique=True)
    hidden = IntegerField(constraints=[SQL("DEFAULT 0")])
    last_visit_date = IntegerField(index=True, null=True)
    origin = ForeignKeyField(model=FirefoxOrigin, null=True)
    preview_image_url = TextField(null=True)
    recalc_alt_frecency = IntegerField(constraints=[SQL("DEFAULT 0")])
    recalc_frecency = IntegerField(constraints=[SQL("DEFAULT 0")])
    rev_host = TextField(index=True, null=True)
    site_name = TextField(null=True)
    title = TextField(null=True)
    typed = IntegerField(constraints=[SQL("DEFAULT 0")])
    url = TextField(null=True)
    url_hash = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    visit_count = IntegerField(
        constraints=[SQL("DEFAULT 0")],
        index=True,
        null=True,
    )

    class Meta:
        table_name = 'moz_places'


class FirefoxBookmark(_BaseModel):
    """Represents an entry in the `moz_bookmarks` table"""

    date_added = IntegerField(column_name='dateAdded', index=True, null=True)
    fk = IntegerField(null=True)
    folder_type = TextField(null=True)
    guid = TextField(null=True, unique=True)
    keyword_id = IntegerField(null=True)
    last_modified = IntegerField(column_name='lastModified', null=True)
    parent = IntegerField(null=True)
    position = IntegerField(null=True)
    sync_change_counter = IntegerField(
        column_name='syncChangeCounter',
        constraints=[SQL("DEFAULT 1")],
    )
    sync_status = IntegerField(
        column_name='syncStatus',
        constraints=[SQL("DEFAULT 0")],
    )
    title = TextField(null=True)
    type = IntegerField(null=True)
    place = ForeignKeyField(
        FirefoxPlace,
        column_name="fk",
        backref="bookmarks",
    )

    class Meta:
        table_name = 'moz_bookmarks'
        indexes = (
            (('fk', 'last_modified'), False),
            (('fk', 'type'), False),
            (('parent', 'position'), False),
        )


def connect_firefox_models(
    *,
    look_under_path: str | None = None,
    criterion: ProfileCriterion = ProfileCriterion.LATEST,
):
    """Connects `Firefox*` models to a Places database according to the chosen criterion

    Args:
        look_under_path: Path from where to start searching. \
        If not supplied, looks under default profiles directory.
        criterion: Which profile to choose, in case there are multiple. \
        Defaults to `ProfileCriterion.LATEST`.
    """
    from .connect import connect_to_places_db

    connect_to_places_db(
        database=database_obj,
        look_under_path=look_under_path,
        criterion=criterion,
    )
