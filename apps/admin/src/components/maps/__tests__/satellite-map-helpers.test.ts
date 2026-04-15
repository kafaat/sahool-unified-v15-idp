import { describe, it, expect } from 'vitest';
import { getNDVIColor, getHealthLabel } from '../SatelliteMap';

describe('SatelliteMap getNDVIColor (8-color scale)', () => {
  it('returns very dark green for excellent NDVI (>= 0.85)', () => {
    expect(getNDVIColor(0.85)).toBe('#004d00');
    expect(getNDVIColor(1.0)).toBe('#004d00');
  });

  it('returns dark green for very healthy NDVI (0.7 - 0.85)', () => {
    expect(getNDVIColor(0.7)).toBe('#1B5E20');
    expect(getNDVIColor(0.8)).toBe('#1B5E20');
  });

  it('returns green for healthy NDVI (0.55 - 0.7)', () => {
    expect(getNDVIColor(0.55)).toBe('#4CAF50');
    expect(getNDVIColor(0.65)).toBe('#4CAF50');
  });

  it('returns light green for moderate NDVI (0.45 - 0.55)', () => {
    expect(getNDVIColor(0.45)).toBe('#8BC34A');
    expect(getNDVIColor(0.5)).toBe('#8BC34A');
  });

  it('returns yellow for stressed NDVI (0.35 - 0.45)', () => {
    expect(getNDVIColor(0.35)).toBe('#FDD835');
    expect(getNDVIColor(0.4)).toBe('#FDD835');
  });

  it('returns orange for very stressed NDVI (0.25 - 0.35)', () => {
    expect(getNDVIColor(0.25)).toBe('#FF9800');
    expect(getNDVIColor(0.3)).toBe('#FF9800');
  });

  it('returns red for critical NDVI (0.15 - 0.25)', () => {
    expect(getNDVIColor(0.15)).toBe('#F44336');
    expect(getNDVIColor(0.2)).toBe('#F44336');
  });

  it('returns dark red for bare soil (< 0.15)', () => {
    expect(getNDVIColor(0.0)).toBe('#8B0000');
    expect(getNDVIColor(0.1)).toBe('#8B0000');
  });

  it('handles negative NDVI values', () => {
    expect(getNDVIColor(-0.5)).toBe('#8B0000');
  });
});

describe('SatelliteMap getHealthLabel (8-level Arabic)', () => {
  it('returns ممتاز for >= 0.85', () => {
    expect(getHealthLabel(0.9)).toBe('ممتاز');
  });

  it('returns صحي جداً for 0.7 - 0.85', () => {
    expect(getHealthLabel(0.75)).toBe('صحي جداً');
  });

  it('returns صحي for 0.55 - 0.7', () => {
    expect(getHealthLabel(0.6)).toBe('صحي');
  });

  it('returns معتدل for 0.45 - 0.55', () => {
    expect(getHealthLabel(0.5)).toBe('معتدل');
  });

  it('returns مجهد for 0.35 - 0.45', () => {
    expect(getHealthLabel(0.4)).toBe('مجهد');
  });

  it('returns مجهد جداً for 0.25 - 0.35', () => {
    expect(getHealthLabel(0.3)).toBe('مجهد جداً');
  });

  it('returns حرج for 0.15 - 0.25', () => {
    expect(getHealthLabel(0.2)).toBe('حرج');
  });

  it('returns تربة عارية for < 0.15', () => {
    expect(getHealthLabel(0.1)).toBe('تربة عارية');
  });
});
