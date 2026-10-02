# Artigos — arquivo

Cópia de arquivo de artigos sobre Araripina e o Sertão do Araripe, mantida por
Hermes Alves, para que continuem existindo (e aparecendo no Google) mesmo que o
site onde saíram primeiro saia do ar.

Publicado em **https://hermesalvesbr.github.io/artigos/**.

| Artigo | Data | Original |
|---|---|---|
| [Daqui. De Araripina. Do Araripe.](daqui-de-araripina/) | 02/10/2026 | partidonovoararipe.com.br/daqui-de-araripina |

## Como está montado

- `fonte/*.md` é o texto. `gerar.py` transforma em `<slug>/index.html`,
  `<slug>/<slug>.pdf`, `index.html` e `sitemap.xml`.
- O HTML gerado é commitado junto com a fonte. Quem clonar o repositório lê o
  artigo sem instalar nada.
- HTML e CSS puros: sem JavaScript, sem CDN, fontes em `fontes/` e fotos em
  JPEG, para abrir em qualquer coisa daqui a 20 anos.

```bash
python3 gerar.py   # precisa de python3-markdown e google-chrome (para o PDF)
```

## Por que só foi ao ar depois de 05/10/2026

O artigo nasceu durante a campanha eleitoral de 2026 e traz números de urna.
Durante a campanha:

- site de candidato precisa estar hospedado no Brasil (Lei 9.504, art. 57-B, I),
  e o GitHub Pages não está;
- blog novo de candidato precisa ser comunicado à Justiça Eleitoral;
- em 04/10, dia da eleição, publicar conteúdo novo é crime (art. 87, IV).

Por isso o repositório ficou **privado** até o fim da eleição. Depois do pleito,
o texto vira registro histórico, e a nota no topo de cada página diz onde e
quando ele saiu primeiro.

Para colocar no ar, a partir de 05/10/2026:

```bash
gh repo edit hermesalvesbr/artigos --visibility public --accept-visibility-change-consequences
gh api -X POST repos/hermesalvesbr/artigos/pages -f 'source[branch]=main' -f 'source[path]=/'
```

Depois, no Google Search Console, adicione a propriedade
`https://hermesalvesbr.github.io/artigos/` e envie `sitemap.xml`.
