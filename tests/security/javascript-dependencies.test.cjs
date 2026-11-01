/** Real package regressions for the October 2026 critical dependency fixes. */
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { mkdtempSync, readFileSync, rmSync, writeFileSync } = require('node:fs');
const { createRequire } = require('node:module');
const { tmpdir } = require('node:os');
const path = require('node:path');
const { test } = require('node:test');
const { pathToFileURL } = require('node:url');

const root = path.resolve(__dirname, '../..');
const readJson = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const minimum = (version, floor) => {
  assert.match(version, /^\d+\.\d+\.\d+$/, `Expected a stable version: ${version}`);
  const actual = version.split('.').map(Number);
  const required = floor.split('.').map(Number);
  for (let index = 0; index < 3; index += 1) {
    if (actual[index] !== required[index]) return actual[index] > required[index];
  }
  return true;
};

const floors = {
  'proxy-addr': '2.0.8',
  'maplibre-gl': '6.4.1',
  handlebars: '4.7.10',
  vitest: '3.2.6',
  tinypool: '2.1.2',
  storybook: '8.6.19',
  '@storybook/core': '8.6.19',
};
const patched = (name, version) => {
  if (name === 'next') {
    return minimum(version, '15.5.28') &&
      (!version.startsWith('16.') || minimum(version, '16.4.1'));
  }
  if (name === '@sentry/nextjs') {
    return minimum(version, '9.47.2') &&
      (!version.startsWith('10.') || minimum(version, '10.75.2'));
  }
  return minimum(version, floors[name]);
};

const lockPaths = execFileSync('git', ['ls-files', '-z', 'package-lock.json', '**/package-lock.json'], {
  cwd: root, encoding: 'utf8',
}).split('\0').filter(Boolean);
assert.ok(lockPaths.includes('package-lock.json'), 'The workspace lock must be checked');

for (const lockPath of lockPaths) {
  test(`patched dependencies in ${lockPath}`, () => {
    const lock = readJson(lockPath);
    assert.ok(lock.packages, `${lockPath} must expose its resolved packages`);
    for (const [location, entry] of Object.entries(lock.packages)) {
      for (const name of [...Object.keys(floors), 'next', '@sentry/nextjs']) {
        if (location.endsWith(`node_modules/${name}`)) {
          assert.ok(patched(name, entry.version), `${lockPath}: ${location}@${entry.version} is affected`);
          assert.match(entry.integrity, /^sha(256|384|512)-/, `${location} must retain registry integrity`);
        }
      }
    }
  });
}

const proxyaddr = require('proxy-addr');
for (const subnet of ['::ffff:10.0.0.0/8', '::/1']) {
  for (const address of ['198.51.100.23', '::ffff:198.51.100.23']) {
    test(`proxy-addr rejects a spoofed forwarded client through ${subnet} from ${address}`, () => {
      const request = {
        socket: { remoteAddress: address },
        headers: { 'x-forwarded-for': '192.0.2.123' },
      };
      assert.equal(proxyaddr(request, proxyaddr.compile(subnet)), address);
    });
  }
}
for (const subnet of ['10.0.0.0/8', '::ffff:10.0.0.0/104']) {
  test(`proxy-addr preserves legitimate proxy forwarding through ${subnet}`, () => {
    const request = {
      socket: { remoteAddress: '10.0.0.2' },
      headers: { 'x-forwarded-for': '198.51.100.23' },
    };
    assert.equal(proxyaddr(request, proxyaddr.compile(subnet)), '198.51.100.23');
  });
}

const handlebars = require('handlebars');
test('Handlebars still renders valid parsed templates and escapes user content', () => {
  const ast = handlebars.parse('{{#if enabled}}{{name}}{{/if}}');
  assert.equal(handlebars.compile(ast)({ enabled: true, name: '<script>test</script>' }),
    '&lt;script&gt;test&lt;/script&gt;');
});

test('Handlebars denies the Function constructor even when it is an own prototype property', () => {
  const render = handlebars.compile('{{lookup source "constructor"}}');
  assert.equal(render({ source: Function.prototype }, { allowProtoMethodsByDefault: true }), '');
});

test('Handlebars rejects an executable blockParams length in an untrusted AST', () => {
  const ast = handlebars.parse('{{#if enabled}}ok{{/if}}');
  ast.body[0].program.blockParams = { length: '(globalThis.__sahoolAstProbe = 1, 0)' };
  const previous = globalThis.__sahoolAstProbe;
  delete globalThis.__sahoolAstProbe;
  try {
    assert.throws(() => handlebars.compile(ast)({ enabled: true }));
    assert.throws(() => handlebars.precompile(ast));
    assert.equal(globalThis.__sahoolAstProbe, undefined, 'AST input must never execute as JavaScript');
  } finally {
    if (previous === undefined) delete globalThis.__sahoolAstProbe;
    else globalThis.__sahoolAstProbe = previous;
  }
});

test('the actual Vitest worker pool ignores an inherited worker filename', async () => {
  const vitestRequire = createRequire(require.resolve('vitest/package.json'));
  const { default: Tinypool } = await import(pathToFileURL(vitestRequire.resolve('tinypool')).href);
  const temporary = mkdtempSync(path.join(tmpdir(), 'sahool-worker-boundary-'));
  const expected = path.join(temporary, 'expected.mjs');
  const alternate = path.join(temporary, 'alternate.mjs');
  writeFileSync(expected, 'export default task => ({worker: "expected", task});\n');
  writeFileSync(alternate, 'export default task => ({worker: "alternate", task});\n');
  const pool = new Tinypool({ filename: expected, minThreads: 1, maxThreads: 1 });
  try {
    // Local prototypes keep the negative control isolated from unrelated tests.
    const options = Object.create({ filename: alternate });
    options.signal = new AbortController().signal;
    assert.deepEqual(await pool.run({ value: 7 }, options), { worker: 'expected', task: { value: 7 } });
    // An explicitly supplied filename remains supported; both workers are real.
    assert.deepEqual(await pool.run({ value: 8 }, { filename: alternate }),
      { worker: 'alternate', task: { value: 8 } });
  } finally {
    await pool.destroy();
    rmSync(temporary, { recursive: true, force: true });
  }
});

for (const app of ['web', 'admin']) {
  const appRequire = createRequire(path.join(root, `apps/${app}/package.json`));
  test(`${app}: installed Next.js matches the declared patched version`, () => {
    const manifest = readJson(`apps/${app}/package.json`);
    const installed = appRequire('next/package.json');
    assert.equal(installed.version, manifest.dependencies.next);
    assert.ok(patched('next', installed.version));
    assert.ok(patched('@sentry/nextjs', appRequire('@sentry/nextjs/package.json').version));
  });

  test(`${app}: Sentry cannot bypass authorization outside its exact envelope route`, async () => {
    // Exercise the installed public wrapper, without mocking Sentry or Next.js.
    const { wrapMiddlewareWithSentry } = appRequire('@sentry/nextjs');
    const previous = globalThis._sentryRewritesTunnelPath;
    globalThis._sentryRewritesTunnelPath = '/monitoring';
    const rejectedRequests = [
      ['GET', '/monitoring?o=1&p=2'],
      ['POST', '/monitoring'],
      ['POST', '/monitoring/admin?o=1&p=2'],
      ['POST', '/monitoring-other?o=1&p=2'],
      ['POST', '/monitoring?o=1'],
      ['POST', '/monitoring?o=1&p=invalid'],
      ['POST', '/monitoring?o=1&o=invalid&p=2'],
      ['POST', '/monitoring?o=invalid&o=1&p=2'],
    ];
    let authorizations = 0;
    const wrapped = wrapMiddlewareWithSentry(() => {
      authorizations += 1;
      return new Response('authentication required', { status: 401 });
    });
    try {
      for (const [method, route] of rejectedRequests) {
        const response = await wrapped(new Request(`https://sahool.test${route}`, { method }));
        assert.equal(response.status, 401, `${method} ${route} must reach authorization`);
      }
      assert.equal(authorizations, rejectedRequests.length);
      for (const route of ['/monitoring?o=1&p=2', '/monitoring/?o=1&p=2']) {
        const response = await wrapped(new Request(`https://sahool.test${route}`, { method: 'POST' }));
        assert.equal(response.headers.get('x-middleware-next'), '1');
      }
      assert.equal(authorizations, rejectedRequests.length, 'Valid envelopes still reach the tunnel rewrite');
    } finally {
      if (previous === undefined) delete globalThis._sentryRewritesTunnelPath;
      else globalThis._sentryRewritesTunnelPath = previous;
    }
  });

  test(`${app}: Next.js image optimizer uses patched Sharp and performs native image conversion`, async () => {
    const { getSharp, optimizeImage, detectContentType } = appRequire('next/dist/server/image-optimizer');
    const sharp = getSharp(1);
    assert.ok(minimum(sharp.versions.sharp, '0.35.5'));
    const input = await sharp({ create: { width: 8, height: 8, channels: 3, background: '#55aa33' } }).png().toBuffer();
    const result = await optimizeImage({
      buffer: input, contentType: 'image/jpeg', quality: 80, width: 4,
      concurrency: 1, limitInputPixels: 1024, timeoutInSeconds: 5,
    });
    assert.equal(await detectContentType(result), 'image/jpeg');
    const metadata = await sharp(result).metadata();
    assert.equal(metadata.width, 4);
    assert.equal(metadata.height, 4);
  });
}
