from peewee import SqliteDatabase

from .constants import ProfileCriterion
from .locate import locate_db


def connect_to_places_db(
    *,
    look_under_path: str | None = None,
    criterion: ProfileCriterion = ProfileCriterion.LATEST,
) -> SqliteDatabase:
    """Connects to a Places database according to the chosen criterion

    Args:
        look_under_path: Path from where to start searching. \
        If not supplied, looks under default profiles directory.
        criterion: Which profile to choose, in case there are multiple. \
        Defaults to `ProfileCriterion.LATEST`.

    Returns:
        A connection to the Places database under the chosen profile
    """

    db_path = locate_db(look_under_path=look_under_path, criterion=criterion)

    database = SqliteDatabase(db_path)
    database.connect(reuse_if_open=True)

    return database
