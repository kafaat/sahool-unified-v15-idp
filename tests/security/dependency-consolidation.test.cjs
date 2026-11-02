/** Exercise the installed fixes used by the November dependency consolidation. */
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { readFileSync } = require('node:fs');
const { createRequire } = require('node:module');
const path = require('node:path');
const { test } = require('node:test');
const { pathToFileURL } = require('node:url');

const root = path.resolve(__dirname, '../..');
const requireFrom = (consumer) => createRequire(path.join(root, consumer, 'package.json'));

// A crashing parser must fail its own process, never the regression runner.
// The probe only binds loopback and makes two requests to that ephemeral port.
const parserProbe = String.raw`
const assert = require('node:assert/strict');
const http = require('node:http');
const { gzipSync } = require('node:zlib');
const parser = require(process.argv[1]).json();
const trailing = process.argv[2] === 'true';
const expected = { field: 'sahool-regression', value: 17 };
const json = JSON.stringify(expected);
const server = http.createServer((request, response) => {
  parser(request, response, (error) => {
    response.statusCode = error ? (error.status || 500) : 200;
    response.end(JSON.stringify(error ? { error: error.type } : request.body));
  });
});

function request(body, encoding) {
  return new Promise((resolve, reject) => {
    const call = http.request({
      hostname: '127.0.0.1', port: server.address().port, method: 'POST',
      agent: false,
      headers: {
        'content-type': 'application/json', 'content-length': body.length,
        ...(encoding ? { 'content-encoding': encoding } : {}),
      },
    }, (response) => {
      const chunks = [];
      response.on('data', (chunk) => chunks.push(chunk));
      response.on('error', reject);
      response.on('end', () => resolve({
        status: response.statusCode, body: Buffer.concat(chunks).toString(),
      }));
    });
    call.setTimeout(2000, () => call.destroy(new Error('loopback request timed out')));
    call.on('error', reject);
    call.end(body);
  });
}

server.listen(0, '127.0.0.1', async () => {
  try {
    const compressed = gzipSync(json);
    // Padding and garbage after a valid gzip member must not become an
    // unhandled decoder error after the response has been sent.
    const body = trailing
      ? Buffer.concat([compressed, Buffer.from([0]), Buffer.alloc(128 * 1024, 0x58)])
      : compressed;
    const first = await request(body, 'gzip');
    assert.equal(first.status, 200);
    assert.deepEqual(JSON.parse(first.body), expected);
    await new Promise((resolve) => setTimeout(resolve, 200));
    const followup = await request(Buffer.from(json));
    assert.equal(followup.status, 200);
    assert.deepEqual(JSON.parse(followup.body), expected);
    process.stdout.write(JSON.stringify({ first: first.status, followup: followup.status }));
  } catch (error) {
    console.error(error);
    process.exitCode = 1;
  } finally {
    server.close();
    server.closeAllConnections();
  }
});
`;

// A workspace consumer may resolve to the hoisted parser while another
// framework uses a nested major. Exercise every copy in the frozen root tree.
const installedLock = JSON.parse(readFileSync(path.join(root, 'package-lock.json'), 'utf8'));
const parsers = new Set(Object.keys(installedLock.packages)
  .filter((location) => location.endsWith('node_modules/body-parser'))
  .map((location) => require.resolve(path.join(root, location))));
assert.ok(parsers.size > 0, 'The installed workspace must expose its parser dependencies');

for (const entry of parsers) {
  for (const trailing of [false, true]) {
    test(`${path.relative(root, entry)}: gzip ${trailing ? 'with trailing bytes' : 'ordinary body'} keeps the service alive`, () => {
      const result = spawnSync(process.execPath, ['-e', parserProbe, entry, String(trailing)], {
        encoding: 'utf8', timeout: 8000, maxBuffer: 1024 * 1024,
      });
      assert.ifError(result.error);
      assert.equal(result.status, 0, `Parser subprocess failed: ${result.stderr}`);
      assert.deepEqual(JSON.parse(result.stdout), { first: 200, followup: 200 });
    });
  }
}

const mockers = new Map();
for (const consumer of ['', 'apps/services/code-review-agent']) {
  const vitestRequire = createRequire(requireFrom(consumer).resolve('vitest/package.json'));
  mockers.set(vitestRequire.resolve('@vitest/mocker/node'), vitestRequire.resolve('@vitest/mocker'));
}

for (const [pluginEntry, registryEntry] of mockers) {
  for (const unusualExport of [false, true]) {
    test(`${path.relative(root, pluginEntry)}: manual mocks treat ${unusualExport ? 'export names' : 'module URLs'} as data`, async () => {
      const { interceptorPlugin } = await import(pathToFileURL(pluginEntry).href);
      const { ManualMockedModule, MockerRegistry } = await import(pathToFileURL(registryEntry).href);
      const registry = new MockerRegistry();
      const marker = '__sahoolConsolidationMockProbe';
      const mockUrl = unusualExport
        ? '/safe-fixture.js'
        : `fixture"); globalThis.${marker} = true; void("`;
      const exportName = unusualExport ? 'quoted"export' : 'answer';
      const exports = { [exportName]: 42 };
      registry.add(ManualMockedModule.fromJSON({
        type: 'manual', raw: './fixture', id: mockUrl, url: mockUrl,
      }, () => exports));
      const plugin = interceptorPlugin({ registry });
      const load = typeof plugin.load === 'function' ? plugin.load : plugin.load.handler;
      const source = await load.call({}, mockUrl);
      assert.equal(typeof source, 'string', 'The real installed plugin must generate a mock module');
      const previousMocker = globalThis.__vitest_mocker__;
      const previousMarker = globalThis[marker];
      const received = [];
      globalThis.__vitest_mocker__ = {
        getFactoryModule(url) { received.push(url); return exports; },
      };
      delete globalThis[marker];
      try {
        // Evaluate only the local, benign marker probe generated above. It has
        // no imports, filesystem operations, credentials, or external requests.
        const module = await import(
          `data:text/javascript;base64,${Buffer.from(source).toString('base64')}#${encodeURIComponent(pluginEntry)}`
        );
        assert.equal(module[exportName], 42, 'Legitimate mocking must still work');
        assert.equal(globalThis[marker], undefined, 'A mock URL must never inject executable source');
        assert.deepEqual(received, [mockUrl], 'The complete URL must remain a single string argument');
      } finally {
        if (previousMocker === undefined) delete globalThis.__vitest_mocker__;
        else globalThis.__vitest_mocker__ = previousMocker;
        if (previousMarker === undefined) delete globalThis[marker];
        else globalThis[marker] = previousMarker;
      }
    });
  }
}
