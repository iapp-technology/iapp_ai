#!/usr/bin/env node
/**
 * npm wrapper for the iApp AI MCP server.
 *
 * The actual server is a Python package (`iapp-ai` on PyPI). This wrapper
 * launches it via `uvx`, which fetches and runs the package automatically.
 * Requires uv: https://docs.astral.sh/uv/getting-started/installation/
 */
"use strict";

const { spawn } = require("node:child_process");

const child = spawn("uvx", ["iapp-ai", ...process.argv.slice(2)], {
  stdio: "inherit",
  env: process.env,
});

child.on("error", (err) => {
  if (err.code === "ENOENT") {
    console.error(
      [
        "iapp-ai: `uvx` was not found on your PATH.",
        "",
        "The iApp AI MCP server runs on Python and is launched through uv.",
        "Install uv first (one-time, ~10 seconds):",
        "",
        "  curl -LsSf https://astral.sh/uv/install.sh | sh",
        "",
        "or with Homebrew:",
        "",
        "  brew install uv",
        "",
        "then re-run this command. Alternatively, install the server directly",
        "from PyPI with `pip install iapp-ai` and run `iapp-ai`.",
      ].join("\n")
    );
    process.exit(127);
  }
  console.error(`iapp-ai: failed to launch server: ${err.message}`);
  process.exit(1);
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
  } else {
    process.exit(code ?? 0);
  }
});

// Forward termination signals to the child so the MCP server shuts down cleanly.
for (const sig of ["SIGINT", "SIGTERM", "SIGHUP"]) {
  process.on(sig, () => child.kill(sig));
}
