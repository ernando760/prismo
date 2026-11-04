import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { catalog, tokenIndex, resolver, colorCSS, dimensionCSS, shadowCSS, familyCSS } from '../../skills/prismo/assets/storybook/dtcg.mjs';
import config from '../../skills/prismo/assets/storybook/catalog.config.mjs';
import { dim, color, token, fixture } from './fixture.mjs';

test('resolve aliases, inherited types and $root without mutating the source', () => {
  const data = { a: { $type: 'dimension', base: { $value: dim(4) }, $root: { $value: '{a.base}' } } };
  const before = JSON.stringify(data);
  assert.deepEqual(resolver(tokenIndex(data))('a.$root'), dim(4));
  assert.equal(JSON.stringify(data), before);
});
test('models include all five foundations and theme-specific values', () => {
  const light = catalog(fixture(), config, 'light'), dark = catalog(fixture(), config, 'dark');
  for (const name of ['colors','typography','spacing','radius','width','elevation']) assert.ok(light.sections[name].length);
  assert.notEqual(light.surfaces.background, dark.surfaces.background);
  assert.equal(light.sections.elevation[0].path, 'semantic.elevation.light.none');
  assert.equal(dark.sections.elevation[0].path, 'semantic.elevation.dark.low');
});
test('a token change propagates into the visual model without copying values', () => {
  const data = fixture();
  data.primitive.brand.white.$value.components = [.25,.5,.75];
  assert.equal(catalog(data, config, 'light').surfaces.surface, 'rgb(63.75 127.5 191.25 / 1)');
});
test('missing aliases and cycles are explicit row errors', () => {
  const data = fixture(); data.semantic.typography.body.$value = '{semantic.typography.body}';
  assert.match(catalog(data, config, 'light').sections.typography[0].error, /circular/);
  data.semantic.light.surface.$value = '{missing}';
  assert.match(catalog(data, config, 'light').errors[0], /ausente/);
});
test('missing theme never silently uses the other theme', () => {
  const custom = structuredClone(config); delete custom.themes.dark;
  assert.throws(() => catalog(fixture(), custom, 'dark'), /Tema não mapeado/);
});
test('type mismatches inside composites are rejected', () => {
  const data = fixture(); data.semantic.typography.body.$value.fontSize = '{primitive.brand.white}';
  assert.match(catalog(data, config, 'light').sections.typography[0].error, /Tipo incompatível/);
});
test('invalid and unsupported values are reported rather than invented', () => {
  for (const value of [token('color', {colorSpace:'display-p3',components:[1,0,0]}),token('dimension',{value:4,unit:'dp'}),token('number',Infinity)]) {
    assert.throws(() => resolver(tokenIndex({x:value}))('x'));
  }
  assert.throws(() => tokenIndex({x:{$extends:'{y}'}}), /Expanda/);
});
test('shadow none, negative offset/spread, inset, alpha and aliases serialize to CSS', () => {
  assert.equal(shadowCSS([]),'none');
  const model = catalog(fixture(), config, 'dark');
  assert.equal(shadowCSS(model.sections.elevation[0].value), 'inset -1px 2px 4px -1px rgb(0 0 0 / 1)');
});
test('shadow layer arrays are not flattened and invalid blur fails', () => {
  const data = fixture();
  data.semantic.elevation.dark.low.$value = ['{semantic.elevation.light.none}'];
  assert.match(catalog(data,config,'dark').sections.elevation[0].error,/array/);
  data.semantic.elevation.dark.low.$value = {color:color([0,0,0]),offsetX:dim(0),offsetY:dim(0),blur:dim(-1),spread:dim(0)};
  assert.match(catalog(data,config,'dark').sections.elevation[0].error,/Blur/);
});
test('CSS dimensions and color alpha retain exported precision', () => {
  assert.equal(dimensionCSS({value:.12345678,unit:'rem'}), '.12345678rem'.replace(/^\./,'0.'));
  assert.equal(colorCSS({...color([0,0,0]),alpha:.1234}), 'rgb(0 0 0 / 0.1234)');
});
test('collection mappings may follow project conventions without renaming tokens', () => {
  const custom=structuredClone(config);custom.collections.spacing.prefixes=['custom.space'];
  const data=fixture();data.custom={space:{small:token('dimension',dim(6))}};
  assert.equal(catalog(data,custom,'light').sections.spacing[0].path,'custom.space.small');
});
test('templates expose five stories and reference a JSON import', () => {
  for(const filename of ['Foundations.stories.js','Foundations.react.stories.js']) {
    const source=readFileSync(new URL(`../../skills/prismo/assets/storybook/${filename}`,import.meta.url),'utf8');
    for(const name of ['Colors','Typography','Spacing','Borders','Elevation']) assert.match(source,new RegExp(`export const ${name}`));
    assert.match(source,/import tokens from/);
  }
});

test('font families quote names while retaining CSS generic fallbacks', () => {
  assert.equal(familyCSS(['Example Sans', 'Arial', 'sans-serif']), '\"Example Sans\", \"Arial\", sans-serif');
});
