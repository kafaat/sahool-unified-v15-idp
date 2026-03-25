/**
 * Remaining Pages Tests
 * اختبارات الصفحات المتبقية
 *
 * Tests for: Vision, Terrain, Edge Devices, Drone, Scouting, Disasters,
 * Logistics, Virtual Sensors, Seasons, Lab, Research, Copilot, Support,
 * Reports/Seasonal
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const APP_DIR = path.resolve(__dirname, '..');

function readPage(pagePath: string): string {
  return fs.readFileSync(path.join(APP_DIR, pagePath, 'page.tsx'), 'utf-8');
}

function pageExists(pagePath: string): boolean {
  return fs.existsSync(path.join(APP_DIR, pagePath, 'page.tsx'));
}

// ═══════════════════════════════════════════════════════════════════════════
// Vision & AI Pages
// ═══════════════════════════════════════════════════════════════════════════

describe('Vision Page', () => {
  it('file exists', () => expect(pageExists('vision')).toBe(true));

  it('has use client directive', () => {
    expect(readPage('vision')).toMatch(/['"]use client['"]/);
  });

  it('exports default component', () => {
    expect(readPage('vision')).toMatch(/export default/);
  });

  it('imports lucide-react icons', () => {
    expect(readPage('vision')).toContain('lucide-react');
  });

  it('has Arabic labels', () => {
    const content = readPage('vision');
    expect(content).toMatch(/[\u0600-\u06FF]/);
  });

  it('handles image upload or analysis', () => {
    expect(readPage('vision')).toMatch(/image|upload|detect|analysis|camera/i);
  });
});

describe('Copilot Page', () => {
  it('file exists', () => expect(pageExists('copilot')).toBe(true));

  it('has use client directive', () => {
    expect(readPage('copilot')).toMatch(/['"]use client['"]/);
  });

  it('exports default component', () => {
    expect(readPage('copilot')).toMatch(/export default/);
  });

  it('has AI/chat functionality', () => {
    expect(readPage('copilot')).toMatch(/chat|message|send|ai|assistant|copilot/i);
  });

  it('has Arabic labels', () => {
    expect(readPage('copilot')).toMatch(/[\u0600-\u06FF]/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Terrain & Geospatial Pages
// ═══════════════════════════════════════════════════════════════════════════

describe('Terrain Page', () => {
  it('file exists', () => expect(pageExists('terrain')).toBe(true));

  it('has use client directive', () => {
    expect(readPage('terrain')).toMatch(/['"]use client['"]/);
  });

  it('exports default component', () => {
    expect(readPage('terrain')).toMatch(/export default/);
  });

  it('has terrain/DEM related content', () => {
    expect(readPage('terrain')).toMatch(/terrain|dem|elevation|slope|aspect/i);
  });

  it('has Arabic labels', () => {
    expect(readPage('terrain')).toMatch(/[\u0600-\u06FF]/);
  });
});

describe('Edge Devices Page', () => {
  it('file exists', () => expect(pageExists('edge-devices')).toBe(true));

  it('has use client directive', () => {
    expect(readPage('edge-devices')).toMatch(/['"]use client['"]/);
  });

  it('exports default component', () => {
    expect(readPage('edge-devices')).toMatch(/export default/);
  });

  it('has device management content', () => {
    expect(readPage('edge-devices')).toMatch(/device|edge|jetson|firmware|deploy/i);
  });

  it('has Arabic labels', () => {
    expect(readPage('edge-devices')).toMatch(/[\u0600-\u06FF]/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Field Operations Pages
// ═══════════════════════════════════════════════════════════════════════════

describe('Drone Page', () => {
  it('file exists', () => expect(pageExists('drone')).toBe(true));
  it('has use client directive', () => expect(readPage('drone')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('drone')).toMatch(/export default/));
  it('has drone/flight content', () => expect(readPage('drone')).toMatch(/drone|flight|uav|mission|vra/i));
  it('has Arabic labels', () => expect(readPage('drone')).toMatch(/[\u0600-\u06FF]/));
});

describe('Scouting Page', () => {
  it('file exists', () => expect(pageExists('scouting')).toBe(true));
  it('has use client directive', () => expect(readPage('scouting')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('scouting')).toMatch(/export default/));
  it('has scouting/pest content', () => expect(readPage('scouting')).toMatch(/scout|pest|observation|field|report/i));
  it('has Arabic labels', () => expect(readPage('scouting')).toMatch(/[\u0600-\u06FF]/));
});

describe('Disasters Page', () => {
  it('file exists', () => expect(pageExists('disasters')).toBe(true));
  it('has use client directive', () => expect(readPage('disasters')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('disasters')).toMatch(/export default/));
  it('has disaster/risk content', () => expect(readPage('disasters')).toMatch(/disaster|risk|flood|drought|assessment/i));
  it('has Arabic labels', () => expect(readPage('disasters')).toMatch(/[\u0600-\u06FF]/));
});

// ═══════════════════════════════════════════════════════════════════════════
// Supply Chain & Operations Pages
// ═══════════════════════════════════════════════════════════════════════════

describe('Logistics Page', () => {
  it('file exists', () => expect(pageExists('logistics')).toBe(true));
  it('has use client directive', () => expect(readPage('logistics')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('logistics')).toMatch(/export default/));
  it('has logistics content', () => expect(readPage('logistics')).toMatch(/logistic|shipment|transport|delivery|route/i));
  it('has Arabic labels', () => expect(readPage('logistics')).toMatch(/[\u0600-\u06FF]/));
});

describe('Seasons Page', () => {
  it('file exists', () => expect(pageExists('seasons')).toBe(true));
  it('has use client directive', () => expect(readPage('seasons')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('seasons')).toMatch(/export default/));
  it('has season/calendar content', () => expect(readPage('seasons')).toMatch(/season|calendar|planting|harvest|crop/i));
  it('has Arabic labels', () => expect(readPage('seasons')).toMatch(/[\u0600-\u06FF]/));
});

// ═══════════════════════════════════════════════════════════════════════════
// Sensor & IoT Pages
// ═══════════════════════════════════════════════════════════════════════════

describe('Virtual Sensors Page', () => {
  it('file exists', () => expect(pageExists('virtual-sensors')).toBe(true));
  it('has use client directive', () => expect(readPage('virtual-sensors')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('virtual-sensors')).toMatch(/export default/));
  it('has sensor/indicator content', () => expect(readPage('virtual-sensors')).toMatch(/sensor|virtual|indicator|computed|derived/i));
  it('has Arabic labels', () => expect(readPage('virtual-sensors')).toMatch(/[\u0600-\u06FF]/));
});

// ═══════════════════════════════════════════════════════════════════════════
// Research & Support Pages
// ═══════════════════════════════════════════════════════════════════════════

describe('Lab Page', () => {
  it('file exists', () => expect(pageExists('lab')).toBe(true));
  it('has use client directive', () => expect(readPage('lab')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('lab')).toMatch(/export default/));
  it('has lab/test content', () => expect(readPage('lab')).toMatch(/lab|test|analysis|sample|result/i));
  it('has Arabic labels', () => expect(readPage('lab')).toMatch(/[\u0600-\u06FF]/));
});

describe('Research Page', () => {
  it('file exists', () => expect(pageExists('research')).toBe(true));
  it('has use client directive', () => expect(readPage('research')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('research')).toMatch(/export default/));
  it('has research/trial content', () => expect(readPage('research')).toMatch(/research|trial|experiment|data|study/i));
  it('has Arabic labels', () => expect(readPage('research')).toMatch(/[\u0600-\u06FF]/));
});

describe('Support Page', () => {
  it('file exists', () => expect(pageExists('support')).toBe(true));
  it('has use client directive', () => expect(readPage('support')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('support')).toMatch(/export default/));
  it('has support/help content', () => expect(readPage('support')).toMatch(/support|help|ticket|faq|contact/i));
  it('has Arabic labels', () => expect(readPage('support')).toMatch(/[\u0600-\u06FF]/));
});

describe('Reports Seasonal Page', () => {
  it('file exists', () => expect(pageExists('reports/seasonal')).toBe(true));
  it('has use client directive', () => expect(readPage('reports/seasonal')).toMatch(/['"]use client['"]/));
  it('exports default component', () => expect(readPage('reports/seasonal')).toMatch(/export default/));
  it('has report/seasonal content', () => expect(readPage('reports/seasonal')).toMatch(/report|season|export|chart|summary/i));
  it('has Arabic labels', () => expect(readPage('reports/seasonal')).toMatch(/[\u0600-\u06FF]/));
});

// ═══════════════════════════════════════════════════════════════════════════
// Cross-cutting
// ═══════════════════════════════════════════════════════════════════════════

describe('All remaining pages cross-cutting', () => {
  const pages = [
    'vision', 'terrain', 'edge-devices', 'drone', 'scouting',
    'disasters', 'logistics', 'virtual-sensors', 'seasons',
    'lab', 'research', 'copilot', 'support', 'reports/seasonal',
  ];

  pages.forEach((page) => {
    it(`${page} uses icons or UI components`, () => {
      expect(readPage(page)).toMatch(/lucide-react|Icon|import.*from/);
    });

    it(`${page} is a valid React component`, () => {
      expect(readPage(page)).toMatch(/export default|function.*Page|return.*</);
    });
  });
});
