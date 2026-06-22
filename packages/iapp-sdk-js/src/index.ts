import { IApp, IAppOptions } from "./client";

export { IApp } from "./client";
export type { IAppOptions } from "./client";
export { DEFAULT_BASE_URL } from "./client";

/**
 * Convenience factory mirroring the Python SDK's `api("KEY")` entry point.
 *
 *   import { api } from "iapp-ai";
 *   const client = api("YOUR_API_KEY");
 */
export function api(apiKey: string, options?: IAppOptions): IApp {
  return new IApp(apiKey, options);
}

export default api;
