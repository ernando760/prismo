// Testes DOM opcionais; produção não depende de jsdom. Defina PRISMO_JSDOM_PATH
// para usar uma instalação disponível, ou instale jsdom no ambiente de testes.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { renderFoundations } from '../../skills/prismo/assets/storybook/catalog.mjs';
import config from '../../skills/prismo/assets/storybook/catalog.config.mjs';
import { fixture } from './fixture.mjs';
const require=createRequire(import.meta.url);
let JSDOM;
try { ({JSDOM}=require(process.env.PRISMO_JSDOM_PATH || 'jsdom')); } catch { /* opcionais */ }
function run(title,fn){test(title,{skip:!JSDOM},()=>{
 const dom=new JSDOM('<!doctype html><html><body></body></html>');
 globalThis.document=dom.window.document;
 try { fn(dom.window); } finally { delete globalThis.document; dom.window.close(); }
});}
run('renders all five foundations in both theme panels',()=>{
 const root=renderFoundations(fixture(),config);
 assert.equal(root.querySelectorAll('.panel').length,2);
 assert.equal(root.querySelectorAll('.panel [data-foundation]').length,12);
 assert.equal(root.querySelectorAll('[data-foundation="color-primitives"]').length,1);
 for(const category of ['colors','typography','spacing','radius','width','elevation'])
  assert.ok(root.querySelector(`[data-foundation="${category}"] article`));
});
run('theme control switches and comparison returns without global side effects',window=>{
 const root=renderFoundations(fixture(),config);
 const control=root.querySelector('select');control.value='dark';control.dispatchEvent(new window.Event('change'));
 assert.equal(root.querySelectorAll('.panel').length,1);assert.equal(root.querySelector('.panel').dataset.theme,'dark');
 control.value='compare';control.dispatchEvent(new window.Event('change'));
 assert.equal(root.querySelectorAll('.panel').length,2);
 assert.equal(document.documentElement.style.cssText,'');
});
run('filter operates on token paths and reports empty results',window=>{
 const root=renderFoundations(fixture(),config,{section:'spacing'});
 const input=root.querySelector('input');input.value='not-found';input.dispatchEvent(new window.Event('input'));
 assert.equal(root.querySelectorAll('article').length,0);assert.equal(root.querySelectorAll('.empty').length,2);
 input.value='gap.default';input.dispatchEvent(new window.Event('input'));
 assert.equal(root.querySelectorAll('article').length,2);
});
run('typography dimensions and fallback family follow source changes',()=>{
 const data=fixture();data.semantic.typography.body.$value.fontSize.value=18;
 data.fallback={ $type:'fontFamily', $value:['Arial','sans-serif'] };
 const mapping={...config,fontFallback:'fallback'};
 const root=renderFoundations(data,mapping,{section:'typography'});
 const sample=root.querySelector('.sample');assert.equal(sample.style.fontSize,'18px');
 assert.equal(sample.style.lineHeight,'1.5');
 assert.match(sample.style.fontFamily,/Arial/);assert.match(sample.style.fontFamily,/sans-serif/);
});
run('full radius and zero width are displayed without interpreting full as pixels',()=>{
 const data=fixture();data.semantic.borders.width.default.$value.value=0;
 const root=renderFoundations(data,config,{section:'borders'});
 assert.equal(root.querySelector('[data-token="semantic.borders.radius.pill"] .sample').style.borderRadius,'24px');
 assert.equal(root.querySelector('[data-token="semantic.borders.width.default"] .sample').style.borderWidth,'0px');
});
run('unsupported aliases and missing themes remain visible',()=>{
 const data=fixture();data.semantic.typography.body.$value='{missing}';
 const mapping=structuredClone(config);delete mapping.themes.dark;
 const root=renderFoundations(data,mapping,{section:'typography'});
 assert.match(root.textContent,/Token ausente/);assert.match(root.textContent,/Tema não mapeado/);
});
run('token names cannot inject HTML',()=>{
 const data=fixture();data.semantic.spacing.gap['<img src=x onerror=alert(1)>']=data.semantic.spacing.gap.default;
 const root=renderFoundations(data,config,{section:'spacing'});
 assert.equal(root.querySelectorAll('img').length,0);assert.match(root.textContent,/<img src=x/);
});
run('actual light and dark surfaces are applied from token aliases',()=>{
 const root=renderFoundations(fixture(),config,{section:'elevation'});
 const panels=root.querySelectorAll('.panel');
 assert.notEqual(panels[0].style.backgroundColor,panels[1].style.backgroundColor);
 assert.equal(root.querySelector('[data-theme="light"] .shadow-sample').style.boxShadow,'none');
 assert.match(root.querySelector('[data-theme="dark"] .shadow-sample').style.boxShadow,/inset/);
});
run('colors organize primitives and semantics with HEX labels',()=>{
 const root=renderFoundations(fixture(),config,{section:'colors'});
 assert.equal(root.querySelectorAll('[data-color-group="Primitivos"]').length,1);
 assert.equal(root.querySelectorAll('[data-color-group="Semânticos"]').length,2);
 assert.ok(root.querySelector('.color-grid .color-tile .color-sample'));
 assert.equal(root.querySelector('[data-token="primitive.brand.white"] .hex').textContent,'#FFFFFF');
 assert.equal(root.querySelector('[data-token="primitive.brand.black"] .hex').textContent,'#000000');
});
run('aliases remain secondary in collapsed native details, without raw JSON',()=>{
 const root=renderFoundations(fixture(),config);
 const details=root.querySelectorAll('details.technical');assert.ok(details.length);
 assert.equal(root.querySelectorAll('details[open]').length,0);
 const alias=root.querySelector('[data-token="semantic.light.surface"] .technical');
 assert.match(alias.textContent,/\{primitive.brand.white\}/);
 assert.equal(root.querySelectorAll('.value').length,0);
 assert.doesNotMatch(root.textContent,/\{"(?:fontFamily|colorSpace|value|color)"/);
});
run('spacing comparisons retain exact widths and readable measurements',()=>{
 const data=fixture();data.semantic.spacing.gap.default.$value.value=12.5;
 const root=renderFoundations(data,config,{section:'spacing'});
 const row=root.querySelector('[data-token="semantic.spacing.gap.default"]');
 assert.ok(['calc(50px)','calc(12.5px * 4)','50px'].includes(row.querySelector('.ruler-distance').style.width));
 assert.equal(row.querySelector('.measurement').textContent,'12.5px');
 assert.ok(row.closest('.scale-list'));
});
run('typographic hierarchy has formatted properties without flattening token styles',()=>{
 const root=renderFoundations(fixture(),config,{section:'typography'});
 const row=root.querySelector('.type-row');
 assert.equal(row.querySelector('.sample').style.fontSize,'16px');
 assert.match(row.querySelector('.properties').textContent,/FamíliaExample/);
 assert.match(row.querySelector('.properties').textContent,/Tamanho16px/);
 assert.match(row.querySelector('.properties').textContent,/Linha1.5×/);
});
run('elevation uses theme surfaces, actual shadows and layer measurements',()=>{
 const root=renderFoundations(fixture(),config,{section:'elevation'});
 const row=root.querySelector('[data-token="semantic.elevation.dark.low"]');
 assert.ok(row.querySelector('.elevation-stage .shadow-sample'));
 assert.match(row.querySelector('.shadow-sample').style.boxShadow,/inset -1px 2px 4px -1px/);
 assert.match(row.querySelector('.layer-metrics').textContent,/Blur 4px/);
 assert.match(row.querySelector('.layer-metrics').textContent,/Alpha 100%/);
});
run('transparent colors show alpha and explain approximated HEX without changing values',()=>{
 const data=fixture();data.primitive.brand.white.$value.components=[.1,.2,.3];data.primitive.brand.white.$value.alpha=.125;
 const before=JSON.stringify(data), root=renderFoundations(data,config,{section:'colors'});
 const row=root.querySelector('[data-token="primitive.brand.white"]');
 assert.equal(row.querySelector('.hex').textContent,'#1A334D');
 assert.equal(row.querySelector('.alpha-label').textContent,'Alpha 12.5%');
 assert.match(row.querySelector('.technical').textContent,/8 bits/);
 assert.equal(JSON.stringify(data),before);
});
run('errors stay attached to individual swatches instead of hiding valid palettes',()=>{
 const data=fixture();data.primitive.brand.white.$value.components=[2,0,0];
 const root=renderFoundations(data,config,{section:'colors'});
 assert.ok(root.querySelector('[data-token="primitive.brand.white"] .notice'));
 assert.ok(root.querySelector('[data-token="primitive.brand.black"] .color-sample'));
});
run('primitive colors render once outside theme panels in all display modes',window=>{
 const data=fixture(), root=renderFoundations(data,config,{section:'colors'});
 const select=root.querySelector('select');
 for(const mode of ['compare','dark','light']){
  select.value=mode;select.dispatchEvent(new window.Event('change'));
  assert.equal(root.querySelectorAll('[data-token="primitive.brand.white"]').length,1);
  assert.equal(root.querySelectorAll('.panel [data-token^="primitive."]').length,0);
  assert.equal(root.querySelectorAll('.panel [data-color-group="Semânticos"]').length,mode==='compare'?2:1);
 }
});
run('primitive filter works independently from semantic theme comparisons',window=>{
 const root=renderFoundations(fixture(),config,{section:'colors'}), search=root.querySelector('input');
 search.value='primitive.brand.white';search.dispatchEvent(new window.Event('input'));
 assert.equal(root.querySelectorAll('article').length,1);
 search.value='semantic.dark.text';search.dispatchEvent(new window.Event('input'));
 assert.equal(root.querySelectorAll('article').length,1);
 assert.equal(root.querySelector('article').dataset.token,'semantic.dark.text');
});
run('typographic scale uses existing dimensions, sorts sizes and rounds labels only',()=>{
 const data=fixture(), before=JSON.stringify(data), root=renderFoundations(data,config,{section:'typography'});
 const rows=root.querySelectorAll('[data-theme="light"] [data-scale-token]');
 assert.equal(rows.length,3);
 assert.equal(rows[0].dataset.scaleToken,'primitive.typography.size.small');
 assert.equal(rows[0].querySelector('.type-scale-sample').style.fontSize,'12.641975px');
 assert.equal(rows[0].querySelector('.measurement').textContent,'12.64px');
 assert.match(rows[0].querySelector('.technical').textContent,/12.641975px/);
 assert.equal(JSON.stringify(data),before);
});
run('specimen properties round while exact size, line and tracking are retained',()=>{
 const data=fixture(), value=data.semantic.typography.body.$value;
 value.fontSize.value=28.83252;value.lineHeight=1.234567;value.letterSpacing.value=-.123456;
 const before=JSON.stringify(data), root=renderFoundations(data,config,{section:'typography'});
 const row=root.querySelector('.type-row');
 assert.equal(row.querySelector('.sample').style.fontSize,'28.83252px');
 assert.equal(row.querySelector('.sample').style.lineHeight,'1.234567');
 assert.equal(row.querySelector('.sample').style.letterSpacing,'-0.123456px');
 assert.match(row.querySelector('.properties').textContent,/28.83px/);
 assert.match(row.querySelector('.technical').textContent,/28.83252px/);
 assert.equal(JSON.stringify(data),before);
});
run('spacing ruler clearly separates presentation magnification from source distance',()=>{
 const data=fixture(), root=renderFoundations(data,config,{section:'spacing'});
 const row=root.querySelector('.scale-row'), ruler=row.querySelector('.ruler-distance');
 assert.equal(ruler.dataset.zoom,'4');assert.ok(['calc(32px)','calc(8px * 4)','32px'].includes(ruler.style.width));
 assert.equal(row.querySelectorAll('.ruler-anchor').length,2);
 assert.match(row.querySelector('.ruler-window').getAttribute('aria-label'),/8px.*4 vezes/);
 assert.equal(row.querySelector('.measurement').textContent,'8px');
 assert.ok(root.querySelector('.scale-note'));assert.ok(root.querySelector('.panel').style.getPropertyValue('--prismo-accent'));
});
run('full displays both a capsule and a circle without changing the token',window=>{
 const data=fixture(), before=JSON.stringify(data), root=renderFoundations(data,config,{section:'borders'});
 const row=root.querySelector('[data-token="semantic.borders.radius.pill"]');
 document.body.append(root);
 assert.equal(row.querySelectorAll('figure').length,2);
 assert.equal(window.getComputedStyle(row.querySelector('.full-shapes')).display,'flex');
 assert.equal(row.querySelector('.shape').style.borderRadius,'24px');
 const circle=row.querySelector('.full-circle');
 assert.equal(circle.style.width,'48px');assert.equal(circle.style.height,'48px');assert.equal(circle.style.borderRadius,'24px');
 assert.match(row.textContent,/Cápsula/);assert.match(row.textContent,/Círculo/);
 assert.equal(JSON.stringify(data),before);
});
run('dark shadows use mapped inspection surfaces with unchanged shadow values',()=>{
 const data=fixture(), before=JSON.stringify(data), root=renderFoundations(data,config,{section:'elevation'});
 const panel=root.querySelector('[data-theme="dark"]'), stage=panel.querySelector('.elevation-stage');
 assert.notEqual(stage.style.backgroundColor,panel.style.backgroundColor);
 assert.match(panel.querySelector('.shadow-sample').style.boxShadow,/inset -1px 2px 4px -1px/);
 assert.ok(panel.querySelector('.inspection-note'));assert.equal(JSON.stringify(data),before);
});
run('missing inspection mapping is reported only in elevation with original surface fallback',()=>{
 const mapping=structuredClone(config);mapping.elevationSurfaces.dark.background='missing';
 const colors=renderFoundations(fixture(),mapping,{section:'colors'});
 assert.equal(colors.querySelectorAll('.notice').length,0);
 const shadows=renderFoundations(fixture(),mapping,{section:'elevation'});
 assert.match(shadows.textContent,/Fundo de inspeção: Token ausente/);
 const stage=shadows.querySelector('[data-theme="dark"] .elevation-stage');
 assert.equal(stage.style.backgroundColor,shadows.querySelector('[data-theme="dark"]').style.backgroundColor);
});
run('typographic scale falls back to existing style sizes without inventing steps',()=>{
 const mapping=structuredClone(config);mapping.collections.typographyScale.prefixes=['not-mapped'];
 const root=renderFoundations(fixture(),mapping,{section:'typography'});
 const rows=root.querySelectorAll('[data-theme="light"] [data-scale-token]');
 assert.equal(rows.length,1);assert.equal(rows[0].dataset.scaleToken,'semantic.typography.body');
 assert.equal(rows[0].querySelector('.type-scale-sample').style.fontSize,'16px');
 assert.match(rows[0].querySelector('.technical').textContent,/CampofontSize/);
});
