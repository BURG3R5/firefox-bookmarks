from enum import Enum


class ProfileCriterion(Enum):
    """Strategies to choose a Firefox profile if multiple are found"""

    LARGEST = "Choose the profile with the largest Places DB"
    LATEST = "Choose the profile with the most recent changes in its Places DB"


BATCH_SIZE = 100
BOOKMARK_TYPE = 1
FOLDER_TYPE = 2

__all__ = [
    'ProfileCriterion',
    'BATCH_SIZE',
    'BOOKMARK_TYPE',
    'FOLDER_TYPE',
]
