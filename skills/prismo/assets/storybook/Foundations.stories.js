// Adapte apenas o caminho de import e o render ao renderer Storybook existente.
import tokens from './tokens.json';
import config from './catalog.config.mjs';
import { renderFoundations } from './catalog.mjs';

export default {
  title: 'Prismo/Foundations',
  parameters: { layout: 'fullscreen' },
  args: { mode: 'compare' },
  argTypes: { mode: { control: 'select', options: ['compare', 'light', 'dark'] } },
};
const render = (section) => (args) => renderFoundations(tokens, config, { section, mode: args.mode });
export const Colors = { render: render('colors') };
export const Typography = { render: render('typography') };
export const Spacing = { render: render('spacing') };
export const Borders = { render: render('borders') };
export const Elevation = { render: render('elevation') };
