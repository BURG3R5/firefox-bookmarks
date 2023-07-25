from enum import Enum


class ProfileCriterion(Enum):
    """Strategies to choose a Firefox profile if multiple are found"""

    LARGEST = "Choose the profile with the largest Places DB"
    LATEST = "Choose the profile with the most recent changes in its Places DB"


BOOKMARK_TYPE = 1
FOLDER_TYPE = 2

__all__ = [
    'ProfileCriterion',
    'BOOKMARK_TYPE',
    'FOLDER_TYPE',
]
