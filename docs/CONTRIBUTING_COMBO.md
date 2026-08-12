# Guia para desenvolver combos personalizados

Este documento explica como desenvolver combos personalizados para novos Ressonadores, incluindo detecção de habilidades, projeto da rotação e validação em testes.

---

## 📚 Índice

1. [Preparação antes do desenvolvimento](#preparação-antes-do-desenvolvimento)
2. [Desenvolvimento da classe base](#desenvolvimento-da-classe-base)
3. [Desenvolvimento da classe concreta](#desenvolvimento-da-classe-concreta)
4. [Registro e testes](#registro-e-testes)
5. [Melhores práticas](#melhores-práticas)
6. [Perguntas frequentes](#perguntas-frequentes)

---

## Preparação antes do desenvolvimento

### Ferramentas necessárias

1. **Ferramenta de captura** - usada para obter imagens da tela do jogo
2. **Seletor de cores** - recomenda-se o seletor de cores do PowerToys ou uma ferramenta equivalente
3. **Ambiente de desenvolvimento Python** - Python 3.10-3.12
4. **Ambiente de jogo** - campo de treinamento ou combate real

### Conhecimento necessário

1. Conheça as habilidades do Ressonador e sua rotação de combos
2. Compreenda o sistema de coordenadas de pixels (1280×720 é a resolução básica)
3. Habilidades básicas de programação Python

### Estrutura dos arquivos

```
src/core/combat/resonator/
├── your_character.py  # Arquivo do novo Ressonador
└── ...

src/core/combat/
├── combat_core.py     # Definições das classes base
└── combat_system.py   # Sistema de combate; requer registro
```

---

## Desenvolvimento da classe base

### Etapa 1: crie o arquivo do Ressonador

Crie `your_character.py` no diretório `src/core/combat/resonator/`.

### Etapa 2: defina a estrutura da classe base

```python
import logging
import numpy as np

from src.core.combat.combat_core import ColorChecker, BaseResonator, CharClassEnum, LogicEnum, ResonatorNameEnum
from src.core.interface import ControlService, ImgService

logger = logging.getLogger(__name__)


class BaseYourCharacter(BaseResonator):

    def __init__(self, control_service: ControlService, img_service: ImgService):
        super().__init__(control_service, img_service)

        # Defina aqui todos os detectores de habilidades

    def __str__(self):
        return self.resonator_name().name

    def resonator_name(self) -> ResonatorNameEnum:
        return ResonatorNameEnum.your_character  # Adicione antes o valor em combat_core.py

    def char_class(self) -> list[CharClassEnum]:
        # Retorna a função: MainDPS / SubDPS / Support / Healer
        return [CharClassEnum.MainDPS]

    # Implemente todos os métodos de detecção obrigatórios
```

### Etapa 3: obtenha as coordenadas dos ícones de habilidade

**Procedimento:**

1. Entre no modo de combate no campo de treinamento
2. Capture a tela do jogo com resolução de 1280×720
3. Com os ícones de habilidade **acesos**, use o seletor para obter as coordenadas dos pixels brancos
4. Registre as coordenadas e os valores das cores

**Pontos principais** (com base em 1280×720):

```python
# Coordenadas de exemplo (ajuste para o Ressonador real)

# Energia de Concerto (círculo colorido junto à barra de PV)
# - Vermelho: ColorChecker.concerto_fusion()
# - Amarelo: ColorChecker.concerto_spectro()
# - Azul: ColorChecker.concerto_glacio()
# - Verde: ColorChecker.concerto_aero()
# - Roxo: ColorChecker.concerto_havoc()
self._concerto_energy_checker = ColorChecker.concerto_fusion()

# Habilidade de Ressonância E (ícone no canto inferior direito)
self._resonance_skill_point = [(1074, 635), (1091, 634), (1082, 658)]
self._resonance_skill_color = [(255, 255, 255)]  # Branco em BGR
self._resonance_skill_checker = ColorChecker(
    self._resonance_skill_point,
    self._resonance_skill_color
)

# Habilidade de Eco Q (ícone no canto inferior direito)
self._echo_skill_point = [(1146, 632), (1141, 652), (1160, 656)]
self._echo_skill_color = [(255, 255, 255)]
self._echo_skill_checker = ColorChecker(
    self._echo_skill_point,
    self._echo_skill_color
)

# Liberação de Ressonância R (ícone no canto inferior direito)
self._resonance_liberation_point = [(1202, 657), (1219, 656)]
self._resonance_liberation_color = [(255, 255, 255)]
self._resonance_liberation_checker = ColorChecker(
    self._resonance_liberation_point,
    self._resonance_liberation_color
)
```

### Etapa 4: detecte estados especiais

Se o Ressonador possuir mecânicas especiais, como barra de energia, transformação ou bônus, defina detectores adicionais:

```python
# Exemplo: detecção da quantidade de segmentos de energia
self._energy1_point = [(547, 668), (548, 668), (552, 668)]
self._energy1_color = [(107, 97, 250)]  # BGR
self._energy1_checker = ColorChecker(
    self._energy1_point,
    self._energy1_color
)

# Método de detecção de energia
def energy_count(self, img: np.ndarray) -> int:
    energy_count = 0
    if self._energy1_checker.check(img):
        energy_count = 1
    if self._energy2_checker.check(img):
        energy_count = 2
    # ... outros segmentos de energia
    logger.debug(f"{self.resonator_name().value}-energia: {energy_count} segmento(s)")
    return energy_count
```

### Etapa 5: implemente os métodos de detecção

Implemente métodos de detecção para cada habilidade:

```python
def is_resonance_skill_ready(self, img: np.ndarray) -> bool:
    is_ready = self._resonance_skill_checker.check(img)
    logger.debug(f"{self.resonator_name().value}-Habilidade de Ressonância: {is_ready}")
    return is_ready

def is_echo_skill_ready(self, img: np.ndarray) -> bool:
    is_ready = self._echo_skill_checker.check(img)
    logger.debug(f"{self.resonator_name().value}-Habilidade de Eco: {is_ready}")
    return is_ready

def is_resonance_liberation_ready(self, img: np.ndarray) -> bool:
    is_ready = self._resonance_liberation_checker.check(img)
    logger.debug(f"{self.resonator_name().value}-Liberação de Ressonância: {is_ready}")
    return is_ready

def is_concerto_energy_ready(self, img: np.ndarray) -> bool:
    is_ready = self._concerto_energy_checker.check(img)
    logger.debug(f"{self.resonator_name().value}-Concerto: {is_ready}")
    return is_ready
```

**Observações:**

1. **`LogicEnum.OR` versus `AND`:**
   - `OR` (padrão): retorna `True` se qualquer ponto corresponder; adequado à distinção simples entre ícone aceso e cinza
   - `AND`: retorna `True` somente se todos os pontos corresponderem; adequado a habilidades com vários estados visuais

2. **Tolerância de cor:**
   - A tolerância padrão é 30
   - Para habilidades com grande variação de cor, ajuste o parâmetro `tolerance`

---

## Desenvolvimento da classe concreta

### Etapa 1: defina a estrutura da classe concreta

```python
class YourCharacter(BaseYourCharacter):
    # COMBO_SEQ é o combo estático individual de referência do campo de treinamento

    COMBO_SEQ = [
        # Sequência completa do combo (referência)
        ["a", 0.05, 0.30],
        ["a", 0.05, 0.30],
        # ...
    ]

    def __init__(self, control_service: ControlService, img_service: ImgService):
        super().__init__(control_service, img_service)

    # Defina os métodos dos fragmentos de combo

    def combo(self):
        # Lógica principal do combo
        pass
```

### Etapa 2: definir o formato da sequência de ação

Cada ação é uma tupla `[key, press_time, wait_time]`:

```python
# Formato: [tecla, duração do pressionamento (s), espera (s)]

["a", 0.05, 0.30]  # Ataque básico: pressiona 0,05 s, espera 0,30 s
["E", 0.05, 1.25]  # E: pressiona 0,05 s, espera 1,25 s
["z", 3.50, 0.41]  # Ataque pesado: segura 3,50 s, espera 0,41 s
["R", 0.05, 2.63]  # Liberação: pressiona 0,05 s, espera 2,63 s
["Q", 0.05, 0.50]  # Eco: pressiona 0,05 s, espera 0,50 s
["j", 0.05, 0.30]  # Salto: pressiona 0,05 s, espera 0,30 s
["d", 0.05, 0.30]  # Esquiva: pressiona 0,05 s, espera 0,30 s
["w", 0.00, 1.00]  # Avanço (usado como intervalo): espera 1,00 s
```

**Descrição das teclas:**

| Botão | Operação do jogo | Descrição |
|------|----------|------|
| `a` | botão esquerdo do mouse | Ataque básico (duração do pressionamento ≤ 0,2 segundos) |
| `z` | botão esquerdo do mouse | Ataque pesado (duração do pressionamento ≥ 0,3 segundo) |
| `E` | Tecla E | Habilidade de Ressonância |
| `R` | Tecla R | Liberação de Ressonância |
| `Q` | Tecla Q | Habilidade de Eco |
| `j` | Espaço | Saltar |
| `d` | Shift/botão direito do mouse | Esquivar |
| `w` | Tecla W | Avançar (geralmente usada como intervalo; defina `press_time` como `0.00`) |
| `G` | Tecla G | Mirar com Ressonadores que usam pistolas |

### Etapa 3: projete fragmentos de combo

Divida o combo completo em fragmentos reutilizáveis:

```python
def a4(self):
    """Quatro ataques básicos."""
    logger.debug("a4")
    return [
        ["a", 0.05, 0.30],
        ["a", 0.05, 0.30],
        ["a", 0.05, 0.30],
        ["a", 0.05, 0.30],
    ]

def E(self):
    """Habilidade de Ressonância E."""
    logger.debug("E")
    return [
        ["E", 0.05, 1.25],
    ]

def R(self):
    """Liberação de Ressonância."""
    logger.debug("R")
    return [
        ["R", 0.05, 2.50],
    ]

def Q(self):
    """Habilidade de Eco."""
    logger.debug("Q")
    return [
        ["Q", 0.05, 0.50],
    ]

def a4E(self):
    """Quatro ataques básicos seguidos de E."""
    logger.debug("a4E")
    return [
        ["a", 0.05, 0.30],
        ["a", 0.05, 0.30],
        ["a", 0.05, 0.30],
        ["a", 0.05, 0.30],
        ["E", 0.05, 1.25],
    ]
```

**Estratégia de fragmentação:**

1. **Fragmento básico:** uma única habilidade ou combinação simples, como `a4()`, `E()` ou `R()`
2. **Fragmento composto:** uma sequência usada com frequência, como `a4E()` ou `Eza()`
3. **Espera fragmentada:** divida esperas longas em vários intervalos curtos para aumentar a tolerância a falhas

```python
# Não recomendado: espera longa sem entradas
["a", 0.05, 0.90]

# Recomendado: dividir em vários intervalos curtos
["a", 0.05, 0.30],
["a", 0.05, 0.30],
["a", 0.05, 0.30],
```

### Etapa 4: implemente a lógica principal de `combo()`

`combo()` é o método principal do combo e tem três responsabilidades:
1. capturar a tela e detectar o estado atual
2. escolher uma sequência conforme esse estado
3. chamar `combo_action()` para executar as ações

**Modelo padrão:**

```python
def combo(self):
    """Lógica principal do combo."""

    # 1. Captura a tela e detecta todos os estados
    img = self.img_service.screenshot()

    is_resonance_skill_ready = self.is_resonance_skill_ready(img)
    is_echo_skill_ready = self.is_echo_skill_ready(img)
    is_resonance_liberation_ready = self.is_resonance_liberation_ready(img)
    is_concerto_energy_ready = self.is_concerto_energy_ready(img)
    energy_count = self.energy_count(img)  # Sobrescreva este método na classe base
    boss_hp = self.boss_hp(img)  # Detecta os PV do BOSS

    # 2. Ativa o Eco (prioridade normalmente baixa; uso antecipado sincroniza a rotação)
    self.combo_action(self.Q(), False)

    # 3. Árvore de decisão do combo (da maior para a menor prioridade)

    # Prioridade 1: Liberação de Ressonância
    if is_resonance_liberation_ready:
        self.combo_action(self.R(), True)
        return

    # Prioridade 2: tratamento de estados especiais
    if energy_count >= 4 and is_resonance_skill_ready:
        self.combo_action(self.a4E(), False)
        return

    # Prioridade 3: ciclo da Habilidade de Ressonância
    if is_resonance_skill_ready:
        self.combo_action(self.a4E(), False)
        return

    # Prioridade 4: ataques básicos de contingência
    self.combo_action(self.a4(), False)
```

**Descrição dos parâmetros principais:**

- `combo_action(sequence, end_wait, ignore_event=False)`
  - `sequence`: sequência de ação
  - `end_wait`: indica se deve aguardar a recuperação da última ação
    - `True`: espera a animação terminar antes de trocar de Ressonador
    - `False`: permite trocar logo após ativar a habilidade, para sincronizar a rotação
  - `ignore_event`: indica se os eventos de pausa devem ser ignorados (normalmente `False`)

**Prioridade de decisão recomendada:**

1. **Liberação de Ressonância (R)** - prioridade máxima; use-a quando estiver disponível
2. **Estado especial** - mecânica própria do Ressonador, como o florescimento de Camellya ou a fúria de Encore
3. **Habilidade de Ressonância (E)** - núcleo da rotação
4. **Habilidade de Eco (Q)** - normalmente usada ao final para sincronizar a rotação
5. **Sequência de ataques básicos** - opção de contingência

### Etapa 5: técnicas avançadas

#### 1. Verificação dos PV do BOSS

Evite continuar executando sequências longas quando o BOSS já estiver derrotado:

```python
boss_hp = self.boss_hp(img)
if boss_hp <= 0.01:
    # O BOSS está quase derrotado; evita um combo longo
    self.combo_action(self.a4(), False)
    return
```

#### 2. Tratamento de exceções

Alguns Ressonadores precisam tratar estados especiais, como interrupções ou deslocamentos para fora da arena:

```python
def combo(self):
    try:
        # Lógica normal do combo
        img = self.img_service.screenshot()
        # ...
    except StopError as e:
        # Limpeza quando a sequência é interrompida
        self.control_service.jump()  # Exemplo: interromper uma transformação
        raise e
```

#### 3. Seleção aleatória

Adicione aleatoriedade a certas habilidades (como Habilidade de Eco):

```python
def Q(self):
    """Eco: escolhe aleatoriamente a motocicleta Pesadelo ou a comum."""
    if self.random_float() < 0.33:
        # 33% de chance de usar a motocicleta Pesadelo (pressionamento longo)
        return [
            ["Q", 4.00, 0.50],
        ]
    else:
        # 67% de chance de usar a motocicleta comum (toque curto)
        return [
            ["Q", 0.05, 0.50],
        ]
```

#### 4. Detecção da entrada em campo

É possível fornecer tratamento especial ao entrar por uma Habilidade de Intro:

```python
# Define na classe base o detector do estado de entrada
self._resonance_skill_incoming_color = [(173, 238, 249)]  # Estado de entrada amarelo
self._resonance_skill_incoming_checker = ColorChecker(
    self._resonance_skill_point,
    self._resonance_skill_incoming_color,
    tolerance=50
)

# Em combo(), verifica primeiro o estado de entrada
def combo(self):
    img = self.img_service.screenshot()

    is_incoming = self.is_resonance_skill_incoming_ready(img)
    if is_incoming:
        # Combo especial de entrada
        self.combo_action(self.incoming_combo(), False)
        return

    # Lógica normal do combo...
```

---

## Registro e testes

### Etapa 1: adicione o Ressonador ao enum

Adicione o Ressonador a `ResonatorNameEnum`, em `src/core/combat/combat_core.py`:

```python
class ResonatorNameEnum(Enum):
    # ...Ressonadores existentes...

    # v3.x
    your_character = "your_character"  # Nome reconhecido pelo OCR; use o literal exigido pelo idioma do jogo
```

### Etapa 2: registre-o no sistema de combate

Em `src/core/combat/combat_system.py`:

1. Importe a classe do Ressonador:

```python
from src.core.combat.resonator.your_character import YourCharacter
```

2. Instancie o Ressonador:

```python
def __init__(self, ...):
    # ...
    self.your_character = YourCharacter(self.control_service, self.img_service)
```

3. Registre-o em `resonator_map`:

```python
self.resonator_map: dict[ResonatorNameEnum, BaseResonator] = {
    # ...Ressonadores existentes...
    ResonatorNameEnum.your_character: self.your_character,
}
```

### Etapa 3: teste a implementação

1. **Teste no campo de treinamento:**
   - configure uma equipe que inclua o novo Ressonador
   - inicie o combate automático
   - observe se a execução do combo é fluida
   - confira no log o estado detectado para cada habilidade

2. **Teste em combate real:**
   - teste em batalhas reais contra BOSS
   - valide as decisões do combo sob diferentes condições
   - procure travamentos, atrasos ou períodos sem ataque

3. **Dicas de depuração:**
   - acompanhe as mensagens de `logger.debug()`
   - use `sleep()` para aumentar temporariamente os intervalos e observar o comportamento
   - Faça uma captura de tela para verificar se as coordenadas e cores estão corretas

---

## Melhores práticas

### 1. Convenção de nomenclatura

- **Classe base**: `Base<CharacterName>`
- **Classe de implementação**: `<CharacterName>`
- **Variáveis do detector**: `_<feature>_checker`
- **Variável de coordenadas**: `_<feature>_point`
- **Variável de cor**: `_<feature>_color`

### 2. Convenções de log

Cada método de detecção deve gerar um log:

```python
logger.debug(f"{self.resonator_name().value}-Habilidade de Ressonância: {is_ready}")
```

Cada fragmento de combo deve gerar um log:

```python
def a4E(self):
    logger.debug("a4E")
    return [...]
```

### 3. Organização do código

Estrutura de arquivo recomendada:

```python
# 1. Imports
import ...

# 2. Definição da classe base
class BaseYourCharacter(BaseResonator):
    def __init__(...):
        # 2.1 Energia de Concerto
        # 2.2 Barra de energia e estados especiais
        # 2.3 Habilidade de Ressonância E
        # 2.4 Habilidade de Eco Q
        # 2.5 Liberação de Ressonância R
        # 2.6 Outros detectores especiais

    # 2.7 Métodos básicos
    def __str__(...):
    def resonator_name(...):
    def char_class(...):

    # 2.8 Métodos de detecção (na ordem das habilidades)
    def energy_count(...):
    def is_concerto_energy_ready(...):
    def is_resonance_skill_ready(...):
    # ...

# 3. Definição da classe concreta
class YourCharacter(BaseYourCharacter):
    # 3.1 Constante COMBO_SEQ
    # 3.2 Método __init__
    # 3.3 Fragmentos de combo (do simples ao complexo)
    # 3.4 Lógica principal de combo()
```

### 4. Otimização de desempenho

1. **Reduza o número de capturas:** detecte vários estados na mesma imagem
2. **Retorne cedo:** ao satisfazer uma condição, retorne imediatamente para evitar verificações desnecessárias
3. **Divida esperas longas:** melhore o tempo de resposta e a tolerância a falhas

### 5. Convenções de comentários

```python
# COMBO_SEQ é o combo estático individual de referência do campo de treinamento
COMBO_SEQ = [...]

def a4E(self):
    """Quatro ataques básicos seguidos de E."""
    logger.debug("a4E")
    return [...]
```

---

## Perguntas frequentes

### P1: O que fazer se a detecção de habilidades for imprecisa?

**A**: Verifique os seguintes pontos:
1. As coordenadas estão corretas (com base em 1280×720)
2. se as cores estão corretas (obtenha-as novamente com o seletor)
3. se a lógica deveria usar `LogicEnum.AND`
4. se a tolerância precisa de ajuste

### Q2: O que devo fazer se meu combo for interrompido com frequência?

**A**:
1. Divida longas esperas em várias esperas curtas
2. repita algumas teclas no fragmento do combo para criar entradas redundantes
3. use `combo_action(..., False)` quando for seguro trocar de Ressonador antecipadamente

### Q3: Como obter o tempo de espera preciso?

**A**:
1. Grave um vídeo combo completo no campo de treinamento
2. Análise quadro a quadro usando o player de vídeo
3. calcule o tempo de preparação e de recuperação de cada ação
4. faça ajustes finos em combate real e fragmente esperas longas

### Q4: Como lidar com vários estados do Ressonador?

**A**:
1. Defina detectores separados para cada estado
2. verifique-os em ordem de prioridade dentro de `combo()`
3. crie fragmentos de combo específicos para cada estado

### Q5: Qual valor a detecção de energia deve retornar?

**A**:
- Se o Ressonador possuir vários segmentos de energia, retorne a quantidade exata (por exemplo, de 0 a 4)
- Se bastar distinguir vazio de cheio, retorne 0 ou 1
- Em `combo()`, selecione a sequência com base nesse valor

### Q6: Como testar se as coordenadas estão corretas?

**A**:
1. imprima temporariamente as coordenadas no `__init__` da classe base
2. Use a ferramenta de anotação de imagem para marcar as coordenadas na captura de tela
3. registre temporariamente os resultados das verificações em `combo()`
4. use breakpoints para inspecionar os pixels da matriz `img`

### Q7: Qual é o estado atual de `Mornye.combo()`?

**A**:
`BaseMornye` implementa a detecção completa dos dois modos de energia: massa de repouso em `rest_mass_energy_count()` e momento relativo em `relative_momentum_count()`. No entanto, `combo()` ainda usa a mesma lógica aleatória simples de `GenericResonator` (`a4` + ordem aleatória de `[Eaa, R, z]` + `Q`) e não aproveita esses detectores. A lógica personalizada permanece pendente.

---

## Apêndice: Exemplo completo

Consulte as seguintes implementações excelentes:

- **Ressonador simples**: `sanhua.py` - Suporte com lógica direta
- **Complexidade média**: `changli.py` - detecção de segmentos de energia
- **Ressonador complexo**: `jinhsi.py` - Habilidade de Ressonância em vários estágios
- **Mecânica especial**: `camellya.py` - transformação e sistema de energia
- **Duas formas**: `cartethyia.py` - alternância de forma e decisões complexas

---

## Manutenção de documentos

Se encontrar um erro ou quiser complementar este documento:

1. abra uma issue no repositório; ou
2. envie um pull request atualizando o documento.

---

*Última atualização: 07/02/2026*
*Contribuidor: Claude Code Agent*
