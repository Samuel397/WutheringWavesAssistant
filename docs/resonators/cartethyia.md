# Cartethyia — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | Cartethyia |
| Função | MainDPS (DPS principal) |
| Atributo | Aero |
| Tipo de Concerto | Círculo verde (concerto_aero) |
| Versão | v2.4 |
| Arquivo-fonte | `src/core/combat/resonator/cartethyia.py` |

## Mecânicas do Ressonador

Cartethyia possui um sistema exclusivo de **duas formas**:

- **Cartethyia** - forma normal, capaz de invocar três espadas
- **Fleurdelys** - forma transformada, ativada por R

### Sistema de Três Espadas

Cartethyia pode invocar três espadas, que causam dano ao serem recolhidas:
- **Espada da Autoridade Divergente (Espada 1)** - invocada por ataque pesado
- **Espada da Divindade (Espada 2)** - invocada pelo quarto ataque básico
- **Espada da Humanidade (Espada 3)** - invocada pela Habilidade de Ressonância

### Troca de forma

- **Cartethyia → Fleurdelys:** R entra na forma Fleurdelys
- **Fleurdelys → Avatar de Cartethyia:** R assume o avatar de Cartethyia
- **Avatar de Cartethyia → Fleurdelys:** R retorna à forma Fleurdelys

### Efeito de Erosão Aero

- Dura 16 segundos e expira ao fim desse período
- O quarto ataque básico aplica uma carga
- A Habilidade de Ressonância aplica duas cargas
- A Habilidade de Intro aplica duas cargas

## Detecção do estado das habilidades

### Habilidades de Cartethyia

| Item detectado | Lógica | Descrição |
|--------|------|------|
| Habilidade de Ressonância de Cartethyia | AND | Habilidade E de Cartethyia |
| Habilidade de Eco | OR | Eco pronto |
| Liberação de Ressonância R | AND | Ouça as orações do cavaleiro de coração |

### Habilidades de Fleurdelys

| Item detectado | Lógica | Descrição |
|--------|------|------|
| Habilidade de Ressonância E1 - Frudelis | AND | Esta espada significa maré |
| Habilidade de Ressonância E2 - Frudelis | AND | Use o vento para cortar as ondas e derrotar o inimigo |
| Avatar de Fleurdelys | AND | O ícone de R indica a forma Fleurdelys |
| Avatar de Cartethyia | AND | O ícone de R indica a forma Cartethyia |
| Lâmina da Maré Uivante | AND | A Liberação de Fleurdelys está disponível |

### Reconhecimento de status

| Item detectado | Lógica | Descrição |
|--------|------|------|
| Espada da Autoridade Divergente (Espada 1) | AND | Detecta a espada invocada pelo ataque pesado |
| Espada da Divindade (Espada 2) | OR | Detecta a espada invocada pelo ataque básico |
| Espada da Humanidade (Espada 3) | OR | Detecta a espada invocada por E |
| Manifestação | AND | Detecta o estado manifestado de Fleurdelys |
| Determinação | OR | Detecta a barra de energia de Fleurdelys |

### Variáveis dinâmicas de tempo de execução

```python
is_avatar_cartethyia_attack_done = False  # Indica se o Avatar de Cartethyia já concluiu uma sequência de ataques
```

## Fragmentos de combo

### Fragmentos de Cartethyia

| Método | Descrição |
|------|------|
| `cartethyia_a4()` | Quatro ataques básicos; invoca a Espada da Divindade |
| `cartethyia_a2_start()` | Os dois primeiros ataques |
| `cartethyia_a2_end()` | Dois golpes após ataque básico |
| `cartethyia_a4Eza()` | 4 etapas de ataque básico + E + ataque pesado + ataque básico |
| `cartethyia_Ea()` | E + ataque básico; invoca a Espada da Humanidade |
| `cartethyia_Eza()` | E+ataque crítico+ataque básico |
| `cartethyia_E()` | Apenas habilidade E |
| `cartethyia_z()` | Ataque pesado; invoca a Espada da Autoridade Divergente |
| `cartethyia_ja()` | Ataque caindo, espada embainhada |
| `cartethyia_R()` | R transforma Cartethyia em Fleurdelys |

### Fragmentos de Fleurdelys

| Método | Descrição |
|------|------|
| `fleurdelys_a5()` | Cinco ataques básicos de Fleurdelys |
| `fleurdelys_a2()` | Os dois primeiros ataques básicos de Fleurdelys |
| `fleurdelys_EaaEaaa()` | Sequência dupla de E de Fleurdelys |
| `fleurdelys_EaaE()` | E + ataques básicos + E |
| `fleurdelys_za_a3()` | Ataque pesado, disparo, decolagem e ataques aéreos |
| `fleurdelys_ja2()` | Dois ataques básicos aéreos |
| `fleurdelys_ja3()` | Três ataques básicos aéreos |
| `fleurdelys_R_blade_of_howling_squall()` | Liberação de Fleurdelys: Lâmina da Maré Uivante |

### Troca de forma

| Método | Descrição |
|------|------|
| `avatar_cartethyia_to_fleurdelys_Ra3()` | Avatar de Cartethyia → Fleurdelys + ataques básicos |
| `fleurdelys_to_avatar_cartethyia_Ra3()` | Fleurdelys → Avatar de Cartethyia + ataques básicos |

## Lógica de decisão do combo (`combo()`)

```
Entrada em campo: a3() executa alguns ataques básicos

Captura a tela e detecta todas as habilidades e formas

1. A Liberação do Avatar de Fleurdelys está pronta (detectada pela Lâmina da Maré Uivante):
   ├─ Ativa a Liberação com fleurdelys_R_blade_of_howling_squall()
   ├─ Verifica os PV do BOSS
   └─ Se o E de Cartethyia estiver pronto → Q + cartethyia_a4() + cartethyia_Eza()
   └─ return

2. Ativa o Eco com Q

3. Estado do Avatar de Cartethyia:
   ├─ Com E → cartethyia_a4() + cartethyia_Eza()
   ├─ Sem E → cartethyia_a4()
   ├─ Primeiro ataque → marca a sequência como concluída e aguarda a sincronização da rotação
   └─ Ataques seguintes → marca que é necessário trocar de forma

4. Avatar de Fleurdelys ou troca necessária:
   ├─ Se for necessário trocar → avatar_to_fleurdelys_Ra3() ou R()
   │   └─ fleurdelys_EaaE()
   ├─ Com E → fleurdelys_EaaE()
   ├─ Sem E → fleurdelys_ja3()
   └─ Verifica a Liberação → se estiver pronta, ativa-a e complementa com o E de Cartethyia ou com as três espadas

5. Cartethyia na forma normal (com E ou R):
   ├─ Com R → completa as três espadas (a4+Eza+z+ja)
   ├─ Sem R → executa a sequência de ataques básicos e verifica E
   ├─ Verifica R → se estiver pronto, cartethyia_R() transforma a personagem
   └─ Quando Fleurdelys entra → fleurdelys_EaaE() ou fleurdelys_ja3()

6. Contingência → cartethyia_a4()
```

## Características do projeto

1. **Troca dinâmica de forma** - o sistema acompanha se o estado atual é Cartethyia, Fleurdelys ou o avatar
2. **Coleta das três espadas** - detecta quais espadas existem e prioriza completar o conjunto antes da Liberação
3. **Estado em tempo de execução** - `is_avatar_cartethyia_attack_done` acompanha se o ataque do avatar foi concluído
4. **Verificação dos PV do BOSS** - encerra cedo quando os PV ficam em ≤ 0,01, evitando ataques desnecessários

---

*Última atualização: 07/02/2026*
