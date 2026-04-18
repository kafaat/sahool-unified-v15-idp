/**
 * Diff-algorithm unit tests.
 *
 * We test `computeDiff()` as a pure function rather than the full component —
 * the component's visual assertions would double-test the algorithm while
 * adding jsdom setup overhead. Rendering is exercised by the Playwright
 * e2e in apps/admin/e2e/field-audit-history.spec.ts.
 */

import { describe, it, expect } from 'vitest';

import { computeDiff } from '../components/DiffViewer';

describe('computeDiff', () => {
  it('flags added keys', () => {
    const diff = computeDiff({}, { area_ha: 5.0 });
    expect(diff).toHaveLength(1);
    expect(diff[0]).toMatchObject({
      key: 'area_ha',
      kind: 'added',
      newSerialised: '5',
    });
  });

  it('flags removed keys', () => {
    const diff = computeDiff({ area_ha: 5.0 }, {});
    expect(diff).toHaveLength(1);
    expect(diff[0]).toMatchObject({
      key: 'area_ha',
      kind: 'removed',
      oldSerialised: '5',
    });
  });

  it('flags changed keys with both serialisations', () => {
    const diff = computeDiff({ area_ha: 5.0 }, { area_ha: 5.2 });
    expect(diff).toHaveLength(1);
    expect(diff[0]).toMatchObject({
      key: 'area_ha',
      kind: 'changed',
      oldSerialised: '5',
      newSerialised: '5.2',
    });
  });

  it('skips keys whose serialised values are identical', () => {
    // Same number, same serialisation → nothing to render.
    expect(computeDiff({ x: 1 }, { x: 1 })).toHaveLength(0);
  });

  it('serialises nested objects as JSON rather than descending into them', () => {
    // Shallow-by-design (see DiffViewer.tsx header comment). A nested
    // change surfaces as a single "changed" row with JSON-stringified
    // before/after — the operator can open the raw-JSON disclosure if
    // they need to eyeball the nested delta.
    const diff = computeDiff(
      { polygon: [[0, 0], [1, 0]] },
      { polygon: [[0, 0], [1, 1]] },
    );
    expect(diff).toHaveLength(1);
    expect(diff[0].kind).toBe('changed');
    expect(diff[0].oldSerialised).toContain('[1,0]');
    expect(diff[0].newSerialised).toContain('[1,1]');
  });

  it('returns sorted rows for stable UI order', () => {
    const diff = computeDiff(
      { zebra: 1, alpha: 2 },
      { zebra: 2, alpha: 3, mango: 4 },
    );
    const keys = diff.map((d) => d.key);
    expect(keys).toEqual(['alpha', 'mango', 'zebra']);
  });

  it('returns empty diff when both sides are null-ish', () => {
    expect(computeDiff(null, null)).toEqual([]);
  });
});
