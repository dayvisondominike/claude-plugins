# dayvison-plugins

Marketplace pessoal de plugins do Claude Code.

## Plugins

| Plugin | O que faz |
| --- | --- |
| `antigravity` | Delega tarefas ao agente do Google Antigravity (CLI `agy`, modo headless), com permissões restritas por projeto. |

## Instalação

Em qualquer sessão do Claude Code:

```
/plugin marketplace add dayvisondominike/claude-plugins
/plugin install antigravity@dayvison-plugins
```

Ou pelo terminal: `claude plugin marketplace add dayvisondominike/claude-plugins` e `claude plugin install antigravity@dayvison-plugins --scope user`.

Só registrar o marketplace e ativar o plugin no `settings.json` não instala o plugin numa máquina onde ele ainda não foi instalado: rode o `install` acima uma vez.

Para que um repositório indique o plugin a quem o abrir (inclusive em sessões na nuvem), adicione ao `.claude/settings.json` desse repositório:

```json
{
  "extraKnownMarketplaces": {
    "dayvison-plugins": {
      "source": { "source": "github", "repo": "dayvisondominike/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "antigravity@dayvison-plugins": true
  }
}
```

## Requisitos do plugin `antigravity`

- Antigravity CLI (`agy`) instalado no ambiente: https://antigravity.google/docs/install/
- Autenticação: login interativo (`agy` uma vez no terminal) ou, em ambientes sem navegador, `GEMINI_API_KEY` no ambiente + `{"modelProvider": "gemini"}` em `~/.gemini/antigravity-cli/settings.json`.
- Python 3 (só biblioteca padrão).
