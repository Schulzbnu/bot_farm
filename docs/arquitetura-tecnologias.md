# Arquitetura e Tecnologias

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

### Input/controle: **pynput (camada abstrata própria)**
**Por quê:**
- Controle de teclado com API simples
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
   - Estados previstos: `HUNTING`, `LOOTING`, `REFILLING`, `DEPOTING`, `ESCAPE`, `IDLE`
2. **Perception Layer**
   - Leitura inicial por detecção de cores no minimapa
3. **Decision Layer**
   - Conversão de posição relativa do waypoint em direção de movimento
4. **Action Layer**
   - Executor de teclas (`WASD`) com tempo de pressionamento configurável
5. **Profile System**
   - Próxima etapa: persistência de perfis e áreas em YAML
6. **Safety Layer**
   - Próxima etapa: hotkey de parada, timeout e watchdog

## Implementação atual (MVP de navegação)
- `bot/ui/main_window.py`: UI principal com seleção de regiões e controle de execução.
- `bot/ui/region_selector.py`: overlay para escolher posição e tamanho da área.
- `bot/perception/minimap_detector.py`: captura e detecção de player/waypoint em HSV.
- `bot/navigation/waypoint_navigator.py`: decisão de movimento por distância relativa.
- `bot/action/keyboard_controller.py`: envio de teclas.

## Decisões importantes para “uso simples”
- Fluxo de uso em 3 passos: selecionar tela do jogo, selecionar minimapa, iniciar.
- Dependências conhecidas e fáceis de instalar por `pip`.
- Sem leitura de memória/processo: somente visão da tela e simulação de teclado.

## Estrutura inicial de pastas
```text
bot/
  action/
  core/
  navigation/
  perception/
  ui/
configs/
docs/
tests/
```
