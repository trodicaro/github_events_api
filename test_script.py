import pytest
from script import extract_next_url

@pytest.mark.parametrize("link_header,expected", [
    ('<https://api.github.com/page2>; rel="next"', 'https://api.github.com/page2'),
    ('<https://api.github.com/page1>; rel="prev"', None),
    ('<https://api.github.com/page2>; rel="Next"', 'https://api.github.com/page2'),
    ('', None),
])
def test_extract_next_url(link_header, expected):
    assert extract_next_url(link_header) == expected
