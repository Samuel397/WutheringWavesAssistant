# Verina — análise da lógica de combos

## Informações básicas

| Propriedade | Valor |
|---|---|
| Personagem | Verina |
| Função | Curandeira |
| Atributo | Fotônico (`Spectro`) |
| Tipo de Concerto | Círculo amarelo (`concerto_spectro`) |
| Versão | Permanente |
| Arquivo-fonte | `src/core/combat/resonator/verina.py` |

## Mecânica do personagem

Verina é uma curandeira clássica com um ciclo simples e eficiente:

- **aa + EQ** — dois ataques básicos seguidos de E e Q na mesma rotação.
- **salto + 3a** — ataques básicos aéreos que consomem energia.
- **R** — restaura a vida de toda a equipe.

### Sistema de energia

- A barra possui 4 segmentos de energia.
- Ataques básicos e habilidades acumulam energia.
- Com energia disponível, salto + 3a consome esse recurso.

## Detecção do estado das habilidades

### Detecção de energia

| Item detectado | Método | Observação |
|---|---|---|
| 1 segmento | Pixel amarelo `(114,241,255)` | Primeiro segmento de energia |
| 2 segmentos | Igual ao anterior | Segundo segmento de energia |
| 3 segmentos | Igual ao anterior | Terceiro segmento de energia |
| 4 segmentos | Igual ao anterior | Quarto segmento de energia |

### Detecção de habilidades

| Item detectado | Cor do ícone | Lógica | Observação |
|---|---|---|---|
| Habilidade de Ressonância E | Branco `(255,255,255)` | OR | E está pronto |
| Habilidade de Eco Q | Branco `(255,255,255)` | OR | O Eco está pronto |
| Liberação de Ressonância R | Branco/cinza-claro `(253,253,253)/(219,218,215)` | OR | R está pronto |

> **Observação:** o comentário de `_concerto_energy_checker` menciona um “círculo vermelho”, mas o código usa `concerto_spectro()` — o círculo amarelo do atributo Fotônico. Trata-se apenas de um erro no comentário.

## Trechos de combo

| Método | Descrição | Observação |
|---|---|---|
| `a3EQ()` | 3 ataques básicos + E + Q | Combo principal; acrescenta um ataque para evitar inatividade quando E ou Q estiver em recarga |
| `ja3()` | Salto + 3 ataques básicos | Executa três ataques após o salto e divide a espera longa |
| `a3()` | 3 ataques básicos | Versão simplificada dos ataques básicos 3 a 5 |
| `R()` | Liberação de Ressonância | Usa R e aguarda 2.63 segundos |
| `EQR()` | E + Q + R | Usa E, o Eco e a Liberação de Ressonância |

## Lógica de decisão do combo (`combo()`)

```
Captura a tela e verifica a energia e o estado de R

Entrada: a3EQ() é executado sem verificar condições
         R() é pressionado diretamente, mesmo que ainda não esteja pronto,
         porque sua detecção é pouco confiável

1. Há energia (>0):
   ├─ ja3() usa salto + 3 ataques básicos para consumir energia
   └─ return

2. Aguarda 0.1 segundo e verifica novamente:
   └─ energia >1 → ja3()
```

## Características do projeto

1. **Uso incondicional** — `a3EQ()` e `R()` são executados sem verificar disponibilidade, pois a detecção das habilidades de Verina é instável.
2. **R pressionado diretamente** — o código abandona a decisão inteligente para essa habilidade e tenta ativá-la mesmo quando ainda pode estar em recarga.
3. **Consumo de energia** — sempre que há energia, o código usa ataques aéreos para não desperdiçar o recurso.
4. **Detecção adiada** — quando a primeira leitura indica energia zero, aguarda 0.1 segundo e verifica novamente; E ou Q pode ter concedido energia nesse intervalo.
5. **Decisão mínima** — entre as implementações personalizadas, a lógica de Verina é uma das mais concisas.

## Erro no comentário sobre Concerto

Em `BaseVerina.__init__`, o comentário afirma que o indicador de Concerto seria um círculo vermelho ao lado da barra de vida, mas a implementação usa `ColorChecker.concerto_spectro()`, correspondente ao círculo amarelo do atributo Fotônico. O erro é apenas documental e não altera o funcionamento.

---

*Última atualização: 2026-02-06*
