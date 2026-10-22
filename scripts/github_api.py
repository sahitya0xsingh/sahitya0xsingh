"""Tiny GitHub GraphQL client (stdlib only)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

API = "https://api.github.com/graphql"

QUERY = """
query($login: String!, $prq: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    recent: repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 30,
                         orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name description url isFork isArchived stargazerCount pushedAt
        primaryLanguage { name }
        defaultBranchRef { target { ... on Commit { history { totalCount } } } }
      }
    }
  }
  search(query: $prq, type: ISSUE, first: 8) {
    issueCount
    nodes { ... on PullRequest { title url mergedAt repository { nameWithOwner } } }
  }
}
"""


def _post(body: dict) -> dict:
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        raise RuntimeError("GITHUB_TOKEN is not set")
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {tok}", "Content-Type": "application/json",
        "User-Agent": "terminal-profile",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GraphQL HTTP {e.code}: {e.read()[:300]!r}") from e
    if out.get("errors"):
        raise RuntimeError(f"GraphQL errors: {out['errors']}")
    return out["data"]


def fetch_stats(login: str) -> dict:
    d = _post({"query": QUERY, "variables": {
        "login": login,
        "prq": f"is:pr is:merged author:{login} -user:{login} sort:updated-desc",
    }})
    u = d["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [{"date": x["date"], "count": x["contributionCount"]}
            for w in cal["weeks"] for x in w["contributionDays"]]
    repos = []
    for r in u["recent"]["nodes"]:
        if r["isArchived"]:
            continue
        try:
            commits = r["defaultBranchRef"]["target"]["history"]["totalCount"]
        except (TypeError, KeyError):
            commits = 0
        repos.append({
            "name": r["name"], "url": r["url"], "desc": r["description"] or "",
            "stars": r["stargazerCount"], "pushed": r["pushedAt"], "fork": r["isFork"],
            "lang": (r["primaryLanguage"] or {}).get("name") or "—", "commits": commits,
        })
    prs = [{"title": n["title"], "url": n["url"], "merged": n["mergedAt"],
            "repo": n["repository"]["nameWithOwner"]}
           for n in d["search"]["nodes"] if n]
    return {"login": login, "days": days, "total": cal["totalContributions"], "repos": repos,
            "prs": prs, "pr_count": d["search"]["issueCount"],
            "repo_count": u["repositories"]["totalCount"],
            "followers": u["followers"]["totalCount"], "demo": False}
