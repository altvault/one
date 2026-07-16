type Metadata = {
  name: string | undefined;
  bundleIdentifier: string | undefined;
  step_results: unknown;
};

export function parseMetadata(markdownText: string) {
  const match = markdownText.match(/```json\s*([\s\S]*?)\s*```/);
  if (!match) {
    throw new Error("Unable to parse metadata");
  }
  return JSON.parse(match[1]) as Metadata;
}
