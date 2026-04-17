/**
 * Unit tests for src/cli.ts argv parser.
 */

import { describe, expect, it } from "vitest";
import { CLI_USAGE, parseArgs } from "../src/cli.js";

describe("parseArgs defaults", () => {
  it("defaults repo to '.' with no args", () => {
    const p = parseArgs([]);
    expect(p.repo).toBe(".");
    expect(p.format).toBe("json");
    expect(p.model).toBe("opus");
    expect(p.maxTurns).toBe(250);
    expect(p.useSubagents).toBe(true);
    expect(p.output).toBeUndefined();
    expect(p.help).toBe(false);
    expect(p.deprecations).toEqual([]);
  });
});

describe("parseArgs positional & --repo", () => {
  it("reads positional argv[0] as repo", () => {
    expect(parseArgs(["./src"]).repo).toBe("./src");
  });

  it("accepts --repo <path>", () => {
    expect(parseArgs(["--repo", "./foo"]).repo).toBe("./foo");
  });

  it("accepts --repo=<path>", () => {
    expect(parseArgs(["--repo=./bar"]).repo).toBe("./bar");
  });

  it("accepts --directory as an alias of --repo", () => {
    expect(parseArgs(["--directory", "./baz"]).repo).toBe("./baz");
  });

  it("prefers --repo over positional argument", () => {
    expect(parseArgs(["./positional", "--repo", "./explicit"]).repo).toBe(
      "./explicit",
    );
  });

  it("throws on multiple positional arguments", () => {
    expect(() => parseArgs(["./a", "./b"])).toThrow(/positional/);
  });
});

describe("parseArgs --output", () => {
  it("accepts --output <file>", () => {
    expect(parseArgs(["--output", "review.json"]).output).toBe("review.json");
  });

  it("accepts --output=<file>", () => {
    expect(parseArgs(["--output=review.md"]).output).toBe("review.md");
  });

  it("throws when --output is missing a value", () => {
    expect(() => parseArgs(["--output"])).toThrow(/requires a value/);
  });
});

describe("parseArgs --format", () => {
  it("accepts json", () => {
    expect(parseArgs(["--format", "json"]).format).toBe("json");
  });

  it("accepts markdown", () => {
    expect(parseArgs(["--format", "markdown"]).format).toBe("markdown");
  });

  it("accepts sarif", () => {
    expect(parseArgs(["--format=sarif"]).format).toBe("sarif");
  });

  it("rejects unknown formats", () => {
    expect(() => parseArgs(["--format", "xml"])).toThrow(/Invalid --format/);
  });
});

describe("parseArgs --model", () => {
  it("accepts opus", () => {
    expect(parseArgs(["--model", "opus"]).model).toBe("opus");
  });

  it("accepts sonnet", () => {
    expect(parseArgs(["--model", "sonnet"]).model).toBe("sonnet");
  });

  it("accepts haiku", () => {
    expect(parseArgs(["--model=haiku"]).model).toBe("haiku");
  });

  it("rejects unknown models", () => {
    expect(() => parseArgs(["--model", "gpt-5"])).toThrow(/Invalid --model/);
  });
});

describe("parseArgs --max-turns", () => {
  it("parses a positive integer", () => {
    expect(parseArgs(["--max-turns", "100"]).maxTurns).toBe(100);
  });

  it("accepts --max-turns=<n>", () => {
    expect(parseArgs(["--max-turns=42"]).maxTurns).toBe(42);
  });

  it("rejects zero", () => {
    expect(() => parseArgs(["--max-turns", "0"])).toThrow(/Invalid --max-turns/);
  });

  it("rejects negative numbers", () => {
    expect(() => parseArgs(["--max-turns", "-1"])).toThrow(/Invalid --max-turns/);
  });

  it("rejects non-numeric values", () => {
    expect(() => parseArgs(["--max-turns", "many"])).toThrow(/Invalid --max-turns/);
  });
});

describe("parseArgs --no-subagents", () => {
  it("disables subagents when flag is set", () => {
    expect(parseArgs(["--no-subagents"]).useSubagents).toBe(false);
  });

  it("keeps subagents on by default", () => {
    expect(parseArgs([]).useSubagents).toBe(true);
  });
});

describe("parseArgs deprecated --sarif / --markdown", () => {
  it("--sarif sets format to sarif and records a deprecation", () => {
    const p = parseArgs(["--sarif"]);
    expect(p.format).toBe("sarif");
    expect(p.deprecations.some((d) => d.includes("--sarif"))).toBe(true);
  });

  it("--markdown sets format to markdown and records a deprecation", () => {
    const p = parseArgs(["--markdown"]);
    expect(p.format).toBe("markdown");
    expect(p.deprecations.some((d) => d.includes("--markdown"))).toBe(true);
  });

  it("records no deprecations when modern flags are used", () => {
    const p = parseArgs(["--format", "sarif"]);
    expect(p.deprecations).toEqual([]);
  });
});

describe("parseArgs help", () => {
  it("--help returns help: true and does not throw", () => {
    expect(parseArgs(["--help"]).help).toBe(true);
  });

  it("-h returns help: true", () => {
    expect(parseArgs(["-h"]).help).toBe(true);
  });

  it("help short-circuits unknown flags that follow it", () => {
    // Order matters: --help is checked first in the loop, so a bogus flag
    // after it should not cause an error (helpful UX).
    expect(parseArgs(["--help", "--bogus"]).help).toBe(true);
  });
});

describe("parseArgs unknown flags", () => {
  it("throws on unknown flags", () => {
    expect(() => parseArgs(["--frobnicate"])).toThrow(/Unknown flag/);
  });
});

describe("CLI_USAGE", () => {
  it("mentions every supported option", () => {
    for (const token of [
      "--repo",
      "--directory",
      "--output",
      "--format",
      "--model",
      "--max-turns",
      "--no-subagents",
      "--sarif",
      "--markdown",
      "--help",
      "AUDIT_REVIEW_TIMEOUT_MS",
    ]) {
      expect(CLI_USAGE).toContain(token);
    }
  });
});

describe("parseArgs combinations", () => {
  it("handles a full production invocation", () => {
    const p = parseArgs([
      "--repo",
      "./src",
      "--output",
      "out.sarif",
      "--format",
      "sarif",
      "--model",
      "sonnet",
      "--max-turns",
      "120",
      "--no-subagents",
    ]);
    expect(p).toMatchObject({
      repo: "./src",
      output: "out.sarif",
      format: "sarif",
      model: "sonnet",
      maxTurns: 120,
      useSubagents: false,
      help: false,
      deprecations: [],
    });
  });
});
