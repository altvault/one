type QueryResponse<T> = {
  data?: T | null;
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

export async function queryGithub<T>({
  token,
  query,
  variables,
}: {
  token: string;
  query: string;
  variables?: Record<string, string>;
}) {
  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "User-Agent": "Worker",
    },
    body: JSON.stringify({ query, variables }),
  });
  const result = (await response.json()) as QueryResponse<T>;
  if (result.errors && result.errors.length > 0) {
    throw new Error(result.errors[0].message);
  }
  return result;
}
