// Use the same Nunjucks expression delimiters as Backstage fetch:template.
// The caller supplies a pinned, isolated installation; no repository npm install.
const fs = require('node:fs');
const path = require('node:path');

function render(moduleDirectory, template, values) {
  const metadata = require(path.join(moduleDirectory, 'package.json'));
  if (metadata.name !== 'nunjucks' || metadata.version !== '3.2.4') {
    throw new Error('Expected the verified nunjucks@3.2.4 renderer');
  }
  const nunjucks = require(moduleDirectory);
  const environment = new nunjucks.Environment(null, {
    autoescape: false,
    throwOnUndefined: true,
    tags: { variableStart: '${{', variableEnd: '}}' },
  });
  const result = environment.renderString(template, { values });
  if (/\{%|\{\{|\{#/.test(result)) {
    throw new Error('The requirements template contains unrendered expressions');
  }
  return result;
}

if (require.main === module) {
  const [moduleDirectory, templatePath, values] = process.argv.slice(2);
  if (!moduleDirectory || !templatePath || !values) {
    throw new Error('Usage: render_security_requirements.cjs MODULE TEMPLATE VALUES_JSON');
  }
  process.stdout.write(render(moduleDirectory, fs.readFileSync(templatePath, 'utf8'), JSON.parse(values)));
}

module.exports = { render };
