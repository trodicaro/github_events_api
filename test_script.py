import pytest
from unittest.mock import Mock, patch

from script import (extract_next_url, get_top_activities, get_owned_repos, fetch_events, flag_repos)

@pytest.fixture
def sample_events():
    return [
        {'type': 'PushEvent', 'repo': {'name': 'user/repo1'}},
        {'type': 'PushEvent', 'repo': {'name': 'user/repo2'}},
        {'type': 'IssuesEvent', 'repo': {'name': 'other/repo3'}},
    ]


# extract_next_url tests
@pytest.mark.parametrize("link_header,expected", [
    ('<https://api.github.com/page2>; rel="next"', 'https://api.github.com/page2'),
    ('<https://api.github.com/page1>; rel="prev"', None),
    ('<https://api.github.com/page2>; rel="Next"', 'https://api.github.com/page2'),
    ('', None),
])
def test_extract_next_url(link_header, expected):
    assert extract_next_url(link_header) == expected


# fetch_events tests with mocking
@patch('script.fetch_page')
def test_fetch_events_single_page(mock_fetch):
    mock_response = Mock()
    mock_response.json.return_value = [{'type': 'PushEvent'}]
    mock_response.headers.get.return_value = ''
    mock_fetch.return_value = mock_response
    # print('test', mock_fetch.call_args)
    events = fetch_events('user', {}, {})
    assert len(events) == 1
    assert mock_fetch.call_count == 1

@patch('script.fetch_page')
def test_fetch_events_multiple_pages(mock_fetch):
    mock_response1 = Mock()
    mock_response1.json.return_value = [{'type': 'PushEvent'}]
    mock_response1.headers.get.return_value = '<https://api.github.com/page2>; rel="next"'

    mock_response2 = Mock()
    mock_response2.json.return_value = [{'type': 'IssuesEvent'}]
    mock_response2.headers.get.return_value = ''

    mock_fetch.side_effect = [mock_response1, mock_response2]

    events = fetch_events('user', {}, {})
    assert len(events) == 2
    assert mock_fetch.call_count == 2


# get_top_activities tests
@pytest.mark.parametrize("events,expected", [
    ([{'type': 'Push'}, {'type': 'Push'}, {'type': 'Issue'}], ['Push', 'Issue']),
    ([{'type': 'Push'}], ['Push']),
    ([{'type': 'A'}, {'type': 'B'}, {'type': 'C'}, {'type': 'D'}], ['A', 'B', 'C']),
])
def test_get_top_activities(events, expected):
    assert get_top_activities(events, 3) == expected


# get_owned_repos tests
@pytest.mark.parametrize("username,top_activities,expected", [
    ('user', ['PushEvent'], {'user/repo1', 'user/repo2'}),
    ('user', ['IssuesEvent'], set()),
    ('user', ['ForkEvent'], set()),
    ('other', ['IssuesEvent'], {'other/repo3'}),
    ('user', ['PushEvent', 'IssuesEvent'], {'user/repo1', 'user/repo2'}),
])
def test_get_owned_repos(sample_events, username, top_activities, expected):
    result = get_owned_repos(sample_events, username, top_activities)
    assert result == expected


# flag_repos tests
def test_flag_repos_success_single_page(mocker, sample_events):
    mock_fetch = mocker.patch('script.fetch_page')
    mock_response = Mock()
    mock_response.json.return_value = sample_events
    mock_response.headers.get.return_value = ''
    mock_fetch.return_value = mock_response

    repos = flag_repos('user')
    assert repos == {'user/repo1', 'user/repo2'}
    assert mock_fetch.call_count == 1

def test_flag_repos_success_multiple_pages(mocker, sample_events):
    mock_fetch = mocker.patch('script.fetch_page')
    
    mock_response1 = Mock()
    mock_response1.json.return_value = sample_events
    mock_response1.headers.get.return_value = '<https://api.github.com/page2>; rel="next"'
    
    mock_response2 = Mock()
    mock_response2.json.return_value = [{'type': 'IssuesEvent', 'repo': {'name': 'user/repo3'}}]
    mock_response2.headers.get.return_value = ''
    
    mock_fetch.side_effect = [mock_response1, mock_response2]

    repos = flag_repos('user')
    assert repos == {'user/repo1', 'user/repo2', 'user/repo3'}
    assert mock_fetch.call_count == 2

def test_flag_repos_no_events(mocker):
    mock_fetch = mocker.patch('script.fetch_page')
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_response.headers.get.return_value = ''
    mock_fetch.return_value = mock_response

    repos = flag_repos('user')
    assert repos == set()
    assert mock_fetch.call_count == 1

def test_flag_repos_nonexistent_user(mocker):
    mock_fetch = mocker.patch('script.fetch_page')
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_response.headers.get.return_value = ''
    mock_fetch.return_value = mock_response

    repos = flag_repos('nonexistentuser')
    assert repos == set()
    assert mock_fetch.call_count == 1

def test_flag_repos_api_failure(mocker):
    mock_fetch = mocker.patch('script.fetch_page')
    mock_fetch.side_effect = Exception("API failure")

    with pytest.raises(Exception) as excinfo:
        flag_repos('user')
    assert "API failure" in str(excinfo.value)
    assert mock_fetch.call_count == 1