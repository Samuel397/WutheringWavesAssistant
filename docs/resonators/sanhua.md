# Sanhua — análise da lógica de combos

## Informações básicas

| Propriedade | Valor |
|---|---|
| Personagem | Sanhua |
| Função | Suporte |
| Atributo | Glacial (`Glacio`) |
| Tipo de Concerto | Círculo azul (`concerto_glacio`) |
| Versão | Permanente |
| Arquivo-fonte | `src/core/combat/resonator/sanhua.py` |

## Mecânica do personagem

Sanhua é uma personagem clássica de suporte. Seu núcleo consiste em usar rapidamente E, um Ataque Pesado para detonar os espinhos de gelo e a Liberação de Ressonância antes de trocar de personagem:

- **Ez** — E seguido de Ataque Pesado para detonar o gelo.
- **ERz** — E + R + Ataque Pesado mantido pressionado.
- **EQ** — E combinado com a Habilidade de Eco.

## Detecção do estado das habilidades

| Item detectado | Cor do ícone | Lógica | Observação |
|---|---|---|---|
| Habilidade de Ressonância E | Branco `(255,255,255)` | AND | E está pronto |
| Habilidade de Eco Q | Branco `(255,255,255)` | OR | O Eco está pronto |
| Liberação de Ressonância R | Branco/laranja `(255,193,142)/(255,214,181)` | OR | R está pronto; aceita várias cores |

## Trechos de combo

| Método | Descrição | Observação |
|---|---|---|
| `a3()` | 3 ataques básicos | Ataca algumas vezes após a entrada pela Habilidade de Introdução |
| `z()` | Detonação com Ataque Pesado | Mantém pressionado por 0.915 segundo para detonar o gelo |
| `Ez()` | E + Ataque Pesado | Usa E e detona o gelo com o Ataque Pesado |
| `Rz()` | R + Ataque Pesado | Usa R e mantém o Ataque Pesado pressionado |
| `ERz()` | E + R + Ataque Pesado | Combo principal de Sanhua |
| `Q()` | Habilidade de Eco | Usa um Eco, como a Garça da Impermanência |
| `EQ()` | E + Habilidade de Eco | Sincroniza E com o Eco |

## Lógica de decisão do combo (`combo()`)

```
Entrada: a3() após a Habilidade de Introdução; executa alguns ataques básicos

Captura a tela e verifica o estado das habilidades

1. R disponível:
   ├─ E disponível → ERz() (E + R + Ataque Pesado mantido)
   └─ E indisponível → Rz() (R + Ataque Pesado mantido)
   └─ return

2. E disponível:
   ├─ Eco disponível → EQ() (E + Eco sincronizados)
   └─ Eco indisponível → Ez() (E + detonação de gelo)
   └─ return

3. Somente o Eco está disponível:
   └─ Q() usa o Eco
   └─ return

4. Alternativa final:
   └─ a3() executa ataques básicos
```

## Características do projeto

1. **Simples e eficiente** — a sequência de Sanhua é direta e possui prioridades claras.
2. **Prioridade para R** — quando a Liberação de Ressonância está disponível, o código prioriza `ERz()` para combinar suporte e dano.
3. **Sincronização de E** — com o Eco disponível, executa `EQ()`; sem ele, usa `Ez()` para detonar o gelo.
4. **Ataque Pesado mantido** — o Ataque Pesado de `ERz()` permanece pressionado por 1.90 segundo, um pouco acima dos 1.85 segundo usados no campo de treinamento, para garantir a ativação.
5. **Várias cores para R** — a detecção da Liberação de Ressonância aceita os estados branco e laranja do ícone.

---

*Última atualização: 2026-02-06*
