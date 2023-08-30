from enum import Enum


class ProfileCriterion(Enum):
    """Strategies to choose a Firefox profile if multiple are found"""

    LARGEST = "Choose the profile with the largest Places DB"
    LATEST = "Choose the profile with the most recent changes in its Places DB"


class FirefoxEntity(Enum):
    """Types of entities stored in Places DB"""

    BOOKMARK = 1
    """A leaf, if the bookmarks system was a tree. Leads to *a* site."""

    FOLDER = 2
    """A non-leaf node, if the bookmarks system was a tree. Is the parent of
    several `BOOKMARKS`"""


BATCH_SIZE = 100
DEFAULT_FOLDER_GUID = "unfiled_____"

__all__ = [
    'ProfileCriterion',
    'BATCH_SIZE',
    'FirefoxEntity',
]
