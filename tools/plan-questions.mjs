#!/usr/bin/env node
// Interactive planning questionnaire for SAHOOL mobile implementation plan
// Navigate with UP/DOWN arrows, select with ENTER, multi-select with SPACE+ENTER

import * as readline from 'readline';

const RESET  = '\x1b[0m';
const BOLD   = '\x1b[1m';
const DIM    = '\x1b[2m';
const GREEN  = '\x1b[32m';
const CYAN   = '\x1b[36m';
const YELLOW = '\x1b[33m';
const BLUE   = '\x1b[34m';
const MAGENTA= '\x1b[35m';
const WHITE  = '\x1b[37m';
const BG_BLUE= '\x1b[44m';
const CLEAR  = '\x1b[2J\x1b[H';

const questions = [
  {
    id: 'Q1',
    type: 'single',
    title: 'Implementation Scope — Where do we start?',
    subtitle: 'Web has Farms, 6-step Field Wizard, 54 Satellite indices. What is Phase 1?',
    options: [
      { key: '1', label: 'Farms feature only',             desc: 'Create farm + bbox map selection' },
      { key: '2', label: 'Auth upgrade only',              desc: 'Email registration + onboarding' },
      { key: '3', label: 'Field Wizard upgrade only',      desc: '6-step wizard matching the web' },
      { key: '4', label: 'Satellite tabs + indices only',  desc: '54 indices across 6 categories' },
      { key: '5', label: 'Farms + Field Wizard together',  desc: 'Most critical UX gap (recommended)' },
      { key: '6', label: 'All features in full parity',    desc: 'Farms, Auth, Wizard, Satellite all at once' },
    ],
  },
  {
    id: 'Q2',
    type: 'single',
    title: 'Farm Map Selection — Drawing tool style?',
    subtitle: 'How should farmers draw their farm boundary on mobile?',
    options: [
      { key: 'A', label: 'Polygon only',              desc: 'Tap vertices, close to finish (like current field editor)' },
      { key: 'B', label: 'Rectangle/BBox drag only',  desc: 'Drag corner to corner — fast and simple' },
      { key: 'C', label: 'Polygon + Rectangle + Circle', desc: 'Full tool bar matching web (recommended)' },
      { key: 'D', label: 'GPS trace walk',             desc: 'Walk the field perimeter while recording' },
      { key: 'E', label: 'All tools + GPS trace',      desc: 'Maximum flexibility' },
    ],
  },
  {
    id: 'Q3',
    type: 'single',
    title: 'Satellite Indices — How many to implement?',
    subtitle: 'Web has 54 indices (NDVI, NDWI, EVI, LAI, NDMI, chlorophyll…)',
    options: [
      { key: 'A', label: 'Minimal — 4 key indices',   desc: 'NDVI, NDWI, EVI, LAI only' },
      { key: 'B', label: 'Core — 20 indices',          desc: 'All 15 vegetation + 5 water indices' },
      { key: 'C', label: 'Full parity — all 54',       desc: 'Every index the web has, all 6 categories' },
      { key: 'D', label: 'Progressive — start A, easy to extend', desc: 'UI scales, add indices later (recommended)' },
    ],
  },
  {
    id: 'Q4',
    type: 'single',
    title: 'Wizard UX Pattern — How should multi-step wizards feel?',
    subtitle: 'Farm creation and Field creation both need a wizard flow',
    options: [
      { key: 'A', label: 'Full-screen steps + swipe + stepper bar', desc: 'Slide between steps, progress bar on top' },
      { key: 'B', label: 'Bottom sheet wizard',                      desc: 'Slides up from bottom, partial screen' },
      { key: 'C', label: 'Scrollable single page with sections',     desc: 'No steps, all fields visible with scroll' },
      { key: 'D', label: 'Modal dialog (like web)',                   desc: 'Centered overlay dialog' },
      { key: 'E', label: 'Keep current form + add missing steps',    desc: 'Minimal change to existing UI' },
    ],
  },
  {
    id: 'Q5',
    type: 'single',
    title: 'Form Library — What validates the wizard fields?',
    subtitle: 'Farm info, crop selection, soil type, irrigation — how to validate?',
    options: [
      { key: 'A', label: 'flutter_form_builder',  desc: 'Richest widget set, 2800 likes, updated Feb 2026' },
      { key: 'B', label: 'reactive_forms',         desc: 'Angular-style model-driven, clean separation' },
      { key: 'C', label: 'Keep existing pattern',  desc: 'Manual TextEditingController (no new dependency)' },
      { key: 'D', label: 'formz',                  desc: 'Lightweight value objects (needs bloc integration)' },
    ],
  },
  {
    id: 'Q6',
    type: 'single',
    title: 'Satellite Tile Rendering — How to display NDVI/NDWI on the map?',
    subtitle: 'Tiles need to overlay on the field polygon in the satellite view',
    options: [
      { key: 'A', label: 'WMS from Sentinel Hub only',       desc: 'Best quality, requires internet + API key' },
      { key: 'B', label: 'Cached PNG overlays locally',      desc: 'Offline-first, pre-generated tiles' },
      { key: 'C', label: 'WMS online + local cache fallback',desc: 'Best of both worlds (recommended)' },
      { key: 'D', label: 'Compute client-side from raw bands',desc: 'Complex, needs raw band data download' },
    ],
  },
  {
    id: 'Q7',
    type: 'single',
    title: 'Branch Strategy — How to organize the implementation?',
    subtitle: 'This is a big change. How should git branching work?',
    options: [
      { key: 'A', label: 'One feature branch per area',      desc: 'feature/farms, feature/field-wizard, feature/satellite' },
      { key: 'B', label: 'Single feature branch all-in-one', desc: 'feature/mobile-web-parity' },
      { key: 'C', label: 'UI-only branch first, then API',   desc: 'Screens with mocks, then wire real APIs' },
      { key: 'D', label: 'Parallel branches → release branch',desc: 'Merge into release/mobile-v2' },
    ],
  },
  {
    id: 'Q8',
    type: 'single',
    title: 'Bilingual Support — Arabic + English in new screens?',
    subtitle: 'The web app is fully bilingual (AR/EN). What about mobile?',
    options: [
      { key: 'A', label: 'Full bilingual parity',    desc: 'All new screens in Arabic + English' },
      { key: 'B', label: 'English-first',            desc: 'English now, Arabic strings added later' },
      { key: 'C', label: 'Match existing mobile style', desc: 'Whatever current mobile screens do' },
      { key: 'D', label: 'Arabic-first',             desc: 'Farmers are Arabic speakers — Arabic primary' },
    ],
  },
  {
    id: 'Q9',
    type: 'multi',
    title: 'Extra Features — Any additional items to include?',
    subtitle: 'SPACE to toggle, ENTER to confirm. Select all that apply.',
    options: [
      { key: '1', label: 'Account creation screen',       desc: 'Email + password registration (web-style)' },
      { key: '2', label: 'Yemen governorate/district picker', desc: 'Location hierarchy like web' },
      { key: '3', label: 'Field health KPI dashboard',    desc: 'NDVI + temp + AQI tiles per field' },
      { key: '4', label: 'Satellite timeline/date picker',desc: 'Choose historical imagery date' },
      { key: '5', label: 'Split-screen NDVI comparison',  desc: 'Before/after view' },
      { key: '6', label: 'Farm statistics dashboard',     desc: 'Total farms, area, crop count' },
      { key: '7', label: 'Offline map for farm/field areas', desc: 'Download tiles for offline use' },
    ],
  },
];

// ── renderer ────────────────────────────────────────────────────────────────

function header(q, total) {
  const bar = '█'.repeat(q) + '░'.repeat(total - q);
  return [
    `${CYAN}${BOLD}  SAHOOL Mobile — Implementation Plan Designer${RESET}`,
    `${DIM}  ${bar}  ${q}/${total}${RESET}`,
    '',
  ].join('\n');
}

function renderSingle(q, cursor, total) {
  const lines = [
    CLEAR,
    header(questions.indexOf(q) + 1, total),
    `${YELLOW}${BOLD}  ${q.id}. ${q.title}${RESET}`,
    `${DIM}     ${q.subtitle}${RESET}`,
    '',
  ];
  q.options.forEach((opt, i) => {
    const selected = i === cursor;
    const bullet = selected ? `${BG_BLUE}${WHITE}${BOLD} ❯ ${opt.key} ${RESET}` : `     ${DIM}${opt.key}${RESET} `;
    const label  = selected ? `${WHITE}${BOLD}${opt.label}${RESET}` : `${WHITE}${opt.label}${RESET}`;
    const desc   = `  ${DIM}${opt.desc}${RESET}`;
    lines.push(`  ${bullet} ${label}`);
    lines.push(`       ${desc}`);
    lines.push('');
  });
  lines.push(`${DIM}  ↑ ↓ navigate   ENTER select${RESET}`);
  return lines.join('\n');
}

function renderMulti(q, cursor, selected, total) {
  const lines = [
    CLEAR,
    header(questions.indexOf(q) + 1, total),
    `${YELLOW}${BOLD}  ${q.id}. ${q.title}${RESET}`,
    `${DIM}     ${q.subtitle}${RESET}`,
    '',
  ];
  q.options.forEach((opt, i) => {
    const isCursor   = i === cursor;
    const isSelected = selected.has(i);
    const check  = isSelected ? `${GREEN}${BOLD}[✓]${RESET}` : `${DIM}[ ]${RESET}`;
    const pointer = isCursor ? `${CYAN}${BOLD}❯${RESET}` : ' ';
    const label  = isCursor ? `${CYAN}${BOLD}${opt.label}${RESET}` : `${WHITE}${opt.label}${RESET}`;
    lines.push(`  ${pointer} ${check} ${DIM}${opt.key}${RESET}  ${label}`);
    lines.push(`          ${DIM}${opt.desc}${RESET}`);
    lines.push('');
  });
  lines.push(`${DIM}  ↑ ↓ navigate   SPACE toggle   ENTER confirm${RESET}`);
  return lines.join('\n');
}

function renderSummary(answers) {
  const lines = [
    CLEAR,
    `${CYAN}${BOLD}  SAHOOL Mobile — Your Implementation Choices${RESET}`,
    `${DIM}  ─────────────────────────────────────────────${RESET}`,
    '',
  ];
  answers.forEach(({ q, answer }) => {
    lines.push(`  ${YELLOW}${BOLD}${q.id}${RESET} ${BOLD}${q.title}${RESET}`);
    if (Array.isArray(answer)) {
      answer.forEach(a => lines.push(`     ${GREEN}✓${RESET} ${a.label} ${DIM}— ${a.desc}${RESET}`));
    } else {
      lines.push(`     ${GREEN}✓${RESET} ${answer.label} ${DIM}— ${answer.desc}${RESET}`);
    }
    lines.push('');
  });
  lines.push(`${GREEN}${BOLD}  All answers recorded. Building your plan...${RESET}`);
  lines.push('');
  return lines.join('\n');
}

// ── main loop ────────────────────────────────────────────────────────────────

async function ask(q, total) {
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin });
    readline.emitKeypressEvents(process.stdin, rl);
    if (process.stdin.isTTY) process.stdin.setRawMode(true);

    let cursor   = 0;
    const multiSel = new Set();
    const isMulti  = q.type === 'multi';

    const draw = () => {
      process.stdout.write(
        isMulti
          ? renderMulti(q, cursor, multiSel, total)
          : renderSingle(q, cursor, total)
      );
    };

    draw();

    const onKey = (_, key) => {
      if (!key) return;
      if (key.name === 'up')   { cursor = (cursor - 1 + q.options.length) % q.options.length; draw(); return; }
      if (key.name === 'down') { cursor = (cursor + 1) % q.options.length;                    draw(); return; }
      if (key.name === 'space' && isMulti) {
        multiSel.has(cursor) ? multiSel.delete(cursor) : multiSel.add(cursor);
        draw();
        return;
      }
      if (key.name === 'return' || key.name === 'enter') {
        process.stdin.removeListener('keypress', onKey);
        if (process.stdin.isTTY) process.stdin.setRawMode(false);
        rl.close();
        if (isMulti) {
          resolve([...multiSel].map(i => q.options[i]));
        } else {
          resolve(q.options[cursor]);
        }
      }
      if (key.ctrl && key.name === 'c') { process.exit(0); }
    };

    process.stdin.on('keypress', onKey);
  });
}

async function main() {
  if (!process.stdin.isTTY) {
    console.error('\x1b[31mError: must be run in an interactive terminal (TTY required).\x1b[0m');
    process.exit(1);
  }

  const answers = [];
  for (const q of questions) {
    const answer = await ask(q, questions.length);
    answers.push({ q, answer });
  }

  process.stdout.write(renderSummary(answers));

  // Write JSON to file for the plan builder
  const out = answers.map(({ q, answer }) => ({
    id: q.id,
    question: q.title,
    answer: Array.isArray(answer)
      ? answer.map(a => ({ key: a.key, label: a.label }))
      : { key: answer.key, label: answer.label },
  }));

  const fs = await import('fs');
  fs.writeFileSync('tools/plan-answers.json', JSON.stringify(out, null, 2));
  console.log('\x1b[32m  ✓ Answers saved to tools/plan-answers.json\x1b[0m\n');
}

main().catch(console.error);
