import pytest
from peewee import SqliteDatabase
from pytest_mock import MockerFixture

from firefox_bookmarks.connect import *


class TestConnect:

    def test_calls_locate_db(self, mock_locate_db):
        my_path = "/this/is/a/path"
        my_criterion = ProfileCriterion.LARGEST

        _ = connect_to_places_db(
            look_under_path=my_path,
            criterion=my_criterion,
        )

        mock_locate_db.assert_called_once_with(
            look_under_path=my_path,
            criterion=my_criterion,
        )

    @pytest.mark.usefixtures("mock_locate_db")
    def test_connects(self, mock_peewee_connect):
        connection = connect_to_places_db()

        assert isinstance(connection, SqliteDatabase)
        mock_peewee_connect.assert_called_once_with(reuse_if_open=True)


# region FIXTURES


@pytest.fixture
def mock_locate_db(mocker: MockerFixture):

    def mock(*args, **kwargs):
        return ":memory:"

    mocked_locate_db = mocker.patch("firefox_bookmarks.connect.locate_db")
    mocked_locate_db.side_effect = mock

    return mocked_locate_db


@pytest.fixture
def mock_peewee_connect(mocker: MockerFixture):
    mocked_peewee_connect = mocker.patch.object(SqliteDatabase, "connect")
    return mocked_peewee_connect


# endregion
