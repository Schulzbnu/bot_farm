# Visão de Produto

## Escopo funcional (MVP)
1. **Cavehunt**
   - Rotas por waypoints
   - Reentrada em rota após combate
2. **Attack Combo**
   - Sequência configurável por prioridade
   - Regras por tipo de monstro (opcional no MVP)
3. **Healing**
   - Threshold por HP/Mana
   - Ordem de uso: spell > potion > emergência
4. **Refill**
   - Volta automática para NPC/loja
   - Recompra por estoque mínimo
5. **Depot**
   - Depósito por listas (loot, consumíveis)
   - Reorganização básica de backpack
6. **Auto Spells**
   - Buffs por intervalo/condição
   - Cooldown-aware

## Fora de escopo (MVP)
- Painel web distribuído
- Suporte multi-char com orquestração em cluster
- Machine learning para decisão de combate

## Princípios do projeto
- **Uso autorizado**: apenas em servidores que permitem bot.
- **Simplicidade**: instalação e uso com mínimo atrito.
- **Confiabilidade**: estados claros, logs e recuperação automática.
- **Transparência**: comportamento previsível e auditável (sem técnicas ocultas).
