// Artefato descartável de revisão. Não é uma segunda fonte de tokens das stories.
// node tests/storybook/export-preview.mjs tokens.json /tmp/catalog.html
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import config from '../../skills/prismo/assets/storybook/catalog.config.mjs';
const [tokensPath, outputPath] = process.argv.slice(2);
if (!tokensPath || !outputPath || resolve(tokensPath) === resolve(outputPath)) throw Error('Informe fonte JSON e saída HTML distinta.');
const tokens = JSON.parse(readFileSync(tokensPath,'utf8'));
const mapping = structuredClone(config);
if (tokens.primitive?.typography?.family?.webFallback) mapping.fontFallback = 'primitive.typography.family.webFallback';
const source = name => readFileSync(new URL(`../../skills/prismo/assets/storybook/${name}`,import.meta.url),'utf8').replace(/^import .*\n/gm,'').replace(/^export /gm,'');
const json = value => JSON.stringify(value).replaceAll('<','\\u003c');
const script = `${source('dtcg.mjs')}\n${source('catalog.mjs')}\nconst tokens=${json(tokens)};const config=${json(mapping)};document.querySelector('#catalog').append(renderFoundations(tokens,config));`;
writeFileSync(outputPath, `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Prismo · catálogo de fundações</title><body style="margin:0"><div id="catalog"></div><script type="module">${script.replaceAll('</script','<\\/script')}</script></body></html>`);
console.log(outputPath);
