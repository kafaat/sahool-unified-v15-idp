/**
 * CLI argument parser for the code review agent.
 *
 * Hand-rolled (no dependencies) so the service stays dependency-free.
 * Extracted into its own module so it can be unit tested directly.
 */

export type OutputFormat = "json" | "markdown" | "sarif";
export type Model = "opus" | "sonnet" | "haiku";

export interface ParsedCli {
  /** Directory to review. */
  repo: string;
  /** Output file path, or undefined for stdout. */
  output?: string;
  /** Output format. */
  format: OutputFormat;
  /** Whether to enable subagents. */
  useSubagents: boolean;
  /** Claude model to use. */
  model: Model;
  /** Maximum number of turns. */
  maxTurns: number;
  /** If true, the CLI should print help text and exit 0. */
  help: boolean;
  /** Deprecation warnings accumulated during parsing. */
  deprecations: string[];
}

export const CLI_USAGE = `Usage: code-review-agent [options] [<repo>]

Options:
  --repo <path>              Directory to review (alias for positional arg, default: ".")
  --directory <path>         Alias of --repo
  --output <file>            Write report to <file> instead of stdout
  --format <fmt>             Output format: json | markdown | sarif (default: json)
  --model <name>             Model: opus | sonnet | haiku (default: opus)
  --max-turns <n>            Maximum agent turns (default: 250)
  --no-subagents             Disable specialized subagents
  --sarif                    [DEPRECATED] Alias for --format sarif
  --markdown                 [DEPRECATED] Alias for --format markdown
  -h, --help                 Show this help text

Environment variables:
  AUDIT_REVIEW_TIMEOUT_MS    Review timeout in milliseconds (default: 600000)
  LOG_FORMAT                 "json" for structured logs, otherwise pretty
  LOG_LEVEL                  "info" | "warn" | "error" (default: info)
`;

const VALID_FORMATS = new Set<OutputFormat>(["json", "markdown", "sarif"]);
const VALID_MODELS = new Set<Model>(["opus", "sonnet", "haiku"]);

/**
 * Pulls the value for a flag that accepts `--flag value` or `--flag=value`.
 * Returns the value (possibly empty string) or undefined if the token is
 * malformed. Advances the caller's index via the returned `consumed` count.
 */
function takeValue(
  args: string[],
  idx: number,
  name: string,
): { value: string; consumed: number } {
  const tok = args[idx];
  const eq = tok.indexOf("=");
  if (eq !== -1) {
    return { value: tok.slice(eq + 1), consumed: 1 };
  }
  const next = args[idx + 1];
  if (next === undefined || next.startsWith("--")) {
    throw new Error(`Flag ${name} requires a value`);
  }
  return { value: next, consumed: 2 };
}

/**
 * Parses argv tokens (excluding `node` and script name).
 *
 * Throws on invalid combinations (unknown flags, invalid enum values,
 * missing values). Callers should catch and translate to exit code 2.
 */
export function parseArgs(argv: string[]): ParsedCli {
  const parsed: ParsedCli = {
    repo: ".",
    format: "json",
    useSubagents: true,
    model: "opus",
    maxTurns: 250,
    help: false,
    deprecations: [],
  };

  let positional: string | undefined;
  let repoExplicit = false;
  let i = 0;

  while (i < argv.length) {
    const arg = argv[i];

    if (arg === "-h" || arg === "--help") {
      parsed.help = true;
      return parsed;
    }

    if (arg === "--no-subagents") {
      parsed.useSubagents = false;
      i += 1;
      continue;
    }

    if (arg === "--sarif") {
      parsed.format = "sarif";
      parsed.deprecations.push(
        "--sarif is deprecated; use --format sarif instead",
      );
      i += 1;
      continue;
    }

    if (arg === "--markdown") {
      parsed.format = "markdown";
      parsed.deprecations.push(
        "--markdown is deprecated; use --format markdown instead",
      );
      i += 1;
      continue;
    }

    if (arg === "--repo" || arg.startsWith("--repo=")) {
      const { value, consumed } = takeValue(argv, i, "--repo");
      parsed.repo = value;
      repoExplicit = true;
      i += consumed;
      continue;
    }

    if (arg === "--directory" || arg.startsWith("--directory=")) {
      const { value, consumed } = takeValue(argv, i, "--directory");
      parsed.repo = value;
      repoExplicit = true;
      i += consumed;
      continue;
    }

    if (arg === "--output" || arg.startsWith("--output=")) {
      const { value, consumed } = takeValue(argv, i, "--output");
      parsed.output = value;
      i += consumed;
      continue;
    }

    if (arg === "--format" || arg.startsWith("--format=")) {
      const { value, consumed } = takeValue(argv, i, "--format");
      if (!VALID_FORMATS.has(value as OutputFormat)) {
        throw new Error(
          `Invalid --format "${value}" (expected: json | markdown | sarif)`,
        );
      }
      parsed.format = value as OutputFormat;
      i += consumed;
      continue;
    }

    if (arg === "--model" || arg.startsWith("--model=")) {
      const { value, consumed } = takeValue(argv, i, "--model");
      if (!VALID_MODELS.has(value as Model)) {
        throw new Error(
          `Invalid --model "${value}" (expected: opus | sonnet | haiku)`,
        );
      }
      parsed.model = value as Model;
      i += consumed;
      continue;
    }

    if (arg === "--max-turns" || arg.startsWith("--max-turns=")) {
      const { value, consumed } = takeValue(argv, i, "--max-turns");
      const n = Number.parseInt(value, 10);
      if (!Number.isFinite(n) || n <= 0) {
        throw new Error(`Invalid --max-turns "${value}" (expected positive integer)`);
      }
      parsed.maxTurns = n;
      i += consumed;
      continue;
    }

    if (arg.startsWith("--")) {
      throw new Error(`Unknown flag: ${arg}`);
    }

    // Positional: first one wins, treated as repo path.
    if (positional === undefined) {
      positional = arg;
      i += 1;
      continue;
    }

    throw new Error(`Unexpected positional argument: ${arg}`);
  }

  // Positional is the legacy form (args[0] was the directory). Explicit --repo
  // or --directory always wins.
  if (positional !== undefined && !repoExplicit) {
    parsed.repo = positional;
  }

  return parsed;
}
