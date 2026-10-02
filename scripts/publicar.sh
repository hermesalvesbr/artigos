#!/usr/bin/env bash
# Abre o arquivo ao público: repositório público + GitHub Pages + aviso aos buscadores.
# Roda pelo timer artigos-publicar.timer (systemd --user) em 05/10/2026 18:00.
# A trava de data existe porque antes disso o artigo é propaganda eleitoral
# hospedada fora do país (Lei 9.504, art. 57-B) e, em 04/10, publicação nova é crime.
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=publicar.log
exec >>"$LOG" 2>&1
echo "== $(date -Is) =="

if [ "$(date +%Y%m%d)" -lt 20261005 ]; then
  echo "antes de 05/10/2026 — nada a fazer"; exit 0
fi

REPO=hermesalvesbr/artigos
BASE=https://hermesalvesbr.github.io/artigos
KEY=453b0d7ea615ef7cc4a65b8789a6bf19

vis=$(gh repo view $REPO --json visibility -q .visibility) || { echo "gh falhou"; exit 1; }
if [ "$vis" != "PUBLIC" ]; then
  gh repo edit $REPO --visibility public --accept-visibility-change-consequences || exit 1
  echo "repositório público"
fi
gh api repos/$REPO/pages >/dev/null 2>&1 \
  || gh api -X POST repos/$REPO/pages -f 'source[branch]=main' -f 'source[path]=/' >/dev/null \
  || { echo "falhou ao ativar o Pages"; exit 1; }
echo "Pages ativo"

for i in $(seq 60); do
  c=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/daqui-de-araripina/?cb=$(date +%s)")
  [ "$c" = 200 ] && break; sleep 10
done
echo "artigo responde $c"
[ "$c" = 200 ] || exit 1

# IndexNow (Bing, Yandex, Seznam, Naver). O Google não usa IndexNow: para ele, Search Console.
curl -s -o /dev/null -w "IndexNow %{http_code}\n" -X POST https://api.indexnow.org/indexnow \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d "{\"host\":\"hermesalvesbr.github.io\",\"key\":\"$KEY\",\"keyLocation\":\"$BASE/$KEY.txt\",\"urlList\":[\"$BASE/\",\"$BASE/daqui-de-araripina/\",\"$BASE/daqui-de-araripina/daqui-de-araripina.pdf\"]}"

systemctl --user disable artigos-publicar.timer 2>/dev/null
command -v notify-send >/dev/null && notify-send "Artigos no ar" "$BASE/daqui-de-araripina/"
echo "pronto"
