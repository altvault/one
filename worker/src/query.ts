import globals from "../../globals.json";

type GithubSearchResponse = {
  data?: {
    search: {
      nodes: Array<{
        latestRelease: {
          tagName: string;
          releaseAssets: {
            nodes: Array<{
              name: string;
              size: number;
              createdAt: string;
              url: string;
            }>;
          };
          description: string;
        };
      }>;
    };
  } | null;
  errors?: Array<{
    message: string;
    locations?: Array<{
      line: number;
      column: number;
    }>;
    path?: Array<string | number>;
    extensions?: Record<string, unknown>;
  }>;
};

const query = `query ($searchQuery: String!) {
  search(query: $searchQuery, type: REPOSITORY, first: 100) {
    nodes {
      ... on Repository {
        latestRelease {
          tagName
          releaseAssets(first: 100) {
            nodes {
              name
              size
              createdAt
              url
            }
          }
          description
        }
      }
    }
  }
}`;

const variables = {
  searchQuery: `org:${globals.owner} topic:tweaked-ipas archived:false`,
};

export async function queryReleases(token: string) {
  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "User-Agent": "Worker",
    },
    body: JSON.stringify({ query, variables }),
  });
  const result = (await response.json()) as GithubSearchResponse;
  if (result.errors && result.errors.length > 0) {
    throw new Error(result.errors[0].message);
  }
  return result;
}
