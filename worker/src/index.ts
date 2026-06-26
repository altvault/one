import { Hono } from "hono";
import { basicAuth } from "hono/basic-auth";
import { createAppAuth } from "@octokit/auth-app";
import { queryReleases } from "./query";
import { AltSourceApp, AltSourceRepo } from "./types";
import { parseMetadata } from "./metadata";

const app = new Hono<{ Bindings: CloudflareBindings }>();

app.use(
  "/*",
  // Basic Auth Middleware
  async (c, next) => {
    if (!c.env.BASICAUTH_USERNAME || !c.env.BASICAUTH_PASSWORD) {
      return c.json({ error: "Server configuration error" }, 500);
    }
    const auth = basicAuth({
      username: c.env.BASICAUTH_USERNAME,
      password: c.env.BASICAUTH_PASSWORD,
    });
    return auth(c, next);
  },
);

app.get("/latest.json", async (c) => {
  if (!c.env.GITHUB_APP_ID || !c.env.GITHUB_APP_PRIVATE_KEY) {
    return c.json({ error: "Server configuration error" }, 500);
  }
  const appAuth = createAppAuth({
    appId: c.env.GITHUB_APP_ID,
    privateKey: c.env.GITHUB_APP_PRIVATE_KEY,
  });

  const { token } = await appAuth({
    type: "installation",
    installationId: c.env.GITHUB_APP_INSTALLATION_ID,
  });
  if (!token) {
    return c.json({ error: "Server configuration error" }, 500);
  }

  const queryResult = await queryReleases(token);

  const altSourceApps: Array<AltSourceApp> = [];

  if (queryResult.data?.search) {
    for (const release of queryResult.data?.search.nodes) {
      if (release.latestRelease) {
        const metadata = parseMetadata(release.latestRelease.description);

        for (const asset of release.latestRelease.releaseAssets.nodes) {
          const name = metadata.name || "";
          const bundleIdentifier = metadata.bundleIdentifier || "";

          altSourceApps.push({
            name: name,
            bundleIdentifier: bundleIdentifier,
            version: release.latestRelease.tagName,
            localizedDescription: asset.name,
            downloadURL: asset.url,
            iconURL: new URL(`/icon/${name}.jpg`, c.req.url).toString(),
            versionDate: asset.createdAt,
            size: asset.size,
          });
        }
      }
    }
  }

  const altSourceRepo: AltSourceRepo = {
    name: "AltVault",
    identifier: "altvault.latest",
    iconURL: new URL("/icon.png", c.req.url).toString(),
    apps: altSourceApps,
  };

  return c.json(altSourceRepo);
});

export default app;
