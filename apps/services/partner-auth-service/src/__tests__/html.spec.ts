import { escape } from "../utils/html";

describe("escape", () => {
  it("encodes the 5 dangerous characters", () => {
    expect(escape('<script>alert("xss")</script>')).toBe(
      "&lt;script&gt;alert(&#34;xss&#34;)&lt;/script&gt;",
    );
    expect(escape("Farmer's field")).toBe("Farmer&#39;s field");
    expect(escape("a & b")).toBe("a &amp; b");
  });

  it("passes through safe strings unchanged", () => {
    expect(escape("Hello world")).toBe("Hello world");
    expect(escape("مرحبا بالعالم")).toBe("مرحبا بالعالم");
  });

  it("handles null/undefined/number gracefully", () => {
    expect(escape(null)).toBe("");
    expect(escape(undefined)).toBe("");
    expect(escape(42)).toBe("42");
  });

  it("encodes attribute-injection payloads", () => {
    const payload = '" onmouseover="alert(1)"';
    const out = escape(payload);
    expect(out).not.toContain('"');
    expect(out).toContain("&#34;");
  });
});
