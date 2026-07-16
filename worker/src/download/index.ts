import { HTTPException } from "hono/http-exception";
import { factory } from "../types";
import { query } from "./query";

const app = factory.createApp();

app.get("/:repo/:tagName/:assetName", async (c) => {
  const { repo, tagName, assetName } = c.req.param();
  const queryResult = await query({
    token: c.get("github_token"),
    repo,
    tagName,
    assetName,
  });
  const cdnUrl =
    queryResult.data?.repository.release.releaseAssets.nodes.at(0)?.url;
  if (cdnUrl) {
    return c.redirect(cdnUrl);
  }
  throw new HTTPException(502);
});

export default app;
