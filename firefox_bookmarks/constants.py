from enum import Enum


class ProfileCriterion(Enum):
    """Strategies to choose a Firefox profile if multiple are found"""

    LARGEST = "Choose the profile with the largest Places DB"
    LATEST = "Choose the profile with the most recent changes in its Places DB"


__all__ = [
    'ProfileCriterion',
]
