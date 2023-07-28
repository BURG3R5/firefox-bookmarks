import os
import shutil
from tempfile import gettempdir
from time import time
from typing import Any, Iterable

from peewee import JOIN, DoesNotExist, Expression, Field, Model, ModelAlias, fn

from .bookmark import Bookmark, connect_bookmark_model
from .constants import BATCH_SIZE, BOOKMARK_TYPE, FOLDER_TYPE, ProfileCriterion
from .locate import locate_db
from .models import FirefoxBookmark, FirefoxOrigin, FirefoxPlace, connect_firefox_models

FieldOrModel = Model | ModelAlias | Field


class FirefoxBookmarks:

    def __init__(self):
        self._db_path = os.path.join(gettempdir(), 'bookmarks.sqlite')

        self._TRANSLATION = {
            "COMBINE": {
                "FROM": (
                    FirefoxBookmark.id,
                    FirefoxBookmark.title,
                    FirefoxPlace.url,
                    FirefoxPlace.description,
                    FirefoxBookmark.type,
                    FirefoxBookmark.parent,
                    FirefoxBookmark.fk,
                    FirefoxPlace.origin,
                    FirefoxBookmark.date_added,
                    FirefoxBookmark.folder_type,
                    FirefoxPlace.foreign_count,
                    FirefoxBookmark.guid,
                    FirefoxPlace.hidden,
                    FirefoxBookmark.keyword_id,
                    FirefoxBookmark.last_modified,
                    FirefoxPlace.last_visit_date,
                    FirefoxOrigin.alt_frecency,
                    FirefoxOrigin.frecency,
                    FirefoxOrigin.host,
                    FirefoxOrigin.prefix,
                    FirefoxOrigin.recalc_alt_frecency,
                    FirefoxOrigin.recalc_frecency,
                    FirefoxPlace.alt_frecency,
                    FirefoxPlace.frecency,
                    FirefoxPlace.guid,
                    FirefoxPlace.recalc_alt_frecency,
                    FirefoxPlace.recalc_frecency,
                    FirefoxPlace.preview_image_url,
                    FirefoxBookmark.position,
                    FirefoxPlace.rev_host,
                    FirefoxPlace.site_name,
                    FirefoxBookmark.sync_change_counter,
                    FirefoxBookmark.sync_status,
                    FirefoxPlace.typed,
                    FirefoxPlace.url_hash,
                    FirefoxPlace.visit_count,
                ),
                "TO": (
                    Bookmark.id,
                    Bookmark.title,
                    Bookmark.url,
                    Bookmark.description,
                    Bookmark.type,
                    Bookmark.parent,
                    Bookmark.place_id,
                    Bookmark.origin_id,
                    Bookmark.date_added,
                    Bookmark.folder_type,
                    Bookmark.foreign_count,
                    Bookmark.guid,
                    Bookmark.hidden,
                    Bookmark.keyword_id,
                    Bookmark.last_modified,
                    Bookmark.last_visit_date,
                    Bookmark.origin_alt_frecency,
                    Bookmark.origin_frecency,
                    Bookmark.origin_host,
                    Bookmark.origin_prefix,
                    Bookmark.origin_recalc_alt_frecency,
                    Bookmark.origin_recalc_frecency,
                    Bookmark.place_alt_frecency,
                    Bookmark.place_frecency,
                    Bookmark.place_guid,
                    Bookmark.place_recalc_alt_frecency,
                    Bookmark.place_recalc_frecency,
                    Bookmark.preview_image_url,
                    Bookmark.position,
                    Bookmark.rev_host,
                    Bookmark.site_name,
                    Bookmark.sync_change_counter,
                    Bookmark.sync_status,
                    Bookmark.typed,
                    Bookmark.url_hash,
                    Bookmark.visit_count,
                ),
            },
            "SEPARATE": {
                "FROM": (
                    Bookmark.id,
                    Bookmark.title,
                    # Bookmark.url,
                    # Bookmark.description,
                    Bookmark.type,
                    Bookmark.parent,
                    Bookmark.place_id,
                    # Bookmark.origin_id,
                    Bookmark.date_added,
                    Bookmark.folder_type,
                    # Bookmark.foreign_count,
                    Bookmark.guid,
                    # Bookmark.hidden,
                    Bookmark.keyword_id,
                    Bookmark.last_modified,
                    # Bookmark.last_visit_date,
                    # Bookmark.origin_alt_frecency,
                    # Bookmark.origin_frecency,
                    # Bookmark.origin_host,
                    # Bookmark.origin_prefix,
                    # Bookmark.origin_recalc_alt_frecency,
                    # Bookmark.origin_recalc_frecency,
                    # Bookmark.place_alt_frecency,
                    # Bookmark.place_frecency,
                    # Bookmark.place_guid,
                    # Bookmark.place_recalc_alt_frecency,
                    # Bookmark.place_recalc_frecency,
                    # Bookmark.preview_image_url,
                    Bookmark.position,
                    # Bookmark.rev_host,
                    # Bookmark.site_name,
                    Bookmark.sync_change_counter,
                    Bookmark.sync_status,
                    # Bookmark.typed,
                    # Bookmark.url_hash,
                    # Bookmark.visit_count,
                ),
                "TO": (
                    FirefoxBookmark.id,
                    FirefoxBookmark.title,
                    # FirefoxPlace.url,
                    # FirefoxPlace.description,
                    FirefoxBookmark.type,
                    FirefoxBookmark.parent,
                    FirefoxBookmark.fk,
                    # FirefoxPlace.origin,
                    FirefoxBookmark.date_added,
                    FirefoxBookmark.folder_type,
                    # FirefoxPlace.foreign_count,
                    FirefoxBookmark.guid,
                    # FirefoxPlace.hidden,
                    FirefoxBookmark.keyword_id,
                    FirefoxBookmark.last_modified,
                    # FirefoxPlace.last_visit_date,
                    # FirefoxOrigin.alt_frecency,
                    # FirefoxOrigin.frecency,
                    # FirefoxOrigin.host,
                    # FirefoxOrigin.prefix,
                    # FirefoxOrigin.recalc_alt_frecency,
                    # FirefoxOrigin.recalc_frecency,
                    # FirefoxPlace.alt_frecency,
                    # FirefoxPlace.frecency,
                    # FirefoxPlace.guid,
                    # FirefoxPlace.recalc_alt_frecency,
                    # FirefoxPlace.recalc_frecency,
                    # FirefoxPlace.preview_image_url,
                    FirefoxBookmark.position,
                    # FirefoxPlace.rev_host,
                    # FirefoxPlace.site_name,
                    FirefoxBookmark.sync_change_counter,
                    FirefoxBookmark.sync_status,
                    # FirefoxPlace.typed,
                    # FirefoxPlace.url_hash,
                    # FirefoxPlace.visit_count,
                ),
            },
        }

    def connect(
        self,
        *,
        look_under_path: str | None = None,
        criterion: ProfileCriterion = ProfileCriterion.LATEST,
    ):
        """"Duplicates a Places database (chosen according to `criterion`) and connects the `Bookmark` model to it"

        Args:
            look_under_path: Path from where to start searching. \
            If not supplied, looks under default profiles directory.
            criterion: Which profile to choose, in case there are multiple. \
            Defaults to `ProfileCriterion.LATEST`.
        """

        # Connect old models
        from .models import database_obj
        self._places_database = database_obj
        self._places_path = locate_db(
            look_under_path=look_under_path,
            criterion=criterion,
        )
        connect_firefox_models(
            look_under_path=look_under_path,
            criterion=criterion,
        )

        # Connect new model
        self._database = connect_bookmark_model(db_path=self._db_path)

        # Insert data into duplicate database
        self._load()

    def _load(self):
        """Inserts data from places.sqlite to our duplicate bookmarks.sqlite database"""

        max_id = FirefoxBookmark.select(fn.MAX(FirefoxBookmark.id)).scalar()

        with self._database.atomic():
            for idx in range(0, max_id, BATCH_SIZE):
                try:
                    selected = FirefoxBookmark.select(
                        *(self._TRANSLATION["COMBINE"]["FROM"]))

                    joined = selected.join(
                        FirefoxPlace,
                        on=(FirefoxBookmark.fk == FirefoxPlace.id),
                        join_type=JOIN.LEFT_OUTER,
                    ).join(
                        FirefoxOrigin,
                        on=(FirefoxPlace.origin == FirefoxOrigin.id),
                        join_type=JOIN.LEFT_OUTER,
                    )

                    start = (FirefoxBookmark.id >= idx)
                    end = (FirefoxBookmark.id < idx + BATCH_SIZE)

                    query = joined.where(start & end)

                    source = list(query.tuples())
                except DoesNotExist:
                    # This just means that there are no ids in this batch. This is not unusual.
                    # Hence we just...
                    #
                    # Ignore,
                    # Barua
                    continue

                Bookmark.insert_many(
                    source,
                    fields=self._TRANSLATION["COMBINE"]["TO"],
                ).execute()

    def bookmarks(
        self,
        *,
        fields: Iterable[FieldOrModel] = [],
        query: Expression | None = None,
    ) -> Iterable[Bookmark]:
        final_query: Expression = (Bookmark.type == BOOKMARK_TYPE)
        if query is not None:
            final_query &= query

        return Bookmark.select(*fields).where(final_query).execute()

    def folders(
        self,
        *,
        fields: Iterable[FieldOrModel] = [],
        query: Expression | None = None,
    ) -> Iterable[Bookmark]:
        final_query: Expression = (Bookmark.type == FOLDER_TYPE)
        if query is not None:
            final_query &= query

        return Bookmark.select(*fields).where(final_query).execute()

    def update(
        self,
        *,
        query: Expression | None = None,
        data: dict[Field, Any],
    ) -> int:
        return Bookmark.update(data).where(query).execute()

    def diff(self) -> list[str]:
        """Generates diff between current state of our duplicate database, and the chosen Places database

        Returns:
            List of `guid`s, representing the bookmarks that have changed
        """

        bookmarks = list(
            FirefoxBookmark \
                .select(FirefoxBookmark.guid) \
                .execute()
        )
        differing_bookmarks = []

        for bk in bookmarks:
            original = FirefoxBookmark \
                .select(*self._TRANSLATION["SEPARATE"]["TO"]) \
                .where(FirefoxBookmark.guid == bk.guid) \
                .tuples() \
                .first()

            changed = Bookmark \
                .select(*self._TRANSLATION["SEPARATE"]["FROM"]) \
                .where(Bookmark.guid == bk.guid) \
                .tuples() \
                .first()

            if original != changed:
                differing_bookmarks.append(bk.guid)

        return differing_bookmarks

    def commit(self):
        self._back_up_places()

        diff_guids = self.diff()

        with self._places_database.atomic():
            for guid in diff_guids:
                source_tuple = Bookmark \
                    .select(*self._TRANSLATION["SEPARATE"]["FROM"]) \
                    .where(Bookmark.guid == guid) \
                    .tuples() \
                    .first()

                source_dict = {
                    field: value
                    for field, value in zip(
                        self._TRANSLATION["SEPARATE"]["TO"],
                        source_tuple,
                    )
                }

                FirefoxBookmark.replace(source_dict).execute()

    def _back_up_places(self):
        file_name = f"backup-{int(time())}.sqlite"
        dest = os.path.join(os.path.dirname(self._places_path), file_name)
        shutil.copy(self._places_path, dest)

    def disconnect(self):
        self._database.close()
        os.remove(self._db_path)

    def restore_latest_backup(self):
        """Finds the latest backup and copies it to places.sqlite"""

        dir_path, timestamps = self._get_backups()
        backup_path = os.path.join(
            dir_path,
            f"backup-{max(timestamps)}.sqlite",
        )
        shutil.copy(backup_path, self._places_path)

    def _get_backups(self) -> tuple[str, list[int]]:
        dir_path = os.path.dirname(self._places_path)
        files = os.listdir(dir_path)
        timestamps = [
            int(file.split('-')[1].split('.')[0]) for file in files
            if file.startswith('backup-') and file.endswith('.sqlite')
        ]

        return dir_path, timestamps


__all__ = [
    'FirefoxBookmarks',
    'Bookmark',  # For convenience
    'ProfileCriterion',  # For convenience
]
