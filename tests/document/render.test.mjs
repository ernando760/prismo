// PRISMO_DOCUMENT_TEST_PACKAGE=/ambiente/package.json node tests/document/render.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { readFile } from 'node:fs/promises';
import { fixture } from '../storybook/fixture.mjs';
import config from '../../skills/prismo/assets/storybook/catalog.config.mjs';

const require = createRequire(process.env.PRISMO_DOCUMENT_TEST_PACKAGE || import.meta.url);
let available = true;
try { for (const p of ['react', 'react-dom/server', 'react-dom/client', 'esbuild', 'jsdom', '@mdx-js/mdx']) require.resolve(p); }
catch { available = false; }
const dir = fileURLToPath(new URL('../../skills/prismo/assets/document/', import.meta.url));
let ui;
async function bundle(options) {
  const { build } = require('esbuild');
  const result = await build({ bundle: true, platform: 'node', format: 'cjs', write: false,
    external: ['react', 'react/jsx-runtime'], loader: {'.css':'empty'}, ...options });
  const module = {exports:{}};
  new Function('module','exports','require',result.outputFiles[0].text)(module,module.exports,require);
  return module.exports;
}
async function setup() {
  ui ??= await bundle({entryPoints:[dir + '/DocumentUI.jsx']});
  return { ...ui, React: require('react'), server: require('react-dom/server') };
}
async function mount(callback) {
  const {React} = await setup(), {JSDOM} = require('jsdom');
  const dom = new JSDOM('<!doctype html><html><body><main><div id="root"></div></main></body></html>');
  globalThis.window=dom.window; globalThis.document=dom.window.document;
  globalThis.IS_REACT_ACT_ENVIRONMENT=true;
  const {createRoot}=require('react-dom/client'), root=createRoot(document.querySelector('#root'));
  const render=async element=>{ await React.act(async()=>root.render(element)); };
  try { await callback({React, root, render, host:document.querySelector('#root'), dom}); }
  finally { await React.act(async()=>root.unmount()); dom.window.close(); delete globalThis.window; delete globalThis.document; delete globalThis.IS_REACT_ACT_ENVIRONMENT; }
}
const t=(name,fn)=>test(name,{skip:!available},fn);
t('SSR works without browser globals and keeps readable values and source details',async()=>{
  const {React,server,DocLayout,FoundationCatalog,TokenFacts}=await setup();
  const html=server.renderToStaticMarkup(React.createElement(DocLayout,null,
    React.createElement(FoundationCatalog,{tokens:fixture(),config,section:'colors'}),
    React.createElement(TokenFacts,{tokens:fixture(),paths:['semantic.light.primary','semantic.spacing.gap.default']})));
  assert.match(html,/carrega com JavaScript/); assert.match(html,/#/);
  assert.doesNotMatch(html,/\[object Object\]|&quot;colorSpace&quot;|<main|<h1/);
  assert.match(html,/<details/); assert.doesNotMatch(html,/<details[^>]*open/);
});
t('all five foundations mount with shared visuals, themes and no nested main or h1',async()=>{
  await mount(async({React,render,host})=>{
    const {DocLayout,FoundationCatalog}=ui;
    for(const section of ['colors','typography','spacing','borders','elevation']) {
      await render(React.createElement(DocLayout,null,React.createElement(FoundationCatalog,{tokens:fixture(),config,section})));
      assert.equal(host.querySelectorAll('.panel').length,2,section);
      assert.ok(host.querySelector('article'),section);
      assert.equal(host.querySelectorAll('main,h1').length,0,section);
      assert.ok(host.querySelector('h3[data-doc-heading]'),section);
      assert.doesNotMatch(host.textContent,/\[object Object\]|"colorSpace"/);
    }
  });
});
t('filter and theme selector remain functional, with adapted headings after redraw',async()=>{
  await mount(async({React,render,host,dom})=>{
    await render(React.createElement(ui.FoundationCatalog,{tokens:fixture(),config,section:'colors'}));
    const search=host.querySelector('input');
    await React.act(async()=>{search.value='primary';search.dispatchEvent(new dom.window.Event('input',{bubbles:true}));});
    assert.ok(host.querySelectorAll('[data-token]').length>0);
    assert.ok([...host.querySelectorAll('[data-token]')].every(n=>n.dataset.token.includes('primary')));
    const select=host.querySelector('select');
    await React.act(async()=>{select.value='dark';select.dispatchEvent(new dom.window.Event('change',{bubbles:true}));});
    assert.equal(host.querySelectorAll('.panel').length,1);
    assert.equal(host.querySelector('.panel').dataset.theme,'dark');
    assert.equal(host.querySelectorAll('h2,h1').length,0);
  });
});
t('token changes propagate into visuals and labels without mutating source precision',async()=>{
  await mount(async({React,render,host})=>{
    const tokens=fixture(); const before=JSON.stringify(tokens);
    const view=data=>React.createElement(ui.DocLayout,null,
      React.createElement(ui.FoundationCatalog,{tokens:data,config,section:'colors'}),
      React.createElement(ui.TokenFacts,{tokens:data,paths:['semantic.light.primary']}));
    await render(view(tokens));
    const old=host.querySelector('.prismo-doc-value').textContent;
    assert.equal(JSON.stringify(tokens),before);
    tokens.primitive.brand.white.$value.components=[.123456789,.5,.9];
    const changed=JSON.stringify(tokens);
    await render(view(structuredClone(tokens)));
    const swatch=host.querySelector('[data-token="semantic.light.primary"] .color-sample');
    assert.ok(swatch.style.backgroundColor);
    assert.notEqual(swatch.style.backgroundColor, 'rgb(255, 255, 255)');
    assert.notEqual(host.querySelector('.prismo-doc-value').textContent,old);
    assert.match(host.textContent,/0.123456789/);
    assert.equal(JSON.stringify(tokens),changed);
  });
});
t('readable dimensions, typography and shadows do not dump JSON',async()=>{
  const {readableValue}=await setup();
  assert.equal(readableValue('dimension',{value:16.123456,unit:'px'}),'16.12px');
  assert.equal(readableValue('fontFamily',['Inter','sans-serif']),'Inter, sans-serif');
  assert.equal(readableValue('shadow',[]),'Sem sombra');
  const {tokenIndex,resolver}=await import('../../skills/prismo/assets/storybook/dtcg.mjs');
  const index=tokenIndex(fixture()),resolve=resolver(index);
  for(const [path,token] of index) {
    const value=readableValue(token.type,resolve(path));
    assert.doesNotMatch(value,/\[object Object\]|"\$value"|"components"/);
  }
});
t('missing aliases and unsupported types remain visible beside valid values',async()=>{
  const {React,server,TokenFacts}=await setup();
  const tokens={good:{$type:'dimension',$value:{value:4,unit:'px'}},bad:{$type:'color',$value:'{missing}'},odd:{$type:'duration',$value:{value:2,unit:'ms'}}};
  const html=server.renderToStaticMarkup(React.createElement(TokenFacts,{tokens,paths:['bad','good','odd']}));
  assert.match(html,/Token ausente/); assert.match(html,/4px/); assert.match(html,/Tipo não suportado/);
});
t('missing configuration, runtime errors and ready-to-pending updates stay explicit',async()=>{
  await mount(async({React,render,host})=>{
    await render(React.createElement(ui.FoundationCatalog,{tokens:fixture(),config,section:'colors'}));
    assert.ok(host.querySelector('.panel'));
    await render(React.createElement(ui.FoundationCatalog,{tokens:null,config:null,section:undefined}));
    assert.equal(host.querySelectorAll('.panel').length,0); assert.match(host.textContent,/Selecionar fundação/);
    await render(React.createElement(ui.FoundationCatalog,{tokens:fixture(),config:{},section:'colors'}));
    assert.match(host.textContent,/Visualização indisponível/);
  });
});
t('component examples render the supplied implementation, not a duplicate',async()=>{
  const {React,server,DocLayout,Example,ExampleGrid}=await setup();
  const Existing=({label})=>React.createElement('button',{'data-existing':true,type:'button'},label);
  const html=server.renderToStaticMarkup(React.createElement(DocLayout,null,React.createElement(ExampleGrid,null,
    React.createElement(Example,{caption:'Exemplo da fonte existente'},React.createElement(Existing,{label:'Confirmar'})))));
  assert.match(html,/data-existing/); assert.match(html,/Confirmar/); assert.match(html,/<figcaption/);
  assert.doesNotMatch(html,/Pendente/);
});
t('catalog references accept confirmed links and expose local paths without invented URLs',async()=>{
  const {React,server,CatalogLink}=await setup();
  for(const href of ['https://example.test/?path=/story/button--default','/catalog/button','#api'])
    assert.match(server.renderToStaticMarkup(React.createElement(CatalogLink,{href})),/<a href=/);
  for(const href of [undefined,'javascript:alert(1)','//example.test','file:///tmp/catalog','https://a.test/"onclick="x']) {
    const html=server.renderToStaticMarkup(React.createElement(CatalogLink,{href,local:'widgetbook/lib/button.dart'}));
    assert.doesNotMatch(html,/<a /); assert.match(html,/widgetbook\/lib\/button.dart/);
  }
});
t('missing design guidance and examples never get default product decisions',async()=>{
  const {React,server,Guidance,Example}=await setup();
  assert.match(server.renderToStaticMarkup(React.createElement(Guidance)),/Confirmar usos/);
  assert.match(server.renderToStaticMarkup(React.createElement(Example)),/exemplo aprovado/);
});
t('untrusted labels are escaped, aliases stay secondary and details are native',async()=>{
  const {React,server,TokenFacts}=await setup();
  const path='<img src=x onerror=alert(1)>';
  const html=server.renderToStaticMarkup(React.createElement(TokenFacts,{tokens:{[path]:{$type:'dimension',$value:{value:4,unit:'px'}}},paths:[path]}));
  assert.doesNotMatch(html,/<img/); assert.match(html,/&lt;img/);
  assert.match(html,/<summary>/);
});
t('all shipped MDX templates compile and render on server with explicit pending content',async()=>{
  const {compile}=await import(pathToFileURL(require.resolve('@mdx-js/mdx')).href);
  const {React,server}=await setup();
  for(const name of ['Foundation','Component','Identity']) {
    const raw=await readFile(dir + '/' + name + '.mdx','utf8');
    const body=raw.replace(/^---\n[\s\S]*?\n---\n/,'');
    const code=String(await compile(body,{development:false}));
    const module=await bundle({stdin:{contents:code,resolveDir:dir,sourcefile:name+'.mdx.js'}});
    const html=server.renderToStaticMarkup(React.createElement(module.default));
    assert.match(html,/prismo-docs/,name); assert.match(html,/Pendente/,name);
    assert.doesNotMatch(html,/\[object Object\]|"colorSpace"/,name);
    if(name==='Component') for(const label of ['Anatomia','Variantes e tamanhos','Estados e comportamento','Acessibilidade','API']) assert.ok(html.includes(label),label);
  }
});
t('server markup hydrates without mismatch and preserves textual fallback outside the client gallery',async()=>{
  const {React,server}=await setup(),{JSDOM}=require('jsdom');
  const props={tokens:fixture(),config,section:'spacing'};
  const element=React.createElement(ui.DocLayout,null,
    React.createElement(ui.FoundationCatalog,props),
    React.createElement(ui.TokenFacts,{tokens:props.tokens,paths:['semantic.spacing.gap.default']}));
  const html=server.renderToString(element);
  assert.match(html,/8px/);
  const dom=new JSDOM('<!doctype html><html><body><div id="root">'+html+'</div></body></html>');
  globalThis.window=dom.window; globalThis.document=dom.window.document;globalThis.IS_REACT_ACT_ENVIRONMENT=true;
  const errors=[],{hydrateRoot}=require('react-dom/client'); let root;
  try {
    await React.act(async()=>{root=hydrateRoot(document.querySelector('#root'),element,{onRecoverableError:e=>errors.push(e.message)});});
    assert.deepEqual(errors,[]); assert.equal(document.querySelectorAll('.panel').length,2);
    assert.match(document.querySelector('.prismo-doc-token-facts').textContent,/8px/);
  } finally {if(root)await React.act(async()=>root.unmount());dom.window.close();delete globalThis.window;delete globalThis.document;delete globalThis.IS_REACT_ACT_ENVIRONMENT;}
});
t('gallery controls retain associated labels and technical details remain closed native disclosures',async()=>{
  await mount(async({React,render,host})=>{
    await render(React.createElement(ui.FoundationCatalog,{tokens:fixture(),config,section:'colors'}));
    for(const control of host.querySelectorAll('input,select')) {
      assert.ok(control.id); assert.ok(host.querySelector(`label[for="${control.id}"]`));
    }
    assert.ok(host.querySelector('summary'));
    for(const details of host.querySelectorAll('details')) assert.equal(details.open,false);
    assert.equal(host.querySelectorAll('h1,main').length,0);
  });
});
