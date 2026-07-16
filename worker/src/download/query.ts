import globals from "../../../globals.json";
import { queryGithub } from "../graphql";

type QueryResponse = {
  repository: {
    release: {
      releaseAssets: {
        nodes: {
          url: string;
        }[];
      };
    };
  };
};

export async function query({
  token,
  repo,
  tagName,
  assetName,
}: {
  token: string;
  repo: string;
  tagName: string;
  assetName: string;
}) {
  return queryGithub<QueryResponse>({
    token,
    query: `
query ($owner: String!, $repo: String!, $tagName: String!, $assetName: String!, $firstAssets: Int = 1) {
  repository(name: $repo, owner: $owner) {
    release(tagName: $tagName) {
      releaseAssets(first: $firstAssets, name: $assetName) {
        nodes {
          url
        }
      }
    }
  }
}
`,
    variables: { owner: globals.owner, repo, tagName, assetName },
  });
}
