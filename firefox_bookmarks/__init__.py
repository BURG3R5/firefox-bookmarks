import os
from tempfile import gettempdir
from typing import Iterable

from peewee import JOIN, DoesNotExist, fn

from .bookmark import Bookmark, connect_bookmark_model
from .constants import BATCH_SIZE, BOOKMARK_TYPE, FOLDER_TYPE, ProfileCriterion
from .models import FirefoxBookmark, FirefoxOrigin, FirefoxPlace, connect_firefox_models


class FirefoxBookmarks:

    def __init__(self):
        self._db_path = os.path.join(gettempdir(), 'bookmarks.sqlite')

        self._TRANSLATION = {
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
        connect_firefox_models(
            look_under_path=look_under_path,
            criterion=criterion,
        )

        # Connect new model
        self._database = connect_bookmark_model(db_path=self._db_path)

        # region Insert data into temp database
        max_id = FirefoxBookmark.select(fn.MAX(FirefoxBookmark.id)).scalar()

        with self._database.atomic():
            for idx in range(0, max_id, BATCH_SIZE):
                try:
                    selected = FirefoxBookmark.select(
                        *(self._TRANSLATION["FROM"]))

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
                    fields=self._TRANSLATION["TO"],
                ).execute()
        # endregion

    def bookmarks(self) -> Iterable[Bookmark]:
        return Bookmark \
            .select() \
            .where((Bookmark.type == BOOKMARK_TYPE)) \
            .execute()

    def folders(self) -> Iterable[Bookmark]:
        return Bookmark \
            .select() \
            .where(Bookmark.type == FOLDER_TYPE) \
            .execute()

    def disconnect(self):
        self._database.close()
        os.remove(self._db_path)


__all__ = [
    'FirefoxBookmarks',
    'Bookmark',  # For convenience
    'ProfileCriterion',  # For convenience
]
