import pytest
from script import extract_next_url

def test_extract_next_url_found():
    link = '<https://api.github.com/page2>; rel="next"'
    assert extract_next_url(link) == 'https://api.github.com/page2'