# SYSTUR SCRAPPER — Base de Conhecimento

## O que é este projeto

Scraper Python que consulta vendedores no sistema interno SYSTUR (systur.cvc.com.br).
Lê uma lista de `codigo_pessoa` de um Excel, consulta cada um no sistema e grava os resultados em outro Excel.

## Como executar

```
python Scrapping_SysTur.py
```

Executar sempre a partir da raiz do projeto (onde está o arquivo `.py`).

---

## Estrutura de pastas

```
systur_scrapping/
├── Scrapping_SysTur.py       ← script principal — ESTE é o que o usuário executa
├── gerar_exe.py              ← gera SysTur_Scrapper.exe (PyInstaller)
├── src/
│   ├── sessao.py             ← abre Edge, login automático no popup
│   ├── navegacao.py          ← navega para tela de Vendedores via JS
│   ├── consulta.py           ← preenche campo, clica, captura tabela
│   ├── fila.py               ← fila de processamento com checkpoint JSON
│   ├── saida.py              ← grava Excel de saída formatado
│   └── sincronizar.py        ← grava log txt e faz git push ao final
├── config/
│   ├── config.xml            ← headless (true/false) e limite (0=tudo)
│   ├── credenciais.xml       ← usuario e senha do SYSTUR (NÃO ignorado no git)
│   └── xpaths.xml            ← referência dos seletores confirmados
├── entrada/                  ← colocar aqui o Excel com os codigos_pessoa
├── saida/                    ← Excel de saída gerado automaticamente (gitignored)
├── processamento/            ← fila.json com checkpoint (gitignored)
├── logs/                     ← logs de execução sincronizados via git
└── assets/prints/            ← prints de referência das telas do sistema
```

---

## Configuração (config/config.xml)

```xml
<config>
  <headless>true</headless>   <!-- true = sem janela | false = mostra Edge -->
  <limite>0</limite>          <!-- 0 = processa tudo | 50 = só 50 itens (teste) -->
</config>
```

**Para teste:** `<limite>50</limite>`
**Para produção:** `<limite>0</limite>`

---

## Credenciais (config/credenciais.xml)

```xml
<credenciais>
  <usuario>CORPP132336</usuario>
  <senha>Nova.Senh@230426</senha>
</credenciais>
```

Arquivo rastreado no git (não está no .gitignore). Credenciais reais preenchidas.

---

## Fluxo de execução

1. Lê `config/config.xml`
2. Previne hibernação do Windows (ctypes)
3. Auto-instala dependências (`selenium`, `openpyxl`) se ausentes
4. Localiza Excel em `entrada/` (qualquer .xlsx ou .xls)
5. Valida que coluna A é numérica
6. Inicializa fila (`processamento/fila.json`):
   - Se já existe: retoma + mescla novos itens do Excel + remove duplicatas
   - Se não existe: cria do zero
7. Cria arquivo de saída em `saida/vendedores_DD_MM_HH_MM_SS.xlsx`
8. Abre Edge (headless ou não), faz login automático se popup aparecer
9. Navega para RH → Vendedores via JavaScript no frame FRM_MENU
10. Loop: para cada item pendente (respeitando `limite`):
    - Garante sessão ativa
    - Preenche campo `prc_cd_pessoa`, clica `prc_evento`
    - Captura tabela de resultados (table[1], linhas a partir da 2)
    - Salva no Excel e marca como `concluido`, ou marca como `sem_resultado`
    - Em erro WebDriver: retenta até 3x com pausa de 5s, depois marca `erro`
11. Ao finalizar: salva log em `logs/`, faz git add + commit + push automático

---

## Navegação no SYSTUR

O sistema usa frames. Estrutura confirmada:
- `FRM_MENU` — menu lateral esquerdo
- `FRM_PRINCIPAL` — conteúdo principal
- `FRM_CABECALHO` — cabeçalho
- `FRM_ESQUERDO` — container esquerdo

Para ir para Vendedores, executa JS dentro do `FRM_MENU`:
```javascript
open_html("pkg_gen_consulta_padrao.prc_inicial?prc_cd_consulta=4", "462")
```

Login: popup detectado por URL contendo `p_tipo_acao=POPUP`.
Campos do login: `p_usuario`, `p_senha`, botão `//input[@value='Login']`.

---

## Campos capturados da tabela de resultados

| Coluna Excel       | Campo na tabela |
|--------------------|-----------------|
| Codigo Pessoa      | (vem do Excel)  |
| Nome Entrada       | (vem do Excel)  |
| Situacao           | celulas[0]      |
| Filial             | celulas[1]      |
| Codigo             | celulas[2]      |
| Pessoa             | celulas[3]      |
| Nome Systur        | celulas[4]      |
| CPF                | celulas[5]      |
| Telefone           | celulas[6]      |

---

## Estado atual do projeto (15/05/2026)

### Testado e funcionando
- Execução headless no Edge sem abrir janela
- Login automático via popup
- Fila com checkpoint e retomada após falha
- Deduplicação e mesclagem de novos itens ao retomar
- Geração de Excel formatado
- Log automático + git push ao finalizar

### Resultado do teste (50 itens — 15/05/2026 18:58)
- **157 concluídos** (acumulado), **0 erros**, **0 sem_resultado**
- 632 itens ainda pendentes na fila
- Execução funcionou corretamente

### Próximos passos
- Definir `<limite>0</limite>` e rodar a base completa (632 itens restantes)
- Analisar Excel de saída gerado

### Observações sobre os dados
- Dois registros têm sujeira no campo nome do Excel de entrada:
  - `[10249068]` e `[9202065]` — texto extra misturado na coluna B
  - Não afeta a consulta (codigo_pessoa está correto)
- Excel de entrada: `Email Franqueadosver.xlsx` (789 registros após deduplicação)

---

## Máquinas envolvidas

- **Máquina local (desenvolvimento):** onde está este repositório aberto no VSCode
- **Máquina remota (execução):** acessa o SYSTUR, roda `python Scrapping_SysTur.py`
- Sincronização via **git push/pull** — após cada alteração no código, fazer pull na máquina remota

### Fluxo de deploy para a máquina remota
```
git pull
python Scrapping_SysTur.py
```

---

## Dependências

Instaladas automaticamente pelo próprio script:
- `selenium` — automação do Edge
- `openpyxl` — leitura/escrita Excel

Para gerar o executável:
- `pyinstaller` — instalado automaticamente pelo `gerar_exe.py`

Python: 3.10+ (usa `list[dict]`, `str | None`, `tuple[...]`)

---

## Gerar executável

```
python gerar_exe.py
```

Gera `dist/SysTur_Scrapper.exe`. As pastas `config/`, `entrada/`, `saida/` devem ficar ao lado do `.exe`.

---

## Arquivos ignorados pelo git (.gitignore)

- `processamento/` — estado da fila (regenerado a cada execução)
- `saida/*.xlsx`, `saida/*.xls` — arquivos de saída
- `.env`, `credenciais.json` — (credenciais.xml está rastreado)
- `__pycache__/`, `.venv/`

---

## Repositório

https://github.com/caracelli/systur_scrapping
Branch: master
