# Visão geral do sistema de combate

## 1. Visão geral

O sistema de combate do WWA (`CombatSystem`) é o módulo responsável por controlar os Ressonadores e executar combos durante o farm automático de BOSS. A partir de capturas de tela, ele analisa as cores dos ícones, determina em tempo real quais habilidades estão disponíveis e seleciona dinamicamente a melhor sequência.

## 2. Classes principais

### 2.1 CombatSystem (`combat_system.py`)

O agendador geral do sistema de combate. As responsabilidades incluem:

- **Gerenciamento da equipe** - associa o nome reconhecido à instância correspondente de `BaseResonator`
- **Ordenação dos Ressonadores** - define a ordem de atuação pela prioridade Suporte → DPS → Cura
- **Ciclo de combate** - o método `run()` alterna entre os Ressonadores e executa seus combos
- **Pausa/retomada** - usa `threading.Event` para controlar o estado do combate

```python
class CombatSystem:
    def set_resonators(resonator_names_zh: list[str])  # Configura a equipe
    def run(event: threading.Event)                     # Loop principal do combate
    def start(delay_seconds: float)                     # Inicia o combate
    def pause()                                         # Pausa o combate
```

**Tabela de mapeamento de Ressonadores (`resonator_map`):**

Ressonadores registrados com combos personalizados:

| Valor do enum | Nome no jogo | Implementação do combo |
|--------|--------|--------|
| jinhsi |  Jinhsi  | Jinhsi |
| changli |  Changli  | Changli |
| shorekeeper |  Shorekeeper  | Shorekeeper |
| encore |  Encore  | Encore |
| verina |  Verina  | Verina |
| camellya |  Camellya  | Camellya |
| sanhua |  Sanhua  | Sanhua |
| cartethyia |  Cartethyia  | Cartethyia |
| ciaccona |  Ciaccona  | Ciaccona |
| phrolova |  Phrolova  | Phrolova |
| lynae |  Lynae  | Lynae |
| mornye |  Mornye  | Mornye |
| cantarella |  Cantarella  | Cantarella |

> **Nota:** Phoebe possui uma classe própria, mas sua entrada em `resonator_map` continua comentada. Como `combo()` ainda contém apenas `pass`, ela usa o comportamento genérico de `GenericResonator`. Mornye e Phrolova estão registradas, porém seus métodos `combo()` ainda empregam a mesma lógica aleatória simples do Ressonador genérico, sem aproveitar toda a detecção de estado implementada nas respectivas classes base.

Ressonadores sem combo personalizado registrado usam o combo genérico de `GenericResonator`.

### 2.2 BaseResonator (`combat_core.py`)

Classe base de todos os Ressonadores, responsável pela interface principal:

```python
class BaseResonator:
    def resonator_name() -> ResonatorNameEnum  # Identificador do Ressonador
    def char_class() -> list[CharClassEnum]     # Função do Ressonador
    def combo()                                 # Lógica principal (implementada pela subclasse)
    def combo_action(seq, is_interruptible)     # Executa uma sequência de ações
    def boss_hp(img) -> float                   # Detecta os PV do BOSS
```

**Enum de função do Ressonador (`CharClassEnum`):**

| Valor do enum | Significado | Prioridade no combate |
|--------|------|----------|
| `MainDPS` | DPS principal | 2 |
| `SubDPS` | DPS secundário | 2 |
| `Support` | Suporte | 1 (primeiro) |
| `Healer` | Cura | 3 (último) |

### 2.3 ColorChecker (`combat_core.py`)

Detector de cores de pixels, os “olhos” do sistema de combate:

```python
class ColorChecker:
    def __init__(points, colors, tolerance=30, logic=LogicEnum.OR)
    def check(img: np.ndarray) -> bool
```

**Descrição dos parâmetros:**
- `points` - Lista de pontos de coordenadas da tela (com base na resolução 1280×720)
- `colors` - Lista de cores alvo (formato BGR)
- `tolerance` - Tolerância de cores, padrão 30
- `logic` - lógica de correspondência entre vários pontos:
  - `OR` - retorna `True` se qualquer ponto corresponder (padrão, adequado à distinção simples entre pronto e em recarga)
  - `AND` - retorna `True` somente quando todos os pontos correspondem (útil para habilidades com vários estados visuais)

**Detectores predefinidos de Energia de Concerto:**

```python
ColorChecker.concerto_fusion()    # Círculo vermelho — Fusion
ColorChecker.concerto_spectro()   # Círculo amarelo — Spectro
ColorChecker.concerto_glacio()    # Círculo azul — Glacio
ColorChecker.concerto_aero()      # Círculo verde — Aero
ColorChecker.concerto_havoc()     # Círculo roxo — Havoc
```

## 3. Mecanismo de execução de combos

### 3.1 Formato da sequência de ação

Cada ação é uma tupla `[key, press_duration, wait_duration]`:

```python
["a", 0.05, 0.30]  # Ataque básico: pressiona por 0,05 s e espera 0,30 s
["E", 0.05, 1.25]  # E: pressiona por 0,05 s e espera 1,25 s
["z", 3.50, 0.41]  # Ataque pesado: segura por 3,50 s e espera 0,41 s
["R", 0.05, 2.63]  # Liberação: pressiona por 0,05 s e espera 2,63 s
```

### 3.2 Mapeamento de botões

| Valor da tecla | Operação no jogo | Descrição |
|------|----------|------|
| `a` | botão esquerdo do mouse | Ataque básico |
| `z` | Botão esquerdo do mouse (pressionado) | Ataque pesado (pressionamento > 0,5 segundo) |
| `E` | Tecla de habilidade | Habilidade de Ressonância |
| `R` | Tecla de Liberação | Liberação de Ressonância |
| `Q` | Tecla de Eco | Habilidade de Eco |
| `j` | Espaço | Saltar |
| `d` | Tecla de esquiva | Esquivar |
| `w` | Tecla de movimento | Avançar (também usada para representar intervalos de espera) |
| `G` | Tecla de mira | Mirar com Ressonadores que usam pistolas |
| `A` | Botão esquerdo do mouse (especial) | Ataque básico especial |
| `W_down` / `W_up` | Tecla W pressionada/solta | Controlar o avanço contínuo |

### 3.3 Estratégia de fragmentação dos combos

Para lidar com variações na taxa de quadros e interrupções durante o combate, a sequência é dividida em fragmentos menores:

```python
# Linha do tempo original (valor exato do campo de treinamento)
["a", 0.05, 0.90]  # O terceiro ataque básico espera 0,90 s

# Depois da fragmentação (versão para combate real)
["a", 0.05, 0.30],  # Divide a espera em trechos menores
["a", 0.05, 0.30],  # Insere entradas adicionais entre os trechos
["a", 0.05, 0.30],  # Aumenta a tolerância a falhas
```

**Benefícios da fragmentação:**
- recuperação mais rápida após uma interrupção
- menor risco de longos períodos sem ação
- entradas redundantes que o jogo pode ignorar com segurança quando não forem necessárias

## 4. Explicação detalhada do ciclo de combate

### 4.1 Regras de ordenação dos Ressonadores

```python
def _sort_resonators(resonators):
    # Prioridade: Support > DPS > Healer > None
    sorted = support + dps + healer + none
```

O Suporte aplica os bônus primeiro, os personagens de DPS causam dano em seguida e, por fim, o personagem de Cura restaura os PV da equipe.

### 4.2 Lógica de troca de Ressonador

```
while True:
    1. Verifica o estado de pausa
    2. Obtém o próximo Ressonador
    3. Tenta trocar de Ressonador (toggle)
       ├─ Sucesso → executa o combo
       ├─ Falha (não é possível trocar durante uma Liberação) → avança
       └─ None (posição vazia) → avança
    4. Impede que o mesmo Ressonador permaneça em campo por dois turnos
    5. Executa resonator.combo()
    6. Solta os botões do mouse (limpeza de segurança)
```

### 4.3 Mecanismo `exit_special_state`

Antes de prosseguir depois do combate, o sistema precisa encerrar alguns estados especiais dos Ressonadores:

- **Camellya** - chama `ja()` (salto + ataque básico) para sair do estado de florescimento e depois `dash_dodge()` para reiniciar a esquiva
- **Phrolova** - detecta o estado de comando da cortina e pressiona R para sair da Liberação
- **Mornye** - detecta o modo de observação em área ampla e salta para sair da forma especial

## 5. Padrão de projeto dos combos por Ressonador

Cada Ressonador com combo personalizado segue este padrão de projeto:

### 5.1 Classe base + classe de implementação

```python
class BaseXxx(BaseResonator):
    """Define os métodos de detecção do estado das habilidades."""
    def is_resonance_skill_ready(img) -> bool
    def is_echo_skill_ready(img) -> bool
    def is_resonance_liberation_ready(img) -> bool

class Xxx(BaseXxx):
    """Define fragmentos de combo e a lógica de decisão."""
    COMBO_SEQ = [...]           # Combo completo do campo de treinamento (referência)
    def a4(): return [...]       # Fragmento: quatro ataques básicos
    def E(): return [...]        # Fragmento: Habilidade de Ressonância
    def combo():                 # Lógica principal de decisão
        img = screenshot()
        if is_R_ready: ...
        elif is_E_ready: ...
        else: basic_attack_fallback  # Contingência: ataques básicos
```

### 5.2 Priorização de Decisão

Ordem de decisão seguida pela maioria dos Ressonadores:

1. **Liberação de Ressonância (R)** - prioridade máxima; usa a Liberação quando estiver disponível
2. **Tratamento de estados especiais** - por exemplo, o estado de florescimento de Camellya e o estado de fúria de Encore
3. **Habilidade de Ressonância (E)** - núcleo da rotação de habilidades
4. **Habilidade de Eco (Q)** - geralmente usada no fim para sincronizar a rotação
5. **Sequência de ataques básicos** - opção de contingência

### 5.3 Convenção COMBO_SEQ

Em cada classe de Ressonador, `COMBO_SEQ` representa um combo estático completo para testes individuais no campo de treinamento. Durante o combate real, `combo()` seleciona dinamicamente os fragmentos adequados de acordo com o estado das habilidades.

---

*Última atualização: 07/02/2026*
