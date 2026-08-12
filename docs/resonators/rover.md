# Rover — análise da lógica de combos

## Informações básicas

| Propriedade | Valor |
|---|---|
| Personagem | Rover |
| Função | Sub-DPS |
| Atributo | Genérico |
| Tipo de Concerto | Nenhum (detecção não implementada) |
| Versão | Permanente |
| Arquivo-fonte | `src/core/combat/resonator/rover.py` |
| Registro | ✅ Referenciado diretamente em `set_resonators()` (fora de `resonator_map`) |

## Mecânica do personagem

Rover é o personagem do jogador e, nesta implementação, não possui uma mecânica especial. `BaseRover` é a classe-base de personagem mais simples e não implementa nenhuma detecção de estado de habilidade.

## Detecção do estado das habilidades

`BaseRover` **não contém nenhuma detecção de estado de habilidade**; ele apenas herda a interface básica de `BaseResonator`.

## Trechos de combo

| Método | Descrição | Observação |
|---|---|---|
| `a4()` | 4 ataques básicos | Intervalo de 0.30 segundo entre os ataques |
| `a2()` | 2 ataques básicos | Duas sequências rápidas |
| `Eaa()` | E + 2 ataques básicos | Usa E e, em seguida, dois ataques básicos |
| `E()` | Habilidade E | Usa somente E e aguarda 0.50 segundo |
| `z()` | Ataque pesado | Mantém pressionado por 0.50 segundo |
| `Q()` | Habilidade de Eco | Usa o Eco |
| `R()` | Liberação de Ressonância | Usa a Liberação de Ressonância |
| `full_combo()` | Combo completo | Destinado a testes; retorna `COMBO_SEQ` |

## Lógica de decisão do combo (`combo()`)

O método `combo()` de Rover executa uma sequência fixa, sem depender da análise de capturas de tela:

```python
def combo(self):
    self.combo_action(self.a2(), True)     # Dois ataques básicos
    self.combo_action(self.Eaa(), True)    # E + dois ataques básicos
    self.combo_action(self.z(), False)     # Ataque pesado
    self.combo_action(self.a2(), True)     # Dois ataques básicos
    self.combo_action(self.R(), False)     # Liberação de Ressonância
    self.combo_action(self.Q(), False)     # Habilidade de Eco
```

Ciclo fixo: `a2 → Eaa → z → a2 → R → Q`.

## Características do projeto

1. **Sem decisão inteligente** — não verifica o estado das habilidades e executa tudo em ordem fixa.
2. **Implementação mínima** — funciona como referência básica para o uso da estrutura de combos.
3. **Registro especial** — embora não esteja em `resonator_map`, Rover recebe tratamento específico em `set_resonators()`, que usa diretamente a instância `self.rover`; portanto, **seu próprio `combo()` é executado**.
4. **Ritmo fixo** — todos os intervalos de ação ficam entre 0.30 e 0.50 segundo.

---

*Última atualização: 2026-02-06*
