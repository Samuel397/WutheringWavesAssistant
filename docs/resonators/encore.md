# Encore — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | Encore |
| Função | MainDPS (DPS principal) |
| Atributo | Fusion |
| Tipo de Concerto | Círculo vermelho (`concerto_fusion`) |
| Versão | Permanente |
| Arquivo-fonte | `src/core/combat/resonator/encore.py` |

## Mecânicas do Ressonador

O mecanismo central de Encore é o estado **Cosmos Rave**:

- R (Liberação de Ressonância) ativa Cosmos Rave
- Durante o estado, E recebe uma versão aprimorada e a rotação usa E + ataques básicos + E
- Com a energia cheia (um segmento), Encore pode executar um ataque pesado

## Detecção do estado das habilidades

### Detecção de energia

| Item detectado | Método | Descrição |
|--------|----------|------|
| Energia cheia | Detecta o pixel vermelho `(97,121,255)` no fim da barra | Retorna 1 quando cheia e 0 caso contrário |

### Detecção de habilidades

| Item detectado | Cor do ícone | Lógica | Descrição |
|--------|----------|------|------|
| Habilidade de Ressonância E | Branco `(255,255,255)` | OR | E disponível |
| Habilidade de Eco Q | Branco `(255,255,255)` | OR | Eco disponível |
| Liberação de Ressonância R | Branco `(255,255,255)` | OR | R disponível |
| Cosmos Rave | Azul-arroxeado `(73,81,181)` | AND | Detecta a mudança geral de cor da barra durante o estado aprimorado |

## Fragmentos de combo

| Método | Ação | Descrição |
|------|------|------|
| `E()` | Habilidade de Ressonância | Usa somente E e espera 1,9 segundo |
| `Ea()` | E + ataques básicos | E seguido de entradas redundantes de ataque para garantir o derivado |
| `a5()` | Cinco ataques básicos | Sequência completa, com a espera longa fragmentada |
| `a3()` | Três ataques básicos rápidos | Cliques em frequência fixa para sair do estado aéreo |
| `a2()` | Dois ataques básicos finais | Quarto e quinto ataques da sequência |
| `R()` | Liberação de Ressonância | Ativa R e espera 2,63 segundos |
| `Ea11E()` | Combo de Cosmos Rave | E + 11 ataques básicos + E; principal sequência do estado aprimorado |
| `z()` | Ataque pesado | Mantém pressionado por 0,7 segundo e espera 3 segundos |
| `Qa3()` | Eco motocicleta Pesadelo | Eco + três ataques básicos durante o deslocamento |
| `Q()` | Eco comum | Ativa somente o Eco |

## Lógica de decisão do combo (`combo()`)

```
Entrada em campo: sleep(0.1) + a3() executa alguns ataques básicos (ativa o ataque descendente)

Captura a tela e detecta o estado de todas as habilidades

1. Estado Cosmos Rave:
   └─ Ea11E(), combo do estado Cosmos Rave
   └─ return

2. Energia cheia:
   └─ z() executa um ataque pesado
   └─ return

3. Liberação pronta (R não pode ser ativado no ar):
   ├─ R() ativa a Liberação
   ├─ Ea11E(), combo do estado Cosmos Rave
   ├─ Verifica se a energia está cheia → z() executa um ataque pesado
   └─ return

4. Com E:
   ├─ 66% de chance → Ea(), com E seguido do ataque básico derivado
   ├─ 34% de chance → E(), somente E
   └─ return

5. Com Eco:
   ├─ Escolhe aleatoriamente entre a motocicleta Pesadelo e a comum
   └─ E()
   └─ return

6. Contingência → a2(), com ataques básicos
   ├─ Verifica o ícone da Liberação uma segunda vez (ao trocar de Ressonador, ele fica vermelho por um instante e a cor pode não corresponder)
   │   ├─ Com R → R() + Ea11E()
   │   └─ Verifica o estado Cosmos Rave e a energia cheia → z()
   ├─ Com Eco → escolhe aleatoriamente uma motocicleta
   └─ Sem Eco → E()
```

## Características do projeto

1. **Detecção de Cosmos Rave** - identifica o estado pela mudança de cor da barra de energia
2. **Segunda verificação de R** - ao trocar de Ressonador, o ícone pode aparecer vermelho e falhar na primeira leitura; por isso, R é verificado novamente ao final
3. **Entrada com `a3()`** - executa ataques básicos antes da rotação principal para acionar o ataque descendente
4. **Motocicleta aleatória** - escolhe com 50% de chance entre o Eco Pesadelo e o comum
5. **Prioridade do ataque pesado** - quando a energia está cheia, prioriza o ataque pesado para consumi-la
6. **Otimização de `Ea()`** - fragmenta a espera e aumenta a frequência dos ataques básicos para garantir o derivado

---

*Última atualização: 06/02/2026*
