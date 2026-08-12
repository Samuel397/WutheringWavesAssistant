# Documentação de arquitetura do sistema

## 1. Visão geral do sistema

### 1.1 Posicionamento do projeto

O **WutheringWavesAssistant (WWA)** é um assistente de automação para Wuthering Waves. Ele opera exclusivamente por reconhecimento visual, combinando OCR para textos e YOLO para detecção de objetos. Os principais recursos incluem:

- **Farm automático de BOSS** - navegação, combate e coleta de Ecos
- **Combos inteligentes** - execução automática do combo mais adequado ao estado das habilidades do Ressonador
- **Bloqueio de Ecos** - identificação e bloqueio automáticos de Ecos com bons atributos
- **História automática** - avanço automático de diálogos e cenas
- **Atividades diárias** - execução automática de tarefas diárias

### 1.2 Pilha de tecnologia

| Categoria | Tecnologia |
|------|------|
| Linguagem | Python 3.10 ~ 3.12 |
| Estrutura GUI | PySide6 + PySide6-FluentWidgets |
| Mecanismo de OCR | RapidOCR / PaddleOCR |
| Detecção de alvo | YOLO (ONNX Runtime) |
| Processamento de imagem | OpenCV, NumPy, Pillow |
| Captura de tela | MSS, DXCam |
| Simulação de teclado e mouse | pynput, pydirectinput |
| Injeção de dependência | dependency-injector |
| Gerenciamento de configuração | OmegaConf (YAML) |
| Gerenciamento de pacotes | Poetry |

### 1.3 Princípios de projeto

1. **Reconhecimento exclusivamente visual** - não altera a memória do jogo nem injeta DLLs; todas as funções dependem da análise de capturas de tela
2. **Decisão inteligente** - detecta o estado das habilidades pelas cores dos pixels e seleciona dinamicamente o combo mais adequado
3. **Projeto modular** - encapsula a lógica de combo de cada Ressonador para facilitar manutenção e extensão
4. **Tolerância a falhas** - usa operações redundantes para reduzir falhas de combo causadas por variações na taxa de quadros ou interrupções

## 2. Estrutura do projeto

```
WutheringWavesAssistant/
├── main.py                    # Ponto de entrada do programa
├── config.yaml                # Arquivo de configuração do usuário
├── pyproject.toml             # Dependências e configuração de build
├── WWA.exe                    # Inicializador do Windows
├── WWA一键更新.bat            # Script de atualização em um clique (nome de arquivo legado)
│
├── src/                       # Diretório-raiz do código-fonte
│   ├── __init__.py            # Definição da versão
│   ├── application.py         # Inicialização e composição do aplicativo
│   │
│   ├── config/                # Camada de configuração
│   │   ├── app_config.py      # Leitura da configuração do aplicativo
│   │   ├── config.py          # Classe base de configuração
│   │   ├── echo_config.py     # Configuração do bloqueio de Ecos
│   │   ├── gui_config.py      # Configuração da GUI
│   │   ├── keyboard_mapping_config.py  # Mapeamento de teclas
│   │   └── logging_config.py  # Configuração de logs
│   │
│   ├── controller/            # Camada de controladores
│   │   ├── base_controller.py # Classe base dos controladores
│   │   └── main_controller.py # Controlador principal e agendamento de tarefas
│   │
│   ├── core/                  # Lógica de negócio central
│   │   ├── boss.py            # Definições de dados dos BOSS
│   │   ├── combat/            # Sistema de combate ⭐️
│   │   │   ├── combat_core.py # Núcleo do combate (BaseResonator, ColorChecker)
│   │   │   ├── combat_system.py # Gerenciamento da equipe e agendamento de combos
│   │   │   └── resonator/     # Implementações dos combos por Ressonador
│   │   │       ├── generic.py      # Ressonador genérico
│   │   │       ├── camellya.py     # Camellya
│   │   │       ├── cantarella.py   # Cantarella
│   │   │       ├── cartethyia.py   # Cartethyia
│   │   │       ├── changli.py      # Changli
│   │   │       ├── ciaccona.py     # Ciaccona
│   │   │       ├── encore.py       # Encore
│   │   │       ├── jinhsi.py       # Jinhsi
│   │   │       ├── lynae.py        # Lynae
│   │   │       ├── mornye.py       # Mornye
│   │   │       ├── phoebe.py       # Phoebe
│   │   │       ├── phrolova.py     # Phrolova
│   │   │       ├── rover.py        # Rover
│   │   │       ├── sanhua.py       # Sanhua
│   │   │       ├── shorekeeper.py  # Shorekeeper
│   │   │       └── verina.py       # Verina
│   │   │
│   │   ├── contexts.py        # Gerenciamento de contexto
│   │   ├── environs.py        # Variáveis de ambiente
│   │   ├── exceptions.py      # Exceções personalizadas
│   │   ├── injector.py        # Contêiner de injeção de dependências
│   │   ├── interface.py       # Interfaces dos serviços
│   │   ├── i18n.py            # Textos, páginas e idiomas reconhecidos
│   │   ├── pages.py           # Definições de páginas
│   │   ├── regions.py         # Definições de regiões
│   │   └── tasks.py           # Definições de tarefas
│   │
│   ├── service/               # Camada de serviços
│   │   ├── auto_boss_service.py      # Farm automático de BOSS
│   │   ├── auto_pickup_service.py    # Coleta automática
│   │   ├── auto_story_service.py     # História automática
│   │   ├── boss_info_service.py      # Informações dos BOSS
│   │   ├── control_service.py        # Controle de teclado e mouse
│   │   ├── daily_workflow.py         # Fluxo das tarefas diárias
│   │   ├── echo_merge_workflow.py    # Fluxo de fusão de Ecos
│   │   ├── img_service.py            # Serviço de captura de tela
│   │   ├── ocr_service.py            # Reconhecimento OCR
│   │   ├── od_service.py             # Detecção de objetos
│   │   ├── page_event_service.py     # Eventos de páginas
│   │   └── window_service.py         # Gerenciamento da janela
│   │
│   ├── gui/                   # Camada da GUI
│   │   ├── gui.py             # Ponto de entrada da GUI
│   │   ├── common/            # Componentes compartilhados
│   │   ├── components/        # Componentes da interface
│   │   ├── resource/          # Recursos (ícones e imagens)
│   │   └── view/              # Telas da interface
│   │
│   ├── util/                  # Camada de utilitários
│   │   ├── audio_util.py      # Utilitários de áudio
│   │   ├── dxcam_util.py      # Capturas com DXCam
│   │   ├── file_util.py       # Utilitários de arquivos
│   │   ├── hwnd_util.py       # Identificadores de janelas
│   │   ├── img_util.py        # Processamento de imagens
│   │   ├── keymouse_util.py   # Simulação de teclado e mouse
│   │   ├── mss_util.py        # Capturas com MSS
│   │   ├── onnx_util.py       # Inferência ONNX
│   │   ├── paddleocr_util.py  # PaddleOCR
│   │   ├── rapidocr_util.py   # RapidOCR
│   │   ├── screenshot_util.py # Utilitários de captura de tela
│   │   ├── windows_util.py    # Utilitários do Windows
│   │   ├── winreg_util.py     # Registro do Windows
│   │   ├── wrap_util.py       # Decoradores
│   │   └── yolo_util.py       # Detecção com YOLO
│   │
├── assets/                    # Recursos
│   ├── model/                 # Modelos YOLO/ONNX
│   ├── map/                   # Dados de mapa
│   ├── macro/                 # Modelos de macro
│   ├── static/                # Recursos estáticos
│   └── template/              # Modelos visuais
│
├── tests/                     # Testes
│   ├── conftest.py            # Configuração dos testes
│   ├── pytest.ini             # Configuração do pytest
│   ├── config/                # Testes de configuração
│   ├── core/                  # Testes da lógica central
│   ├── service/               # Testes dos serviços
│   └── util/                  # Testes dos utilitários
│
├── scripts/                   # Scripts
│   └── rebuild_conda_env.ps1  # Reconstrução do ambiente Conda
│
└── docs/                      # Documentação
    ├── README.md              # Índice da documentação
    ├── ARCH.md                # Arquitetura do sistema
    ├── COMBAT_SYSTEM.md       # Sistema de combate
    ├── CONTRIBUTING_COMBO.md  # Guia de desenvolvimento de combos
    └── resonators/            # Documentação dos combos por Ressonador
```

## 3. Camadas de arquitetura

WWA adota um design de arquitetura de quatro camadas:

```
┌──────────────────────────────────────┐
│          Camada GUI (PySide6)         │  Interação, parâmetros e logs
├──────────────────────────────────────┤
│       Camada de controladores         │  Tarefas, sinais e controle de fluxo
├──────────────────────────────────────┤
│        Camada de serviços             │  Captura, OCR, YOLO e entrada
├──────────────────────────────────────┤
│          Camada de núcleo             │  Combate, BOSS e combos
└──────────────────────────────────────┘
```

### 3.1 Camada GUI

- Interface moderna construída em PySide6 e FluentWidgets
- Fornece início e parada de tarefas, configuração de parâmetros e exibição de log em tempo real
- Comunica-se com o controlador de backend por meio do sistema de sinais do Qt

### 3.2 Camada controladora

- O `MainController` recebe sinais da GUI e agenda os serviços responsáveis por cada tarefa
- Gerencia o ciclo de vida das tarefas (iniciar, pausar e parar)
- Permite trocar dinamicamente a configuração pelo caminho do arquivo

### 3.3 Camada de serviço

- **ControlService** - encapsula operações de teclado e mouse (ataque básico, habilidades, esquiva, salto etc.)
- **ImgService** - Serviço de captura de tela para obter a tela do jogo
- **OcrService** - Reconhecimento de texto OCR (RapidOCR / PaddleOCR)
- **OdService** - detecção de objetos por YOLO (incluindo Ecos)
- **AutoBossService** - controla o fluxo de farm automático de BOSS
- **EchoLockService** - identifica os atributos dos Ecos e aplica o bloqueio

### 3.4 Camada de núcleo

- **CombatSystem** - núcleo do sistema de combate; gerencia a equipe e agenda os combos dos Ressonadores
- **BaseResonator** - classe base dos Ressonadores; define a interface de combos e os métodos comuns
- **ColorChecker** - Detector de cores de pixel para identificar o status de prontidão das habilidades
- Cada classe concreta de Ressonador encapsula a lógica de combo daquele personagem

## 4. Fluxo de dados principal

### 4.1 Processo de inicialização do aplicativo

```
main.py
  ├─ environs.load_env()          # Carrega variáveis de ambiente
  ├─ logging_config.setup_logging() # Configura os logs
  └─ application.run()
       ├─ before()                 # Verifica permissões de administrador
       ├─ MainController()         # Inicializa o backend
       ├─ Vincula os sinais da GUI # Conecta interface e backend
       └─ wwa()                    # Inicia o loop principal do Qt
```

### 4.2 Processo de batalha

```
Usuário clica em Iniciar
  ├─ MainController.execute()
  │    └─ AutoBossService.start()
  │         ├─ Teletransporta até o BOSS
  │         ├─ Aguarda o BOSS aparecer
  │         ├─ CombatSystem.start()
  │         │    └─ CombatSystem.run()        # Loop principal do combate
  │         │         ├─ Verifica pausa e tempo limite
  │         │         ├─ Ordena Ressonadores (Suporte → DPS → Cura)
  │         │         ├─ toggle() troca de Ressonador
  │         │         └─ resonator.combo()    # Executa o combo
  │         │              ├─ Captura e detecta habilidades
  │         │              ├─ Seleciona a rota de combo
  │         │              └─ combo_action() executa as ações
  │         ├─ Aguarda o fim do combate
  │         ├─ Procura e coleta o Eco
  │         └─ Repete para o próximo BOSS
```

### 4.3 Fluxo de decisão dos combos inteligentes

```
resonator.combo()
  ├─ img_service.screenshot()      # Captura a tela do jogo
  ├─ ColorChecker.check()          # Verifica as cores dos ícones
  │    ├─ Habilidade de Ressonância (E) disponível?
  │    ├─ Liberação de Ressonância (R) disponível?
  │    ├─ Habilidade de Eco (Q) disponível?
  │    ├─ Detecta a barra de energia
  │    └─ Detecta estados especiais
  ├─ Decide a rota conforme o estado # Ramificações if/else
  └─ combo_action(action_seq)      # Executa a sequência
       ├─ [tecla, duração, espera]
       └─ Percorre e executa cada ação
```

## 5. Modelo de concorrência

### 5.1 Modelo de threads

```
Thread principal (GUI Qt)
  │
  ├─ Thread de combate (CombatSystem._thread)
  │    └─ Executa continuamente os combos
  │
  └─ Threads de tarefas em segundo plano
       ├─ AutoBossService
       ├─ AutoPickupService
       └─ WindowService (monitoramento da janela do jogo)
```

### 5.2 Mecanismo de pausa/retomada

- Usa `threading.Event` para controlar a pausa e a retomada do combate
- `event.set()` retoma o combate; `event.clear()` o pausa
- Permite pausa automática durante o intervalo configurado em `_delay_time`
- Um `StopError` interrompe imediatamente a sequência de combo do Ressonador

## 6. Tecnologias-chave

### 6.1 Detecção de habilidades em nível de pixel (ColorChecker)

Determina se uma habilidade está pronta verificando a cor dos pixels em coordenadas específicas da tela:

- O ícone fica branco quando a habilidade está pronta `(255, 255, 255)`
- Durante a recarga, o ícone fica cinza ou assume outras cores
- Suporta combinação lógica OR/AND de vários pontos de detecção
- Suporta correspondência de tolerância de cores

### 6.2 Adaptação de Resolução (DynamicPointTransformer)

- A resolução básica é 1280×720
- Suporta escala na proporção padrão 16:9
- Suporta mapeamento e alinhamento para proporções não padrão, como 16:10 e 21:9
- Calcula automaticamente a transformação das coordenadas com base no tamanho da captura de tela

### 6.3 Sequência de ações do combo

Cada ação é uma tupla `[tecla, duração do pressionamento, tempo de espera]`:

- `Tecla`: `"a"` (ataque básico), `"E"` (habilidade), `"R"` (Liberação), `"Q"` (Eco), `"z"` (ataque pesado), `"j"` (salto), `"d"` (esquiva), `"w"` (avançar) etc.
- `Duração do pressionamento`: tempo em segundos durante o qual a tecla permanece pressionada; distingue toques de pressionamentos longos
- `Tempo de espera`: intervalo em segundos após soltar a tecla, usado para aguardar a animação

---

*Última atualização: 07/02/2026*
