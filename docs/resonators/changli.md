# Changli — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | Changli |
| Função | SubDPS (DPS secundário) |
| Atributo | Fusion |
| Tipo de Concerto | Círculo vermelho (concerto_fusion) |
| Versão | v1.1 |
| Arquivo-fonte | `src/core/combat/resonator/changli.py` |

## Mecânicas do Ressonador

O mecanismo central de Changli é o sistema de **Enflamement**, representado por uma barra de quatro segmentos:

- Ataques básicos podem acumular Enflamement.
- A sequência E + ataque básico (`Ea`) também acumula energia e ativa o ataque derivado.
- Com quatro segmentos, um ataque pesado (`z`) ativa **Flaming Sacrifice**.
- Ataque pesado, R e outro ataque pesado formam uma sequência de alto dano.

## Detecção do estado das habilidades

### Detecção de energia

| Item detectado | Método de detecção | Descrição |
|--------|----------|------|
| 1 segmento | O primeiro pixel acima da barra de PV é vermelho `(107,97,250)` | Um segmento de Enflamement |
| 2 segmentos | Detecta o pixel do segundo segmento | Dois segmentos de Enflamement |
| 3 segmentos | Detecta o pixel do terceiro segmento | Três segmentos de Enflamement |
| 4 segmentos | Detecta o pixel do quarto segmento | Energia cheia; permite Flaming Sacrifice |

### Teste de habilidade

| Item detectado | Cor do ícone | Descrição |
|--------|----------|------|
| Habilidade de Ressonância E | branco `(255,255,255)` | Habilidade E pronta |
| Habilidade de Eco Q | branco `(255,255,255)` | Eco pronto |
| Liberação de Ressonância R | branco `(255,255,255)` | Liberação de Ressonância pronta |

## Fragmentos de combo

| Método | Ação | Descrição |
|------|------|------|
| `Ea()` | E + ataques básicos | Habilidade de Ressonância seguida de entradas redundantes de ataque para ativar o derivado |
| `E()` | Apenas habilidade E | Habilidades E individuais |
| `a2()` | 2 etapas de ataque básico | 2 etapas de ataque básico na entrada |
| `a3()` | Três últimos ataques básicos | Executa do terceiro ao quinto ataque da sequência |
| `a()` | Ataque básico de estágio único | Um ataque básico |
| `z()` | Ataque pesado | Mantém o ataque pressionado por 0,7 segundo |
| `az()` | Ataque básico + ataque crítico | Um período de ataque básico seguido por um ataque pesado |
| `Rz()` | R + ataque pesado | Liberação seguida de ataque pesado |
| `zR()` | Ataque pesado + R | Ataque pesado seguido da Liberação, com ataque básico intercalado |
| `Qa3()` | Eco + três ataques básicos | Ativa o Eco de motocicleta e continua atacando |
| `Q()` | Habilidade de Eco | Ativa o Eco de motocicleta |
| `R()` | Liberação de Ressonância | Apenas Liberação de Ressonância |

## Lógica de decisão do combo (`combo()`)

```
Entrada em campo: sleep(0.1) + a2() executa dois ataques básicos (ativa True Sight: Charge)
Captura a tela e detecta o estado da energia e das habilidades

1. Quatro segmentos de Enflamement:
   ├─ z() executa um ataque pesado
   ├─ a2() aguarda o fim da animação
   ├─ Confirma novamente os quatro segmentos → executa z() outra vez
   │   ├─ Consumo concluído (menos de quatro segmentos) → Rz(), com Liberação e ataque pesado
   │   └─ Ainda há quatro segmentos → o ataque pesado falhou; não executa outra ação e retorna imediatamente
   └─ Se não houver quatro segmentos → E()
   └─ return

2. Três segmentos de Enflamement e E disponível:
   ├─ Ea() completa o quarto segmento
   ├─ Detecta quatro segmentos → z() executa um ataque pesado
   │   └─ Com R → Rz()
   ├─ Sem quatro segmentos, mas com R → Rz()
   └─ return

3. Pouco Enflamement (< 3 segmentos) e R disponível:
   └─ Rz() ativa diretamente a Liberação e o ataque pesado
   └─ return

4. Contingência:
   ├─ Com E → E() para sincronizar a rotação
   ├─ Sem E → a3() executa ataques básicos e verifica se há quatro segmentos para o ataque pesado
   ├─ Ativa o Eco por último → Q()
```

## Características do projeto

1. **Gerenciamento de Enflamement** - o objetivo principal é usar um ataque pesado depois de preencher os quatro segmentos
2. **Verificação dupla** - após o ataque pesado, confere a energia novamente para evitar que um ataque aéreo seja interpretado como ataque descendente
3. **Entrada com `a2()`** - dois ataques básicos ativam a sequência de entrada e aceleram o ganho de energia
4. **Eco por último** - a Habilidade de Eco fica no fim para sincronizar a rotação
5. **Prioridade de E** - com três segmentos, E recebe prioridade para completar a barra; com pouca energia e R disponível, usa a Liberação diretamente

---

*Última atualização: 06/02/2026*
