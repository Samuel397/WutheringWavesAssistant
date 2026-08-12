# Ressonador genérico — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | `generic` (genérico) |
| Função | SubDPS (DPS secundário) |
| Atributo | Nenhum |
| Tipo de Concerto | Nenhum (não detectado) |
| Arquivo-fonte | `src/core/combat/resonator/generic.py` |
| Aplicável a | Ressonadores sem combo personalizado registrado |

## Visão geral

`GenericResonator` é a implementação padrão para Ressonadores sem uma classe de combo registrada. Quando o nome reconhecido não existe em `resonator_map`, o sistema usa automaticamente esse combo genérico.

## Detecção do estado das habilidades

O Ressonador genérico **não detecta o estado das habilidades**; ele depende apenas de sequências fixas de teclas.

## Fragmentos de combo

| Método | Ação | Descrição |
|------|------|------|
| `a4()` | Quatro ataques básicos | Quatro ataques rápidos |
| `Eaa()` | E + dois ataques básicos | Habilidade de Ressonância seguida de dois ataques |
| `E()` | Habilidade de Ressonância | Usa somente E |
| `z()` | Ataque pesado | Mantém pressionado por 0,50 segundo |
| `Q()` | Habilidade de Eco | Ativa o Eco |
| `R()` | Liberação de Ressonância | Ativa R |

### `COMBO_SEQ` (referência para o campo de treinamento)

```python
COMBO_SEQ = [
    ["a", 0.05, 0.30],  # Quatro ataques básicos
    ["a", 0.05, 0.30],
    ["a", 0.05, 0.30],
    ["a", 0.05, 0.30],
    ["z", 0.50, 0.50],  # Ataque pesado
    ["R", 0.05, 0.50],  # Liberação de Ressonância
    ["Q", 0.05, 0.50],  # Habilidade de Eco
]
```

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

## Ressonadores aplicáveis

Os seguintes Ressonadores usam o combo genérico:

- Phoebe - `BasePhoebe` existe, mas não está registrada em `resonator_map`, e `combo()` não possui implementação
- Qualquer outro Ressonador sem registro específico

> **Nota:** Rover não aparece em `resonator_map`, mas recebe tratamento específico em `set_resonators()`. O sistema instancia `Rover` e usa seu próprio `combo()`, sem recorrer a `GenericResonator`. Consulte [rover.md](rover.md).

## Características do projeto

1. **Compatibilidade ampla** - sequência simples que funciona com qualquer Ressonador
2. **Ordem aleatória** - embaralha `Eaa`, `R` e `z` para evitar um padrão rígido
3. **Contingência segura** - serve como alternativa para Ressonadores sem implementação própria
4. **Sem detecção de estado** - executa a sequência sem analisar capturas de tela

---

*Última atualização: 07/02/2026*
