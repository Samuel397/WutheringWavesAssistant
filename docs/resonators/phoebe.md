# Phoebe — análise da lógica de combos

## Informações básicas

| Propriedade | Valor |
|---|---|
| Personagem | Phoebe |
| Função | Suporte |
| Atributo | Fotônico (`Spectro`) |
| Tipo de Concerto | Círculo amarelo (`concerto_spectro`) |
| Versão | v2.1 |
| Arquivo-fonte | `src/core/combat/resonator/phoebe.py` |
| Registro | ⚠️ Não registrada em `resonator_map`; usa o combo genérico |

## Mecânica do personagem

Phoebe é uma personagem de suporte que usa pistolas e possui um sistema próprio de **Oração/Voz Divina**.

### Sistema de Oração

- A **Oração possui no máximo 120 pontos** e é preenchida automaticamente em 24 segundos.
- Antes da escolha de um estado, a detecção verifica quatro pixels azuis acima da barra de vida.
- Após a escolha, o ponto de detecção se desloca para a direita.

### Sistema de Voz Divina

- A **Voz Divina possui no máximo 60 pontos**.
- **Absolvição** (modo de dano): concede 60 pontos ao entrar no estado; cada Ataque Pesado aprimorado consome 15 pontos, permitindo até 4 usos.
- **Confissão** (modo de suporte): concede 60 pontos ao entrar no estado; cada Ataque Pesado aprimorado consome 30 pontos, aplica 5 acúmulos de Estridência Fotônica e permite até 2 usos.
- A barra da Voz Divina fica **amarela** durante a Absolvição e **azul-clara** durante a Confissão.

### Operação

- Quando a Oração está cheia e a Voz Divina está vazia:
  - mantenha o **Ataque Básico** pressionado para entrar em Absolvição;
  - mantenha **E** pressionado para entrar em Confissão.
- No ciclo de dano, execute 3 Ataques Básicos + 1 Ataque Pesado até consumir a Voz Divina e aguarde a Oração recarregar.

## Detecção do estado das habilidades

### Detecção de Oração

| Item detectado | Lógica | Observação |
|---|---|---|
| Oração (estado inicial) | AND | Verifica quatro pontos antes da escolha de estado |
| Oração (após trocar de estado) | OR | Verifica um ponto após a troca |

### Detecção de Voz Divina

| Item detectado | Lógica | Observação |
|---|---|---|
| Voz Divina 15 | OR | Voz Divina ≥ 15 pontos; três pontos de detecção |
| Voz Divina 30 | OR | Voz Divina ≥ 30 pontos; três pontos de detecção |

### Detecção dos estados aprimorados

| Item detectado | Lógica | Observação |
|---|---|---|
| Absolvição (dano) | AND | Amarelo no centro da barra: `(175,234,248)` |
| Confissão (suporte) | AND | Azul-claro no centro da barra: `(255,255,253)` |

### Detecção de habilidades

| Item detectado | Lógica | Observação |
|---|---|---|
| Habilidade de Ressonância E1 | AND | Primeira forma de E pronta |
| Habilidade de Ressonância E2 | AND | Segunda forma de E pronta |
| Habilidade de Eco | OR | O Eco está pronto |
| Liberação de Ressonância R | OR | R está pronto |

## Trechos de combo

Phoebe oferece diversos trechos de combo, mas o método `combo()` ainda não foi implementado:

| Método | Descrição | Observação |
|---|---|---|
| `a4()` | 4 ataques básicos | Sequência completa de quatro ataques |
| `a_intro()` | Ataque da Introdução | Aguarda 1.3 segundo para cobrir a animação de entrada |
| `a2_end()` | 2 ataques finais | Executa os dois últimos ataques de `a4()` |
| `z_musical_essence_3()` | Ataque Pesado com 3 segmentos | Consome três segmentos e mantém o Ataque Pesado pressionado |
| `E()` | Habilidade E | Pressiona E duas vezes como redundância |
| `E3a()` | E + 3 ataques básicos | E aplica um acúmulo; a sequência começa no segundo Ataque Básico |
| `jEz()` | Salto + E + Ataque Pesado | Usa E no ar e, em seguida, o Ataque Pesado com três segmentos |
| `jEaaa()` | Salto + 3 ataques básicos | O nome contém E, mas a sequência não pressiona a tecla `e` |
| `jEaaajaaa()` | Ciclo duplo | Alterna `jE`, ataques básicos, salto e novos ataques básicos |
| `jaaa()` | Salto + 3 ataques básicos | Executa ataques após o salto |
| `Q()` | Habilidade de Eco | Usa o Eco |
| `R_aero_erosion()` | R para Erosão Eólica | Variante de R para Erosão Eólica |
| `R_spectro_frazzle()` | R para Estridência Fotônica | Variante de R para Estridência Fotônica, seguida de Ataque Básico |

### Operações especiais com pistolas

`COMBO_SEQ` contém operações genéricas para personagens que usam pistolas:

- **Metralhadora em mira** — alterna rapidamente `G` para mirar e `a` para atacar.
- **Ataque contínuo em mira** — alterna `a` e `G` em ritmo mais lento.

## Lógica de decisão do combo (`combo()`)

```python
def combo(self):
    # Usa Phoebe como suporte na equipe de Zani
    pass  # Ainda não implementado
```

⚠️ **`combo()` está vazio.** Phoebe não está registrada em `resonator_map`; em uso real, a execução recua para o combo genérico de `GenericResonator`.

## Estado atual do projeto

1. `BasePhoebe` implementa todos os métodos de detecção de estado das habilidades.
2. `Phoebe` implementa diversos métodos com trechos de combo.
3. `COMBO_SEQ` contém a sequência completa do campo de treinamento, inclusive as operações especiais com pistolas.
4. **A única parte ausente é a lógica de decisão de `combo()`.**

## Próximos passos sugeridos

Segundo os comentários do código, a lógica de Phoebe deve girar em torno deste ciclo:

1. Aguardar o preenchimento da Oração.
2. Consumir a Oração para entrar em Absolvição ou Confissão e obter Voz Divina.
3. Consumir a Voz Divina com ciclos de três Ataques Básicos + um Ataque Pesado.
4. Quando a Voz Divina acabar, aguardar a Oração recarregar e repetir o ciclo.

---

*Última atualização: 2026-02-06*
