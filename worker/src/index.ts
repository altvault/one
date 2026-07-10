import { Hono } from "hono";
import { basicAuth } from "hono/basic-auth";
import { createAppAuth } from "@octokit/auth-app";
import { queryReleases } from "./query";
import { AltSourceApp, AltSourceRepo } from "./types";
import { parseMetadata } from "./metadata";
import globals from "../../globals.json";

const app = new Hono<{
  Bindings: CloudflareBindings;
  Variables: {
    token: string;
  };
}>();

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
  // GitHub App Token
  async (c, next) => {
    // if (!c.env.GITHUB_APP_ID || !c.env.GITHUB_APP_PRIVATE_KEY) {
    //   return c.json({ error: "Server configuration error" }, 500);
    // }
    // const appAuth = createAppAuth({
    //   appId: c.env.GITHUB_APP_ID,
    //   privateKey: c.env.GITHUB_APP_PRIVATE_KEY,
    // });
    //
    // const { token } = await appAuth({
    //   type: "installation",
    //   installationId: c.env.GITHUB_APP_INSTALLATION_ID,
    // });
    // if (!token) {
    //   return c.json({ error: "Server configuration error" }, 500);
    // }
    // c.set("token", token)
    c.set("token", "###########################");
    await next();
  },
);

app.get("/download/:repo/:tag/:name", async (c) => {
  const { repo, tag, name } = c.req.param();
  const token = c.get("token");
  const downloadUrl = `https://github.com/${globals.owner}/${repo}/releases/download/${encodeURIComponent(tag)}/${encodeURIComponent(name)}`;
  const response = await fetch(downloadUrl, {
    method: "GET",
    headers: {
      Accept: "application/octet-stream",
      Authorization: `Bearer ${token}`,
      "User-Agent": "Worker",
    },
    redirect: "manual",
  });
  const location = response.headers.get("Location");
  if (location) {
    return c.redirect(location, 302);
  }
  return c.text(
    `Error\n${JSON.stringify(
      Object.fromEntries(response.headers.entries()),
      null,
      2,
    )}\n${await response.text()}`,
  );
});

app.get("/latest.json", async (c) => {
  const token = c.get("token");
  const queryResult = await queryReleases(token);

  const altSourceApps: Array<AltSourceApp> = [];

  if (queryResult.data?.search) {
    for (const repo of queryResult.data?.search.nodes) {
      if (repo.latestRelease) {
        const metadata = parseMetadata(repo.latestRelease.description);

        for (const asset of repo.latestRelease.releaseAssets.nodes) {
          const name = metadata.name || "";
          const bundleIdentifier = metadata.bundleIdentifier || "";

          altSourceApps.push({
            name: `${name} (${repo.name.replace("files-", "")})`,
            bundleIdentifier: bundleIdentifier,
            version: repo.latestRelease.tagName,
            localizedDescription: asset.name,
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
