// Somente caminhos. Ajuste o mapeamento aos tokens e decisões do consumidor.
export default {
  themes: {
    light: { background: 'semantic.light.background', surface: 'semantic.light.surface', text: 'semantic.light.text', border: 'semantic.light.border', accent: 'semantic.light.primary' },
    dark: { background: 'semantic.dark.background', surface: 'semantic.dark.surface', text: 'semantic.dark.text', border: 'semantic.dark.border', accent: 'semantic.dark.primary' },
  },
  fontFallback: null, // Caminho de token fontFamily adicional, se aprovado nas decisões.
  // Fundo de inspeção, sem alterar as cores ou sombras do tema. Ajuste aos caminhos do projeto.
  elevationSurfaces: {
    dark: { background: 'primitive.neutral.800', surface: 'semantic.dark.surface', text: 'semantic.dark.text' },
  },
  collections: {
    colors: { prefixes: ['primitive.brand', 'primitive.neutral', 'semantic.{theme}'], type: 'color' },
    typography: { prefixes: ['semantic.typography'], type: 'typography' },
    typographyScale: { prefixes: ['primitive.typography.size'], type: 'dimension' },
    spacing: { prefixes: ['semantic.spacing'], type: 'dimension' },
    radius: { prefixes: ['semantic.borders.radius'] },
    width: { prefixes: ['semantic.borders.width'], type: 'dimension' },
    elevation: { prefixes: ['semantic.elevation.{theme}'], type: 'shadow' },
  },
};
