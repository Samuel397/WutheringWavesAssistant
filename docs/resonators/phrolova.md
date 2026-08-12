# Phrolova — análise da lógica de combos

## Informações básicas

| Propriedade | Valor |
|---|---|
| Personagem | Phrolova |
| Função | DPS principal |
| Atributo | Aniquilante (`Havoc`) |
| Tipo de Concerto | Círculo roxo (`concerto_havoc`) |
| Versão | v2.5 |
| Arquivo-fonte | `src/core/combat/resonator/phrolova.py` |

## Mecânica do personagem

Phrolova possui um sistema de **Notas Voláteis**:

- Ataques Básicos e a Habilidade de Ressonância geram Notas Voláteis dos tipos Cordas, Sopros e Cadência.
- O código detecta a quantidade de notas em até 6 posições.
- A Liberação de Ressonância ativa um estado especial no qual Phrolova comanda Hécate.

## Detecção do estado das habilidades

`BasePhrolova` implementa a detecção completa das habilidades.

### Detecção das Notas Voláteis

| Item detectado | Método | Observação |
|---|---|---|
| Notas 1–6 | Três conjuntos de cores: Cordas, Sopros e Cadência | Verifica a presença de uma nota em cada uma das seis posições |

Cores das notas em BGR:

- Cordas (`strings`): `(28,14,176)`, `(26,15,134)`, `(29,19,149)`
- Sopros (`winds`): `(181,28,45)`, `(138,36,52)`
- Cadência (`cadenza`): `(65,53,143)`, `(59,53,102)`

### Detecção de habilidades

| Item detectado | Cor do ícone | Lógica | Observação |
|---|---|---|---|
| ATQ Básico: Sinfonia da Vida e da Morte | Branco `(255,255,255)` | AND | Primeira forma do Ataque Básico |
| ATQ Básico: Sinfonia do Destino e da Finalidade | Branco `(255,255,255)` | AND | Segunda forma do Ataque Básico |
| Habilidade de Ressonância: Murmúrios num Sonho Fugaz | Branco `(255,255,255)` | AND | Primeira forma de E |
| Habilidade de Ressonância: Murmúrios num Sonho Assombrado | Branco `(255,255,255)` | AND | Segunda forma de E |
| Habilidade de Eco | Branco `(255,255,255)` | AND | O Eco está pronto |
| Liberação de Ressonância | Branco `(255,255,255)` | AND | R está pronto |
| Deixa: Saudação Final | R e Ataque Básico prontos simultaneamente | AND | A deixa final está disponível |

## Estado atual da implementação

```python
class Phrolova(BasePhrolova):
```

Phrolova herda de `BasePhrolova` e possui todos os recursos de detecção de habilidade. Porém, o `combo()` atual usa a mesma lógica simples e aleatória de `GenericResonator`, sem aproveitar essas informações.

## Trechos de combo

| Método | Descrição | Observação |
|---|---|---|
| `a4()` | 4 ataques básicos | Quatro ataques rápidos |
| `Eaa()` | E + 2 ataques básicos | Usa E e, em seguida, dois ataques básicos |
| `E()` | Habilidade E | Usa somente E |
| `z()` | Ataque Pesado | Mantém pressionado por 0.50 segundo |
| `Q()` | Habilidade de Eco | Usa o Eco |
| `R()` | Liberação de Ressonância | Usa R |

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

A lógica atual é igual à de `GenericResonator`: `a4` + ordem aleatória de `[Eaa, R, z]` + `Q`.

## `exit_special_state()`

`exit_special_state()` retira Phrolova do estado especial da Liberação de Ressonância antes da busca por Ecos:

```python
def exit_special_state(self, scenario_enum):
    if scenario_enum != ScenarioEnum.BeforeEchoSearch:
        return
    img = self.img_service.screenshot()
    if not self.is_cue_curtain_call_ready(img):
        return
    # Pressiona R para sair do estado da Liberação; a aterrissagem leva 2,37 segundos
    quit_seq = [["R", 0.05, 2.37]]
    self.combo_action(quit_seq, True, ignore_event=True)
```

## Análise do projeto

### Estado atual

Phrolova está registrada em `resonator_map` e herda de `BasePhrolova`. A classe-base implementa a detecção das Notas Voláteis e de várias habilidades, mas `combo()` ainda não usa esses dados.

### Próximos passos sugeridos

Uma rotação inteligente pode ser construída com os métodos de `BasePhrolova`:

1. Usar `volatile_note_count()` para contar as Notas Voláteis.
2. Distinguir as duas formas de Ataque Básico e as duas formas da Habilidade de Ressonância.
3. Usar `is_cue_curtain_call_ready()` para detectar a Deixa: Saudação Final.
4. Controlar o tempo de recarga de 24 segundos do Acorde Resolutivo da Liberação de Ressonância.

---

*Última atualização: 2026-02-07*
