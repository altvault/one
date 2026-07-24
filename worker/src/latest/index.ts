import { AltSourceApp, AltSourceRepo, factory } from "../types";
import { query } from "./query";
import { parseMetadata } from "./metadata";

const app = factory.createApp();

const formatter = new Intl.DateTimeFormat("en-TH", {
  timeZone: "Asia/Bangkok",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
});

app.get("/", async (c) => {
  const queryResult = await query({ token: c.get("github_token") });

  const altSourceApps: Array<AltSourceApp> = [];

  if (queryResult.data?.search) {
    for (const repo of queryResult.data?.search.nodes) {
      if (repo.latestRelease) {
        const metadata = parseMetadata(repo.latestRelease.description);

        for (const asset of repo.latestRelease.releaseAssets.nodes) {
          if (asset.name.endsWith(".ipa")) {
            const name = metadata.name || "";
            const bundleIdentifier = metadata.bundleIdentifier || "";

            altSourceApps.push({
              name: `${name} (${repo.name.replace("files-", "")})`,
              bundleIdentifier: bundleIdentifier,
              version: repo.latestRelease.tagName,
              // subtitle: asset.name,
              localizedDescription: `${asset.name}${asset.createdAt
                  ? "\n" + formatter.format(new Date(asset.createdAt))
                  : ""
                }`,
              // downloadURL: asset.url,
              downloadURL: new URL(
                `/download/${repo.name}/${repo.latestRelease.tagName}/${asset.name}`,
                c.req.url,
              ).toString(),
              iconURL: new URL(`/icon/${name}.jpg`, c.req.url).toString(),
              versionDate: asset.createdAt,
              size: asset.size,
            });
          }
        }
      }
    }
  }

  altSourceApps.sort((a, b) => b.versionDate.localeCompare(a.versionDate)); // desc

  const altSourceRepo: AltSourceRepo = {
    name: "AltVault",
    identifier: "altvault.latest",
    iconURL: new URL("/icon.png", c.req.url).toString(),
    apps: altSourceApps,
  };

  return c.json(altSourceRepo);
});

export default app;
