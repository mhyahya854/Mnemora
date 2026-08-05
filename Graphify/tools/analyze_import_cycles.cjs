#!/usr/bin/env node
// Resolve local JS/TS module imports with the repository's installed TypeScript compiler.
// Reads codebase; writes only Graphify/IMPORT_CYCLES.json.

const fs = require("node:fs");
const path = require("node:path");
const ts = require(path.resolve(__dirname, "../../codebase/node_modules/typescript"));

const root = path.resolve(__dirname, "../..");
const codebase = path.join(root, "codebase");
const output = path.join(root, "Graphify", "IMPORT_CYCLES.json");
const extensions = new Set([".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]);

function walk(dir, result = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === "build-output") continue;
    const current = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(current, result);
    else if (extensions.has(path.extname(entry.name).toLowerCase())) result.push(path.resolve(current));
  }
  return result;
}

const files = walk(codebase).sort();
const fileSet = new Set(files.map((f) => f.toLowerCase()));
const configPath = ts.findConfigFile(codebase, ts.sys.fileExists, "tsconfig.json");
let options = { allowJs: true, checkJs: false, moduleResolution: ts.ModuleResolutionKind.Node10 };
if (configPath) {
  const config = ts.readConfigFile(configPath, ts.sys.readFile);
  options = { ...options, ...ts.parseJsonConfigFileContent(config.config, ts.sys, path.dirname(configPath)).options };
}
const graph = new Map(files.map((f) => [f, new Set()]));
const unresolvedRelative = [];
const nonCodeAssetReferences = [];
let importCount = 0;

for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  const imports = ts.preProcessFile(text, true, true).importedFiles.map((x) => x.fileName);
  for (const specifier of imports) {
    importCount += 1;
    const resolved = ts.resolveModuleName(specifier, file, options, ts.sys).resolvedModule;
    if (!resolved) {
      if (specifier.startsWith(".")) {
        const exact = path.resolve(path.dirname(file), specifier);
        const evidence = { from: path.relative(root, file).replaceAll("\\", "/"), specifier, target: path.relative(root, exact).replaceAll("\\", "/") };
        if (fs.existsSync(exact) && fs.statSync(exact).isFile()) nonCodeAssetReferences.push(evidence);
        else unresolvedRelative.push(evidence);
      }
      continue;
    }
    const target = path.resolve(resolved.resolvedFileName);
    if (fileSet.has(target.toLowerCase())) graph.get(file).add(files.find((f) => f.toLowerCase() === target.toLowerCase()));
  }
}

let index = 0;
const stack = [];
const onStack = new Set();
const indices = new Map();
const low = new Map();
const components = [];

function strongConnect(v) {
  indices.set(v, index);
  low.set(v, index);
  index += 1;
  stack.push(v);
  onStack.add(v);
  for (const w of graph.get(v)) {
    if (!indices.has(w)) {
      strongConnect(w);
      low.set(v, Math.min(low.get(v), low.get(w)));
    } else if (onStack.has(w)) {
      low.set(v, Math.min(low.get(v), indices.get(w)));
    }
  }
  if (low.get(v) === indices.get(v)) {
    const component = [];
    while (true) {
      const w = stack.pop();
      onStack.delete(w);
      component.push(w);
      if (w === v) break;
    }
    if (component.length > 1 || graph.get(v).has(v)) components.push(component);
  }
}

for (const file of files) if (!indices.has(file)) strongConnect(file);
const relative = (p) => path.relative(root, p).replaceAll("\\", "/");
const result = {
  analyzer: "TypeScript compiler module resolution + Tarjan SCC",
  generated_at: new Date().toISOString(),
  files: files.length,
  import_specifiers: importCount,
  resolved_local_edges: [...graph.values()].reduce((n, values) => n + values.size, 0),
  unresolved_relative_imports: unresolvedRelative,
  non_code_asset_references: nonCodeAssetReferences,
  cycles: components.map((component, i) => ({
    id: `CYCLE-${String(i + 1).padStart(3, "0")}`,
    files: component.map(relative).sort(),
    edges: component.flatMap((from) => [...graph.get(from)].filter((to) => component.includes(to)).map((to) => ({ from: relative(from), to: relative(to) }))),
  })),
};
fs.writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ files: result.files, imports: result.import_specifiers, local_edges: result.resolved_local_edges, unresolved_relative: result.unresolved_relative_imports.length, cycles: result.cycles.length }, null, 2));
