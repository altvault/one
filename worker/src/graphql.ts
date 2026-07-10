async function graphqlQuery({
  token,
  query,
  variables,
}: {
  token: string;
  query: string;
  variables: { [name: string]: unknown };
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
  const result = (await response.json()) as GithubErrorResponse;
  if (result.errors && result.errors.length > 0) {
    throw new Error(result.errors[0].message);
  }
  return result;
}
