import os
import sys

from .constants import ProfileCriterion

FILE_NAME = "places.sqlite"


def locate_db(
    *,
    look_under_path: str | None = None,
    criterion: ProfileCriterion = ProfileCriterion.LATEST,
) -> str:
    """Returns the path to a Places database according to the chosen criterion

    Args:
        look_under_path: Path from where to start searching. \
        If not supplied, looks under default profiles directory.
        criterion: Which profile to choose, in case there are multiple. \
        Defaults to `ProfileCriterion.LATEST`.

    Returns:
        Path of the Places database under the chosen profile
    """

    candidates = locate_db_candidates(look_under_path=look_under_path)

    if criterion == ProfileCriterion.LATEST:
        return max(candidates, key=_last_modified, default=":(")
    if criterion == ProfileCriterion.LARGEST:
        return max(candidates, key=_file_size, default=":(")

    return ":("


def locate_db_candidates(*, look_under_path: str | None = None) -> list[str]:
    """Locates all `places.sqlite` under the given directory OR under the default profiles directory

    Args:
        look_under_path: Path from where to start searching. \
        If not supplied, looks under default profiles directory.

    Returns:
        Paths of `places.sqlite` files found
    """

    profiles_dir: str = look_under_path or _get_profiles_dir()
    candidates: list[str] = []

    for dir_path, _, filenames in os.walk(profiles_dir):
        if FILE_NAME in filenames:
            candidates.append(os.path.join(dir_path, FILE_NAME))

    return candidates


def _get_profiles_dir() -> str:
    # ref: https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data
    if sys.platform.startswith("win"):
        return os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")
    if sys.platform.startswith("darwin"):
        return os.path.expanduser(
            "~/Library/Application Support/Firefox/Profiles")
    return os.path.expanduser("~/.mozilla/firefox")


def _last_modified(file_path: str) -> float:
    return os.path.getmtime(file_path)


def _file_size(file_path: str) -> float:
    return os.path.getsize(file_path)


__all__ = [
    'locate_db',
    'locate_db_candidates',
    'ProfileCriterion',  # For convenience
]
