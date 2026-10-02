"""Gera o arquivo estático dos artigos a partir do Markdown em fonte/.

    python3 gerar.py

Escreve <slug>/index.html, <slug>/<slug>.pdf, index.html e sitemap.xml. O que
vai para o GitHub Pages é o HTML gerado, commitado junto com a fonte: quem
clonar o repositório daqui a 20 anos lê o artigo sem rodar nada.

Escolhas pensando em durar:
- HTML e CSS puros, sem JavaScript, sem CDN. As fontes moram em fontes/, e se
  faltarem a página cai para a fonte do sistema e continua legível.
- Fotos em JPEG, o formato com mais chance de abrir em qualquer coisa em 2046.
- Sem <link rel=canonical> para o site original. Enquanto ele existir o Google
  escolhe sozinho, e quando ele sair do ar esta cópia não fica apontando para
  um endereço morto.
"""
import html
import json
import pathlib
import re
import subprocess

import markdown

RAIZ = pathlib.Path(__file__).parent
BASE = 'https://hermesalvesbr.github.io/artigos'

ARTIGOS = [
    {
        'slug': 'daqui-de-araripina',
        'fonte': RAIZ / 'fonte' / '2026-10-02-daqui-de-araripina.md',
        'data': '2026-10-02',
        'data_extenso': '2 de outubro de 2026',
        'original': 'https://partidonovoararipe.com.br/daqui-de-araripina',
        'destaque': ('img/hermes-alves-e-renan-bihum.jpg', 1200, 900),
        'capa': 'img/capa-1200x630.jpg',
        'fotos': {
            'novo-pe-grupo-2025-12-10.jpg': ('img/novo-pernambuco-2025-12.jpg', 1200, 675),
        },
        'palavras': ['Araripina', 'Sertão do Araripe', 'Renan Bihum', 'Hermes Alves',
                     'Partido NOVO', 'Eleições 2026', 'Pernambuco'],
    },
]

CSS = """
@font-face { font-family: 'Bebas Neue'; src: url(../fontes/bebas-neue.woff2) format('woff2'); font-display: swap; }
@font-face { font-family: Inter; src: url(../fontes/inter.woff2) format('woff2'); font-weight: 100 900; font-display: swap; }
:root { --azul: #1a2644; --laranja: #ec671c; --texto: #1d2330; --cinza: #5b6474; --fundo: #ffffff; --linha: #d9dde5; }
@media (prefers-color-scheme: dark) {
  :root { --texto: #e9ecf0; --cinza: #a9b1bf; --fundo: #121a2e; --azul: #e9ecf0; --linha: #2b3550; }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--fundo); color: var(--texto);
       font: 1.125rem/1.7 Georgia, 'Noto Serif', 'DejaVu Serif', serif; }
main { max-width: 720px; margin: 0 auto; padding: 32px 16px 64px; }
.nota { font: 0.9rem/1.5 Inter, system-ui, sans-serif; color: var(--cinza);
        border: 1px solid var(--linha); border-left: 4px solid var(--laranja);
        border-radius: 6px; padding: 12px 14px; margin: 0 0 28px; }
.nota a, .rodape a { color: inherit; }
.rotulo { font: 600 0.8rem Inter, system-ui, sans-serif; letter-spacing: 0.18em;
          text-transform: uppercase; color: var(--laranja); margin: 0 0 6px; }
h1 { font: 3rem/1 'Bebas Neue', Impact, 'Arial Narrow', sans-serif; text-transform: uppercase;
     color: var(--azul); margin: 0 0 14px; letter-spacing: 0.01em; }
.sub { font: 500 1.15rem/1.5 Inter, system-ui, sans-serif; color: var(--cinza); margin: 0 0 24px; }
figure { margin: 28px 0; }
figure img { width: 100%; height: auto; display: block; border-radius: 8px; }
figcaption { font: 0.85rem/1.45 Inter, system-ui, sans-serif; color: var(--cinza); margin-top: 8px; }
h2 { font: 2rem/1.1 'Bebas Neue', Impact, 'Arial Narrow', sans-serif; color: var(--laranja);
     margin: 40px 0 10px; letter-spacing: 0.02em; }
p { margin: 0 0 16px; }
blockquote { margin: 22px 0; padding: 2px 0 2px 18px; border-left: 4px solid var(--laranja);
             font-style: italic; font-size: 1.22rem; line-height: 1.5; }
blockquote p { margin: 0; }
a { color: var(--laranja); }
hr { border: 0; border-top: 1px solid var(--linha); margin: 40px 0 16px; }
.rodape { font: 0.85rem/1.5 Inter, system-ui, sans-serif; color: var(--cinza); }
.lista { list-style: none; padding: 0; }
.lista li { margin: 0 0 24px; }
.lista a { font: 1.8rem/1.1 'Bebas Neue', Impact, sans-serif; text-decoration: none; }
@media (min-width: 600px) { h1 { font-size: 4rem; } main { padding-top: 56px; } }
@media print {
  :root { --texto: #1d2330; --cinza: #5b6474; --fundo: #fff; --azul: #1a2644; --linha: #d9dde5; }
  @page { size: A4; margin: 16mm 18mm; }
  body { font-size: 10.5pt; }
  main { max-width: none; padding: 0; }
  figure, blockquote { break-inside: avoid; }
  h2 { break-after: avoid; }
}
"""


def pagina_artigo(a: dict) -> tuple[str, str, str]:
    texto = a['fonte'].read_text()
    titulo = re.search(r'^# (.+)$', texto, re.M)[1]
    subtitulo = re.search(r'^### (.+)$', texto, re.M)[1]
    legenda_destaque = re.search(r'!\[[^\]]*\]\([^)]*\)\n\*(.+?)\*', texto)[1]

    corpo = markdown.markdown(texto.split('\n---\n', 1)[1])

    def figura(m: re.Match) -> str:
        src, w, h = a['fotos'][m[2]]
        return (f'<figure><img src="{src}" width="{w}" height="{h}" loading="lazy" alt="{m[1]}">'
                f'<figcaption>{m[3]}</figcaption></figure>')

    corpo = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" />\s*<em>(.+?)</em></p>', figura, corpo, flags=re.S)
    # Links relativos do site original viram absolutos: aqui eles não existem.
    corpo = corpo.replace('href="/', 'href="https://partidonovoararipe.com.br/')
    corpo = re.sub(r'<hr />\s*<p><em>(Propaganda eleitoral.+?)</em></p>\s*$',
                   r'<hr /><p class="rodape">\1</p>', corpo, flags=re.S)

    src, w, h = a['destaque']
    url = f"{BASE}/{a['slug']}/"
    ld = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': titulo,
        'description': subtitulo,
        'datePublished': a['data'],
        'inLanguage': 'pt-BR',
        'image': f"{url}{a['capa']}",
        'url': url,
        'isBasedOn': a['original'],
        'author': {'@type': 'Person', 'name': 'Hermes Alves', 'url': 'https://www.instagram.com/hermesalvesbr/'},
        'about': [{'@type': 'Person', 'name': 'Renan Bihum'}, {'@type': 'Person', 'name': 'Hermes Alves'},
                  {'@type': 'Place', 'name': 'Araripina, Pernambuco, Brasil'}],
        'keywords': ', '.join(a['palavras']),
    }
    e = html.escape
    pagina = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)} — Renan Bihum e Hermes Alves</title>
<meta name="description" content="{e(subtitulo)}">
<meta name="keywords" content="{e(', '.join(a['palavras']))}">
<meta name="author" content="Hermes Alves">
<meta name="date" content="{a['data']}">
<meta property="og:type" content="article">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(subtitulo)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}{a['capa']}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="article:published_time" content="{a['data']}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
<main>
<p class="nota">Publicado originalmente em {a['data_extenso']}, em
<a href="{a['original']}">partidonovoararipe.com.br/{a['slug']}</a>, durante a campanha
eleitoral de 2026. Esta é a cópia de arquivo, mantida por Hermes Alves.
<a href="{a['slug']}.pdf">Baixar em PDF</a>.</p>
<p class="rotulo">Artigo · {a['data_extenso']}</p>
<h1>{e(titulo)}</h1>
<p class="sub">{e(subtitulo)}</p>
<figure><img src="{src}" width="{w}" height="{h}" fetchpriority="high" alt="Hermes Alves e Renan Bihum, lado a lado, com camisas do NOVO, diante do painel NOVO 30 Pernambuco"><figcaption>{legenda_destaque}</figcaption></figure>
{corpo}
<p class="rodape"><a href="../">Outros artigos</a></p>
</main>
</body>
</html>
"""
    return titulo, subtitulo, pagina


def main() -> None:
    itens, urls = [], [f'{BASE}/']
    for a in ARTIGOS:
        titulo, subtitulo, pagina = pagina_artigo(a)
        pasta = RAIZ / a['slug']
        (pasta / 'index.html').write_text(pagina)
        subprocess.run([
            'google-chrome', '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
            f"--print-to-pdf={pasta / (a['slug'] + '.pdf')}", (pasta / 'index.html').as_uri(),
        ], check=True, capture_output=True)
        itens.append(f'<li><a href="{a["slug"]}/">{html.escape(titulo)}</a>'
                     f'<br><span class="rodape">{a["data_extenso"]} · {html.escape(subtitulo)}</span></li>')
        urls.append(f"{BASE}/{a['slug']}/")

    (RAIZ / 'index.html').write_text(f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Artigos — Hermes Alves</title>
<meta name="description" content="Arquivo de artigos sobre Araripina e o Sertão do Araripe, mantido por Hermes Alves.">
<style>{CSS.replace('../fontes/', 'fontes/')}</style>
</head>
<body>
<main>
<p class="rotulo">Arquivo</p>
<h1>Artigos</h1>
<p class="sub">Textos sobre Araripina e o Sertão do Araripe, guardados aqui para não se perderem.
Mantido por Hermes Alves.</p>
<ul class="lista">
{chr(10).join(itens)}
</ul>
</main>
</body>
</html>
""")

    (RAIZ / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls)
        + '</urlset>\n')
    # Sem robots.txt: num site de projeto ele ficaria em /artigos/robots.txt, que
    # o buscador ignora. O sitemap se envia pelo Search Console.
    print('\n'.join(urls))


if __name__ == '__main__':
    main()
