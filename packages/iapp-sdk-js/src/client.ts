/**
 * iApp AI SDK — client core.
 *
 * Mirrors the Python SDK (`iapp_ai`): construct with an API key, then call
 * one method per API endpoint. Each method returns the parsed response.
 *
 * NOTE: This is the Phase 1 scaffold. The request core (Phase 2) and the
 * ~58 API methods (Phase 3) are not implemented yet.
 */

export interface IAppOptions {
  /** Override the API base URL. Defaults to https://api.iapp.co.th */
  baseUrl?: string;
  /** Per-request timeout in milliseconds. Defaults to 60000. */
  timeoutMs?: number;
}

export const DEFAULT_BASE_URL = "https://api.iapp.co.th";

export class IApp {
  readonly apiKey: string;
  readonly baseUrl: string;
  readonly timeoutMs: number;

  constructor(apiKey: string, options: IAppOptions = {}) {
    if (!apiKey) {
      throw new Error("IApp: apiKey is required");
    }
    this.apiKey = apiKey;
    this.baseUrl = options.baseUrl ?? DEFAULT_BASE_URL;
    this.timeoutMs = options.timeoutMs ?? 60000;
  }

  // --- API methods are added in Phase 3 ---
}
