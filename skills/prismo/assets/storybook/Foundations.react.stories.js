import React, { useEffect, useRef } from 'react';
import tokens from './tokens.json';
import config from './catalog.config.mjs';
import { renderFoundations } from './catalog.mjs';

// Adaptador de story; nenhum componente do Design System é criado.
function Preview({ section, mode }) {
  const ref = useRef(null);
  useEffect(() => {
    const host = ref.current;
    host.replaceChildren(renderFoundations(tokens, config, { section, mode }));
    return () => host.replaceChildren();
  }, [section, mode]);
  return React.createElement('div', { ref });
}
export default {
  title: 'Prismo/Foundations', parameters: { layout: 'fullscreen' },
  args: { mode: 'compare' },
  argTypes: { mode: { control: 'select', options: ['compare', 'light', 'dark'] } },
};
const render = section => args => React.createElement(Preview, { section, mode: args.mode });
export const Colors = { render: render('colors') };
export const Typography = { render: render('typography') };
export const Spacing = { render: render('spacing') };
export const Borders = { render: render('borders') };
export const Elevation = { render: render('elevation') };
