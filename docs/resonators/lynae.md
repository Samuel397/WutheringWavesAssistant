# Lynae — análise da lógica de combos

## Informações básicas

| Campo | Valor |
|------|------|
| Ressonador | Lynae |
| Função | Support (Suporte) |
| Atributo | Spectro |
| Tipo de Concerto | Círculo amarelo (`concerto_spectro`) |
| Versão | v3.0 |
| Arquivo-fonte | `src/core/combat/resonator/lynae.py` |

## Mecânicas do Ressonador

Lynae possui um sistema de combate em **duas fases**:

### Fase de Amostragem Óptica (forma normal)

- Ataques básicos e pesados possuem até três etapas
- Ao preencher a energia Iridescente, carregar o ataque pesado — com resistência a interrupção e redução de dano — ativa a forma de patins
- Uma carga completa concede 120 pontos de Luz Fluente

### Estado Desfile Caleidoscópico (forma de patins)

- Ataques básicos possuem até cinco etapas
- O salto aprimorado consome 40 pontos de Luz Fluente e concede um ponto de Cor Verdadeira, até o máximo de três
- Três pontos de Cor Verdadeira permitem um ataque descendente aprimorado
- O ataque pesado mantém Lynae girando automaticamente e consome Vigor
- **A Habilidade de Outro encerra o Desfile Caleidoscópico; a Intro não**
- Depois de E, a sequência continua a partir do segundo ataque básico

## Detecção do estado das habilidades

### Detecção de estados especiais

| Item detectado | Lógica | Descrição |
|--------|------|------|
| Colisão de Inspiração | AND | Energia Iridescente cheia; permite entrar na forma de patins (quatro pontos brancos) |
| Luz Fluente cheia (120) | OR | Energia Luz Fluente no máximo |
| Cor Verdadeira 1 | Tolerância 50 | Primeiro segmento, em tons de verde |
| Cor Verdadeira 2 | Tolerância 50 | Segundo segmento, em tons de amarelo |
| Cor Verdadeira 3 | Tolerância 50 | Terceiro segmento, em tons de rosa |
| Ataque do Desfile Caleidoscópico | AND | Ícone de ataque básico da forma de patins |
| Salto de Luz Ilusória | OR | Salto aprimorado disponível |
| Respingo Iridescente | AND | Primeira versão do ataque descendente aprimorado |
| Impacto Visual | AND | Ataque descendente aprimorado |

### Detecção de habilidades

| Item detectado | Lógica | Descrição |
|--------|------|------|
| Habilidade de Ressonância E | AND | E disponível |
| Habilidade de Eco Q | OR | Eco disponível |
| Liberação de Ressonância R | OR | R disponível |

## Fragmentos de combo

### Fase de Amostragem Óptica

| Método | Descrição |
|------|------|
| `optical_sampling_stage_a3()` | Três ataques básicos |
| `optical_sampling_stage_E2a()` | E + dois ataques básicos |
| `optical_sampling_stage_z()` | Carrega o ataque pesado e entra na forma de patins |

### Estado Desfile Caleidoscópico

| Método | Descrição |
|------|------|
| `kaleidoscopic_parade_a5()` | Cinco ataques básicos sobre os patins |
| `kaleidoscopic_parade_E4a()` | E + quatro ataques básicos sobre os patins |
| `kaleidoscopic_parade_z()` | Ataque pesado giratório |
| `kaleidoscopic_parade_j()` | Salto aprimorado |
| `kaleidoscopic_parade_3jza()` | Três saltos + ataque pesado + ataque básico |
| `kaleidoscopic_parade_2jzja()` | Dois saltos + ataque pesado + salto + ataque básico |

### Ações gerais

| Método | Descrição |
|------|------|
| `a()` | Um ataque básico |
| `a2()` | Dois ataques básicos |
| `E()` | Habilidade de Ressonância |
| `aQ()` | Ataque básico + Eco |
| `Q()` | Habilidade de Eco |
| `R()` | Liberação de Ressonância (espera 4,7 segundos) |

## Lógica de decisão do combo (`combo()`)

```
Ativa o Eco com Q()
Captura a tela e detecta todos os estados

## Fase de Amostragem Óptica (fora dos patins)
se não estiver no Desfile Caleidoscópico:
    se a Energia Iridescente não estiver cheia:
        ├─ E disponível → optical_sampling_stage_E2a()
        ├─ E indisponível → optical_sampling_stage_a3()
        └─ R disponível → R()
    verifica novamente a Energia Iridescente
    se ainda não estiver cheia → return
    entra na forma de patins: optical_sampling_stage_z()

## Estado Desfile Caleidoscópico
se estiver no Desfile Caleidoscópico ou tiver acabado de entrar nos patins:
    E disponível → E()
    R disponível → R()

    três segmentos de Cor Verdadeira cheios:
        └─ j() para saltar + a() + a() para atacar em queda
        └─ return

    escolha aleatória: 50% kaleidoscopic_parade_z() / 50% optical_sampling_stage_a3()

    ## Fluxo de ataques aéreos
    verifica a Luz Fluente:
    ├─ Luz Fluente cheia → kaleidoscopic_parade_2jzja(), com três saltos e ataque em queda
    ├─ Salto de Luz Ilusória indisponível → return
    ├─ primeiro salto aprimorado: j() + z()
    ├─ verifica novamente:
    │   ├─ Luz Fluente cheia ou insuficiente → aQ() encerra com ataque em queda
    │   └─ segundo salto aprimorado: j()
    │       ├─ Luz Fluente cheia ou insuficiente → aQ()
    │       └─ terceiro salto aprimorado: j() + aQ()

alternativa final: R() + optical_sampling_stage_a3() + E()
```

## Características do projeto

1. **Sistema de duas fases** - Amostragem Óptica e Desfile Caleidoscópico possuem comportamentos completamente diferentes
2. **Gerenciamento da Luz Fluente** - controla a energia com precisão para decidir quantos saltos executar
3. **Detecção em várias camadas** - acompanha Energia Iridescente, Luz Fluente e Cor Verdadeira
4. **Gerenciamento de Vigor** - como o giro consome Vigor, alterna com 50% de chance entre ataque pesado e básico
5. **Cores distintas de energia** - os três segmentos de Cor Verdadeira usam verde, amarelo e rosa e exigem detectores diferentes

---

*Última atualização: 06/02/2026*
