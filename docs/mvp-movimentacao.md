# MVP de Movimentação por Mapa

## Escopo atual
- Movimentação por **waypoints** em grid 2D.
- Pathfinding por **A\*** com vizinhança 4-direções.
- Tratamento de tiles bloqueados.
- UI desktop com parametrização e simulação.

## Limitações intencionais do MVP
- Apenas mesmo andar (`z` fixo).
- Não integra ainda leitura de radar/screenshot do jogo.
- Não integra ainda combate, loot, refill e depot.

## Formato de perfil salvo (JSON)
```json
{
  "map": {"width": 20, "height": 14, "floor": 0},
  "start": {"x": 1, "y": 1, "z": 0},
  "blocked": [{"x": 6, "y": 6}],
  "waypoints": [
    {
      "label": "wp1",
      "type": "walk",
      "ignore": false,
      "passinho": false,
      "coordinate": {"x": 3, "y": 3, "z": 0}
    }
  ],
  "tick_ms": 180
}
```
