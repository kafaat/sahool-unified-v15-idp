const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const { render } = require('../render_security_requirements.cjs');

const moduleDirectory = process.env.NUNJUCKS_MODULE;
assert.ok(moduleDirectory, 'The mandatory renderer checks need the pinned Nunjucks installation');
const template = fs.readFileSync(
  path.resolve(__dirname, '../../../idp/templates/data-pipeline/skeleton/requirements.txt'), 'utf8',
);

for (const input of ['nats', 'kafka', 'postgres', 's3', 'api']) {
  for (const output of ['nats', 'postgres', 's3', 'api']) {
    test(`render requirements for ${input} -> ${output}`, () => {
      const result = render(moduleDirectory, template, {
        name: 'audit-fixture', input_source: input, output_sink: output,
      });
      assert.match(result, /# audit-fixture - Data Pipeline Requirements/);
      assert.match(result, /pydantic>=2\.10\.0/);
      assert.match(result, /numpy>=1\.26\.0,<2\.5\.0/);
      assert.equal(result.includes('nats-py==2.14.0'), input === 'nats' || output === 'nats');
      assert.equal(result.includes('asyncpg>=0.30.0'), input === 'postgres' || output === 'postgres');
      assert.equal(result.includes('aioboto3>=13.0.0'), input === 's3' || output === 's3');
      assert.doesNotMatch(result, /\{%|\{\{|\{#/);
    });
  }
}

test('undefined template values fail rather than produce an incomplete requirement', () => {
  assert.throws(() => render(moduleDirectory, '${{ values.missing }}', {}));
});

test('malformed template syntax fails', () => {
  assert.throws(() => render(moduleDirectory, '{% if %}', {}));
});
