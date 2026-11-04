import { catalog, colorCSS, dimensionCSS, shadowCSS, familyCSS } from './dtcg.mjs';

const labels = { colors: 'Colors', typography: 'Typography', spacing: 'Spacing', borders: 'Borders', elevation: 'Elevation' };
const descriptions = {
  colors: 'Paletas e papéis de cor, do valor primitivo à aplicação semântica.',
  typography: 'Famílias, hierarquia e ritmo de leitura em exemplos tipográficos.',
  spacing: 'Uma escala comum para os intervalos e respiros da interface.',
  borders: 'Formas, raios e espessuras comparados nas mesmas dimensões.',
  elevation: 'Profundidade e separação de superfícies em cada tema.',
};
const css = `
.prismo-catalog{font:14px/1.55 system-ui,sans-serif;color:#182230;background:#f8fafc;padding:clamp(20px,4vw,56px);isolation:isolate;min-height:100vh}
.prismo-catalog *{box-sizing:border-box}.prismo-catalog .catalog-inner{max-width:1480px;margin-inline:auto}
.prismo-catalog h1,.prismo-catalog h2,.prismo-catalog h3,.prismo-catalog h4,.prismo-catalog p{margin:0}
.prismo-catalog h1{font-size:clamp(28px,3vw,40px);line-height:1.15;font-weight:650;letter-spacing:-.03em;text-wrap:balance}
.prismo-catalog .intro{margin-top:12px;max-width:68ch;color:#475467;font-size:16px}
.prismo-catalog h2{font-size:20px;line-height:1.3;font-weight:650;letter-spacing:-.02em}
.prismo-catalog h3{font-size:18px;font-weight:650;letter-spacing:-.015em}.prismo-catalog h4{font-size:14px;font-weight:600}
.prismo-catalog .toolbar{display:flex;align-items:end;gap:20px;flex-wrap:wrap;padding-block:28px;margin-bottom:28px;border-bottom:1px solid #d0d5dd}
.prismo-catalog label{display:grid;gap:7px;font-size:13px;font-weight:600}.prismo-catalog .search-label{flex:1;min-width:min(100%,220px);max-width:440px}
.prismo-catalog input,.prismo-catalog select{font:inherit;font-weight:400;color:#182230;background:#fff;border:1px solid #667085;border-radius:6px;padding:10px 12px;min-height:44px;max-width:100%;width:100%}
.prismo-catalog input::placeholder{color:#475467}.prismo-catalog :focus-visible{outline:2px solid currentColor;outline-offset:4px}
.prismo-catalog .panels{display:grid;grid-template-columns:minmax(0,1fr);gap:28px;align-items:start}
.prismo-catalog[data-mode=compare] .panels{grid-template-columns:repeat(2,minmax(0,1fr))}
.prismo-catalog .panel{padding:clamp(20px,2.5vw,32px);min-width:0;border:1px solid #d0d5dd;border-radius:12px}
.prismo-catalog .panel-header{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding-bottom:20px;border-bottom:1px solid var(--prismo-line,currentColor)}
.prismo-catalog .theme-caption{font-size:12px}.prismo-catalog .foundation{margin-top:32px;min-width:0}
.prismo-catalog .foundation-header{margin-bottom:20px}.prismo-catalog .foundation-header p{margin-top:5px;font-size:13px;max-width:65ch}
.prismo-catalog .token-group+.token-group{margin-top:28px}.prismo-catalog .group-title{font-size:14px;font-weight:600;margin-bottom:14px}
.prismo-catalog .palette-title{font-size:13px;font-weight:500;margin:16px 0 10px}
.prismo-catalog .color-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:18px 12px}
.prismo-catalog .row{min-width:0}.prismo-catalog .token-name{overflow-wrap:anywhere;font-size:13px;font-weight:600;line-height:1.4}
.prismo-catalog .sample{overflow-wrap:anywhere}.prismo-catalog .color-sample{height:76px;border-radius:6px;margin-bottom:10px;box-shadow:inset 0 0 0 1px rgb(128 128 128 / .2)}
.prismo-catalog code{font:12px/1.55 ui-monospace,monospace;overflow-wrap:anywhere}.prismo-catalog .hex{display:block;margin-top:3px;font-variant-numeric:tabular-nums}
.prismo-catalog .alpha-label{display:block;font-size:12px;margin-top:2px}
.prismo-catalog .technical{font-size:12px;margin-top:10px}.prismo-catalog summary{cursor:pointer;min-height:32px;display:list-item;list-style-position:inside;padding-block:6px;font-size:12px;font-weight:500}
.prismo-catalog .technical[open]{padding-bottom:8px}.prismo-catalog dl{margin:0}.prismo-catalog .technical dl{display:grid;gap:10px;margin-top:8px}
.prismo-catalog dt{font-size:12px;font-weight:500}.prismo-catalog dd{margin:0;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.prismo-catalog .properties{display:flex;gap:12px 24px;flex-wrap:wrap;margin-top:18px;font-size:13px}
.prismo-catalog .properties>div{min-width:64px}.prismo-catalog .properties dt{margin-bottom:2px}.prismo-catalog .properties dd{font-weight:500}
.prismo-catalog .shared-palette{padding:clamp(20px,2.5vw,32px);background:#fff;border:1px solid #d0d5dd;border-radius:12px;margin-bottom:28px}
.prismo-catalog .shared-palette .foundation-header{margin-bottom:24px}.prismo-catalog .shared-palette .color-grid{grid-template-columns:repeat(auto-fill,minmax(92px,1fr))}
.prismo-catalog .type-scale{margin-bottom:32px}.prismo-catalog .type-scale-list{display:grid;gap:0;margin-top:16px}
.prismo-catalog .type-scale-step{display:grid;grid-template-columns:minmax(64px,92px) minmax(0,1fr) auto;gap:12px;align-items:baseline;padding-block:12px;border-bottom:1px solid var(--prismo-line,currentColor)}
.prismo-catalog .type-scale-step .technical{grid-column:1/-1;margin-top:0}.prismo-catalog .type-scale-sample{overflow-wrap:anywhere;line-height:1.35;min-width:0}
.prismo-catalog .specimen-frame{padding-block:16px}.prismo-catalog .specimen-frame .type-sample{margin-top:0}
.prismo-catalog .scale-note{font-size:12px;margin-bottom:16px}.prismo-catalog .ruler-window{overflow-x:auto;min-width:0;padding:12px 4px}
.prismo-catalog .ruler-line{display:flex;align-items:center;width:max-content;min-height:36px}
.prismo-catalog .ruler-anchor{width:10px;height:24px;flex-shrink:0;border:1px solid currentColor;border-radius:2px}
.prismo-catalog .ruler-distance{height:28px;position:relative;flex-shrink:0;border-block:2px solid var(--prismo-accent,currentColor)}
.prismo-catalog .ruler-distance::before,.prismo-catalog .ruler-distance::after{content:"";position:absolute;top:-6px;bottom:-6px;width:2px;background:var(--prismo-accent,currentColor)}
.prismo-catalog .ruler-distance::before{left:0}.prismo-catalog .ruler-distance::after{right:0}.prismo-catalog .ruler-fill{position:absolute;inset:0;background:var(--prismo-accent,currentColor);opacity:.18}
.prismo-catalog figure{margin:0}.prismo-catalog figcaption{font-size:12px;text-align:center;margin-top:10px}
.prismo-catalog .inspection-note{font-size:12px;margin-bottom:20px}
.prismo-catalog .type-row{padding-block:24px;border-top:1px solid var(--prismo-line,currentColor)}
.prismo-catalog .type-row:first-child{padding-top:0;border-top:0}.prismo-catalog .type-sample{margin-top:16px;max-width:68ch;overflow-wrap:anywhere}
.prismo-catalog .scale-list{display:grid;gap:4px}.prismo-catalog .scale-row{display:grid;grid-template-columns:minmax(72px,100px) minmax(0,1fr) minmax(40px,auto);gap:12px;align-items:center;padding-block:14px;border-bottom:1px solid var(--prismo-line,currentColor)}
.prismo-catalog .scale-row .technical{grid-column:1/-1;margin-top:0}.prismo-catalog .measurement{font-size:13px;font-variant-numeric:tabular-nums;white-space:nowrap}
.prismo-catalog .shape-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:32px 24px}
.prismo-catalog .shape-stage{padding:24px 16px;display:grid;place-items:center;min-height:128px;margin-bottom:18px;background:var(--prismo-surface,Canvas);border-radius:6px}
.prismo-catalog .shape-grid .full-radius-tile{grid-column:1/-1}
.prismo-catalog .shape-stage.full-shapes{display:flex;flex-wrap:wrap;justify-content:center;align-items:start;gap:24px 20px;min-height:152px}
.prismo-catalog .shape{width:120px;height:48px;border:1px solid currentColor;display:grid;place-items:center;font-size:12px}
.prismo-catalog .shape-label{display:flex;justify-content:space-between;gap:12px;align-items:baseline}
.prismo-catalog .elevation-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(188px,1fr));gap:28px 20px}
.prismo-catalog .elevation-stage{padding:40px 24px;min-height:184px;display:grid;place-items:center;border-radius:6px;margin-bottom:12px}
.prismo-catalog .shadow-sample{width:100%;max-width:200px;min-height:96px;display:grid;place-items:center;background:var(--prismo-surface,Canvas);font-size:13px;font-weight:500}
.prismo-catalog .shadow-caption{margin-top:6px;font-size:12px;overflow-wrap:anywhere}.prismo-catalog .layer-metrics{display:flex;gap:4px 12px;flex-wrap:wrap;margin-top:6px;font-size:12px;font-variant-numeric:tabular-nums}
.prismo-catalog .notice{padding:12px;border:1px dashed currentColor;border-radius:6px;margin-top:12px;overflow-wrap:anywhere}
.prismo-catalog .empty{padding-block:16px;font-size:13px}.prismo-catalog ::selection{background:#dbeafe;color:#182230}
@media(max-width:1000px){.prismo-catalog[data-mode=compare] .panels{grid-template-columns:minmax(0,1fr)}}
@media(max-width:520px){.prismo-catalog .toolbar{align-items:stretch;gap:16px}.prismo-catalog label{width:100%}.prismo-catalog .search-label{max-width:none}.prismo-catalog .panel-header{flex-wrap:wrap}.prismo-catalog .color-grid{grid-template-columns:repeat(auto-fill,minmax(84px,1fr))}.prismo-catalog .shape-grid,.prismo-catalog .elevation-grid{grid-template-columns:minmax(0,1fr)}.prismo-catalog .scale-row{grid-template-columns:80px minmax(0,1fr) auto;gap:8px}}
`;
let sequence = 0;
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
const leaf = path => path.split('.').at(-1);
const human = value => value.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/[-_]/g, ' ').replace(/^\w/, c => c.toUpperCase());
const measure = value => dimensionCSS(value);
export const displayNumber = value => Number((Math.abs(value) < 0.005 && value !== 0 ? value.toPrecision(2) : value.toFixed(2))).toString();
const displayMeasure = value => `${displayNumber(value.value)}${value.unit}`;
const percent = value => `${Number((value * 100).toFixed(6))}%`;
export function colorHex(value) {
  return '#' + value.components.map(v => Math.round(v * 255).toString(16).padStart(2, '0')).join('').toUpperCase();
}
function notice(message) {
  const node = element('p', message, 'notice'); node.setAttribute('role', 'status'); return node;
}
function properties(items) {
  const dl = element('dl', undefined, 'properties');
  for (const [key, value] of items) { const pair = element('div'); pair.append(element('dt', key), element('dd', String(value))); dl.append(pair); }
  return dl;
}
function technical(row, extra = []) {
  const details = element('details', undefined, 'technical'); details.append(element('summary', 'Detalhes do token'));
  const dl = element('dl');
  for (const [label, value] of [['Caminho', row.path], ['Tipo', row.type], ...(row.alias ? [['Alias', row.alias]] : []), ...extra]) {
    const pair = element('div'); pair.append(element('dt', label), element('dd'));
    pair.lastChild.append(element('code', String(value))); dl.append(pair);
  }
  details.append(dl); return details;
}
function article(row, className = '') {
  const node = element('article', undefined, `row ${className}`); node.dataset.token = row.path; return node;
}
function name(row, tag = 'p') { return element(tag, human(leaf(row.path)), 'token-name'); }
function colorTile(row) {
  const node = article(row, 'color-tile');
  if (row.error) { node.append(name(row), notice(row.error)); return node; }
  const hex = colorHex(row.value), swatch = element('div', undefined, 'sample color-sample');
  swatch.style.backgroundColor = colorCSS(row.value); swatch.setAttribute('role', 'img');
  swatch.setAttribute('aria-label', `${row.path}: ${hex}, alpha ${percent(row.value.alpha)}`);
  node.append(swatch, name(row), element('code', hex, 'hex'));
  if (row.value.alpha !== 1) node.append(element('span', `Alpha ${percent(row.value.alpha)}`, 'alpha-label'));
  const approximate = row.value.components.some(v => Math.abs(v * 255 - Math.round(v * 255)) > 1e-9);
  node.append(technical(row, [['CSS exato', colorCSS(row.value)], ...(approximate ? [['HEX', 'Aproximação sRGB de 8 bits; a amostra usa os componentes exatos.']] : [])]));
  return node;
}
function colors(rows, group, showHeading = true) {
  // Classificação visual; os caminhos e valores originais não são alterados.
  const sections = new Map();
  for (const row of rows) {
    const parts = row.path.split('.'), kind = parts[0] === 'primitive' ? 'Primitivos' : parts[0] === 'semantic' ? 'Semânticos' : 'Outras cores';
    const palette = kind === 'Primitivos' ? human(parts.slice(1, -1).join(' / ')) : '';
    if (!sections.has(kind)) sections.set(kind, new Map());
    const palettes = sections.get(kind); if (!palettes.has(palette)) palettes.set(palette, []); palettes.get(palette).push(row);
  }
  for (const kind of ['Primitivos', 'Semânticos', 'Outras cores']) {
    if (!sections.has(kind)) continue;
    const block = element('section', undefined, 'token-group'); block.dataset.colorGroup = kind;
    if (showHeading) block.append(element('h4', kind, 'group-title')); group.append(block);
    for (const [palette, items] of sections.get(kind)) {
      if (palette) block.append(element('h5', palette, 'palette-title'));
      const grid = element('div', undefined, 'color-grid'); items.forEach(row => grid.append(colorTile(row))); block.append(grid);
    }
  }
}
function typography(row, fallback) {
  const node = article(row, 'type-row'); node.append(name(row, 'h4'));
  if (row.error) { node.append(notice(row.error)); return node; }
  const v = row.value, role = leaf(row.path).toLowerCase();
  const text = role.includes('heading') ? 'Clareza em cada palavra.' : role.includes('label') ? 'Continuar · Ver detalhes' : 'Uma linguagem visual consistente torna a informação mais clara e a experiência mais fácil de usar.';
  const specimen = element('div', text, 'sample type-sample');
  const families = [...new Set([...(Array.isArray(v.fontFamily) ? v.fontFamily : [v.fontFamily]), ...(Array.isArray(fallback) ? fallback : [fallback])])];
  specimen.style.fontFamily = familyCSS(families); specimen.style.fontSize = measure(v.fontSize);
  specimen.style.fontWeight = String(v.fontWeight); specimen.style.lineHeight = String(v.lineHeight); specimen.style.letterSpacing = measure(v.letterSpacing);
  const frame = element('div', undefined, 'specimen-frame'); frame.append(specimen);
  node.append(frame, properties([['Família', families.join(', ')], ['Tamanho', displayMeasure(v.fontSize)], ['Peso', displayNumber(v.fontWeight)], ['Linha', `${displayNumber(v.lineHeight)}×`], ['Tracking', displayMeasure(v.letterSpacing)]]), technical(row, [['Tamanho exato', measure(v.fontSize)], ['Linha exata', `${v.lineHeight}×`], ['Tracking exato', measure(v.letterSpacing)]]));
  return node;
}
function typeScale(model, query) {
  const source = model.sections.typographyScale || [];
  const rows = source.length ? source : (model.sections.typography || []).filter(row => !row.error).map(row => ({ ...row, value: row.value.fontSize, field: 'fontSize' }));
  const block = element('section', undefined, 'type-scale'); block.dataset.typographyScale = '';
  block.append(element('h4', 'Escala tipográfica', 'group-title'));
  const filtered = rows.filter(row => row.path.toLowerCase().includes(query)).sort((a, b) => {
    if (a.error || b.error) return 0;
    return a.value.unit.localeCompare(b.value.unit) || a.value.value - b.value.value;
  });
  if (!filtered.length) { block.append(element('p', 'Nenhum tamanho neste mapeamento ou filtro.', 'empty')); return block; }
  const list = element('div', undefined, 'type-scale-list');
  const style = (model.sections.typography || []).find(row => !row.error)?.value;
  for (const row of filtered) {
    const step = element('div', undefined, 'type-scale-step'); step.dataset.scaleToken = row.path; step.append(name(row));
    if (row.error) { step.append(notice(row.error)); list.append(step); continue; }
    if (row.value.value <= 0) { step.append(notice('Tamanho tipográfico deve ser positivo')); list.append(step); continue; }
    const sample = element('div', 'Aa · Ag', 'type-scale-sample'); sample.style.fontSize = measure(row.value);
    if (style) {
      const families = Array.isArray(style.fontFamily) ? style.fontFamily : [style.fontFamily];
      const fallback = Array.isArray(model.fontFallback) ? model.fontFallback : [model.fontFallback];
      sample.style.fontFamily = familyCSS([...new Set([...families, ...fallback])]);
    }
    step.append(sample, element('span', displayMeasure(row.value), 'measurement'), technical(row, [['Tamanho exato', measure(row.value)], ...(row.field ? [['Campo', row.field]] : [])]));
    list.append(step);
  }
  block.append(list); return block;
}
function spacing(row) {
  const node = article(row, 'scale-row'); node.append(name(row));
  if (row.error) { node.append(notice(row.error)); return node; }
  if (row.value.value < 0) { node.append(notice('Spacing negativo não suportado neste catálogo')); return node; }
  const track = element('div', undefined, 'ruler-window'); track.tabIndex = 0;
  track.setAttribute('role', 'img'); track.setAttribute('aria-label', `${row.path}: ${measure(row.value)}, representação ampliada 4 vezes`);
  const line = element('div', undefined, 'ruler-line'), distance = element('div', undefined, 'sample ruler-distance');
  distance.style.width = `calc(${measure(row.value)} * 4)`; distance.dataset.zoom = '4';
  distance.setAttribute('aria-hidden', 'true'); distance.append(element('span', undefined, 'ruler-fill'));
  line.append(element('span', undefined, 'ruler-anchor'), distance, element('span', undefined, 'ruler-anchor')); track.append(line);
  node.append(track, element('span', measure(row.value), 'measurement'), technical(row, [['Régua', 'Ampliação visual de 4×; não altera a distância do token.']])); return node;
}
function border(row, category) {
  const node = article(row, 'border-tile');
  if (row.error) { node.append(name(row), notice(row.error)); return node; }
  const stage = element('div', undefined, 'shape-stage'), shape = element('div', undefined, 'sample shape');
  let value;
  if (category === 'radius' && row.type === 'number' && row.value === 0.5) {
    shape.style.borderRadius = `${Math.min(120, 48) * row.value}px`; shape.textContent = 'Full'; value = 'full';
    stage.classList.add('full-shapes'); node.classList.add('full-radius-tile');
    const capsule = element('figure'); capsule.append(shape, element('figcaption', 'Cápsula')); stage.append(capsule);
    const circle = element('div', 'Full', 'sample shape full-circle'); circle.style.width = '48px'; circle.style.height = '48px'; circle.style.borderRadius = `${48 * row.value}px`;
    circle.setAttribute('role', 'img'); circle.setAttribute('aria-label', 'Círculo full de 48 × 48px');
    const figure = element('figure'); figure.append(circle, element('figcaption', 'Círculo')); stage.append(figure);
  } else {
    if (row.type !== 'dimension' || row.value.value < 0) { node.append(name(row), notice('Borda exige dimensão não negativa ou full Prismo')); return node; }
    value = measure(row.value);
    if (category === 'radius') shape.style.borderRadius = value;
    else { shape.style.borderWidth = value; if (row.value.value === 0) shape.textContent = 'Sem borda'; }
  }
  shape.setAttribute('role', 'img'); shape.setAttribute('aria-label', `${human(leaf(row.path))}: ${value}`); if (value !== 'full') stage.append(shape);
  const caption = element('div', undefined, 'shape-label'); caption.append(name(row), element('span', value, 'measurement'));
  node.append(stage, caption, technical(row, value === 'full' ? [['Amostra', 'Cápsula 120 × 48px e círculo 48 × 48px; raio de 24px, metade do menor lado.']] : [])); return node;
}
function elevation(row, surfaces, context) {
  const node = article(row, 'elevation-tile');
  if (row.error) { node.append(name(row), notice(row.error)); return node; }
  const layers = Array.isArray(row.value) ? row.value : [row.value];
  const stage = element('div', undefined, 'elevation-stage'), plane = element('div', layers.length ? 'Superfície elevada' : 'Sem sombra', 'sample shadow-sample');
  stage.style.backgroundColor = context.background || surfaces.background || 'Canvas';
  plane.style.backgroundColor = context.surface || surfaces.surface || 'Canvas';
  plane.style.color = context.text || surfaces.text || 'CanvasText'; plane.style.boxShadow = shadowCSS(row.value); stage.append(plane);
  node.append(stage, name(row, 'h4'));
  if (!layers.length) node.append(element('p', 'Sem camadas de sombra', 'shadow-caption'));
  layers.forEach((layer, i) => {
    if (layers.length > 1) node.append(element('p', `Camada ${i + 1}${layer.inset ? ' · interna' : ''}`, 'shadow-caption'));
    const metrics = element('div', undefined, 'layer-metrics');
    for (const value of [`X ${measure(layer.offsetX)}`, `Y ${measure(layer.offsetY)}`, `Blur ${measure(layer.blur)}`, `Spread ${measure(layer.spread)}`, `Alpha ${percent(layer.color.alpha)}`]) metrics.append(element('span', value));
    node.append(metrics);
  });
  node.append(technical(row, [['box-shadow', shadowCSS(row.value)]])); return node;
}
function renderRows(rows, category, group, model) {
  if (category === 'colors') { colors(rows, group, false); return; }
  if (category === 'spacing') {
    group.append(element('p', 'Réguas ampliadas 4× para inspeção. As medidas indicadas são os valores originais.', 'scale-note'));
    const kinds = new Map();
    for (const row of rows) { const parts = row.path.split('.'), kind = ['gap', 'padding', 'margin'].find(v => parts.includes(v)) || 'Escala'; if (!kinds.has(kind)) kinds.set(kind, []); kinds.get(kind).push(row); }
    for (const [kind, items] of kinds) {
      const block = element('section', undefined, 'token-group'); block.append(element('h4', human(kind), 'group-title'));
      const list = element('div', undefined, 'scale-list'); items.forEach(row => list.append(spacing(row))); block.append(list); group.append(block);
    }
    return;
  }
  if (category === 'elevation') model.elevationErrors.forEach(error => group.append(notice(error)));
  if (category === 'elevation' && Object.keys(model.elevationSurfaces).length) group.append(element('p', 'Fundo de inspeção para tornar as sombras legíveis. As camadas de sombra são as originais do tema.', 'inspection-note'));
  const list = element('div', undefined, category === 'typography' ? 'type-list' : category === 'elevation' ? 'elevation-grid' : 'shape-grid');
  for (const row of rows) {
    try { list.append(category === 'typography' ? typography(row, model.fontFallback) : category === 'elevation' ? elevation(row, model.surfaces, model.elevationSurfaces) : border(row, category)); }
    catch (error) { const item = article(row); item.append(name(row), notice(error.message)); list.append(item); }
  }
  group.append(list);
}

export function renderFoundations(tokens, config, { section = 'all', mode = 'compare' } = {}) {
  const root = element('main', undefined, 'prismo-catalog'); root.dataset.mode = mode;
  root.append(element('style', css));
  const inner = element('div', undefined, 'catalog-inner'); root.append(inner);
  inner.append(element('h1', labels[section] || 'Fundações'), element('p', descriptions[section] || 'Cor, tipografia, ritmo, forma e profundidade em uma linguagem visual compartilhada.', 'intro'));
  const toolbar = element('div', undefined, 'toolbar'), modeLabel = element('label', 'Temas'), select = element('select');
  for (const [value, title] of [['compare', 'Comparar claro e escuro'], ['light', 'Claro'], ['dark', 'Escuro']]) { const option = element('option', title); option.value = value; select.append(option); }
  select.value = ['compare', 'light', 'dark'].includes(mode) ? mode : 'compare'; modeLabel.append(select);
  const searchLabel = element('label', 'Filtrar tokens', 'search-label'), search = element('input'); search.type = 'search'; search.placeholder = 'Buscar pelo nome ou caminho'; searchLabel.append(search);
  const id = ++sequence; select.id = `prismo-mode-${id}`; modeLabel.htmlFor = select.id; search.id = `prismo-filter-${id}`; searchLabel.htmlFor = search.id;
  toolbar.append(modeLabel, searchLabel); inner.append(toolbar);
  const shared = element('div', undefined, 'shared-foundations');
  const panels = element('div', undefined, 'panels'); inner.append(shared, panels);
  function draw() {
    root.dataset.mode = select.value; panels.replaceChildren(); shared.replaceChildren();
    const themes = select.value === 'compare' ? ['light', 'dark'] : [select.value];
    const models = new Map();
    for (const theme of new Set([...Object.keys(config.themes), ...themes])) {
      try { models.set(theme, { model: catalog(tokens, config, theme) }); }
      catch (error) { models.set(theme, { error }); }
    }
    const query = search.value.toLowerCase();
    if (section === 'all' || section === 'colors') {
      const unique = new Map();
      for (const { model } of models.values()) for (const row of model?.sections.colors || []) {
        if (row.path.startsWith('primitive.')) unique.set(row.path, row);
      }
      const block = element('section', undefined, 'shared-palette'); block.dataset.foundation = 'color-primitives';
      const header = element('header', undefined, 'foundation-header'); header.append(element('h2', 'Paletas primitivas'), element('p', 'Escalas compartilhadas, exibidas uma única vez.')); block.append(header);
      const rows = [...unique.values()].filter(row => row.path.toLowerCase().includes(query));
      if (rows.length) colors(rows, block, false); else block.append(element('p', 'Nenhum primitivo neste mapeamento ou filtro.', 'empty'));
      shared.append(block);
    }
    for (const theme of themes) {
      const panel = element('section', undefined, 'panel'); panel.dataset.theme = theme;
      const header = element('header', undefined, 'panel-header'); header.append(element('h2', theme === 'light' ? 'Claro' : 'Escuro'), element('span', 'Tema', 'theme-caption')); panel.append(header); panels.append(panel);
      try {
        if (models.get(theme).error) throw models.get(theme).error;
        const model = models.get(theme).model, surfaces = model.surfaces;
        panel.style.backgroundColor = surfaces.background || 'Canvas'; panel.style.color = surfaces.text || 'CanvasText';
        panel.style.setProperty('--prismo-accent', surfaces.accent || surfaces.text || 'currentColor');
        panel.style.setProperty('--prismo-line', surfaces.border || 'currentColor'); panel.style.setProperty('--prismo-surface', surfaces.surface || 'Canvas');
        if (!Object.keys(config.themes[theme]).length) panel.append(notice('Superfície do tema não mapeada; usando cores de apresentação do navegador.'));
        model.errors.forEach(error => panel.append(notice(error)));
        const sections = section === 'all' ? ['colors', 'typography', 'spacing', 'radius', 'width', 'elevation'] : section === 'borders' ? ['radius', 'width'] : [section];
        for (const category of sections) {
          const group = element('section', undefined, 'foundation'); group.dataset.foundation = category;
          const heading = element('header', undefined, 'foundation-header');
          const titles = section === 'all' ? { radius: 'Raios', width: 'Espessuras', ...labels } : { colors: 'Cores semânticas', typography: 'Estilos', spacing: 'Escalas', radius: 'Raios', width: 'Espessuras', elevation: 'Níveis' };
          heading.append(element('h3', titles[category] || category));
          if (section === 'all' && descriptions[category]) heading.append(element('p', descriptions[category])); group.append(heading); panel.append(group);
          const rows = (model.sections[category] || []).filter(row => (category !== 'colors' || !row.path.startsWith('primitive.')) && row.path.toLowerCase().includes(query));
          if (category === 'typography') group.append(typeScale(model, query));
          if (!rows.length) group.append(element('p', 'Nenhum token neste mapeamento ou filtro.', 'empty'));
          else renderRows(rows, category, group, model);
        }
      } catch (error) { panel.append(notice(error.message)); }
    }
  }
  select.addEventListener('change', draw); search.addEventListener('input', draw); draw(); return root;
}
