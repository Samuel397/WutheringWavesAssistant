# Mornye — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | Mornye |
| Função | Healer (Cura) |
| Atributo | Fusion |
| Tipo de Concerto | Círculo vermelho (`concerto_fusion`) |
| Versão | v3.0 |
| Arquivo-fonte | `src/core/combat/resonator/mornye.py` |

## Mecânicas do Ressonador

Mornye possui um sistema de combate com **dois modos**:

### Modo Base (forma normal)

- **Rest Mass Energy** - barra que, quando cheia, permite entrar no Wide-Field Observation Mode com um ataque pesado
- Três ataques básicos acumulam energia
- E ativa Expected Error
- O ataque pesado Potential Transformation ativa a forma borboleta quando a energia está cheia

### Wide-Field Observation Mode (forma borboleta)

- **Relative Momentum** - barra que, quando cheia, permite usar o ataque pesado Inversion
- Ataques básicos e E recebem versões aprimoradas
- E ativa Distributed Array
- O ataque pesado Inversion consome Relative Momentum

### Rotação avançada principal

1. Três ataques básicos acumulam quatro segmentos de energia.
2. Um ataque pesado ativa a forma borboleta.
3. E encerra a forma e concede cinco segmentos de energia.
4. Salto + ataque básico esvazia a energia.
5. A Habilidade de Eco sincroniza o fim da rotação.

## Detecção do estado das habilidades

### Detecção de energia

| Item detectado | Valor | Descrição |
|--------|------|------|
| Rest Mass Energy 20% | Azul `(63,119,250)` | Energia do Modo Base |
| Rest Mass Energy 50% | Azul | Energia do Modo Base |
| Rest Mass Energy 80% | Azul | Energia do Modo Base |
| Relative Momentum 20% | Tons quentes | Energia do Wide-Field Observation Mode |
| Relative Momentum 50% | Tons quentes | Energia do Wide-Field Observation Mode |
| Relative Momentum 80% | Tons quentes | Energia do Wide-Field Observation Mode |

### Detecção de estados

| Item detectado | Lógica | Descrição |
|--------|------|------|
| Ataque pesado — Potential Transformation | AND | Energia cheia permite transformar (quatro pontos brancos) |
| Wide-Field Observation Mode | AND | Indica a forma borboleta (quatro pontos brancos) |
| Habilidade de Ressonância — Distributed Array | AND | E da forma borboleta |
| Ataque pesado — Inversion | AND | Ataque da forma borboleta (cinco pontos brancos) |
| Habilidade de Eco Q | OR | Eco disponível |
| Liberação de Ressonância R | AND | R disponível |
| Segunda Liberação de Ressonância | AND | R disponível dentro do campo de ressonância |

## Fragmentos de combo

| Método | Ação | Descrição |
|------|------|------|
| `a4()` | Quatro ataques básicos | Quatro ataques rápidos |
| `Eaa()` | E + dois ataques básicos | Habilidade de Ressonância seguida de dois ataques |
| `E()` | Habilidade de Ressonância | Usa somente E |
| `z()` | Ataque pesado | Mantém pressionado por 0,50 segundo |
| `Q()` | Habilidade de Eco | Ativa o Eco |
| `R()` | Liberação de Ressonância | Ativa R |

## Lógica de decisão do combo (`combo()`)

```python
def combo(self):
    self.combo_action(self.a4(), False)

    combo_list = [self.Eaa(), self.R(), self.z()]
    random.shuffle(combo_list)
    for i in combo_list:
        self.combo_action(i, False)
        time.sleep(0.15)

    self.combo_action(self.Q(), False)
```

1. Executa `a4()`, com quatro ataques básicos.
2. Embaralha `[Eaa, R, z]` e executa os três itens nessa ordem aleatória.
3. Por fim, ativa o Eco com `Q()`.

> **Nota:** embora `BaseMornye` implemente a detecção completa de Rest Mass Energy, Relative Momentum e Wide-Field Observation Mode, o `combo()` atual ainda não utiliza esses dados. Ele emprega a mesma lógica aleatória simples de `GenericResonator`; o combo personalizado permanece pendente.

## `exit_special_state()`

`exit_special_state()` encerra o Wide-Field Observation Mode antes da busca de Ecos:

```python
def exit_special_state(self, scenario_enum):
    if scenario_enum != ScenarioEnum.BeforeEchoSearch:
        return
    img = self.img_service.screenshot()
    if not self.is_wide_field_observation_mode_ready(img):
        return
    # Salta para sair da forma de borboleta
    quit_seq = [["j", 0.05, 2.00]]
    self.combo_action(quit_seq, True, ignore_event=True)
```

## Características do projeto

1. **Detecção abrangente** - `BaseMornye` implementa a energia dos dois modos e prepara a futura lógica personalizada
2. **Execução simples** - o `combo()` atual usa a mesma ordem aleatória de `GenericResonator`
3. **Saída segura da forma borboleta** - `exit_special_state()` detecta e encerra o modo antes da busca de Ecos
4. **Registro próprio** - Mornye está em `resonator_map` e usa seu próprio método `combo()`

---

*Última atualização: 07/02/2026*
