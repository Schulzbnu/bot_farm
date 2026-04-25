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

## MVP implementado (movimentação em mapa + UI)
Este repositório agora possui um MVP funcional para:
- parametrizar mapa (`largura x altura`)
- definir bloqueios de tiles
- definir ponto inicial
- definir waypoints
- executar movimentação com pathfinding A* em grid 2D (mesmo andar)
- salvar/carregar perfil em JSON

### Executar
```bash
python -m bot.main
```

### Controles da UI
- **Aplicar parâmetros**: valida e recria mapa/waypoints.
- **Iniciar/Pausar**: inicia ou pausa a simulação.
- **Step**: avança 1 passo.
- **Reset**: reinicia no ponto inicial.
- **Salvar perfil / Carregar perfil**: persistência das configurações.

## Primeira entrega (documentação base)
- [Visão de Produto](docs/visao-produto.md)
- [Arquitetura e Tecnologias](docs/arquitetura-tecnologias.md)

## Base de referência
Foram avaliados conceitos do TibiaPilotNG como referência de fluxo/funcionalidades:
- https://github.com/paulordyl/TibiaPilotNG/tree/master

Para este projeto, o escopo inicial é **sem Arduino** e com instalação simples.
