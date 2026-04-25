# Arquitetura e Tecnologias

## Diretriz sobre "indetectável"
Para manter o projeto sustentável e alinhado a uso permitido:
- Não implementar técnicas de evasão de anti-cheat.
- Não usar drivers/kernel hooks/injeções ocultas.
- Preferir integração explícita e observável.

No contexto de OTServer com uso autorizado, a melhor estratégia é **compatibilidade + estabilidade**, não ocultação.

## Stack recomendada

### Linguagem principal: **Python 3.12+**
**Por quê:**
- Ecossistema maduro para automação desktop e CV
- Curva de aprendizado baixa
- Excelente para prototipação rápida

### Interface desktop: **PySide6 (Qt)**
**Por quê:**
- UI estável e moderna
- Fácil distribuir binário
- Bom suporte para painéis de configuração

### Visão computacional: **OpenCV + mss**
**Por quê:**
- Captura de tela eficiente
- Matching por template/cores
- Mantém o bot desacoplado de memória/processo (mais seguro e simples)

### Input/controle: **pynput/pyautogui (camada abstrata própria)**
**Por quê:**
- Controle de teclado/mouse com API simples
- Permite encapsular delays, retries e perfis

### Configuração: **YAML**
**Por quê:**
- Fácil edição por usuário
- Bom para perfis por vocação/rota

### Logs e observabilidade: **structlog + arquivos rotativos**
**Por quê:**
- Diagnóstico simples
- Ajuda a depurar comportamentos sem “caixa preta”

## Arquitetura em módulos
1. **Core FSM (Finite State Machine)**
   - Estados: `HUNTING`, `LOOTING`, `REFILLING`, `DEPOTING`, `ESCAPE`, `IDLE`
2. **Perception Layer**
   - Leitura de HUD/vida/mana/alvos via OCR/template matching
3. **Decision Layer**
   - Regras declarativas por prioridade e contexto
4. **Action Layer**
   - Executor de teclas/mouse com fila e confirmação
5. **Profile System**
   - Configs por personagem, cidade, supplies e rota
6. **Safety Layer**
   - Timeouts, watchdog, hotkey de parada, anti-loop

## Decisões importantes para “uso simples”
- Instalador único (PyInstaller)
- Perfil guiado por wizard inicial
- “Modo teste” com overlay de debug
- Botão de emergência (kill switch)

## Estrutura inicial de pastas (proposta)
```text
bot/
  core/
  perception/
  decision/
  action/
  profiles/
  ui/
  infra/
configs/
docs/
```
