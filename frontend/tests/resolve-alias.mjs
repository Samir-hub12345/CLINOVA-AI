import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const srcDir = fileURLToPath(new URL("../src/", import.meta.url));

export async function resolve(specifier, context, nextResolve) {
  if (specifier.startsWith("@/")) {
    const subpath = specifier.slice(2);
    let resolvedPath = path.join(srcDir, subpath);
    if (fs.existsSync(resolvedPath) && fs.statSync(resolvedPath).isDirectory()) {
      resolvedPath = path.join(resolvedPath, "index.ts");
    } else if (!fs.existsSync(resolvedPath)) {
      for (const ext of [".ts", ".tsx", ".js", ".json"]) {
        if (fs.existsSync(resolvedPath + ext)) {
          resolvedPath = resolvedPath + ext;
          break;
        }
      }
    }
    return nextResolve(pathToFileURL(resolvedPath).href, context);
  }
  return nextResolve(specifier, context);
}
