import { factory } from "./types";
import { basicAuth } from "hono/basic-auth";
import { createAppAuth } from "@octokit/auth-app";

export const basicAuthMiddleware = factory.createMiddleware(async (c, next) => {
  if (!c.env.BASICAUTH_USERNAME || !c.env.BASICAUTH_PASSWORD) {
    return c.json({ error: "Server configuration error" }, 500);
  }
  const auth = basicAuth({
    username: c.env.BASICAUTH_USERNAME,
    password: c.env.BASICAUTH_PASSWORD,
  });
  return auth(c, next);
});

export const githubTokenMiddleware = factory.createMiddleware(
  async (c, next) => {
    if (c.get("github_token")) {
      return await next();
    }

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
    c.set("github_token", token);

    return await next();
  },
);
