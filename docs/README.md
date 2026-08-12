# Central de documentação do Wuthering Waves Assistant

Bem-vindo à documentação técnica do WutheringWavesAssistant (WWA).

## 📚 Documentação principal

### [ARCH.md](./ARCH.md) - Documentação da arquitetura do sistema ⭐️

**Descrição completa da arquitetura do sistema**, incluindo o seguinte:

1. **Visão geral do sistema** - objetivo do projeto, pilha tecnológica e princípios de projeto
2. **Estrutura do projeto** - organização dos diretórios, divisão dos módulos e arquivos principais
3. **Camadas de arquitetura** - Explicação detalhada da arquitetura de quatro camadas (GUI → Controlador → Serviço → Núcleo)
4. **Módulos principais** - sistema de combate, farm automático de BOSS, bloqueio de Ecos e reconhecimento OCR/YOLO
5. **Fluxo de dados** - processo completo entre a ação do usuário e o controle do jogo
6. **Modelo de concorrência** - combate em múltiplas threads e pausa/retomada orientada por eventos

---

### [config.yaml](../config.yaml) - Parâmetros de configuração

**Guia completo do arquivo de configuração** (`config.yaml`), cobrindo todas as seções:

- **Configuração básica** - Caminhos de jogo, modelos, OCR, logs
- **Tratamento de travamentos do jogo** - Reinicialização agendada
- **Configuração de combate** - duração máxima do combate, tempo ocioso e busca de Ecos
- **Estratégia de combate** - sintaxe de combos em `FightTactics` e ordem de atuação em `FightOrder`
- **BOSS alvo** - listas de BOSS das versões 1.0 e 2.0

---

### [COMBAT_SYSTEM.md](./COMBAT_SYSTEM.md) - Visão geral do sistema de combate

**Documentação técnica completa do sistema de combos inteligentes:**

- **Projeto da arquitetura** - `CombatSystem`, `BaseResonator` e `ColorChecker`
- **Mecanismo de detecção de cores** - Reconhecimento de status de habilidade em nível de pixel
- **Mecanismo de execução de combos** - sequências de ações em `combo_action`
- **Classificação e ordenação dos Ressonadores** - prioridade de DPS, Suporte e Cura
- **Gerenciamento da equipe** - lógica de troca e tratamento de Ressonadores abatidos

---

### [CONTRIBUTING_COMBO.md](./CONTRIBUTING_COMBO.md) - Guia de contribuição para desenvolvimento de combo ⭐️

**Tutorial completo para desenvolver combos personalizados para novos Ressonadores:**

- **Preparação antes do desenvolvimento** - Ferramentas, conhecimento, estrutura de arquivos
- **Desenvolvimento de classe base** - Definição de detector de habilidades, aquisição de coordenadas e implementação de método de detecção
- **Desenvolvimento da classe concreta** - sequências de ações, fragmentos de combo e lógica principal de `combo()`
- **Registro e teste** - Adição de enumeração, registro do sistema, método de teste
- **Melhores práticas** - convenções de nomenclatura, organização de código e otimização de desempenho
- **Perguntas frequentes** - Perguntas frequentes e dicas de depuração

---

## 🎮 Documentação de combos por Ressonador

Cada Ressonador com combo personalizado possui um documento de análise detalhada:

| Ressonador | Documentação | Função | Atributo |
|------|------|------|------|
| Camellya | [camellya.md](./resonators/camellya.md) | DPS principal | Havoc |
| Cantarella | [cantarella.md](./resonators/cantarella.md) | Suporte | Havoc |
| Cartethyia | [cartethyia.md](./resonators/cartethyia.md) | DPS principal | Aero |
| Changli | [changli.md](./resonators/changli.md) | DPS secundário | Fusion |
| Ciaccona | [ciaccona.md](./resonators/ciaccona.md) | Suporte | Aero |
| Encore | [encore.md](./resonators/encore.md) | DPS principal | Fusion |
| Jinhsi | [jinhsi.md](./resonators/jinhsi.md) | DPS principal | Spectro |
| Lynae | [lynae.md](./resonators/lynae.md) | Suporte | Spectro |
| Mornye | [mornye.md](./resonators/mornye.md) | Cura | Fusion |
| Phoebe | [phoebe.md](./resonators/phoebe.md) | Suporte | Spectro |
| Phrolova | [phrolova.md](./resonators/phrolova.md) | DPS principal | Fusion |
| Rover | [rover.md](./resonators/rover.md) | DPS secundário | Genérico |
| Sanhua | [sanhua.md](./resonators/sanhua.md) | Suporte | Glacio |
| Shorekeeper | [shorekeeper.md](./resonators/shorekeeper.md) | Cura | Spectro |
| Verina | [verina.md](./resonators/verina.md) | Cura | Spectro |
| Ressonador genérico | [generic.md](./resonators/generic.md) | DPS secundário | Genérico |

---

## 🚀 Início rápido

### Para usuários

1. **Entenda o sistema** → leia [ARCH.md](./ARCH.md) para conhecer a arquitetura geral
2. **Configure o projeto** → consulte o arquivo [config.yaml](../config.yaml)
3. **Conheça o combate** → leia [COMBAT_SYSTEM.md](./COMBAT_SYSTEM.md) para entender o mecanismo de combos
4. **Veja cada Ressonador** → consulte os documentos em [resonators/](./resonators/)

### Para contribuir com o desenvolvimento

1. **Desenvolvimento de combos** → leia [CONTRIBUTING_COMBO.md](./CONTRIBUTING_COMBO.md) para aprender a criar um combo personalizado
2. **Implementações de referência** → use os documentos em [resonators/](./resonators/) como exemplos
3. **Validação** → teste os combos no campo de treinamento e em combate real

---

*Última atualização: 07/02/2026*
