# Ciaccona — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | Ciaccona |
| Função | Support (Suporte) |
| Atributo | Aero |
| Tipo de Concerto | Círculo verde (`concerto_aero`) |
| Versão | v2.3 |
| Arquivo-fonte | `src/core/combat/resonator/ciaccona.py` |

## Mecânicas do Ressonador

Ciaccona usa pistolas e compartilha algumas operações especiais desse tipo de arma com Phoebe. Suas mecânicas principais são:

- **Energia musical** - possui três segmentos; com a barra cheia, um ataque pesado aplica uma carga de Aero Erosion
- **Cargas de Aero Erosion** - o quarto ataque básico, E e a Habilidade de Intro podem aplicar cargas
- **Estado de canto** - R inicia um estado que dura cerca de 34,5 segundos
- **Proteção durante o canto** - a marca `_is_singing` impede a troca de Ressonador enquanto o estado estiver ativo

### Energia musical

| Operação | Efeito |
|------|------|
| Quarto ataque básico | +1 segmento de energia musical |
| Habilidade de Intro | +1 segmento de energia musical |
| Ataque pesado com 3 segmentos | Consome os três segmentos e aplica uma carga de Aero Erosion |

## Detecção do estado das habilidades

### Detecção de energia

| Item detectado | Método | Descrição |
|--------|----------|------|
| 1 segmento | Detecta o primeiro pixel de energia em verde | Um segmento de energia musical |
| 2 segmentos | Detecta o pixel do segundo segmento | Dois segmentos de energia musical |
| 3 segmentos | Detecta o pixel do terceiro segmento | Energia cheia; permite o ataque pesado |

### Detecção de habilidades

| Item detectado | Cor do ícone | Descrição |
|--------|----------|------|
| Habilidade de Ressonância E | Branco `(255,255,255)` | E disponível |
| Habilidade de Eco Q | Branco `(255,255,255)` | Eco disponível |
| Liberação de Ressonância R | Branco/vários tons de verde | R disponível |

### Estado dinâmico

```python
_is_singing = False              # Indica se Ciaccona está no estado de canto
_singing_timeout_seconds = 34.5  # Tempo limite do estado de canto
_singing_start_time = None       # Momento em que o canto começou
```

## Fragmentos de combo

| Método | Ação | Descrição |
|------|------|------|
| `a4()` | Quatro ataques básicos | Sequência básica completa |
| `a_intro()` | Ataque básico ao entrar pela Intro | Dura 1,3 segundo para cobrir a animação da Intro |
| `a2_end()` | Dois ataques básicos finais | Terceiro e quarto ataques da sequência |
| `z_musical_essence_3()` | Ataque pesado com três segmentos | Mantém pressionado por 1,54 segundo |
| `E()` | Habilidade de Ressonância | Pressiona E duas vezes por redundância |
| `E3a()` | E + três ataques básicos | Depois de E, continua a partir do segundo ataque da sequência |
| `jEz()` | Salto + E + ataque pesado | E aéreo seguido do ataque com três segmentos |
| `jEaaa()` | Salto + três ataques básicos | Salta e ataca; apesar do nome, o método não pressiona E |
| `jEaaajaaa()` | Dois ciclos aéreos | Executa duas rodadas de salto, E e ataques básicos |
| `jaaa()` | Salto + três ataques básicos | Ataques básicos durante a queda |
| `Q()` | Habilidade de Eco | Ativa o Eco |
| `R_aero_erosion()` | R de Aero Erosion | Modo Aero Erosion da Liberação |
| `R_spectro_frazzle()` | R de Spectro Frazzle | Modo Spectro Frazzle da Liberação |

## Lógica de decisão do combo (`combo()`)

```
Entrada em campo: encerra o estado de canto + a_intro() executa o ataque básico da Intro (1,3 segundo)

Captura a tela e detecta o estado da energia e das habilidades
Ativa o Eco com Q()

1. Com R (Liberação pronta):
   ├─ Três segmentos de energia musical:
   │   ├─ Com E → jEz(), com E aéreo e ataque pesado
   │   └─ Sem E → z_musical_essence_3(), com ataque pesado
   ├─ Menos de três segmentos:
   │   ├─ Com E → jEaaa(), com E aéreo e ataques básicos
   │   └─ Sem E → jaaa(), com ataques básicos aéreos
   └─ R_aero_erosion() ativa a Liberação
   └─ Marca o estado de canto
   └─ return

2. Sem R:
   ├─ Três segmentos de energia musical → z_musical_essence_3(), com ataque pesado
   ├─ Com E:
   │   ├─ Dois segmentos → jEaaa()
   │   └─ Outras quantidades → jEaaajaaa(), com dois ciclos
   ├─ Sem E → a2_end(), com ataques básicos
   └─ Verifica novamente:
       ├─ Três segmentos de energia musical → z_musical_essence_3()
       ├─ Com R → R_aero_erosion() + marca o estado de canto
       └─ Sem R → encerra a sequência
```

## Características do projeto

1. **Proteção do canto** - `is_singing()` verifica o estado; `CombatSystem` não troca de Ciaccona enquanto ela canta
2. **Limpeza ao entrar** - `_set_singing(False)` encerra qualquer marca antiga quando Ciaccona entra em campo
3. **Prioridade da energia musical** - com três segmentos, prioriza o ataque pesado e a aplicação de Aero Erosion
4. **Prioridade de R** - quando a Liberação está disponível, escolhe sequências centradas nela
5. **TODO explícito** - a seleção entre Spectro Frazzle e Aero Erosion ainda está pendente no código

---

*Última atualização: 06/02/2026*
