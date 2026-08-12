# Jinhsi — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | Jinhsi |
| Função | MainDPS (DPS principal) |
| Atributo | Spectro |
| Tipo de Concerto | Círculo amarelo (`concerto_spectro`) |
| Versão | v1.1 |
| Arquivo-fonte | `src/core/combat/resonator/jinhsi.py` |

## Mecânicas do Ressonador

Jinhsi possui um dos sistemas mais complexos, com **quatro estados da Habilidade de Ressonância**:

- **E1 — Luz do Entardecer** - E básico, usado como indicador de recarga
- **E2 — Brilho Divino** - surge após quatro ataques básicos e inicia o estado aéreo
- **E3 — Ascensão Lunar** - ataque ascendente disponível durante a sequência de E2
- **E4 — Dragão Rompe o Céu** - disparo final de maior potência

### Rotas de combo

- **Rotação normal:** a4 → E1 → a3 → E2 → a2 → E3 → a → E4
- **Rotação rápida:** a4 → E2 → cancelamento com esquiva → salto → esquiva → E4
- **Entrada rápida por Intro:** j + a + j + E (dependente de 120 FPS)

## Detecção do estado das habilidades

### Detecção de habilidades

| Item detectado | Lógica | Descrição |
|--------|------|------|
| E1 — Luz do Entardecer | AND | E básico; o ícone indica que a habilidade não está em recarga |
| E2 — Brilho Divino | AND | Surge após quatro ataques básicos |
| Entrada E2 (amarelo) | AND | Estado amarelo de E2 ao entrar pela Intro, com tolerância 50 |
| E3 — Ascensão Lunar | AND | Habilidade de ataque ascendente |
| E4 — Dragão Rompe o Céu | AND | Disparo final |
| Entrada E4 (amarelo) | AND | Estado amarelo de E4 ao entrar pela Intro |
| Habilidade de Eco Q | OR | Eco disponível |
| Liberação de Ressonância R | OR | R disponível |

## Fragmentos de combo

| Método | Ação | Descrição |
|------|------|------|
| `a4()` | Quatro ataques para liberar E2 | Sequência completa + uma entrada redundante de ataque |
| `a2()` | Dois ataques rápidos | Preparação da entrada rápida; aciona o ataque descendente |
| `E2_full_combo_E4()` | E2 direto para E4 | E2 + cancelamento com esquiva + salto + esquiva → E4 |
| `E2_full_combo_E3E4()` | E2, ascensão e E4 | E2 + cancelamento com esquiva + E3 + ataque básico + E4 |
| `E2_intro_full_combo()` | Sequência rápida de Intro | j + a + j + E (dependente de 120 FPS) |
| `E3_full_combo()` | Sequência iniciada por E3 | Ataque básico + E + ataque básico + E + ataque básico + E |
| `E()` | Somente E | Usado para E4/E2; pressiona E duas vezes por redundância |
| `Q()` | Habilidade de Eco | Ativa o Eco |
| `R()` | Liberação de Ressonância | Ativa R e espera 2 segundos |

## Lógica de decisão do combo (`combo()`)

```
Captura a tela e detecta o estado de todas as habilidades
Ativa o Eco com Q()

1. E2 pronta ou entrada em campo no estado E2:
   ├─ sleep(0.5) + E() ativa E2
   ├─ sleep(0.5) + E() pressiona novamente para garantir a ativação
   └─ return

2. E4 pronta ou entrada em campo no estado E4:
   ├─ E() ativa E4 (disparo)
   ├─ R() tenta ativar a Liberação de forma redundante
   └─ return

3. Liberação pronta:
   ├─ R() ativa a Liberação
   ├─ E() tenta ativar E de forma redundante
   └─ return

4. E3 pronta:
   └─ E3_full_combo(), combo completo de E3
   └─ return

5. E1 pronta (E não está em recarga):
   ├─ a4() executa quatro ataques básicos para liberar E2
   ├─ Verifica E2:
   │   ├─ E2 pronta → com poucos PV do BOSS, usa o disparo rápido de E4; caso contrário, escolhe aleatoriamente E4 ou E3E4
   │   └─ E2 não está pronta → E() + R()
   └─ return

6. Contingência (E está em recarga):
   ├─ a4() executa ataques básicos
   ├─ Verifica E4/E2 → E()
   └─ R()
```

## Características do projeto

1. **Quatro estados de E** - identifica quatro aparências distintas do ícone da Habilidade de Ressonância
2. **Cor especial na entrada** - os ícones de E2 e E4 ficam amarelos durante a Intro, em vez de brancos
3. **Duas rotas rápidas** - E4 direto é mais rápido e vulnerável a interrupções; E3 → E4 é mais estável, porém mais lento
4. **Decisão pelos PV do BOSS** - abaixo de 20%, prioriza E4 direto para encerrar o combate
5. **Entradas redundantes de E** - repete E em pontos críticos para compensar quedas na taxa de quadros
6. **Intro rápida** - `j+a+j+E` em `COMBO_SEQ_2` depende de execução a 120 FPS

---

*Última atualização: 06/02/2026*
