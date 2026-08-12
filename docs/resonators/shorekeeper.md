# Guardiã da Costa (Shorekeeper) — análise da lógica de combos

## Informações básicas

| Propriedade | Valor |
|---|---|
| Personagem | Guardiã da Costa (Shorekeeper) |
| Função | Curandeira |
| Atributo | Fotônico (`Spectro`) |
| Tipo de Concerto | Círculo amarelo (`concerto_spectro`) |
| Versão | v1.3 |
| Arquivo-fonte | `src/core/combat/resonator/shorekeeper.py` |

## Mecânica do personagem

A Guardiã da Costa possui uma **barra com 5 segmentos de energia** e uma **transformação em borboleta**.

### Sistema de energia

- Três Ataques Básicos acumulam entre 3 e 4 segmentos de energia.
- Um Ataque Pesado (`z`) pode ativar a forma de borboleta, consumindo energia.
- A Habilidade de Ressonância E encerra a forma de borboleta e concede energia adicional.
- Após sair da forma de borboleta, salto + Ataque Básico (`ja`) pode esvaziar a energia.

### Ciclo avançado principal

1. Executar três Ataques Básicos para chegar a 3–4 segmentos de energia.
2. Usar o Ataque Pesado para entrar na forma de borboleta.
3. Usar E para sair dessa forma e chegar a 5 segmentos de energia.
4. Usar salto + Ataque Básico + Eco para consumir a energia.
5. Ativar a Liberação de Ressonância.

### Risco da forma de borboleta

Se não receber outra ação, a Guardiã da Costa continua voando enquanto está transformada. Por isso, a implementação:

- acrescenta um Ataque Básico `a` para interromper o voo;
- salta imediatamente quando o chefe é derrotado, interrompendo a transformação.

## Detecção do estado das habilidades

### Detecção de energia

| Item detectado | Método | Observação |
|---|---|---|
| 1 segmento | Pixel amarelo `(114,241,255)` | Primeiro segmento de energia |
| 2 segmentos | Igual ao anterior | Segundo segmento de energia |
| 3 segmentos | Igual ao anterior | Terceiro segmento de energia |
| 4 segmentos | Igual ao anterior | Quarto segmento de energia |
| 5 segmentos | Igual ao anterior | Quinto segmento; borboletas nas laterais |

### Detecção de habilidades

| Item detectado | Cor do ícone | Observação |
|---|---|---|
| Habilidade de Ressonância E | Branco `(255,255,255)` | E está pronto |
| Habilidade de Eco Q | Branco `(255,255,255)` | O Eco está pronto |
| Liberação de Ressonância R | Branco `(255,255,255)` | R está pronto |

## Trechos de combo

| Método | Descrição | Observação |
|---|---|---|
| `a2()` | 2 ataques básicos | Dois ataques rápidos |
| `a3()` | 3 ataques básicos | Acumula energia |
| `a3Ea()` | 3 ataques básicos + E + Ataque Básico | Acrescenta `a` após E para evitar inatividade |
| `zaEja()` | Ciclo avançado principal | Ataque Pesado para transformar → E para sair → salto + Ataque Básico para consumir energia |
| `zE()` | Ataque Pesado + E | Entra na forma de borboleta e sai com E |
| `Eja()` | E + salto + Ataque Básico | Sai da transformação e consome energia |
| `ja()` | Salto + Ataque Básico | Esvazia a energia |
| `za()` | Ataque Pesado + Ataque Básico | Ataque Pesado comum seguido de interrupção do voo |
| `E()` | Habilidade E | Usa somente E |
| `Q()` | Habilidade de Eco | Usa o Eco |
| `R()` | Liberação de Ressonância | Usa R e aguarda 3.08 segundos |

## Lógica de decisão do combo (`combo()`)

```
Captura a tela e verifica o estado de R

Entrada: a3() executa três Ataques Básicos de bom custo-benefício

1. R (Modulação Astral) disponível:
   ├─ E()
   ├─ R() (aguarda 3.08 segundos)
   └─ return

2. Captura a tela novamente:
   verifica energia, E, R e a vida do chefe

3. Exatamente 3 segmentos de energia, E disponível e chefe ainda vivo:
   ├─ zaEja() executa o ciclo avançado principal
   ├─ Q()
   └─ return

4. Tratamento geral:
   ├─ E() (aguarda a sincronização quando R está indisponível)
   ├─ R() (quando disponível)
   ├─ 5 segmentos de energia → ja() consome energia
   └─ Q()

Tratamento de exceção:
└─ StopError → jump() interrompe a transformação para evitar que a personagem voe para fora da arena
```

## Características do projeto

1. **Proteção contra voo para fora da arena** — `combo()` captura `StopError` com `try-except` e chama `jump()` para interromper a transformação da Guardiã da Costa.
2. **Ativação com 3 segmentos** — o ciclo avançado `zaEja()` exige exatamente 3 segmentos de energia.
3. **`ja()` no lugar de `za()`** — com 5 segmentos, usa `ja()` para evitar que uma tecla presa mantenha a personagem voando.
4. **Ataque após E** — vários trechos acrescentam um Ataque Básico depois de E para evitar inatividade quando a habilidade está em recarga.
5. **Prioridade para R** — quando R está disponível, a execução prioriza a Modulação Astral para recuperar a vida da equipe.

---

*Última atualização: 2026-02-06*
