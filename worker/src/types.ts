import { createFactory } from "hono/factory";

type HonoAppType = {
  Bindings: CloudflareBindings;
  Variables: {
    github_token: string;
  };
};

export const factory = createFactory<HonoAppType>();

export type AltSourceApp = {
  name: string;
  bundleIdentifier: string;
  version: string;
  localizedDescription: string;
  downloadURL: string;
  iconURL: string;
  versionDate: string;
  size: number;
};

export type AltSourceRepo = {
  name: string;
  identifier: string;
  iconURL: string;
  apps: AltSourceApp[];
};
