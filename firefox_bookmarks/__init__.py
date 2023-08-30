"""A Python library to manage Firefox bookmarks with ease.

Contains the `FirefoxBookmarks` class, which provides a high-level API for
working with Firefox bookmarks, hiding the lower-level implementation details
and offering simplified methods for common operations.

Example:
    >>> from firefox_bookmarks import *
    >>> fb = FirefoxBookmarks()

    # You can pass a `ProfileCriterion` to choose from multiple profiles.
    >>> fb.connect(criterion=ProfileCriterion.LARGEST)

    # Get all the GitHub bookmarks,
    >>> github_bookmarks = fb.bookmarks(
    ...     where=Bookmark.url.contains("mozilla.org"),
    ... )

    # and print their URLs.
    >>> for bookmark in github_bookmarks:
    ...     print(bookmark.url)
    ... # doctest: +ELLIPSIS
    https://support.mozilla.org/products/firefox
    ...

    # Remember to clean up after yourself!
    >>> fb.disconnect()

Copyright (C) 2023 Aditya Rajput & other contributors
"""

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import shutil
from tempfile import gettempdir
from time import time
from typing import Any, Iterable

from peewee import (
    JOIN,
    CharField,
    DoesNotExist,
    Expression,
    Field,
    FloatField,
    Function,
    IntegerField,
    ModelSelect,
    StringExpression,
    TextField,
    fn,
)

from .bookmark import Bookmark, connect_bookmark_model
from .constants import BATCH_SIZE, DEFAULT_FOLDER_GUID, FirefoxEntity, ProfileCriterion
from .locate import locate_db
from .models import FirefoxBookmark, FirefoxOrigin, FirefoxPlace, connect_firefox_models


class FirefoxBookmarks:
    """Class that helps manage Firefox bookmarks with ease.

    Provides a high-level API for working with Firefox bookmarks, hiding the
    lower-level implementation details and offering simplified methods for
    common operations.

    Example:
        >>> from firefox_bookmarks import *
        >>> fb = FirefoxBookmarks()

        # You can pass a `ProfileCriterion` to choose from multiple profiles.
        >>> fb.connect(criterion=ProfileCriterion.LARGEST)

        # Get all the GitHub bookmarks,
        >>> github_bookmarks = fb.bookmarks(
        ...     where=Bookmark.url.contains("mozilla.org"),
        ... )

        # and print their URLs.
        >>> for bookmark in github_bookmarks:
        ...     print(bookmark.url)
        ... # doctest: +ELLIPSIS
        https://support.mozilla.org/products/firefox
        ...

        # Remember to clean up after yourself!
        >>> fb.disconnect()

    Attributes:
        connect: Duplicates the Places database and connects to it
        disconnect: Disconnects and cleans up

        select: Executes a SELECT query
        update: Executes an UPDATE query

        bookmarks: Executes a SELECT query over the bookmarks
        folders: Executes a SELECT query over the folders

        diff: Generates diff between current state and the original Places database
        commit: Commits the updated bookmarks to the Places database
        restore_backup: Finds the ith latest backup and copies it to the Places database
    """

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
                "moz_bookmarks": {
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
                "moz_places": {
                    "FROM": (
                        # Bookmark.id,
                        # Bookmark.title,
                        Bookmark.url,
                        Bookmark.description,
                        # Bookmark.type,
                        # Bookmark.parent,
                        Bookmark.place_id,
                        Bookmark.origin_id,
                        # Bookmark.date_added,
                        # Bookmark.folder_type,
                        Bookmark.foreign_count,
                        # Bookmark.guid,
                        Bookmark.hidden,
                        # Bookmark.keyword_id,
                        # Bookmark.last_modified,
                        Bookmark.last_visit_date,
                        # Bookmark.origin_alt_frecency,
                        # Bookmark.origin_frecency,
                        # Bookmark.origin_host,
                        # Bookmark.origin_prefix,
                        # Bookmark.origin_recalc_alt_frecency,
                        # Bookmark.origin_recalc_frecency,
                        Bookmark.place_alt_frecency,
                        Bookmark.place_frecency,
                        Bookmark.place_guid,
                        Bookmark.place_recalc_alt_frecency,
                        Bookmark.place_recalc_frecency,
                        Bookmark.preview_image_url,
                        # Bookmark.position,
                        Bookmark.rev_host,
                        Bookmark.site_name,
                        # Bookmark.sync_change_counter,
                        # Bookmark.sync_status,
                        Bookmark.typed,
                        Bookmark.url_hash,
                        Bookmark.visit_count,
                    ),
                    "TO": (
                        # FirefoxBookmark.id,
                        # FirefoxBookmark.title,
                        FirefoxPlace.url,
                        FirefoxPlace.description,
                        # FirefoxBookmark.type,
                        # FirefoxBookmark.parent,
                        FirefoxPlace.id,
                        FirefoxPlace.origin,
                        # FirefoxBookmark.date_added,
                        # FirefoxBookmark.folder_type,
                        FirefoxPlace.foreign_count,
                        # FirefoxBookmark.guid,
                        FirefoxPlace.hidden,
                        # FirefoxBookmark.keyword_id,
                        # FirefoxBookmark.last_modified,
                        FirefoxPlace.last_visit_date,
                        # FirefoxOrigin.alt_frecency,
                        # FirefoxOrigin.frecency,
                        # FirefoxOrigin.host,
                        # FirefoxOrigin.prefix,
                        # FirefoxOrigin.recalc_alt_frecency,
                        # FirefoxOrigin.recalc_frecency,
                        FirefoxPlace.alt_frecency,
                        FirefoxPlace.frecency,
                        FirefoxPlace.guid,
                        FirefoxPlace.recalc_alt_frecency,
                        FirefoxPlace.recalc_frecency,
                        FirefoxPlace.preview_image_url,
                        # FirefoxBookmark.position,
                        FirefoxPlace.rev_host,
                        FirefoxPlace.site_name,
                        # FirefoxBookmark.sync_change_counter,
                        # FirefoxBookmark.sync_status,
                        FirefoxPlace.typed,
                        FirefoxPlace.url_hash,
                        FirefoxPlace.visit_count,
                    ),
                },
            },
        }

    def connect(
        self,
        *,
        look_under_path: str | None = None,
        criterion: ProfileCriterion = ProfileCriterion.LATEST,
    ):
        """Duplicates a Places database (chosen according to `criterion`) and connects the `Bookmark` model to it

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

    def create(
        self,
        *,
        entity_type: FirefoxEntity,
        title: str,
        url: str | None = None,
        parent: Bookmark | None = None,
        position: int | None = None,
    ) -> Bookmark | None:
        """Creates a new bookmark or folder under `parent`

        Args:
            entity_type: Type of entity to create
            title: Title of bookmark or folder
            url: URL of resource the bookmark is leading to. Defaults to `None`.
            parent: Folder under which to create the bookmark. Defaults to \
            "Other Bookmarks".

        Returns:
            Newly created bookmark or folder
        """

        if parent is None:
            parent = Bookmark.get(Bookmark.guid == DEFAULT_FOLDER_GUID)

        # region erroneous-inputs
        if (entity_type == FirefoxEntity.BOOKMARK) ^ (url is not None):
            if url is None:
                logging.error("Bookmark needs a URL")
            if url is not None:
                logging.error("Folder cannot have a URL")
            return None

        if not parent.is_folder:
            logging.error("`parent` should be a folder")
            return None
        # endregion

        return Bookmark.create(
            type=entity_type.value,
            title=title,
            parent=parent,
            url=url,
            position=position,
            guid=guid,
            sync_status=sync_status,
            # TODO: Add other fields
        )

    def select(
        self,
        *,
        fields: Iterable[Field] = [],
        where: Expression | None = None,
        limit: int | None = None,
    ) -> Iterable[Bookmark]:
        """Executes a SELECT query

        Args:
            fields: Iterable of fields to select. Defaults to all.
            where: An `Expression` used in the WHERE clause. Defaults to `None`.
            limit: Value to use in the LIMIT clause. Defaults to `None`.

        Returns:
            Iterable of bookmarks and folders matching the SELECT query
        """

        selected: ModelSelect = Bookmark.select(*fields)

        if where is not None:
            selected = selected.where(where)
        if limit is not None:
            selected = selected.limit(limit)

        return selected.execute()

    def update(
        self,
        *,
        where: Expression | None = None,
        data: dict[Field, Any],
    ) -> int:
        """Executes an UPDATE query

        Args:
            data: A `dict` from fields of `Bookmark` to new values
            where: An `Expression` used in the WHERE clause. Defaults to `None`.

        Returns:
            Number of rows affected by the update
        """

        return Bookmark.update(data).where(where).execute()

    def bookmarks(
        self,
        *,
        fields: Iterable[Field] = [],
        where: Expression | None = None,
        limit: int | None = None,
    ) -> Iterable[Bookmark]:
        """Executes a SELECT query over only the rows representing bookmarks

        Args:
            fields: Iterable of fields to select. Defaults to all.
            where: An `Expression` used in the WHERE clause. Defaults to `None`.
            limit: Value to use in the LIMIT clause. Defaults to `None`.

        Returns:
            Iterable of bookmarks matching the SELECT query
        """

        final_where = (Bookmark.type == FirefoxEntity.BOOKMARK.value)
        if where is not None:
            final_where &= where

        return Bookmark \
            .select(*fields) \
            .where(final_where) \
            .limit(limit) \
            .execute()

    def folders(
        self,
        *,
        fields: Iterable[Field] = [],
        where: Expression | None = None,
        limit: int | None = None,
    ) -> Iterable[Bookmark]:
        """Executes a SELECT query over only the rows representing folders

        Args:
            fields: Iterable of fields to select. Defaults to all.
            where: An `Expression` used in the WHERE clause. Defaults to `None`.
            limit: Value to use in the LIMIT clause. Defaults to `None`.

        Returns:
            Iterable of folders matching the SELECT query
        """

        final_where: Expression = (Bookmark.type == FirefoxEntity.FOLDER.value)
        if where is not None:
            final_where &= where

        return Bookmark \
            .select(*fields) \
            .where(final_where) \
            .limit(limit) \
            .execute()

    def str_update(
        self,
        *,
        field: CharField | TextField,
        where: Expression,
        updated: str | StringExpression | Function,
    ) -> int:
        """Executes an UPDATE query on a string field

        Args:
            field: The `Field` to update
            where: An `Expression` used in the WHERE clause
            updated: The field's updated value, or a `peewee.Function` that defines the transform

        Returns:
            Number of rows affected by the update
        """

        return self.update(
            where=where,
            data={field: updated},
        )

    def num_update(
        self,
        *,
        field: IntegerField | FloatField,
        where: Expression,
        updated: int | float | Expression,
    ) -> int:
        """Executes an UPDATE query on a numerical field

        Args:
            field: The `Field` to update
            where: An `Expression` used in the WHERE clause
            updated: The field's updated value

        Returns:
            Number of rows affected by the update
        """

        return self.update(
            where=where,
            data={field: updated},
        )

    def move(
        self,
        *,
        bookmarks: Expression | None,
        source: Expression | None,
        destination: Expression,
    ) -> int:
        """Moves `bookmarks` from `source` to `destination`.

        Either `source` or `bookmarks` must be specified. `source` and \
        `destination` are the criteria with which to search for the \
        respective folders. The first folder matching the corresponding \
        criterion will be chosen.

        Args:
            bookmarks: Which bookmarks are to be moved. Defaults to `None`.
            source: Criteria for the source folder. The first folder that \
            matches this query will be used. Defaults to `None`.
            destination: Criteria for the destination folder. The first \
            folder that matches this query will be used.

        Returns:
            Number of rows affected by the update
        """

        if (bookmarks is None) and (source is None):
            logging.error("Either `source` or `bookmarks` must be specified.")
            return 0

        source_folder = None
        if source is not None:
            source_folder = self.folders(
                fields=(Bookmark.id, ),
                where=source,
                limit=1,
            ).scalar()

        destination_folder = self.folders(
            fields=(Bookmark.id, ),
            where=destination,
            limit=1,
        ).scalar()

    def diff(self) -> list[str]:
        """Generates diff between current state of our duplicate database, and the chosen Places database

        Returns:
            List of `guid`s, representing the bookmarks that have changed
        """

        bookmarks = list(
            FirefoxBookmark \
                .select(FirefoxBookmark.guid, FirefoxBookmark.fk) \
                .execute()
        )
        differing_bookmarks = []

        for bk in bookmarks:
            original_bk = FirefoxBookmark \
                .select(*self._TRANSLATION["SEPARATE"]["moz_bookmarks"]["TO"]) \
                .where(FirefoxBookmark.guid == bk.guid) \
                .tuples() \
                .first()

            changed_bk = Bookmark \
                .select(*self._TRANSLATION["SEPARATE"]["moz_bookmarks"]["FROM"]) \
                .where(Bookmark.guid == bk.guid) \
                .tuples() \
                .first()

            original_pl = FirefoxPlace \
                .select(*self._TRANSLATION["SEPARATE"]["moz_places"]["TO"]) \
                .where(FirefoxPlace.id == bk.fk) \
                .tuples() \
                .first()

            changed_pl = Bookmark \
                .select(*self._TRANSLATION["SEPARATE"]["moz_places"]["FROM"]) \
                .where(Bookmark.guid == bk.guid) \
                .tuples() \
                .first()

            if original_bk != changed_bk or original_pl != changed_pl:
                differing_bookmarks.append(bk.guid)

        return differing_bookmarks

    def commit(self):
        """Commits the updated bookmarks from our duplicate database to the Places database"""

        self._back_up_places()

        diff_guids = self.diff()

        with self._places_database.atomic():
            for guid in diff_guids:
                # region moz_bookmarks
                source_tuple_bk = Bookmark \
                    .select(*self._TRANSLATION["SEPARATE"]["moz_bookmarks"]["FROM"]) \
                    .where(Bookmark.guid == guid) \
                    .tuples() \
                    .first()

                source_dict_bk = {
                    field: value
                    for field, value in zip(
                        self._TRANSLATION["SEPARATE"]["moz_bookmarks"]["TO"],
                        source_tuple_bk,
                    )
                }

                FirefoxBookmark \
                    .update(source_dict_bk) \
                    .where(FirefoxBookmark.guid == guid) \
                    .execute()
                # endregion

                # region moz_places
                place_guid = Bookmark \
                    .select(Bookmark.place_guid) \
                    .where(Bookmark.guid == guid) \
                    .scalar()

                if place_guid is not None:
                    source_tuple_pl = Bookmark \
                        .select(*self._TRANSLATION["SEPARATE"]["moz_places"]["FROM"]) \
                        .where(Bookmark.place_guid == place_guid) \
                        .tuples() \
                        .first()

                    source_dict_pl = {
                        field: value
                        for field, value in zip(
                            self._TRANSLATION["SEPARATE"]["moz_places"]["TO"],
                            source_tuple_pl,
                        )
                    }

                    FirefoxPlace \
                        .update(source_dict_pl) \
                        .where(FirefoxPlace.guid == place_guid) \
                        .execute()
                # endregion

    def _back_up_places(self):
        file_name = f"backup-{int(time())}.sqlite"
        dest = os.path.join(os.path.dirname(self._places_path), file_name)
        shutil.copy(self._places_path, dest)

    def disconnect(self):
        """Disconnects from databases and removes the duplicate database"""

        self._places_database.close()
        self._database.close()
        os.remove(self._db_path)

    def restore_backup(self, *, index=0):
        """Finds the latest backup and copies it to the Places database

        Args:
            index: Index of backup to restore when sorted in a descending \
            order. Defaults to 0 (which refers to the latest backup).
        """

        dir_path, timestamps = self._get_backups()
        timestamps.sort(reverse=True)
        backup_path = os.path.join(
            dir_path,
            f"backup-{timestamps[index]}.sqlite",
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
    'FirefoxEntity',  # For convenience
]
