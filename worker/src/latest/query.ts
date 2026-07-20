import globals from "../../../globals.json";
import { queryGithub } from "../graphql";

type QueryResponse = {
  search: {
    nodes: Array<{
      name: string;
      latestRelease: {
        tagName: string;
        releaseAssets: {
          nodes: Array<{
            name: string;
            size: number;
            createdAt: string;
          }>;
        };
        description: string;
      };
    }>;
  };
};

export async function query({ token }: { token: string }) {
  return queryGithub<QueryResponse>({
    token,
    query: `
query ($searchQuery: String!) {
  search(query: $searchQuery, type: REPOSITORY, first: 30) {
    nodes {
      ... on Repository {
        name
        latestRelease {
          tagName
          releaseAssets(first: 20) {
            nodes {
              name
              size
              createdAt
            }
          }
          description
        }
      }
    }
  }
}`,
    variables: {
      searchQuery: `org:${globals.owner} topic:tweaked-ipas archived:false`,
    },
  });
}
