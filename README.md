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

Para que sessões na nuvem de um repositório já venham com o plugin, adicione ao `.claude/settings.json` desse repositório:

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
