import pytest
from script import (extract_next_url, get_top_activities)

@pytest.mark.parametrize("link_header,expected", [
    ('<https://api.github.com/page2>; rel="next"', 'https://api.github.com/page2'),
    ('<https://api.github.com/page1>; rel="prev"', None),
    ('<https://api.github.com/page2>; rel="Next"', 'https://api.github.com/page2'),
    ('', None),
])
def test_extract_next_url(link_header, expected):
    assert extract_next_url(link_header) == expected

@pytest.mark.parametrize("events,expected", [
    ([{'type': 'Push'}, {'type': 'Push'}, {'type': 'Issue'}], ['Push', 'Issue']),
    ([{'type': 'Push'}], ['Push']),
    ([{'type': 'A'}, {'type': 'B'}, {'type': 'C'}, {'type': 'D'}], ['A', 'B', 'C']),
])
def test_get_top_activities(events, expected):
    assert get_top_activities(events, 3) == expected