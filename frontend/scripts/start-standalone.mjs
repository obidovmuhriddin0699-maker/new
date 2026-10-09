// Runs the production server exactly as the Docker image does (node server.js from the
// Next.js standalone output), after copying the static assets it expects next to it.
// Cross-platform (Windows / Linux). Port: --port <n>, -p <n> or PORT (default 3000).
import { cpSync, existsSync } from "node:fs";
import { spawn } from "node:child_process";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const standalone = join(root, ".next", "standalone");
if (!existsSync(join(standalone, "server.js"))) {
  console.error("Run `npm run build` first (.next/standalone/server.js not found).");
  process.exit(1);
}
cpSync(join(root, ".next", "static"), join(standalone, ".next", "static"), { recursive: true });
cpSync(join(root, "public"), join(standalone, "public"), { recursive: true });

const args = process.argv.slice(2);
const flag = args.findIndex((a) => a === "--port" || a === "-p");
const port = flag >= 0 ? args[flag + 1] : process.env.PORT ?? "3000";
const child = spawn(process.execPath, [join(standalone, "server.js")], {
  stdio: "inherit",
  // Not $HOSTNAME: Linux shells set it to the machine name. BIND_HOST overrides.
  env: { ...process.env, PORT: port, HOSTNAME: process.env.BIND_HOST ?? "0.0.0.0", NODE_ENV: "production" },
});
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => child.kill(signal));
child.on("exit", (code) => process.exit(code ?? 0));
