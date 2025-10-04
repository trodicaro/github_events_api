from collections import Counter

import re
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1)) # it waits 2^x * 1 second between each retry; min=1 waits 1s to start retries
def fetch_page(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response

def extract_next_url(link_header):
    """Extract next URL from Link header"""
    match = re.search(r'<(\S+)>; rel="next"', link_header, re.IGNORECASE)
    # other regexes considered but seem overkill: r'(?<=<)(\S+)(?=>; rel="next")', r'(?<=<).*?(?=>)' 
    return match and match.group(1)

def fetch_events(username, headers, params):
    """Fetch all events for a user with pagination"""
    url = f'https://api.github.com/users/{username}/events/public'
    all_events = []

    # a more naive pagination using a counter for params['page'] didn't play nicely for non-existent pages
    while url:
        response = fetch_page(url, headers, params)
        all_events.extend(response.json())

        link_header = response.headers.get('Link', '')
        url = extract_next_url(link_header)

    return all_events

def get_top_activities(events, n=3):
    """Get top most common activity types"""
    activity_types = [event['type'] for event in events]
    activity_counts = Counter(activity_types)
    return [activity for activity, _ in activity_counts.most_common(n)]

def get_owned_repos(events, username, top_activities):
    """Get unique repos owned by user in top activities"""
    owned_repos = set()

    for event in events:
        repo_name = event['repo']['name']
        repo_owner, _, _ = repo_name.partition('/')
        activity_type = event['type']

        if repo_owner == username and activity_type in top_activities:
            owned_repos.add(repo_name)

    return owned_repos

def flag_repos(username):
    """Main function to analyze user's GitHub activity.
    Endpoint docs: https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-public-events-for-a-user
    """
    headers = {
        'accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    params = {'per_page': 100}

    all_events = fetch_events(username, headers, params)
    top_3_activities = get_top_activities(all_events, 3)
    return get_owned_repos(all_events, username, top_3_activities)

def main():
    username = 'torvalds' # or ge0ffrey
    print(flag_repos(username))

if __name__ == '__main__':
    main()