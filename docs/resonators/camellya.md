# Camellya — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | Camellya |
| Função | MainDPS (DPS principal) |
| Atributo | Havoc |
| Tipo de Concerto | círculo roxo (concerto_havoc) |
| Versão | v1.4 |
| Arquivo-fonte | `src/core/combat/resonator/camellya.py` |

## Detecção do estado das habilidades

### Detecção de energia

| Item detectado | Tipo | Método de detecção |
|--------|------|----------|
| Energia cheia | Nível único (0/1) | Verifica se o pixel no fim da barra de energia, acima da barra de PV, está roxo `(131-135, 48-66, 255)` |

### Teste de habilidade

| Item detectado | Cor do ícone | Lógica | Descrição |
|--------|----------|------|------|
| Habilidade de Ressonância - Red Camellia Bloom | branco `(255,255,255)` | AND | Entrada na forma em floração (Camélia Branca → Camélia Rubra) |
| Habilidade de Ressonância - Dark Core Hunting Heart | branco `(255,255,255)` | AND | Saída da forma em floração (Camélia Rubra → Camélia Branca) |
| Habilidade de Ressonância - Flor Efêmera | branco `(255,255,255)` | AND | Habilidade especial que consome os Botões de Camélia Rubra |
| Habilidade de Ressonância - Flor Efêmera (Intro) | rosa-arroxeado `(153,66,212)` | AND | Estado da Flor Efêmera ao entrar pela Habilidade de Intro |
| Habilidade de Eco | branco `(255,255,255)` | OR | Habilidade de Eco pronta |
| Liberação de Ressonância | branco/rosa-arroxeado `(255,255,255)/(153,66,212)` | OR | Liberação de Ressonância pronta |

## Mecânicas do Ressonador

Camellya possui duas formas:
- **Camélia Branca** - forma normal; E (`Red Camellia Bloom`) ativa a Camélia Rubra
- **Camélia Rubra** - forma em floração; os ataques consomem Botões de Camélia Rubra e E (`Dark Core Hunting Heart`) encerra a forma

**Flor Efêmera** é uma Habilidade de Ressonância especial, disponibilizada após acumular Botões de Camélia Rubra suficientes. Ao usá-la, os Botões acumulados são consumidos.

## Fragmentos de combo

### Forma Camélia Branca

| Método | Descrição | Resumo da sequência de ação |
|------|------|-------------|
| `a4()` | Quatro ataques básicos da Camélia Branca | Ataca rapidamente quatro vezes |
| `a3()` | Três ataques básicos | Evita que a animação da Intro descarte as entradas seguintes |
| `a3z()` | Três ataques básicos + giro | Três ataques seguidos de um ataque pesado giratório |
| `waz()` | Continuação do segundo ataque + giro | Avança, ataca e mantém o botão pressionado para girar |
| `z()` | Giro da Camélia Branca | Mantém o ataque pressionado por 4,78 segundos |

### Forma Camélia Vermelha

| Método | Descrição | Resumo da sequência de ação |
|------|------|-------------|
| `Eaazja()` | Branca → Rubra, ataques, giro e queda | E + 2 ataques + ataque pesado giratório + ataque descendente + ataque básico |
| `aazja()` | Ataques, giro e queda na forma Rubra | 2 ataques + ataque pesado giratório + ataque descendente + ataque básico |
| `Ezja()` | Branca → Rubra, giro e queda | E + ataque pesado giratório + ataque descendente + ataque básico |
| `zja()` | Giro e queda na forma Rubra | Ataque pesado giratório + ataque descendente + ataque básico |
| `ja()` | Saída da forma Rubra ao aterrissar | Salto + ataque básico descendente |

### Operação avançada

| Método | Descrição | Resumo da sequência de ação |
|------|------|-------------|
| `EQdzjE()` | Cancela Q com esquiva, entra na forma Rubra e executa três golpes | E + Q + esquiva + ataque pressionado + salto + E |
| `QdEj()` | Cancela Q com esquiva e retorna à forma Branca | Q + esquiva + E + salto |
| `ephemeral_a()` | Flor Efêmera | E × 4 + ataque básico ao aterrissar |

### Liberação de Ressonância

| Método | Descrição | Resumo da sequência de ação |
|------|------|-------------|
| `R()` | Liberação de Ressonância | R × 4 (entradas redundantes) |
| `RaRa()` | Liberação intercalada com ataques básicos | Alterna R e ataque; espera a animação terminar e então usa Flor Efêmera |

## Lógica de decisão do combo (`combo()`)

```
Entrada em campo: a3() executa alguns ataques básicos (evita que a animação da Intro descarte comandos)

Captura a tela e detecta o estado das habilidades

Etapa 1 — prioriza os estados especiais:
├─ Flor Efêmera pronta AND Liberação pronta → RaRa() + ephemeral_a()
├─ Flor Efêmera pronta → ephemeral_a()
└─ Liberação pronta → R()

Etapa 2 — combos das formas Camélia Branca e Camélia Rubra:
├─ Camélia Branca (Red Camellia Bloom pronta):
│   ├─ Modo Dream of Lost Seas → QdEj()
│   └─ Modo normal → 50% de chance de waz() / 50% de chance de EQdzjE()
├─ Camélia Rubra (Dark Core Hunting Heart pronta):
│   ├─ Modo Dream of Lost Seas → zja()
│   └─ Modo normal → EQdzjE()
└─ Contingência → a4(), com quatro ataques básicos

Etapa 3 — verifica novamente:
├─ Flor Efêmera pronta AND Liberação pronta → se os PV do BOSS forem > 30%, RaRa() + ephemeral_a()
├─ Flor Efêmera pronta → ephemeral_a()
└─ Liberação pronta → RaRa() + nova verificação da Flor Efêmera
```

## Tratamento especial

### `exit_special_state()`

Chamado antes do deslocamento pós-combate para sair da forma Rubra. Executa `ja()` (salto + ataque básico descendente) com `ignore_event=True` e depois `dash_dodge()` para restaurar a esquiva sem fazer Camellya avançar.

### Projeto de operação redundante

Os combos de Camellya usam entradas redundantes de forma intencional:
- **E repetido** - aumenta a chance de a Habilidade de Ressonância ser ativada
- **R repetido** - aumenta a chance de a Liberação ser ativada
- **`RaRa()` alternado** - intercala R e ataque básico para evitar travamentos
- **Esperas fragmentadas** - substituem uma espera longa por várias operações curtas

---

*Última atualização: 06/02/2026*
