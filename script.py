from collections import Counter
from typing import Dict, List, Set, Optional, Any
import re
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1))
def fetch_page(url: str, headers: Dict[str, str], params: Dict[str, int]) -> requests.Response:
    """Fetch a page from the API with retry logic"""
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response


def extract_next_url(link_header: str) -> Optional[str]:
    """Extract next URL from Link header"""
    match = re.search(r'<(\S+)>; rel="next"', link_header, re.IGNORECASE)
    return match.group(1) if match else None


def fetch_events(username: str, headers: Dict[str, str], params: Dict[str, int]) -> List[Dict[str, Any]]:
    """Fetch all events for a user with pagination"""
    url: Optional[str] = f'https://api.github.com/users/{username}/events/public'
    all_events: List[Dict[str, Any]] = []

    while url:
        response = fetch_page(url, headers, params)
        all_events.extend(response.json())
        link_header = response.headers.get('Link', '')
        url = extract_next_url(link_header)

    if not all_events:
        logger.info(f"No events found for user: {username}")

    return all_events


def get_top_activities(events: List[Dict[str, Any]], n: int = 3) -> List[str]:
    """Get top most common activity types"""
    activity_types = [event['type'] for event in events]
    activity_counts = Counter(activity_types)
    return [activity for activity, _ in activity_counts.most_common(n)]


def get_owned_repos(events: List[Dict[str, Any]], username: str, top_activities: List[str]) -> Set[str]:
    """Get unique repos owned by user in top activities"""
    owned_repos: Set[str] = set()

    for event in events:
        repo_name: str = event['repo']['name']
        repo_owner, _, _ = repo_name.partition('/')
        activity_type: str = event['type']

        if repo_owner == username and activity_type in top_activities:
            owned_repos.add(repo_name)

    return owned_repos


def flag_repos(username: str) -> Set[str]:
    """Main function to analyze user's GitHub activity.

    Endpoint docs: https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-public-events-for-a-user
    """
    headers: Dict[str, str] = {
        'accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    params: Dict[str, int] = {'per_page': 100}

    all_events = fetch_events(username, headers, params)
    top_3_activities = get_top_activities(all_events, 3)
    return get_owned_repos(all_events, username, top_3_activities)


def main() -> None:
    username = 'torvalds'  # or ge0ffrey
    print(flag_repos(username))


if __name__ == '__main__':
    main()