from pprint import pprint

from altvault.github import create_github_client

gh = create_github_client()

q1 = """
query {
  q0: repository(owner: "altvault", name: "Apollo-Reborn") {
    nameWithOwner
    defaultBranchRef {
      name
    }
    parent {
      nameWithOwner
      defaultBranchRef {
        name
      }
    }
  }
  q1: repository(owner: "Apollo-Reborn", name: "Apollo-Reborn") {
    ref(qualifiedName: "main") {
      compare(headRef: "altvault:main") {
        status
        aheadBy
        behindBy
      }
    }
  }
  q2: repository(owner: "altvault", name: "PoomSmart.github.io") {
    ref(qualifiedName: "main") {
      compare(headRef: "poomsmart:main") {
        status
        aheadBy
        behindBy
        commits (first: 100) {
          nodes {
            message
          }
          totalCount
        }
      }
    }
  }
}
"""

q2 = """
query {
  q1: repository(owner: "altvault", name: "MyYouTube-ipas") {
    latestRelease {
      tag {
        name
      }
      releaseAssets(first: 100) {
        totalCount
        nodes {
          id
          name
          downloadUrl
        }
      }
    }
  }
}
"""

a = gh.graphql.request(q2)

pprint(a)
