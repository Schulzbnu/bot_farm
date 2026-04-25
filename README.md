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

---

## MVP implementado (movimentação + UI + percepção real)

Foi adicionado um protótipo funcional com:
- processo de movimentação em grid por waypoints (`x,y,z`),
- UI para selecionar e salvar localização de regiões necessárias (ex.: minimap, HUD),
- botão para **ativar/parar** a movimentação,
- botão/UI para descobrir o waypoint atual (mais próximo da posição atual),
- integração com percepção real de tela para estimar coordenada via captura da região e detecção HSV.

## Dependências

Requisito: Python 3.12+

```bash
pip install mss numpy opencv-python
```

> A UI funciona sem essas libs, mas a percepção real só ativa com dependências instaladas.

## Executar

```bash
python main.py
```

## Fluxo rápido
1. Preencha os waypoints no bloco de texto (`x,y,z` por linha).
2. Clique em **Carregar waypoints**.
3. Cadastre a região `minimap` em **Regiões necessárias**.
4. Na seção **Percepção real de tela**, configure:
   - `Região` (ex.: `minimap`),
   - `Origem X/Y/Z` (tile de referência no centro da região),
   - `Tile px` (quantos pixels equivalem a 1 tile),
   - faixa HSV do marcador no minimap.
5. Clique em **Ativar percepção** para atualizar a posição automaticamente.
6. Use **Ativar movimentação** / **Parar movimentação** conforme necessário.
7. Clique em **Descobrir waypoint atual** para validar qual waypoint está mais próximo.

## Observação
A calibração inicial de HSV e `tile_size_px` pode variar por cliente/tema/zoom. Ajuste os parâmetros até estabilizar a leitura.
