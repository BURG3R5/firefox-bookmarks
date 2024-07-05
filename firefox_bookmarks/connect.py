import shutil
import tempfile
import warnings

from peewee import OperationalError, SqliteDatabase

from .constants import ProfileCriterion
from .locate import locate_db


def connect_to_places_db(
    *,
    database: SqliteDatabase | None = None,
    look_under_path: str | None = None,
    criterion: ProfileCriterion = ProfileCriterion.LATEST,
    readonly: bool = False,
) -> SqliteDatabase:
    """Connects to a Places database according to the chosen criterion

    Args:
        database: A dummy pre-existing `SqliteDatabase` object to be \
        initialized with the actual path. If not supplied, a new one is \
        created.
        look_under_path: Path from where to start searching. \
        If not supplied, looks under default profiles directory.
        criterion: Which profile to choose, in case there are multiple. \
        Defaults to `ProfileCriterion.LATEST`.
        readonly: If `True`, connects to a temporary duplicate of the \
        database, which will not be synced with the original. Defaults to `False`.

    Returns:
        A connection to the Places database under the chosen profile
    """

    db_path = locate_db(look_under_path=look_under_path, criterion=criterion)

    if readonly:
        temp_db_path = tempfile.mkstemp()[1]
        shutil.copyfile(db_path, temp_db_path)
        db_path = temp_db_path
        warnings.warn(
            "Connected to a temporary duplicate of the Places database. " + \
            "Any changes made will not be synced with the original. " + \
            f"Please run `os.remove(r'{temp_db_path}')` to clean up before exit.",
        )

    try:
        if database is None:
            database = SqliteDatabase(db_path)
        else:
            database.init(db_path)
    except OperationalError:
        raise Exception(
            "Could not connect to Places database due to sqlite error. " + \
            "The database may be locked by another process. " + \
            "If your task is read-only, pass `readonly=True` to connect " + \
            "to a temporary duplicate of the database instead."
        )
    database.connect(reuse_if_open=True)

    return database


__all__ = [
    'connect_to_places_db',
    'ProfileCriterion',  # For convenience
]
