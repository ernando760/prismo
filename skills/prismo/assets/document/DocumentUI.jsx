import React, { useEffect, useRef, useState } from 'react';
import { renderFoundations, colorHex, displayNumber } from '../storybook/catalog.mjs';
import { tokenIndex, resolver, dimensionCSS, familyCSS, shadowCSS } from '../storybook/dtcg.mjs';
import './document.css';

// Camada editorial. Nenhum token, componente de produto ou regra de marca embutidos.
export function DocLayout({ children }) {
  return <div className="prismo-docs">{children}</div>;
}
export function Lead({ children }) {
  return <div className="prismo-doc-lead">{children}</div>;
}
export function Pending({ children = 'Informação não definida nas fontes consultadas.' }) {
  return <p className="prismo-doc-pending"><strong>Pendente.</strong> {children}</p>;
}
export function Example({ children, caption, label = 'Exemplo de aplicação' }) {
  return <figure className="prismo-doc-example">
    <div className="prismo-doc-stage" role="group" aria-label={label}>
      {children ?? <Pending>Vincular uma demonstração existente ou exemplo aprovado.</Pending>}
    </div>
    {caption && <figcaption>{caption}</figcaption>}
  </figure>;
}
export function ExampleGrid({ children }) {
  return <div className="prismo-doc-examples">{children}</div>;
}
export function Guidance({ recommended = [], avoid = [] }) {
  return <div className="prismo-doc-guidance">
    <section><h3>Quando usar</h3>{recommended.length ? <ul>{recommended.map(item => <li key={item}>{item}</li>)}</ul> : <Pending>Confirmar usos recomendados.</Pending>}</section>
    <section><h3>Quando evitar</h3>{avoid.length ? <ul>{avoid.map(item => <li key={item}>{item}</li>)}</ul> : <Pending>Confirmar restrições e alternativas.</Pending>}</section>
  </div>;
}
export function TechnicalDetails({ children, summary = 'Detalhes técnicos e fontes' }) {
  return <details className="prismo-doc-details"><summary>{summary}</summary><div>{children}</div></details>;
}

function safeLink(href) {
  // Apenas links navegáveis; não embute HTML/JS nem transforma caminhos em URLs publicadas.
  return typeof href === 'string' && /^(https?:\/\/[^\s]+|\/(?!\/)[^\s]*|#[^\s]+)$/.test(href) && !/[<>"'\\]/.test(href);
}
export function CatalogLink({ href, children = 'Abrir no catálogo', local }) {
  if (!safeLink(href)) return <Pending>{local ? <>Catálogo local: <code>{local}</code>. Link publicado não informado.</> : 'Referência de catálogo ainda não confirmada.'}</Pending>;
  return <p className="prismo-doc-catalog-link"><a href={href}>{children}<span aria-hidden="true"> →</span></a></p>;
}

// A amostra é a mesma do Storybook; adaptamos apenas enquadramento/outline da página.
function frameCatalog(node) {
  const root = document.createElement('div');
  for (const attr of node.attributes) root.setAttribute(attr.name, attr.value);
  root.append(...node.childNodes);
  root.querySelector('.catalog-inner > h1')?.remove();
  root.querySelector('.catalog-inner > .intro')?.remove();
  function outline() {
    for (const old of root.querySelectorAll('h2:not([data-doc-heading]),h3:not([data-doc-heading]),h4:not([data-doc-heading]),h5:not([data-doc-heading])')) {
      const next = document.createElement(`h${Math.min(6, Number(old.tagName.slice(1)) + 1)}`);
      for (const attr of old.attributes) next.setAttribute(attr.name, attr.value);
      next.dataset.docHeading = 'true'; next.append(...old.childNodes); old.replaceWith(next);
    }
  }
  outline(); root.addEventListener('input', outline); root.addEventListener('change', outline);
  return root;
}
export function FoundationCatalog({ tokens, config, section, mode = 'compare' }) {
  const ref = useRef(null);
  const [rendered, setRendered] = useState(false);
  const [error, setError] = useState(null);
  const ready = tokens && config && ['colors', 'typography', 'spacing', 'borders', 'elevation'].includes(section);
  useEffect(() => {
    const host = ref.current;
    setError(null); setRendered(false);
    if (!ready) return;
    try {
      host.replaceChildren(frameCatalog(renderFoundations(tokens, config, { section, mode })));
      setRendered(true);
    } catch (error) { setError(error.message); }
    return () => host.replaceChildren();
  }, [tokens, config, section, mode, ready]);
  return <div className="prismo-doc-foundation">
    {(!ready || !rendered) && <Pending>{!ready ? 'Selecionar fundação e conectar tokens DTCG/configuração existentes.' : error ? `Visualização indisponível: ${error}` : 'A demonstração interativa carrega com JavaScript; consulte abaixo os valores e as fontes.'}</Pending>}
    <div ref={ref} />
  </div>;
}

// Formata só para leitura. A amostra compartilhada mantém os valores exatos.
export function readableValue(type, value) {
  const dimension = v => `${displayNumber(v.value)}${v.unit}`;
  if (type === 'color') return `${colorHex(value)}${value.alpha < 1 ? ` · alpha ${displayNumber(value.alpha * 100)}%` : ''}`;
  if (type === 'dimension') return dimension(value);
  if (type === 'number' || type === 'fontWeight') return displayNumber(value);
  if (type === 'fontFamily') return (Array.isArray(value) ? value : [value]).join(', ');
  if (type === 'typography') return `${dimension(value.fontSize)} / ${displayNumber(value.lineHeight)} · ${readableValue('fontFamily', value.fontFamily)} · peso ${value.fontWeight} · tracking ${dimension(value.letterSpacing)}`;
  if (type === 'shadow') {
    const layers = Array.isArray(value) ? value : [value];
    return layers.length ? layers.map(v => `${v.inset ? 'interna · ' : ''}X ${dimension(v.offsetX)} · Y ${dimension(v.offsetY)} · blur ${dimension(v.blur)} · spread ${dimension(v.spread)} · ${readableValue('color', v.color)}`).join('; ') : 'Sem sombra';
  }
  throw Error(`Tipo não suportado nesta visualização: ${type}`);
}
export function TokenFacts({ tokens, paths = [] }) {
  if (!tokens || !paths.length) return <Pending>Selecionar os papéis semânticos relevantes e suas fontes.</Pending>;
  let index, resolve;
  try { index = tokenIndex(tokens); resolve = resolver(index); }
  catch (error) { return <Pending>{error.message}</Pending>; }
  return <dl className="prismo-doc-token-facts">{paths.map(path => {
    try {
      const token = index.get(path), value = resolve(path);
      const alias = typeof token.value === 'string' && token.value.startsWith('{') ? token.value : null;
      const css = token.type === 'dimension' ? dimensionCSS(value) : token.type === 'shadow' ? shadowCSS(value) : token.type === 'fontFamily' ? familyCSS(value) : null;
      return <div key={path}><dt><code>{path}</code></dt><dd>
        <span className="prismo-doc-value">{readableValue(token.type, value)}</span>
        <TechnicalDetails summary="Caminho, alias e precisão">
          <p>Tipo: <code>{token.type}</code>. Fonte: <code>{path}</code>.</p>
          {alias && <p>Alias: <code>{alias}</code></p>}
          {css && <p>CSS exato: <code>{css}</code></p>}
          {token.type === 'color' && <p>HEX aproximado em sRGB de 8 bits. Componentes exatos: <code>{value.components.join(' · ')}</code>; alpha: <code>{value.alpha}</code>.</p>}
          <p>Arredondamento apenas para leitura; a fonte DTCG permanece intacta.</p>
        </TechnicalDetails>
      </dd></div>;
    } catch (error) { return <div key={path}><dt><code>{path}</code></dt><dd><Pending>{error.message}</Pending></dd></div>; }
  })}</dl>;
}
