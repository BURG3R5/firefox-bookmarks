import pytest
from pytest_mock import MockerFixture

from firefox_bookmarks.models import (
    ProfileCriterion,
    connect_firefox_models,
    database_obj,
)


class TestConnectFirefoxModels:

    def test_calls_connect_to_places_db(self, mock_connect_to_places_db):
        my_path = "/this/is/a/path"
        my_criterion = ProfileCriterion.LARGEST

        connect_firefox_models(
            look_under_path=my_path,
            criterion=my_criterion,
        )

        mock_connect_to_places_db.assert_called_once_with(
            database=database_obj,
            look_under_path=my_path,
            criterion=my_criterion,
            readonly=False,
        )


# region FIXTURES


@pytest.fixture
def mock_connect_to_places_db(mocker: MockerFixture):
    mocked_locate_db = mocker \
        .patch("firefox_bookmarks.connect.connect_to_places_db")
    return mocked_locate_db


# endregion
