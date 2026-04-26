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

## Base de referência
É possível usar conceitos do TibiaPilotNG como referência de fluxo/funcionalidades:
- https://github.com/paulordyl/TibiaPilotNG/tree/master

Para este projeto, o escopo inicial é **sem Arduino** e com instalação simples.

## Implementação inicial de navegação por radar
Foi adicionada uma base funcional em Python com:
- detecção da posição do radar na tela (`getRadarToolsPosition`, `getRadarImage`)
- descoberta de coordenada atual por hash + fallback de floor e matching (`getCoordinate`)
- conversão fixa pixel ↔ coordenada (`31744, 30976`)
- pathfinding A* em grid no floor (`generateFloorWalkpoints`)
- execução de movimento por waypoint com abstração de teclado (`WalkTask`)

### Estrutura
```text
bot/
  input/keyboard.py
  navigation/
    radar.py
    pathfinding.py
    map_repository.py
  tasks/walk_tasks.py
```

## Mapas do radar: pasta local ou GitHub?
Você pode usar as duas opções:

1. **Colocar os arquivos manualmente na pasta** `bot/assets/maps`.
2. **Baixar do GitHub** via `.zip` usando `install_maps_from_github_zip(...)`.

Exemplo rápido:
```python
from pathlib import Path
from bot.navigation.map_repository import install_maps_from_folder, install_maps_from_github_zip

# Opção A: copiar de pasta local
install_maps_from_folder(Path("./meus_mapas"))

# Opção B: baixar zip de um repositório
install_maps_from_github_zip("https://github.com/org/repo/archive/refs/heads/main.zip")
```
