import pytest
from pytest_mock import MockerFixture

from firefox_bookmarks import ProfileCriterion, locate_db


class TestLocate:

    def test_calls_locate_db_candidates(self, mock_locate_db_candidates):
        my_path = "/this/is/a/path"
        my_criterion = ProfileCriterion.LARGEST

        _ = locate_db(look_under_path=my_path, criterion=my_criterion)

        mock_locate_db_candidates \
            .assert_called_once_with(look_under_path=my_path)

    @pytest.mark.usefixtures("mock_locate_db_candidates")
    def test_returns_on_fail(self):
        db_path = locate_db()

        assert db_path == ":("

    # TODO
    pass


class TestLocateCandidates:
    # TODO
    pass


# region FIXTURES


@pytest.fixture
def mock_locate_db_candidates(mocker: MockerFixture):

    def mock(*args, **kwargs):
        return []

    mocked_func = mocker.patch("firefox_bookmarks.locate.locate_db_candidates")
    mocked_func.side_effect = mock

    return mocked_func


# endregion
