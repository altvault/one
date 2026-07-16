import { factory } from "./types";
import { basicAuthMiddleware, githubTokenMiddleware } from "./auth";
import latestRoutes from "./latest";
import downloadRoutes from "./download";

const app = factory.createApp();

app.use("/*", basicAuthMiddleware, githubTokenMiddleware);

app.route("/latest.json", latestRoutes);

app.route("/download", downloadRoutes);

export default app;
