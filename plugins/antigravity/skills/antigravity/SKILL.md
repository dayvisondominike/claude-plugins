---
name: antigravity
description: Delegar uma tarefa ao agente do Google Antigravity (CLI agy, modo headless) em qualquer projeto - executar scripts e testes, pedir uma segunda opinião ao Gemini, ou rodar trabalho em paralelo. Use quando o usuário pedir para rodar/executar algo "no Antigravity" ou "com o agy".
---

# Delegar ao Antigravity (agy)

O Claude Code orquestra; o agente do Antigravity executa. A chamada passa sempre pela ponte `agy_executar.py`, que fica na pasta desta skill (o diretório base informado quando a skill é carregada). Ela roda o `agy` na pasta do projeto com permissões restritas e devolve um resumo em JSON.

```
python <pasta desta skill>/agy_executar.py "<tarefa>" [--pasta DIR] [--permitir REGEX ...] [--timeout 15m] [--modelo SLUG] [--continuar]
```

- Use `python3` onde `python` não existir (Linux/macOS). A ponte só usa a biblioteca padrão.
- `--pasta` é a raiz do projeto; o padrão é a pasta atual.
- Rode em segundo plano (`run_in_background`) quando a tarefa puder passar de ~2 minutos.

## Antes da primeira chamada no ambiente

Se a ponte responder `agy não encontrado`, o CLI não está instalado neste ambiente. Peça autorização ao usuário antes de instalar (o instalador baixa e executa um script):

- Windows: `irm https://antigravity.google/cli/install.ps1 | iex`
- Linux/macOS: `curl -fsSL https://antigravity.google/cli/install.sh | bash`

Autenticação:
- Máquina com navegador: o usuário roda `agy` uma vez no terminal e faz login com a conta Google (você não faz o login).
- Ambiente sem navegador (nuvem, SSH, CI): precisa da variável `GEMINI_API_KEY` definida no ambiente **e** de `{"modelProvider": "gemini"}` em `~/.gemini/antigravity-cli/settings.json`. Se a chave não estiver no ambiente, diga ao usuário onde configurá-la; nunca peça que ele cole a chave no chat.

## Permissões

O `agy` em modo headless **nega em silêncio** qualquer comando não liberado (o status continua `SUCCESS`). A ponte resolve as regras assim:

1. Se o projeto tem `.agent/agy-settings.json`, usa esse arquivo.
2. Senão, usa `agy-settings-padrao.json` (ao lado da ponte): nenhum comando liberado, só leitura e escrita de arquivos dentro da pasta; `git push/commit/reset...`, remoções em massa e escrita no `.env` negados.
3. `--permitir REGEX` libera um comando só para aquela chamada.

Regras de regex: precisam casar com a linha de comando **inteira** (termine com `( .*)?` para aceitar argumentos). Exemplos para `--permitir`:
- `\.venv[\\/]Scripts[\\/]python(\.exe)?( .*)?` - Python de um venv no Windows
- `(\.venv/bin/)?python3?( .*)?` - Python no Linux/macOS
- `npm (test|run build)( .*)?`

Libere só o que a tarefa precisa. Liberar o interpretador (python, node) equivale a permitir qualquer código; diga isso ao usuário quando for o caso. Nunca use `--dangerously-skip-permissions`. Para um projeto usado com frequência, sugira criar o `.agent/agy-settings.json` dele em vez de repetir `--permitir`.

## Escrevendo a tarefa

O agente do Antigravity não vê esta conversa. A tarefa precisa ser autocontida: diga o comando exato, o que observar e o que relatar. Ele lê o `AGENTS.md` do projeto, se existir. Exemplo:

> Rode `.venv\Scripts\python.exe App.py` na raiz do projeto. Relate quais etapas concluíram, o nome do arquivo gerado e, se houver erro, o traceback completo. Não altere nenhum arquivo.

## Lendo o resultado

- `ok: true` só quando o status é `SUCCESS` e nada foi negado.
- `permissoes_negadas` não vazio: o comando não rodou. Não trate como sucesso; mostre ao usuário o que foi negado e pergunte se deve liberar.
- A `resposta` é o relato do outro agente, não prova: confira arquivos gerados ou saídas antes de afirmar ao usuário que deu certo.
- Para seguir a mesma conversa, use `--continuar`.
- `authentication required` no stderr: falta login ou `GEMINI_API_KEY` (veja acima).
