// Subconjunto DTCG usado pelas fundações Prismo. Sem valores de identidade embutidos.
const types = { color: null, dimension: null, number: null, fontFamily: null, fontWeight: null,
  typography: { fontFamily: 'fontFamily', fontWeight: 'fontWeight', fontSize: 'dimension',
    letterSpacing: 'dimension', lineHeight: 'number' },
  shadow: { color: 'color', offsetX: 'dimension', offsetY: 'dimension', blur: 'dimension', spread: 'dimension' } };
const isAlias = value => typeof value === 'string' && /^\{[^{}]+\}$/.test(value);
const finite = value => typeof value === 'number' && Number.isFinite(value);

export function tokenIndex(document) {
  const tokens = new Map();
  function visit(node, path, inherited) {
    if (!node || typeof node !== 'object' || Array.isArray(node)) throw Error(`Grupo inválido: ${path}`);
    if ('$extends' in node || '$ref' in node) throw Error(`Expanda $extends/$ref antes de visualizar: ${path}`);
    const type = node.$type ?? inherited;
    if ('$value' in node) {
      if (Object.keys(node).some(k => !k.startsWith('$'))) throw Error(`Token com filhos: ${path}`);
      tokens.set(path, { type, value: node.$value });
      return;
    }
    for (const [key, child] of Object.entries(node)) {
      if (key === '$root' || !key.startsWith('$')) {
        if (/[.{}]/.test(key)) throw Error(`Nome inválido: ${key}`);
        visit(child, path ? `${path}.${key}` : key, type);
      }
    }
  }
  visit(document, '', undefined);
  return tokens;
}

export function resolver(tokens) {
  function value(raw, type, seen) {
    if (isAlias(raw)) return resolve(raw.slice(1, -1), type, seen);
    if (!Object.hasOwn(types, type)) throw Error(`Tipo não suportado: ${type}`);
    if (type === 'dimension') {
      if (!raw || !finite(raw.value) || !['px', 'rem'].includes(raw.unit)) throw Error('Dimensão exige value finito e unit px/rem');
      return { value: raw.value, unit: raw.unit };
    }
    if (type === 'color') {
      if (!raw || raw.colorSpace !== 'srgb' || !Array.isArray(raw.components) || raw.components.length !== 3 ||
          !raw.components.every(v => finite(v) && v >= 0 && v <= 1) ||
          !finite(raw.alpha ?? 1) || (raw.alpha ?? 1) < 0 || (raw.alpha ?? 1) > 1) throw Error('Cor exige sRGB explícito e alpha 0–1');
      return { colorSpace: 'srgb', components: [...raw.components], alpha: raw.alpha ?? 1 };
    }
    if (type === 'number') {
      if (!finite(raw)) throw Error('Número não finito');
      return raw;
    }
    if (type === 'fontFamily') {
      if (typeof raw === 'string' && raw.trim()) return raw;
      if (Array.isArray(raw) && raw.length && raw.every(v => typeof v === 'string' && v.trim() && !isAlias(v))) return [...raw];
      throw Error('Família inválida');
    }
    if (type === 'fontWeight') {
      const weights = { thin: 100, hairline: 100, 'extra-light': 200, 'ultra-light': 200, light: 300,
        normal: 400, regular: 400, book: 400, medium: 500, 'semi-bold': 600, 'demi-bold': 600,
        bold: 700, 'extra-bold': 800, 'ultra-bold': 800, black: 900, heavy: 900, 'extra-black': 950, 'ultra-black': 950 };
      if (typeof raw === 'string' && Object.hasOwn(weights, raw)) return weights[raw];
      if (!finite(raw) || raw < 1 || raw > 1000) throw Error('Peso inválido');
      return raw;
    }
    if (type === 'shadow' && Array.isArray(raw)) {
      const layers = raw.map(layer => value(layer, type, seen));
      if (layers.some(Array.isArray)) throw Error('Alias de camada não pode resolver array');
      return layers;
    }
    const fields = types[type];
    if (!fields || !raw || typeof raw !== 'object' || Array.isArray(raw)) throw Error(`Tipo/valor não suportado: ${type}`);
    const result = {};
    for (const [key, fieldType] of Object.entries(fields)) {
      if (!(key in raw)) throw Error(`Campo obrigatório: ${key}`);
      result[key] = value(raw[key], fieldType, seen);
    }
    if (type === 'typography' && (result.fontSize.value <= 0 || result.lineHeight <= 0)) throw Error('Tipografia exige tamanho e linha positivos');
    if (type === 'shadow') {
      if (result.blur.value < 0 || typeof (raw.inset ?? false) !== 'boolean') throw Error('Blur/inset inválido');
      result.inset = raw.inset ?? false;
    }
    return result;
  }
  function resolve(path, expected, seen = []) {
    const token = tokens.get(path);
    if (!token) throw Error(`Token ausente: ${path}`);
    if (seen.includes(path)) throw Error(`Alias circular: ${path}`);
    if (expected && token.type !== expected) throw Error(`Tipo incompatível em ${path}: ${token.type}, esperado ${expected}`);
    return value(token.value, token.type, [...seen, path]);
  }
  return resolve;
}

export function familyCSS(value) {
  const generic = new Set(['serif', 'sans-serif', 'monospace', 'system-ui', 'ui-serif', 'ui-sans-serif', 'ui-monospace', 'ui-rounded', 'cursive', 'fantasy', 'emoji', 'math', 'fangsong']);
  return (Array.isArray(value) ? value : [value]).map(v => generic.has(v) ? v : JSON.stringify(v)).join(', ');
}
export const dimensionCSS = value => `${value.value}${value.unit}`;
export const colorCSS = value => `rgb(${value.components.map(v => v * 255).join(' ')} / ${value.alpha})`;
export function shadowCSS(value) {
  const layers = Array.isArray(value) ? value : [value];
  return layers.map(layer => `${layer.inset ? 'inset ' : ''}${['offsetX', 'offsetY', 'blur', 'spread'].map(k => dimensionCSS(layer[k])).join(' ')} ${colorCSS(layer.color)}`).join(', ') || 'none';
}

export function catalog(document, config, theme) {
  const tokens = tokenIndex(document), resolve = resolver(tokens);
  if (!Object.hasOwn(config.themes, theme)) throw Error(`Tema não mapeado: ${theme}`);
  const selected = {};
  for (const [section, selection] of Object.entries(config.collections)) {
    const { prefixes, type } = selection;
    const paths = prefixes.map(p => p.replaceAll('{theme}', theme));
    selected[section] = [];
    for (const [path, token] of tokens) {
      if (paths.some(p => path === p || path.startsWith(p + '.')) && (!type || token.type === type)) {
        try { selected[section].push({ path, type: token.type, alias: isAlias(token.value) ? token.value : null, value: resolve(path) }); }
        catch (error) { selected[section].push({ path, error: error.message }); }
      }
    }
  }
  const surfaces = {}, errors = [];
  for (const [role, path] of Object.entries(config.themes[theme])) {
    try { surfaces[role] = colorCSS(resolve(path, 'color')); }
    catch (error) { errors.push(error.message); }
  }
  let fontFallback = [];
  if (config.fontFallback) {
    try { fontFallback = resolve(config.fontFallback, 'fontFamily'); }
    catch (error) { errors.push(error.message); }
  }
  const elevationSurfaces = {}, elevationErrors = [];
  for (const [role, path] of Object.entries(config.elevationSurfaces?.[theme] || {})) {
    try { elevationSurfaces[role] = colorCSS(resolve(path, 'color')); }
    catch (error) { elevationErrors.push(`Fundo de inspeção: ${error.message}`); }
  }
  return { theme, surfaces, sections: selected, errors, fontFallback, elevationSurfaces, elevationErrors };
}
