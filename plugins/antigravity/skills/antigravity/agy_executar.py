r"""
Ponte Claude Code -> Antigravity CLI (agy), para qualquer projeto.

Envia uma tarefa ao agente do Antigravity em modo headless, na pasta do
projeto, e imprime um resumo do resultado em JSON.

Permissões (o agy nega em silêncio qualquer comando não liberado):
  - usa <pasta>/.agent/agy-settings.json se o projeto tiver um;
  - senão, agy-settings-padrao.json (ao lado deste script): nenhum comando
    liberado, só leitura/escrita de arquivos dentro da pasta;
  - --permitir REGEX acrescenta uma regra command(regex:REGEX) só para esta
    chamada (a regex precisa casar com a linha de comando inteira).

Uso:
    python agy_executar.py "tarefa" [--pasta DIR] [--permitir REGEX ...]
                           [--timeout 15m] [--modelo SLUG] [--continuar]

Código de saída: 0 só quando o agy termina com status SUCCESS e nenhuma
ação foi negada por falta de permissão; 1 nos demais casos.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SETTINGS_PADRAO = AQUI / "agy-settings-padrao.json"


def _localizar_agy():
    candidatos = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "agy" / "bin" / "agy.exe",  # Windows
        Path.home() / ".local" / "bin" / "agy",                                  # Linux/macOS
    ]
    return shutil.which("agy") or next((str(c) for c in candidatos if c.is_file()), None)


def _carregar_settings(pasta, regras_extras):
    arquivo = pasta / ".agent" / "agy-settings.json"
    origem = arquivo if arquivo.is_file() else SETTINGS_PADRAO
    settings = json.loads(origem.read_text(encoding="utf-8"))
    if regras_extras:
        permissoes = settings.setdefault("permissions", {})
        permissoes.setdefault("allow", []).extend(f"command(regex:{r})" for r in regras_extras)
    return settings, origem


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("tarefa", help="instrução enviada ao agente do Antigravity")
    parser.add_argument("--pasta", default=os.getcwd(), help="raiz do projeto (padrão: pasta atual)")
    parser.add_argument("--permitir", action="append", default=[], metavar="REGEX",
                        help="libera comandos que casem com REGEX só nesta chamada (repetível)")
    parser.add_argument("--timeout", default="15m", help="limite de tempo (ex.: 10m); 0 espera sem limite")
    parser.add_argument("--modelo", help="slug do modelo (veja: agy models)")
    parser.add_argument("--continuar", action="store_true", help="continua a conversa mais recente")
    args = parser.parse_args()

    agy = _localizar_agy()
    if not agy:
        print(json.dumps({"ok": False, "erro": "agy não encontrado; instale o Antigravity CLI "
                          "(https://antigravity.google/docs/install/)"}, ensure_ascii=False))
        return 1

    pasta = Path(args.pasta).resolve()
    settings, origem = _carregar_settings(pasta, args.permitir)

    # Arquivo temporário evita problemas de aspas/barras ao passar JSON na linha de comando.
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(settings, tmp)
    try:
        comando = [agy, "-p", args.tarefa, "--output-format", "json",
                   "--print-timeout", args.timeout, "--settings", tmp.name]
        if args.modelo:
            comando += ["--model", args.modelo]
        if args.continuar:
            comando.append("--continue")
        proc = subprocess.run(comando, cwd=pasta, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    finally:
        os.unlink(tmp.name)

    try:
        resultado = json.loads(proc.stdout)
    except json.JSONDecodeError:
        resultado = {"status": "INVALID", "response": proc.stdout.strip()}

    # No modo headless, comandos sem permissão são negados em silêncio (status
    # continua SUCCESS); o sinal vem em denied_actions e num aviso no stderr.
    negados = [a.get("display_name") or a.get("action") for a in resultado.get("denied_actions") or []]
    if not negados:
        negados = [linha.strip() for linha in proc.stderr.splitlines()
                   if re.search(r"auto-denied|permission check failed", linha, re.IGNORECASE)]

    ok = proc.returncode == 0 and resultado.get("status") == "SUCCESS" and not negados
    resumo = {
        "ok": ok,
        "status": resultado.get("status"),
        "codigo_saida": proc.returncode,
        "resposta": resultado.get("response"),
        "erro": resultado.get("error"),
        "permissoes_negadas": negados,
        "pasta": str(pasta),
        "permissoes_usadas": str(origem) + (f" + {len(args.permitir)} regra(s) --permitir" if args.permitir else ""),
        "conversation_id": resultado.get("conversation_id"),
        "duracao_s": resultado.get("duration_seconds"),
        "tokens": (resultado.get("usage") or {}).get("total_tokens"),
    }
    if not ok and proc.stderr.strip():
        resumo["stderr"] = proc.stderr.strip()[-2000:]
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
