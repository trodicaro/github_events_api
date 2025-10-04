from collections import Counter

import re
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1)) # it waits 2^x * 1 second between each retry; min=1 waits 1s to start retries
def fetch_records(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response

# https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-public-events-for-a-user
username = 'torvalds' # or ge0ffrey, octocat, torvalds
url = f'https://api.github.com/users/{username}/events/public'

headers = {
    'accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}
params = {'per_page': 100}

all_events = []

while url:
    response = fetch_records(url, headers=headers, params=params)
    all_events.extend(response.json())
    # a more naive approach using a counter for params['page'] doesn't play nicely for non-existent pages
    link_header = response.headers.get('Link', '')
    match = re.search(r'<(\S+)>; rel="next"', link_header, re.IGNORECASE)
    # other regexes considered but seem overkill: r'(?<=<)(\S+)(?=>; rel="next")', r'(?<=<).*?(?=>)' 
    url = match and match.group(1)

activity_types = [event['type'] for event in all_events]
activity_counts = Counter(activity_types)
top_3_activities = [activity for activity, _ in activity_counts.most_common(3)]
print(top_3_activities)
owned_repos = set()
for event in all_events:
    repo_name = event['repo']['name']
    repo_owner, _, _ = repo_name.partition('/')
    activity_type = event['type']
    created_at = event['created_at']
    if repo_owner == username and activity_type in top_3_activities:
        owned_repos.add(repo_name)
print('\n'.join(f"{repo}" for repo in owned_repos))
