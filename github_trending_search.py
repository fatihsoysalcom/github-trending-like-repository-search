import requests
import os
import datetime

# --- Configuration ---
# You can get a personal access token from https://github.com/settings/tokens
# It's recommended to set this as an environment variable for security.
# For this example, it's optional, but unauthenticated requests have lower rate limits.
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# --- GitHub API Endpoint ---
GITHUB_SEARCH_REPOS_URL = "https://api.github.com/search/repositories"

def get_trending_like_repos(
    language="python",
    min_stars=50,
    sort_by="stars",
    order="desc",
    timeframe="weekly", # Options: 'daily', 'weekly', 'monthly', 'all_time'
    per_page=10
):
    """
    Fetches repositories from GitHub that are 'trending-like' based on stars and recent activity.
    This simulates the discovery aspect of GitHub Trending using the GitHub Search API.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    # Calculate date for 'created' or 'pushed' query to simulate trending timeframes
    date_query = ""
    if timeframe == "daily":
        date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        date_query = f"created:>={date}"
    elif timeframe == "weekly":
        date = (datetime.date.today() - datetime.timedelta(weeks=1)).isoformat()
        date_query = f"created:>={date}"
    elif timeframe == "monthly":
        date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
        date_query = f"created:>={date}"
    # For 'all_time', we don't add a date query, just rely on min_stars and sort_by

    # Construct the query string
    # The article discusses discovering talent and projects. Searching by language
    # and stars helps identify impactful projects and the developers behind them.
    query_parts = []
    if language:
        query_parts.append(f"language:{language}")
    if min_stars:
        query_parts.append(f"stars:>={min_stars}")
    if date_query:
        query_parts.append(date_query)

    q_param = " ".join(query_parts) if query_parts else ""

    params = {
        "q": q_param,
        "sort": sort_by,
        "order": order,
        "per_page": per_page
    }

    print(f"Searching GitHub with query: '{q_param}' sorted by '{sort_by}' ({order})...\n")

    try:
        response = requests.get(GITHUB_SEARCH_REPOS_URL, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repositories: {e}")
        if response.status_code == 403 and "rate limit exceeded" in response.text.lower():
            print("You might have hit the GitHub API rate limit. Consider setting a GITHUB_TOKEN environment variable.")
        return []


def main():
    print("--- Discovering GitHub Projects (Trending-like) ---")

    # Example 1: Top Python projects created in the last week with at least 100 stars
    print("\n--- Top Python Projects (Weekly Trending-like, >=100 stars) ---")
    python_repos = get_trending_like_repos(
        language="python",
        min_stars=100,
        timeframe="weekly",
        per_page=5
    )
    if python_repos:
        for i, repo in enumerate(python_repos):
            print(f"  {i+1}. {repo['full_name']} (Stars: {repo['stargazers_count']})")
            print(f"     URL: {repo['html_url']}")
            print(f"     Description: {repo['description'] or 'N/A'}\n")
    else:
        print("  No Python repositories found matching criteria.")

    # Example 2: Top JavaScript projects of all time with at least 5000 stars
    print("\n--- Top JavaScript Projects (All Time, >=5000 stars) ---")
    js_repos = get_trending_like_repos(
        language="javascript",
        min_stars=5000,
        timeframe="all_time",
        per_page=5
    )
    if js_repos:
        for i, repo in enumerate(js_repos):
            print(f"  {i+1}. {repo['full_name']} (Stars: {repo['stargazers_count']})")
            print(f"     URL: {repo['html_url']}")
            print(f"     Description: {repo['description'] or 'N/A'}\n")
    else:
        print("  No JavaScript repositories found matching criteria.")

    # Example 3: Recently updated Go projects with at least 50 stars (simulating recent activity)
    print("\n--- Recently Updated Go Projects (>=50 stars) ---")
    go_repos = get_trending_like_repos(
        language="go",
        min_stars=50,
        sort_by="updated", # Sorting by 'updated' helps find recently active projects
        timeframe="weekly",
        per_page=3
    )
    if go_repos:
        for i, repo in enumerate(go_repos):
            print(f"  {i+1}. {repo['full_name']} (Stars: {repo['stargazers_count']}, Last Updated: {repo['updated_at']})")
            print(f"     URL: {repo['html_url']}")
            print(f"     Description: {repo['description'] or 'N/A'}\n")
    else:
        print("  No Go repositories found matching criteria.")


if __name__ == "__main__":
    # Ensure 'requests' library is installed. If not, run: pip install requests
    # This script uses standard Python libraries + 'requests'.
    main()
