export const dim = value => ({ value, unit: 'px' });
export const color = components => ({ colorSpace: 'srgb', components, alpha: 1 });
export const token = (type, value) => ({ $type: type, $value: value });
export function fixture() {
  return {
    primitive: { neutral: { 800: token('color', color([.18,.18,.18])) }, typography: { size: { small: token('dimension', dim(12.641975)), base: token('dimension', dim(16)), large: token('dimension', dim(28.832520)) } }, brand: { white: token('color', color([1,1,1])), black: token('color', color([0,0,0])) } },
    semantic: {
      light: Object.fromEntries(['background', 'surface', 'border', 'text', 'primary'].map(role => [role, token('color', `{primitive.brand.${role === 'text' ? 'black' : 'white'}}`)])),
      dark: Object.fromEntries(['background', 'surface', 'border', 'text', 'primary'].map(role => [role, token('color', `{primitive.brand.${role === 'text' ? 'white' : 'black'}}`)])),
      typography: { body: token('typography', { fontFamily: ['Example'], fontWeight: 400, fontSize: dim(16), lineHeight: 1.5, letterSpacing: dim(0) }) },
      spacing: { gap: { default: token('dimension', dim(8)) } },
      borders: { radius: { square: token('dimension', dim(0)), pill: token('number', .5) }, width: { default: token('dimension', dim(1)) } },
      elevation: { light: { none: token('shadow', []) }, dark: { low: token('shadow', { color: '{primitive.brand.black}', offsetX: dim(-1), offsetY: dim(2), blur: dim(4), spread: dim(-1), inset: true }) } },
    },
  };
}
