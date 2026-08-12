# Cantarella — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | Cantarella |
| Função | Suporte |
| Atributo | Havoc |
| Tipo de Concerto | círculo roxo (concerto_havoc) |
| Versão | v2.2 |
| Arquivo-fonte | `src/core/combat/resonator/cantarella.py` |

## Mecânicas do Ressonador

`BaseCantarella` define o detector de Energia de Concerto (círculo roxo), mas os métodos de detecção dos segmentos de energia, da Habilidade de Ressonância, da Habilidade de Eco e da Liberação continuam comentados e, portanto, desativados.

## Detecção do estado das habilidades

### Inicializado (detector criado)

| Item detectado | Método de detecção | Descrição |
|--------|----------|------|
| Energia de Concerto | círculo roxo de `concerto_havoc()` | O detector existe, mas o método `is_concerto_energy_ready()` está comentado |

### Comentado (ativação pendente)

| Item detectado | Descrição |
|--------|------|
| Método de detecção de Energia de Concerto | `is_concerto_energy_ready()` está comentado |
| Energia de 1 a 4 segmentos | Quatro segmentos acima da barra de PV |
| Habilidade de Ressonância E | Habilidade E pronta |
| Habilidade de Eco Q | Eco pronto |
| Liberação de Ressonância R | Liberação pronta |

## Fragmentos de combo

| Método | Ação | Descrição |
|------|------|------|
| `a2()` | Dois ataques básicos | Duas entradas rápidas |
| `a3()` | Três ataques básicos | Sequência de três ataques |
| `a4()` | Quatro ataques básicos | Sequência de quatro ataques |
| `Eaa()` | E + dois ataques | Habilidade de Ressonância seguida de dois ataques básicos |
| `E()` | Habilidade de Ressonância | Uma única ativação de E |
| `z()` | Ataque pesado | Mantém o ataque pressionado por 0,50 segundo |
| `Q()` | Habilidade de Eco | Ativação do Eco |
| `R()` | Liberação de Ressonância | Ativação de R |

## Lógica de decisão do combo (`combo()`)

```python
def combo(self):
    self.combo_action(self.a3(), True)
    self.combo_action(self.R(), False)
    if self.random_float() < 0.66:
        self.combo_action(self.z(), True)
        if self.random_float() < 0.66:
            self.combo_action(self.z(), False)
        self.combo_action(self.E(), False)
        if self.random_float() < 0.66:
            self.combo_action(self.a3(), True)
        else:
            self.combo_action(self.a4(), True)
    else:
        self.combo_action(self.a3(), True)
    self.combo_action(self.E(), False)
    self.combo_action(self.Q(), False)
```

```
1. a3() executa três ataques básicos
2. R() tenta ativar a Liberação
3. Há 66% de chance de entrar na ramificação de ataque pesado:
   ├─ z() executa um ataque pesado
   ├─ Há 66% de chance de executar z() novamente
   ├─ E() ativa a habilidade
   └─ Há 66% de chance de usar a3() / 34% de chance de usar a4()
4. Há 34% de chance de executar apenas a3()
5. E() ativa a habilidade
6. Q() ativa o Eco
```

## Características do projeto

1. **Ramificações aleatórias** - usa `random_float()` em vários pontos para evitar um padrão rígido
2. **Execução sem detecção de estado** - segue um fluxo fixo com ramificações aleatórias, sem depender de capturas de tela
3. **Registro próprio** - está em `resonator_map` e usa seu próprio método `combo()`
4. **Detecção pendente** - os detectores de energia e habilidades de `BaseCantarella` estão definidos, mas comentados

---

*Última atualização: 07/02/2026*
