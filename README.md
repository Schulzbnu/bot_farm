# Bot para OTServer (uso permitido pelo servidor)

> **Importante:** este projeto é voltado para automação **autorizada** em OTServers que permitem bot.

## Objetivo
Criar um bot simples de usar para Tibia OTServer com foco em:
- cavehunt
- attack combo
- healing
- refill
- depot
- auto spells

## Primeira entrega
A primeira entrega deste repositório é a documentação de produto, arquitetura e stack técnica:
- [Visão de Produto](docs/visao-produto.md)
- [Arquitetura e Tecnologias](docs/arquitetura-tecnologias.md)

## Navegação por waypoint (entrega atual)
Foi adicionada uma implementação inicial para movimentação via teclado com waypoint detectado por visão computacional do minimapa.

### O que já funciona
- Seleção visual da região da tela do jogo e da área do minimapa.
- Captura da tela do minimapa com `mss`.
- Detecção de cor (HSV) para jogador e waypoint no minimapa.
- Decisão de direção (`W`, `A`, `S`, `D`) com simulação de teclado.
- Loop de navegação simples controlado pela UI.

### Executar localmente
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m bot.main
```

### Testes
```bash
pytest -q
```

## Base de referência
É possível usar conceitos do TibiaPilotNG como referência de fluxo/funcionalidades:
- https://github.com/paulordyl/TibiaPilotNG/tree/master

Para este projeto, o escopo inicial é **sem Arduino** e com instalação simples.
