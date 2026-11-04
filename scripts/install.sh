#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo 'Uso: bash scripts/install.sh --mode symlink|copy [--update] PROJETO'
}
fail() { echo "Erro: $*" >&2; exit 1; }
mode='' project='' update=0
while (($#)); do
  case "$1" in
    --mode)
      (($# >= 2)) || fail '--mode exige um valor.'
      [[ -z "$mode" ]] || fail '--mode repetido.'
      mode=$2; shift 2 ;;
    --update) update=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; [[ -z "$project" ]] || fail 'Informe somente um projeto.'; (($# == 1)) || fail 'Informe um projeto.'; project=$1; shift ;;
    -*) fail "Opção desconhecida: $1" ;;
    *) [[ -z "$project" ]] || fail 'Informe somente um projeto.'; project=$1; shift ;;
  esac
done
[[ "$mode" == symlink || "$mode" == copy ]] || fail 'Escolha --mode symlink ou copy.'
[[ -n "$project" && -d "$project" ]] || fail 'O projeto deve ser um diretório existente.'
command -v realpath >/dev/null || fail 'realpath é necessário.'
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
source_dir="$repo/skills/prismo"
[[ -f "$source_dir/SKILL.md" && ! -L "$source_dir" ]] || fail 'Skill de origem inválida.'
project=$(cd -- "$project" && pwd -P)
# Não atravesse links nos diretórios controlados pelo instalador.
for parent in "$project/.agents" "$project/.agents/skills"; do
  [[ ! -L "$parent" ]] || fail "Diretório pai é symlink: $parent"
  [[ ! -e "$parent" || -d "$parent" ]] || fail "Diretório pai inválido: $parent"
done
dest="$project/.agents/skills/prismo"
case "$dest/" in "$source_dir/"*) fail 'Destino está dentro da origem.' ;; esac
case "$source_dir/" in "$dest/"*) fail 'Destino contém a origem.' ;; esac
mkdir -p -- "$project/.agents/skills"
lock="$project/.agents/.prismo-install.lock"
mkdir -- "$lock" 2>/dev/null || fail "Instalação em andamento ou lock residual: $lock"
stage='' backup='' moved=0
cleanup() {
  local status=$?
  if ((moved)) && [[ ! -e "$dest" && ! -L "$dest" ]]; then
    mv -- "$backup/prismo" "$dest" || echo "Restaure manualmente: $backup/prismo" >&2
  fi
  [[ -z "$stage" ]] || rm -rf -- "$stage"
  rmdir -- "$lock"
  return "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
if [[ -e "$dest" || -L "$dest" ]]; then
  ((update)) || fail 'Destino já existe. Use --update para uma instalação reconhecida.'
  if [[ -L "$dest" ]]; then
    [[ "$(realpath -m -- "$dest")" == "$source_dir" ]] || fail 'Symlink não pertence a esta origem.'
  elif [[ -d "$dest" && -f "$dest/.prismo-install" && ! -L "$dest/.prismo-install" ]]; then
    [[ "$(cat -- "$dest/.prismo-install")" == 'prismo-local-copy-v1' ]] || fail 'Marcador de instalação inválido.'
  else
    fail 'Destino não reconhecido; nenhum arquivo foi substituído.'
  fi
fi
stage=$(mktemp -d "$project/.agents/.prismo-stage.XXXXXX")
if [[ "$mode" == symlink ]]; then
  ln -s -- "$source_dir" "$stage/prismo"
else
  cp -R -- "$source_dir" "$stage/prismo"
  printf '%s\n' 'prismo-local-copy-v1' > "$stage/prismo/.prismo-install"
fi
if [[ -e "$dest" || -L "$dest" ]]; then
  backup=$(mktemp -d "$project/.agents/.prismo-backup.XXXXXX")
  mv -- "$dest" "$backup/prismo"
  moved=1
fi
mv -- "$stage/prismo" "$dest"
moved=0
printf 'Instalado (%s): %s\n' "$mode" "$dest"
[[ -z "$backup" ]] || printf 'Backup preservado: %s/prismo\n' "$backup"
