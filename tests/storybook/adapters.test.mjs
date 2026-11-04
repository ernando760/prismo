// Integração opcional dos adaptadores, sem instalar pacotes no consumidor.
// PRISMO_STORYBOOK_TEST_PACKAGE=/ambiente/package.json node tests/storybook/adapters.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { fixture } from './fixture.mjs';
const require = createRequire(process.env.PRISMO_STORYBOOK_TEST_PACKAGE || import.meta.url);
let dependencies;
try {
  for (const name of ['esbuild','react','react-dom/client','jsdom']) require.resolve(name);
  dependencies = true;
} catch { dependencies = false; }
async function adapter(filename) {
  const { build } = require('esbuild');
  const output = await build({
    entryPoints: [fileURLToPath(new URL(`../../skills/prismo/assets/storybook/${filename}`,import.meta.url))],
    bundle: true, platform: 'node', format: 'cjs', write: false, external: ['react'],
    plugins: [{ name: 'test-token-source', setup(builder) {
      builder.onResolve({filter: /^\.\/tokens\.json$/}, () => ({path:'tokens',namespace:'test-tokens'}));
      builder.onLoad({filter: /.*/,namespace:'test-tokens'}, () => ({contents:`export default ${JSON.stringify(fixture())}`,loader:'js'}));
    }}],
  });
  const module={exports:{}};
  new Function('module','exports','require',output.outputFiles[0].text)(module,module.exports,require);
  return module.exports;
}
const stories=['Colors','Typography','Spacing','Borders','Elevation'];
test('HTML adapter bundles and renders each story with the shared renderer',{skip:!dependencies},async()=>{
  const {JSDOM}=require('jsdom'), dom=new JSDOM('<!doctype html><html><body></body></html>');
  globalThis.document=dom.window.document;
  try {
    const exports=await adapter('Foundations.stories.js');
    for(const name of stories){
      const output=exports[name].render({mode:'compare'});
      assert.equal(output.querySelectorAll('.panel').length,2,name);
      assert.ok(output.querySelector('article'),name);
      if(name==='Colors') assert.equal(output.querySelectorAll('[data-color-group="Primitivos"]').length,1);
      if(name==='Typography') assert.ok(output.querySelector('[data-typography-scale]'));
      assert.equal(output.querySelectorAll('.value').length,0,name);
    }
  } finally {delete globalThis.document;dom.window.close();}
});
test('React adapter mounts all five stories and updates theme without changing the API',{skip:!dependencies},async()=>{
  const {JSDOM}=require('jsdom'), dom=new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>');
  globalThis.window=dom.window;globalThis.document=dom.window.document;globalThis.IS_REACT_ACT_ENVIRONMENT=true;
  const React=require('react'), {createRoot}=require('react-dom/client');
  const host=document.querySelector('#root'), root=createRoot(host);
  try {
    const exports=await adapter('Foundations.react.stories.js');
    for(const name of stories){
      await React.act(async()=>root.render(exports[name].render({mode:'compare'})));
      assert.equal(host.querySelectorAll('.panel').length,2,name);
      assert.ok(host.querySelector('article'),name);
      if(name==='Colors') assert.equal(host.querySelectorAll('[data-color-group="Primitivos"]').length,1);
      if(name==='Typography') assert.ok(host.querySelector('[data-typography-scale]'));
    }
    await React.act(async()=>root.render(exports.Colors.render({mode:'dark'})));
    assert.equal(host.querySelectorAll('.panel').length,1);
    assert.equal(host.querySelector('.panel').dataset.theme,'dark');
    assert.equal(host.querySelectorAll('[data-color-group="Primitivos"]').length,1);
  } finally {
    await React.act(async()=>root.unmount());
    delete globalThis.window;delete globalThis.document;delete globalThis.IS_REACT_ACT_ENVIRONMENT;dom.window.close();
  }
});
