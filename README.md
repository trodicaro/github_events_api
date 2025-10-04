# GitHub Repository Activity Analysis Script

## Overview
This script fetches __public__ events for a specified GitHub user using the GitHub Events API (`/users/{username}/events/public`), identifies the top 3 most frequent activity types, and lists repositories owned by the user that have at least one of these activity types. 

- **Recent Activity**:
  - Assumption As “recent activity” is undefined, the script uses the GitHub Events API’s default, covering up to 300 events from the last 90 days.
  - Limitation: This limit may miss activity for highly active users. Historical data requires alternative sources as noted below.
  - Question:  Should the script filter events to a narrower time window (eg: last 7 days) or use alternative sources for historical data - listed below?

    #### _Alternative Data Sources for historical or more granular data_:
    - [GH Archive](https://www.gharchive.org/): Public GitHub activity since 2011-02-12 for historical analysis.
    - [GitHub GraphQL API](https://docs.github.com/en/graphql/guides/introduction-to-graphql): Custom queries for user contributions.
    - GitHub Search API:
      - `search/commits`: filter commits by date (`committer-date:>=2025-09-01`).
      - `search/issues`: filter issues by user (`author:torvalds type:pr is:merged`).

- **Repository Ownership**:
  - Assumption: Only includes repositories owned by the user due to the use of the user-specifc end-point
  - Limitation: Excludes repositories where the user contributes as a collaborator.
  - Question: Should flagging include non-owned repositories where the user contributes?

- **Flagging**:
  - Assumption: As "flagging" is undefined, the script collects repository names into a set for repositories with events in the top 3 activity types.
  - Limitation: Unclear directions as to how to implement flagging.
  - Question: Should repos be flagged only if the user owns them, or also only if they're part of the top 3 activity types?; should it produce a specific output or actions on flagged repos?

- **Activity Types**:
  - Assumption: Dynamically selects the top 3 most frequent event types.
  - Limitation: Treats all activity types equally, which may not reflect their significance.
  - Question: please see below proposed features for activity measurement 

    #### _Proposed Features_:
    To enhance the script’s utility, please provide feedback on these potential additions:
    1. Assign weights to activity types (eg: `PushEvent: 3`, `PullRequestEvent: 2`, `CreateEvent: 1`) to prioritize significant actions.
    2. Filter events by a custom time window to focus on recent activity.
    3. Assign higher weights to newer events to emphasize current activity.

## To run the project:
```
pipenv shell
pipenv sync # if .lock file doesn't exit run pipenv install --dev
```