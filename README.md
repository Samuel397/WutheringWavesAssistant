<div align="center">
<img src="src/gui/resource/images/logo.ico" alt="Logo do Wuthering Waves Assistant" width="192" height="192" />

# Wuthering Waves Assistant — PT-BR

[![Licença AGPL-3.0](https://img.shields.io/github/license/Samuel397/WutheringWavesAssistant)](LICENSE)
[![Projeto original](https://img.shields.io/badge/upstream-wakening%2FWutheringWavesAssistant-2ea44f)](https://github.com/wakening/WutheringWavesAssistant)

Fork brasileiro do Wuthering Waves Assistant, com interface e reconhecimento do jogo em Português (Brasil).

</div>

![Wuthering Waves Assistant](assets/static/HomePage.png)

## Sobre este fork

Este repositório preserva o histórico e a licença AGPL-3.0 do projeto original de
[wakening](https://github.com/wakening/WutheringWavesAssistant). O objetivo do fork é tratar PT-BR como idioma de primeira classe:

- interface completa do assistente em Português (Brasil);
- reconhecimento por OCR dos textos oficiais do jogo em português;
- nomes de personagens, chefes, desafios, regiões, botões e estados de combate em PT-BR;
- testes de cobertura para evitar que uma atualização deixe tarefas sem tradução;
- documentação e mensagens de diagnóstico compreensíveis para usuários brasileiros.

As traduções usadas para reconhecer o jogo são baseadas nos textos oficiais presentes nos arquivos da versão instalada. Não é feita tradução automática durante a execução.

## Recursos

- tarefas diárias e semanais;
- combate automático com identificação da equipe;
- desafios, chefes e coleta de Ecos;
- exploração e rotas;
- avanço de diálogos e cenas da história;
- síntese e gerenciamento de Ecos;
- execução em segundo plano nos fluxos que usam mensagens de janela.

Nem todo recurso é apropriado para toda conta ou versão do jogo. Comece sempre com uma tarefa curta e observe a primeira execução depois de cada atualização.

## Requisitos do jogo

- Windows 10 ou 11;
- texto do jogo em **Português**;
- atalhos de teclado restaurados para o padrão;
- brilho e filtros do jogo restaurados para o padrão;
- HDR e filtros de GPU desativados;
- resolução 16:9 recomendada;
- câmera: redefinição, correção de movimento e correção de combate ativadas;
- overlays que cobrem a interface do jogo desativados ou movidos para fora das regiões reconhecidas.

O assistente deve ser iniciado como administrador para que captura e comandos de janela funcionem de forma consistente.

## Instalação a partir do código-fonte

### 1. Instale o Conda e o Git

Instale o [Miniconda para Python 3.12](https://repo.anaconda.com/miniconda/Miniconda3-py312_24.11.1-0-Windows-x86_64.exe) e o [Git para Windows](https://git-scm.com/download/win).

Durante a instalação do Miniconda, habilite a opção de adicioná-lo ao `PATH`. Depois, abra um novo PowerShell e execute:

```powershell
conda -V
conda init powershell
```

Feche e abra o PowerShell novamente após a inicialização.

### 2. Clone o fork

Use uma pasta cujo caminho não contenha caracteres especiais:

```powershell
git clone https://github.com/Samuel397/WutheringWavesAssistant.git
cd WutheringWavesAssistant
```

### 3. Prepare o ambiente

Abra o PowerShell como administrador. Na primeira instalação, permita a execução de scripts para o usuário atual:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Crie o ambiente usando o instalador do projeto:

```powershell
./scripts/rebuild_conda_env.ps1
```

Escolha a variante adequada à sua GPU. A opção CPU funciona como alternativa quando não houver um runtime de GPU compatível.

### 4. Inicie o assistente

Ative o ambiente criado pelo instalador e execute:

```powershell
conda activate wwa-cuda
python main.py
```

Se você instalou a variante CPU, use o nome de ambiente correspondente. Depois da primeira inicialização bem-sucedida, o `WWA.exe` também pode ser usado como lançador.

## Configuração em PT-BR

1. Abra as configurações do assistente.
2. Em **Idioma da interface**, selecione **Português (Brasil)**.
3. Na tela inicial, em **Texto do jogo**, selecione **Português (Brasil)**.
4. Confirme que o próprio Wuthering Waves está usando Português.
5. Comece com apenas uma tarefa habilitada e acompanhe o terminal do assistente.

O idioma da interface e o idioma reconhecido no jogo são configurações diferentes. Os dois devem estar corretos.

## Desenvolvimento e testes

O projeto exige Python 3.10–3.12. Com o ambiente de desenvolvimento ativo:

```powershell
python -m pytest -q `
  tests/core/i18n_pt_test.py `
  tests/core/runtime_messages_pt_test.py `
  tests/gui/test_pt_br_translation.py `
  tests/service/legacy_pt_ocr_test.py `
  -c tests/pytest.ini
```

Esse comando executa a suíte hermética de PT-BR. A suíte completa herdada do
upstream inclui testes manuais que enviam comandos ao jogo, além de casos que
dependem de módulos opcionais; não a execute com o jogo aberto sem revisar e
isolar previamente esses testes.

Os testes de localização verificam, entre outros pontos:

- carregamento do catálogo Qt `pt_BR`;
- cobertura das chaves de OCR usadas pelos fluxos executáveis;
- identificação de personagens em português;
- páginas e estados que antes aceitavam apenas chinês ou inglês;
- ausência de traduções vazias nos recursos habilitados.

## Manter o fork atualizado

O repositório original deve permanecer configurado como `upstream`:

```powershell
git remote add upstream https://github.com/wakening/WutheringWavesAssistant.git
git fetch upstream
git rebase upstream/main
```

Depois de cada atualização do jogo, rode os testes de cobertura e valide uma tarefa curta antes de usar fluxos longos.

## Solução de problemas

### O assistente não reconhece a tela

- confirme que **Texto do jogo** está configurado como Português (Brasil) tanto no jogo quanto no assistente;
- restaure brilho, filtros e atalhos;
- desative HDR e overlays;
- confirme que a janela do jogo está em resolução 16:9;
- consulte `logs/wwa.log` e a página **Terminal**.

### A equipe não é reconhecida

Abra a tela de equipe e confirme que os nomes dos personagens estão visíveis. Personagens adicionados em versões posteriores podem exigir atualização do mapa de textos do fork.

### Uma tarefa entra em repetição

Interrompa a execução pelo botão do assistente. Não deixe uma tarefa repetir indefinidamente após atualização do jogo; registre a tela e o trecho correspondente do log para corrigirmos o reconhecimento.

## Licença e aviso

Este fork é distribuído sob a [GNU Affero General Public License v3.0](LICENSE), assim como o projeto original. Modificações distribuídas ou oferecidas como serviço devem respeitar as obrigações da AGPL-3.0.

O projeto usa OCR, visão computacional e automação de entrada. O uso de automação pode contrariar os termos do jogo e causar sanções à conta. Use por sua conta e risco. Este projeto é gratuito e de código aberto; sua venda é proibida pelos termos definidos pelo projeto original.
