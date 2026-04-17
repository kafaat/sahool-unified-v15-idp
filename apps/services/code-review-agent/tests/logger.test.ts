/**
 * Unit tests for src/logger.ts.
 *
 * We exercise createLogger with explicit options (so tests don't depend on
 * process.env) and spy on console.log / console.error to capture output.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createLogger } from "../src/logger.js";

describe("createLogger - pretty format", () => {
  const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});
  const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});

  beforeEach(() => {
    logSpy.mockClear();
    errSpy.mockClear();
  });

  afterEach(() => {
    logSpy.mockClear();
    errSpy.mockClear();
  });

  it("info goes to stdout with a pretty prefix", () => {
    const log = createLogger({ format: "pretty", minLevel: "info" });
    log.info("hello");
    expect(logSpy).toHaveBeenCalledOnce();
    const line = logSpy.mock.calls[0][0] as string;
    expect(line).toContain("INFO");
    expect(line).toContain("hello");
    expect(errSpy).not.toHaveBeenCalled();
  });

  it("warn and error go to stderr", () => {
    const log = createLogger({ format: "pretty", minLevel: "info" });
    log.warn("careful");
    log.error("broken");
    expect(errSpy).toHaveBeenCalledTimes(2);
    expect(logSpy).not.toHaveBeenCalled();
  });

  it("appends meta as JSON in pretty mode", () => {
    const log = createLogger({ format: "pretty", minLevel: "info" });
    log.info("msg", { a: 1, b: "two" });
    const line = logSpy.mock.calls[0][0] as string;
    expect(line).toContain('{"a":1,"b":"two"}');
  });
});

describe("createLogger - json format", () => {
  const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});
  const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});

  beforeEach(() => {
    logSpy.mockClear();
    errSpy.mockClear();
  });

  it("emits parseable JSON with ts/level/msg", () => {
    const log = createLogger({ format: "json", minLevel: "info" });
    log.info("event", { k: "v" });
    const line = logSpy.mock.calls[0][0] as string;
    const parsed = JSON.parse(line);
    expect(parsed).toMatchObject({ level: "info", msg: "event", k: "v" });
    expect(typeof parsed.ts).toBe("string");
  });

  it("emits JSON for errors on stderr", () => {
    const log = createLogger({ format: "json", minLevel: "info" });
    log.error("boom", { code: 500 });
    const line = errSpy.mock.calls[0][0] as string;
    const parsed = JSON.parse(line);
    expect(parsed).toMatchObject({ level: "error", msg: "boom", code: 500 });
  });
});

describe("createLogger - level filtering", () => {
  const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});
  const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});

  beforeEach(() => {
    logSpy.mockClear();
    errSpy.mockClear();
  });

  it("minLevel=warn drops info messages", () => {
    const log = createLogger({ format: "pretty", minLevel: "warn" });
    log.info("dropped");
    log.warn("kept");
    expect(logSpy).not.toHaveBeenCalled();
    expect(errSpy).toHaveBeenCalledOnce();
  });

  it("minLevel=error drops info and warn", () => {
    const log = createLogger({ format: "pretty", minLevel: "error" });
    log.info("x");
    log.warn("y");
    log.error("z");
    expect(logSpy).not.toHaveBeenCalled();
    expect(errSpy).toHaveBeenCalledOnce();
  });

  it("minLevel=info keeps all levels", () => {
    const log = createLogger({ format: "pretty", minLevel: "info" });
    log.info("a");
    log.warn("b");
    log.error("c");
    expect(logSpy).toHaveBeenCalledOnce();
    expect(errSpy).toHaveBeenCalledTimes(2);
  });
});
