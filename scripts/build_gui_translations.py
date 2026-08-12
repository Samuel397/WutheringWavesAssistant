"""Build the Brazilian Portuguese Qt catalog used by WWA.

The upstream catalog contains many inherited QFluentWidgets Gallery entries but
misses most strings from WWA itself.  This script keeps the legacy entries,
extracts the current Python ``tr()`` calls, adds the QFluentWidgets strings used
by the application, and fails if a source string has no reviewed translation.
"""

from __future__ import annotations

import argparse
import ast
import copy
import os
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
GUI_ROOT = ROOT / "src" / "gui"
I18N_ROOT = GUI_ROOT / "resource" / "i18n"
BASE_CATALOG = I18N_ROOT / "gallery.zh_CN.ts"
OUTPUT_CATALOG = I18N_ROOT / "gallery.pt_BR.ts"


# Proper names and identifiers whose established spelling is also used in pt-BR.
KEEP_SOURCE = {
    "20th Century Boy", "Another One Bites The Dust", "Ball Breaker",
    "Born This Way", "Crazy Diamond", "Crazy diamond", "Cream Starter",
    "D4C • Love Train", "Dirty Deeds Done Dirt Cheap", "Dio Brando",
    "Email", "G Cup", "GitHub", "Gold Experience", "Heaven's Door",
    "Hermit Purple", "Hierophant Green", "Jotaro Kujo", "Julius·Zeppeli",
    "Killer Queen", "King Crimson", "King Nothing", "Love Love Deluxe",
    "Made in Haven", "Mandom", "Metallica", "Mikami Yua", "November Rain",
    "Ozone Baby", "Paisley Park", "Paper Moon King", "QFluentWidgets",
    "Rap", "SOFT & WET", "Scary Monster", "Sex Pistols", "Shoko",
    "Silver Chariot", "Smooth Operators", "Soft and Wet", "Star Platinum",
    "Sticky Fingers", "Stone Free", "The Grateful Dead", "The Matte Kudasai",
    "The World", "Tusk Act 4", "Walking Heart", "Will A. Zeppeli",
    "Wonder of U", "Jonathan Joestar", "{boss_name}", "{text}",
    "{text} - {sign}",
}


TRANSLATIONS = {
    # Existing QFluentWidgets Gallery catalog.
    "A simple button with text content": "Um botão simples com texto",
    "A button with graphical content": "Um botão com conteúdo gráfico",
    "A hyperlink button that navigates to a URI": "Um botão de hiperlink que abre um URI",
    "A 2-state CheckBox": "Uma caixa de seleção com dois estados",
    "A 3-state CheckBox": "Uma caixa de seleção com três estados",
    "A ComboBox with items": "Uma caixa de combinação com itens",
    "A group of RadioButton controls in a button group": "Um grupo de botões de opção",
    "A simple horizontal slider": "Um controle deslizante horizontal simples",
    "A simple switch button": "Um botão de alternância simples",
    "Off": "Desativado",
    "On": "Ativado",
    "Standard push button": "Botão padrão",
    "Accent style button": "Botão com estilo de destaque",
    "Two-state CheckBox": "Caixa de seleção com dois estados",
    "Three-state CheckBox": "Caixa de seleção com três estados",
    "Choose your stand": "Escolha seu Stand",
    "An editable ComboBox": "Uma caixa de combinação editável",
    "Send": "Enviar",
    "Save": "Salvar",
    "A push button with drop down menu": "Um botão com menu suspenso",
    "A tool button with drop down menu": "Um botão de ferramenta com menu suspenso",
    "Start practicing": "Começar a praticar",
    "A split push button with drop down menu": "Um botão dividido com menu suspenso",
    "Sing": "Cantar",
    "Jump": "Pular",
    "Music": "Música",
    "A split tool button with drop down menu": "Um botão de ferramenta dividido com menu suspenso",
    "Accent style applied to push button": "Estilo de destaque aplicado ao botão",
    "Accent style applied to tool button": "Estilo de destaque aplicado ao botão de ferramenta",
    "A primary color push button with drop down menu": "Um botão na cor principal com menu suspenso",
    "A primary color tool button with drop down menu": "Um botão de ferramenta na cor principal com menu suspenso",
    "A primary color split push button with drop down menu": "Um botão dividido na cor principal com menu suspenso",
    "A primary color split tool button with drop down menu": "Um botão de ferramenta dividido na cor principal com menu suspenso",
    "A transparent push button": "Um botão transparente",
    "A transparent tool button": "Um botão de ferramenta transparente",
    "A transparent push button with drop down menu": "Um botão transparente com menu suspenso",
    "A transparent tool button with drop down menu": "Um botão de ferramenta transparente com menu suspenso",
    "A simple toggle push button": "Um botão de alternância simples",
    "A simple toggle tool button": "Um botão de ferramenta de alternância simples",
    "A transparent toggle push button": "Um botão de alternância transparente",
    "A transparent toggle tool button": "Um botão de ferramenta de alternância transparente",
    "Transparent push button": "Botão transparente",
    "Pill push button": "Botão em formato de pílula",
    "Tag": "Etiqueta",
    "Pill tool button": "Botão de ferramenta em formato de pílula",
    "QFluentWidgets official website": "Site oficial do QFluentWidgets",
    "Open URL": "Abrir URL",
    "Enter the URL of a file, stream, or playlist": "Insira a URL de um arquivo, transmissão ou playlist",
    "Open": "Abrir",
    "Cancel": "Cancelar",
    "A simple DatePicker": "Um seletor de data simples",
    "A DatePicker in another format": "Um seletor de data em outro formato",
    "A simple TimePicker": "Um seletor de horário simples",
    "A TimePicker using a 24-hour clock": "Um seletor de horário no formato de 24 horas",
    "A TimePicker with seconds column": "Um seletor de horário com coluna de segundos",
    "A simple CalendarPicker": "Um seletor de calendário simples",
    "A CalendarPicker in another format": "Um seletor de calendário em outro formato",
    "Show dialog": "Mostrar caixa de diálogo",
    "A frameless message box": "Uma caixa de mensagem sem moldura",
    "A message box with mask": "Uma caixa de mensagem com máscara",
    "A color dialog": "Uma caixa de diálogo de cores",
    "This is a frameless message dialog": "Esta é uma caixa de mensagem sem moldura",
    "If the content of the message box is veeeeeeeeeeeeeeeeeeeeeeeeeery long, it will automatically wrap like this.": "Se o conteúdo da caixa de mensagem for muuuuuuuuuuuuuuuuuuuuito longo, ele será quebrado automaticamente assim.",
    "Choose color": "Escolher cor",
    "This is a message dialog with mask": "Esta é uma caixa de mensagem com máscara",
    "Show teaching tip": "Mostrar dica explicativa",
    "A teaching tip": "Uma dica explicativa",
    "With respect, let's advance towards a new stage of the spin.": "Com respeito, vamos avançar para uma nova etapa da rotação.",
    "The shortest shortcut is to take a detour.": "O atalho mais curto é fazer um desvio.",
    "A teaching tip with image and button": "Uma dica explicativa com imagem e botão",
    "Show flyout": "Mostrar painel flutuante",
    "A simple flyout": "Um painel flutuante simples",
    "A flyout with image and button": "Um painel flutuante com imagem e botão",
    "Believe in the spin, just keep believing!": "Acredite na rotação; continue acreditando!",
    "A custom message box": "Uma caixa de mensagem personalizada",
    "Where the tennis ball will land when it touches the net, no one can predict.\nIf that moment comes, I hope the 'goddess' exists.\nIn that case, I would accept it no matter which side the ball falls on.": "Ninguém pode prever de que lado a bola de tênis cairá ao tocar a rede.\nSe esse momento chegar, espero que a ‘deusa’ exista.\nNesse caso, eu aceitaria o resultado, não importa de que lado a bola caísse.",
    "Source code": "Código-fonte",
    "Fluent Icons Library": "Biblioteca de ícones Fluent",
    "Icon name": "Nome do ícone",
    "Enum member": "Membro da enumeração",
    "Flow layout without animation": "Layout fluido sem animação",
    "Flow layout with animation": "Layout fluido com animação",
    "Search icons": "Pesquisar ícones",
    "Home": "Início",
    "Settings": "Configurações",
    "Acrylic label": "Rótulo acrílico",
    "Rounded corners menu": "Menu com cantos arredondados",
    "Show menu": "Mostrar menu",
    "Copy": "Copiar",
    "Cut": "Recortar",
    "Video": "Vídeo",
    "Paste": "Colar",
    "Undo": "Desfazer",
    "Select all": "Selecionar tudo",
    "Help": "Ajuda",
    "Feedback": "Comentários",
    "Add to": "Adicionar a",
    "Command bar": "Barra de comandos",
    "Click the image to open a command bar flyout 👇️🥵": "Clique na imagem para abrir o painel da barra de comandos 👇️🥵",
    "Command bar flyout": "Painel da barra de comandos",
    "Add": "Adicionar",
    "Rotate": "Girar",
    "Zoom in": "Ampliar",
    "Zoom out": "Reduzir",
    "Edit": "Editar",
    "Info": "Informações",
    "Delete": "Excluir",
    "Share": "Compartilhar",
    "Create Date": "Data de criação",
    "Shooting Date": "Data da captura",
    "Name": "Nome",
    "Ascending": "Crescente",
    "Descending": "Decrescente",
    "Add to favorate": "Adicionar aos favoritos",
    "Print": "Imprimir",
    "Save image": "Salvar imagem",
    "Sort": "Ordenar",
    "Modified time": "Data de modificação",
    "Checkable menu": "Menu selecionável",
    "Rounded corners menu with custom widget": "Menu com cantos arredondados e widget personalizado",
    "Manage account profile": "Gerenciar perfil da conta",
    "Payment method": "Forma de pagamento",
    "Redemption code and gift card": "Código de resgate e cartão-presente",
    "A basic pivot": "Uma navegação por pivô básica",
    "A segmented control": "Um controle segmentado",
    "A tab bar": "Uma barra de abas",
    "Documents": "Documentos",
    "Study": "Estudos",
    "Janpanese Sensei": "Professor de japonês",
    "Action Film": "Filme de ação",
    "Folder1": "Pasta 1",
    "Folder2": "Pasta 2",
    "Breadcrumb bar": "Barra de navegação estrutural",
    "Another segmented control": "Outro controle segmentado",
    "Song": "Música",
    "Album": "Álbum",
    "Artist": "Artista",
    "Progress": "Progresso",
    "Smooth scroll area": "Área de rolagem suave",
    "Chitanda Eru is too hot 🥵": "Chitanda Eru é atraente demais 🥵",
    "Smooth scroll area implemented by animation": "Área de rolagem suave implementada com animação",
    "Chitanda Eru is so hot 🥵🥵": "Chitanda Eru é muito atraente 🥵🥵",
    "Single direction scroll scroll area": "Área de rolagem em uma única direção",
    "Chitanda Eru is so hot 🥵🥵🥵": "Chitanda Eru é muito atraente 🥵🥵🥵",
    "Pips pager": "Paginação por pontos",
    "Music on this PC": "Músicas neste computador",
    "Local music library": "Biblioteca de músicas local",
    "Choose folder": "Escolher pasta",
    "Download directory": "Pasta de downloads",
    "Personalization": "Personalização",
    "Application theme": "Tema do aplicativo",
    "Change the appearance of your application": "Altere a aparência do aplicativo",
    "Light": "Claro",
    "Dark": "Escuro",
    "Use system setting": "Usar configuração do sistema",
    "Theme color": "Cor do tema",
    "Change the theme color of you application": "Altere a cor do tema do aplicativo",
    "Interface zoom": "Escala da interface",
    "Change the size of widgets and fonts": "Altere o tamanho dos elementos e das fontes",
    "Language": "Idioma",
    "Set your preferred language for UI": "Escolha o idioma da interface",
    "Material": "Material",
    "Acrylic blur radius": "Raio do desfoque acrílico",
    "The greater the radius, the more blurred the image": "Quanto maior o raio, mais desfocada será a imagem",
    "Software update": "Atualização do aplicativo",
    "Check for updates when the application starts": "Procurar atualizações ao iniciar o aplicativo",
    "The new version will be more stable and have more features": "A nova versão terá mais estabilidade e recursos",
    "About": "Sobre",
    "Open help page": "Abrir página de ajuda",
    "Discover new features and learn useful tips about PyQt-Fluent-Widgets": "Conheça novos recursos e dicas úteis sobre o PyQt-Fluent-Widgets",
    "Provide feedback": "Enviar comentários",
    "Help us improve PyQt-Fluent-Widgets by providing feedback": "Ajude a melhorar o PyQt-Fluent-Widgets enviando seus comentários",
    "Check update": "Procurar atualização",
    "Copyright": "Direitos autorais",
    "Version": "Versão",
    "Configuration takes effect after restart": "A configuração terá efeito após reiniciar",
    "Updated successfully": "Atualizado com sucesso",
    "Mica effect": "Efeito Mica",
    "Apply semi transparent to windows and surfaces": "Aplicar transparência parcial a janelas e superfícies",
    "State tool tip": "Dica de status",
    "Label with a ToolTip": "Rótulo com dica de ferramenta",
    "A label with a ToolTip": "Um rótulo com dica de ferramenta",
    "Show StateToolTip": "Mostrar dica de status",
    "Button with a simple ToolTip": "Botão com uma dica de ferramenta simples",
    "Simple ToolTip": "Dica de ferramenta simples",
    "The model training is complete!": "O treinamento do modelo foi concluído!",
    "Training model": "Treinando modelo",
    "Please wait patiently": "Aguarde um momento",
    "Hide StateToolTip": "Ocultar dica de status",
    "Success": "Sucesso",
    "A closable InfoBar": "Uma barra de informações que pode ser fechada",
    "Warning": "Aviso",
    "A closable InfoBar with long message": "Uma barra de informações com mensagem longa que pode ser fechada",
    "When you look long into an abyss, the abyss looks into you.": "Quando você olha por muito tempo para o abismo, o abismo olha para você.",
    "An InfoBar with custom icon, background color and widget.": "Uma barra de informações com ícone, cor de fundo e widget personalizados.",
    "InfoBar with different pop-up locations": "Barra de informações em diferentes posições",
    "No Internet": "Sem conexão com a internet",
    "Lesson 4": "Lição 4",
    "Lesson 5": "Lição 5",
    "My name is kira yoshikake, 33 years old. Living in the villa area northeast of duwangting, unmarried. I work in Guiyou chain store. Every day I have to work overtime until 8 p.m. to go home. I don't smoke. The wine is only for a taste. Sleep at 11 p.m. for 8 hours a day. Before I go to bed, I must drink a cup of warm milk, then do 20 minutes of soft exercise, get on the bed, and immediately fall asleep. Never leave fatigue and stress until the next day. Doctors say I'm normal.": "Meu nome é Kira Yoshikage, tenho 33 anos. Moro na área de mansões a nordeste de Duwangting e sou solteiro. Trabalho na rede de lojas Guiyou. Todos os dias faço hora extra até as 20h antes de voltar para casa. Não fumo e só bebo socialmente. Durmo às 23h por oito horas. Antes de dormir, tomo um copo de leite morno, faço vinte minutos de exercícios leves, deito e adormeço imediatamente. Nunca levo o cansaço e o estresse para o dia seguinte. Os médicos dizem que sou normal.",
    "Lesson 3": "Lição 3",
    "An error message which won't disappear automatically.": "Uma mensagem de erro que não desaparecerá automaticamente.",
    "The Anthem of man is the Anthem of courage.": "O hino da humanidade é o hino da coragem.",
    "Action": "Ação",
    "Top right": "Superior direito",
    "Top": "Superior",
    "Top left": "Superior esquerdo",
    "Bottom right": "Inferior direito",
    "Bottom": "Inferior",
    "Bottom left": "Inferior esquerdo",
    "Lesson 1": "Lição 1",
    "Don't have any strange expectations of me.": "Não crie expectativas estranhas a meu respeito.",
    "Lesson 2": "Lição 2",
    "Don't let your muscles notice.": "Não deixe seus músculos perceberem.",
    "An indeterminate progress bar": "Uma barra de progresso indeterminada",
    "An determinate progress bar": "Uma barra de progresso determinada",
    "An determinate progress ring": "Um anel de progresso determinado",
    "An indeterminate progress ring": "Um anel de progresso indeterminado",
    "InfoBadge in different styles": "Selos de informação em diferentes estilos",
    "A button with a simple ToolTip": "Um botão com uma dica de ferramenta simples",
    "IsTabMovable": "Permitir mover abas",
    "IsTabScrollable": "Permitir rolar as abas",
    "TabCloseButtonDisplayMode": "Exibição do botão de fechar aba",
    "Always": "Sempre",
    "OnHover": "Ao passar o mouse",
    "Never": "Nunca",
    "IsTabShadowEnabled": "Ativar sombra das abas",
    "TabMaximumWidth": "Largura máxima da aba",
    "Title": "Título",
    "Year": "Ano",
    "Duration": "Duração",
    "ko no dio da！": "Mas era eu, Dio!",
    "A LineEdit with a clear button": "Um campo de texto com botão para limpar",
    "A DoubleSpinBox with a spin button": "Um campo numérico decimal com botões de ajuste",
    "A DateEdit with a spin button": "Um campo de data com botões de ajuste",
    "A TimeEdit with a spin button": "Um campo de horário com botões de ajuste",
    "A DateTimeEdit with a spin button": "Um campo de data e hora com botões de ajuste",
    "A SpinBox with a spin button": "Um campo numérico com botões de ajuste",
    "A simple TextEdit": "Um editor de texto simples",
    "A autosuggest line edit": "Um campo de texto com sugestões automáticas",
    "Type a stand name": "Digite o nome de um Stand",
    "Enter your password": "Digite sua senha",
    "A password line edit": "Um campo de senha",
    "Documentation": "Documentação",
    "Source": "Código-fonte",
    "Toggle theme": "Alternar tema",
    "Send feedback": "Enviar comentários",
    "Support me": "Apoiar o projeto",
    "Basic input": "Entrada básica",
    "Status & info": "Status e informações",
    "Scrolling": "Rolagem",
    "Layout": "Layout",
    "Text": "Texto",
    "Icons": "Ícones",
    "View": "Visualização",
    "Date & time": "Data e hora",
    "Navigation": "Navegação",
    "Price": "Preço",
    "Dialogs & flyouts": "Caixas de diálogo e painéis flutuantes",
    "Menus & toolbars": "Menus e barras de ferramentas",
    "JoJo 1 - Phantom Blood": "JoJo 1 — Phantom Blood",
    "JoJo 3 - Stardust Crusaders": "JoJo 3 — Stardust Crusaders",
    "A simple TreeView": "Uma exibição em árvore simples",
    "A TreeView with Multi-selection enabled": "Uma exibição em árvore com seleção múltipla",
    "A simple TableView": "Uma exibição de tabela simples",
    "A simple ListView": "Uma exibição de lista simples",
    "Flip view": "Exibição em cartões",

    # WWA application strings.
    " *有新版本 {version}": " *Nova versão disponível: {version}",
    " *检查更新失败": " *Falha ao verificar atualizações",
    "Add \"Wuthering Waves.exe\"": "Adicionar ‘Wuthering Waves.exe’",
    "BOSS:": "CHEFE:",
    "Boss Rush Parameters": "Parâmetros do farm de chefes",
    "Boss Rush: ": "Farm de chefes: ",
    "Default auto is the lowest boss level that drops Echo; changing it makes it faster": "No modo automático, é escolhido o menor nível de chefe que concede Eco; altere para acelerar o farm",
    "Game Parameters": "Parâmetros do jogo",
    "Help us improve Wuthering Waves Assistant by providing feedback": "Ajude a melhorar o Wuthering Waves Assistant enviando seus comentários",
    "If you play multiple games, configure this accordingly": "Se você usa várias instalações do jogo, configure a pasta correspondente",
    "Installation Directory": "Pasta de instalação",
    "Notice": "Avisos",
    "OK": "OK",
    "Param": "Parâmetros",
    "Refresh: ": "Atualização: ",
    "Reminder: ": "Lembrete: ",
    "Restart every {hours} hours, {minutes} minutes, and {seconds} seconds": "Reiniciar a cada {hours} h, {minutes} min e {seconds} s",
    "Restart the game at regular intervals. This only applies to the Boss Rush task": "Reinicia o jogo em intervalos regulares. Aplica-se somente ao farm de chefes",
    "Scheduled Game Restart": "Reinício programado do jogo",
    "Start": "Iniciar",
    "Stop": "Parar",
    "Successful": "Concluído",
    "Target Boss Level": "Nível do chefe",
    "Target Boss Names": "Chefes selecionados",
    "Task: ": "Tarefa: ",
    "Terminal": "Terminal",
    "Tips": "Dicas",
    "Update": "Atualização",
    "Validate: ": "Validação: ",
    "{challenge} - {boss}": "{challenge} — {boss}",
    "{challenge} - {region}": "{challenge} — {region}",
    "{challenge} - {weapon}": "{challenge} — {weapon}",
    "{challenge} - {weapon} - {region}": "{challenge} — {weapon} — {region}",
    "不选择": "Não selecionar",
    "任务设置": "Configurações de tarefas",
    "任意配队，人数不限，建议带奶，建议1280x720最低画质挂机还省电。\n若游戏内没有1280x720分辨率选项，或修改后游戏微闪一下没有反应，这是游戏的问题，换成其他修改后有效的小分辨率，如1600x900。\n日常可刷梦魇哀声鸷，通过合成获取1c3c。不建议多选。\n萌新建议降低索拉等级刷。": "Use qualquer equipe, sem limite de integrantes; é recomendável levar um curador. Para economizar energia, use 1280×720 e a qualidade gráfica mínima.\nSe 1280×720 não estiver disponível ou a tela piscar sem aplicar a alteração, escolha outra resolução baixa que funcione, como 1600×900.\nNo farm diário, você pode enfrentar o Pesadelo: Mourning Aix e usar a síntese para obter Ecos de custo 1 e 3. Não é recomendável selecionar vários chefes.\nJogadores iniciantes podem reduzir o nível SOL3 para facilitar o farm.",
    "使用自定义模板": "Usar modelo personalizado",
    "保存/停止快捷键: ESC": "Atalho para salvar/parar: Esc",
    "保存目录: {dir}": "Pasta de salvamento: {dir}",
    "先约电台:": "Podcast Pioneiro:",
    "全选": "Selecionar tudo",
    "共鸣者突破材料:": "Materiais de Ascensão de Resonador:",
    "关于": "Sobre",
    "分": "min",
    "刷BOSS:": "Farmar chefes:",
    "刷新": "Atualizar",
    "剧情": "História",
    "参数异常": "Parâmetros inválidos",
    "可任选。日常可刷梦魇哀声鸷来合成1c3c。梦魇或副本内boss建议单刷。": "A seleção é livre. No farm diário, enfrente o Pesadelo: Mourning Aix para sintetizar Ecos de custo 1 e 3. É recomendável enfrentar sozinho chefes de Pesadelo ou de instância.",
    "启动脚本，回到游戏点击开始，挂机别动直到结束": "Inicie o script, volte ao jogo, clique em Iniciar e não mexa nos controles até o fim",
    "启动脚本，回到游戏点击开始，正常操作即可，快捷键ESC可退出并保存，直接点停止不保存": "Inicie o script, volte ao jogo e clique em Iniciar. Jogue normalmente; Esc encerra e salva. O botão Parar encerra sem salvar.",
    "周本:": "Desafio semanal:",
    "基础设置": "Configurações básicas",
    "声骸": "Ecos",
    "声骸材料:": "Materiais de Eco:",
    "声骸融合:": "Fusão de Ecos:",
    "备注: ": "Observação: ",
    "多选": "Seleção múltipla",
    "已经是最新版了": "Você já está usando a versão mais recente",
    "录制自定义模板:": "Gravar modelo personalizado:",
    "战斗、跑图都需手动操作，不能代肝剧情！": "O combate e a navegação pelo mapa são manuais; este recurso não conclui a história por você!",
    "探索": "Exploração",
    "敬请期待": "Em breve",
    "日常": "Diárias",
    "时": "h",
    "智能连招Beta": "Combos inteligentes (Beta)",
    "未选择Boss": "Nenhum chefe selecionado",
    "未选择boss": "Nenhum chefe selecionado",
    "梦魇聚落:": "Acampamentos de Pesadelo:",
    "检查更新失败": "Falha ao verificar atualizações",
    "模板为人工录制，本身并不完美，因设备、网络等影响，可能存在极小的正负延迟，对不上轴ESC重跑即可，都能3S全奖励。作者也打不出100%，部分歌曲只有90%+，欢迎使用录制功能，将你的模板文件、结算分数、按键设置截图打包分享到群里，由群主校准后合进脚本内。\n角色选陆赫斯/莫宁，默认按键0延迟。\n游戏卡顿，节奏无法对齐的，应降低游戏分辨率和画质，如1600x900极致性能60fps60fps60fps，保证流畅。\n请勿直接修改预设模板，有问题先检查选项是否勾选正确": "Os modelos são gravados manualmente e não são perfeitos. O dispositivo ou a rede podem causar pequenos adiantamentos ou atrasos. Se o ritmo dessincronizar, pressione Esc e execute novamente; ainda é possível obter todas as recompensas com classificação 3S. Nem o autor consegue 100% em todas as músicas, e algumas chegam apenas a mais de 90%. Você pode usar a gravação e compartilhar no grupo o arquivo do modelo, a pontuação final e uma captura das teclas configuradas para que o administrador calibre e incorpore o modelo ao script.\nEscolha Luuk Herssen ou Mornye e mantenha o atraso padrão das teclas em 0.\nSe houver travamentos e o ritmo não sincronizar, reduza a resolução e a qualidade gráfica — por exemplo, 1600×900, desempenho máximo e 60 fps — para manter a fluidez.\nNão altere diretamente os modelos predefinidos. Em caso de problema, primeiro confira se as opções corretas estão marcadas.",
    "模板为人工录制，本身并不完美，因设备、网络等影响，可能存在极小的正负延迟，对不上轴ESC重跑即可，都能3S全奖励。作者也打不出100%，部分歌曲只有90%+，欢迎使用录制功能，将你的模板文件、结算分数、按键设置截图打包分享到群里，由群主校准后合进脚本内。\n角色选陆赫斯/莫宁，默认按键0延迟。\n请勿直接修改预设模板，有问题先检查选项是否勾选正确": "Os modelos são gravados manualmente e não são perfeitos. O dispositivo ou a rede podem causar pequenos adiantamentos ou atrasos. Se o ritmo dessincronizar, pressione Esc e execute novamente; ainda é possível obter todas as recompensas com classificação 3S. Nem o autor consegue 100% em todas as músicas, e algumas chegam apenas a mais de 90%. Você pode usar a gravação e compartilhar no grupo o arquivo do modelo, a pontuação final e uma captura das teclas configuradas para que o administrador calibre e incorpore o modelo ao script.\nEscolha Luuk Herssen ou Mornye e mantenha o atraso padrão das teclas em 0.\nNão altere diretamente os modelos predefinidos. Em caso de problema, primeiro confira se as opções corretas estão marcadas.",
    "武器及技能材料:": "Materiais de arma e habilidade:",
    "残象聚落:": "Ninhos de Discórdias Tacet:",
    "没有要运行的任务": "Nenhuma tarefa selecionada para execução",
    "沿着节拍启航:": "Navegar no Ritmo:",
    "活动": "Eventos",
    "活跃度:": "Atividade:",
    "活跃行迹:": "Recompensas de atividade:",
    "测试中，仅开放部分关卡。有问题及时群里反馈，最好录屏，或者截图游戏窗口和脚本日志，遮住uid。\n使用前建议关闭微星小飞机、英伟达统计数据、Mod等，避免遮挡游戏ui影响识别": "Em testes; apenas algumas fases estão disponíveis. Relate problemas no grupo, de preferência com uma gravação ou capturas da janela do jogo e dos logs do script, ocultando o UID.\nAntes de usar, feche o MSI Afterburner, as estatísticas da NVIDIA, mods e outros overlays que possam cobrir a interface do jogo e prejudicar o reconhecimento.",
    "测试版，仅开放部分关卡。有问题及时群里反馈，最好录屏，或者截图游戏窗口和脚本日志，遮住uid。\n使用前建议关闭微星小飞机、英伟达统计数据、Mod等，避免遮挡游戏ui影响识别": "Versão de teste; apenas algumas fases estão disponíveis. Relate problemas no grupo, de preferência com uma gravação ou capturas da janela do jogo e dos logs do script, ocultando o UID.\nAntes de usar, feche o MSI Afterburner, as estatísticas da NVIDIA, mods e outros overlays que possam cobrir a interface do jogo e prejudicar o reconhecimento.",
    "游戏文本:": "Idioma do jogo:",
    "用法：启动脚本，回到游戏，点击鼠标侧键，将自动战斗，再次点击侧键或ESC键，可停止战斗。\n适用于日常锄地，跑到怪附近，点侧键后挂机，打完点侧键停下，上车去下一个点。": "Como usar: inicie o script, volte ao jogo e pressione o botão lateral do mouse para começar o combate automático. Pressione-o novamente ou use Esc para parar.\nÉ indicado para o farm diário no mundo aberto: aproxime-se dos inimigos, pressione o botão lateral e aguarde. Ao terminar, pressione-o outra vez e siga para o próximo ponto.",
    "界面大小": "Tamanho da janela",
    "看剧情-自动剧情": "Assistir à história automaticamente",
    "秒": "s",
    "脚本优先操控运行中的游戏窗口，不管这个参数，多开或游戏没启动时才看选了哪个": "O script prioriza a janela do jogo que já estiver em execução. Esta opção só é usada com várias instâncias abertas ou quando o jogo ainda não foi iniciado.",
    "自动": "Automático",
    "自动对话": "Diálogo automático",
    "自动战斗:": "Combate automático:",
    "自动拾取:": "Coleta automática:",
    "自动拾取路过的声骸、草药、食材、宝箱。任意分辨率": "Coleta automaticamente Ecos, ervas, ingredientes e baús encontrados pelo caminho. Funciona em qualquer resolução.",
    "自动播放": "Reprodução automática",
    "自动音游:": "Jogo rítmico automático:",
    "自定义时间": "Intervalo personalizado",
    "自定义模板  目录: {dir}": "Modelo personalizado — pasta: {dir}",
    "自定义路径，适合多游戏，同时运行多个游戏时优先操控该路径下的游戏窗口": "Pasta personalizada para várias instalações; quando houver mais de um jogo aberto, a janela desta pasta terá prioridade",
    "自定义连招": "Combo personalizado",
    "融合背包内未锁定的声骸，任意分辨率": "Funde os Ecos desbloqueados do inventário. Funciona em qualquer resolução.",
    "触发剧情后可直接双手离开键盘，自动播放，自动选择对话，直到这段剧情结束。任意分辨率": "Quando uma cena de história começar, o script reproduzirá e escolherá os diálogos automaticamente até o fim. Funciona em qualquer resolução.",
    "触发剧情后自动帮你点击跳过，任意分辨率": "Quando uma cena começar, o script acionará Pular automaticamente. Funciona em qualquer resolução.",
    "设置时间": "Definir intervalo",
    "设置连招": "Configurar combo",
    "请勾选需要的功能项": "Marque os recursos que deseja usar",
    "请勾选需要的功能项，暂不支持多选": "Marque o recurso que deseja usar; a seleção múltipla ainda não é compatível",
    "调整界面宽高": "Altere a largura e a altura da janela",
    "跑图等都需手动操作，不能代肝大世界！": "A navegação pelo mapa é manual; este recurso não explora o mundo aberto por você!",
    "跳过剧情": "Pular cenas da história",
    "运行": "Executar",
    "运行设备:": "Dispositivo de execução:",
    "连招: ": "Combo: ",
    "施工中...": "Em desenvolvimento...",
    "逗号分隔, e,q,r为技能, l(小写L)为向后闪避, a为普攻(默认连点0.3秒), 数字为间隔时间,a~0.5为普攻按下0.5秒,a(0.5)为连续普攻0.5秒，摩托车短按请用q~0.1": "Separe as ações por vírgulas. e, q e r são habilidades; l (L minúsculo) esquiva para trás; a executa ataques básicos (cliques a cada 0,3 s por padrão); números definem intervalos; a~0.5 mantém o ataque básico pressionado por 0,5 s; a(0.5) repete ataques básicos por 0,5 s. Para um toque curto na moto, use q~0.1.",
    "邮件:": "Correio:",
    "重置": "Redefinir",
    "预设模板:": "Modelo predefinido:",
    "默认": "Padrão",
    "默认关闭": "Desativado por padrão",
    "默认开启，支持任意角色，不限人数，建议带一个奶。": "Ativado por padrão. Compatível com qualquer personagem e tamanho de equipe; é recomendável levar um curador.",
    "默认自动获取。例: {gamePath}": "Detectado automaticamente por padrão. Exemplo: {gamePath}",
    "默认自动获取。当前未找到游戏路径，请手动设置": "A detecção é automática por padrão, mas a pasta do jogo não foi encontrada. Configure-a manualmente.",

    # QFluentWidgets runtime controls not present in its bundled pt-BR resources.
    "AM": "AM",
    "PM": "PM",
    "hour": "hora",
    "minute": "minuto",
    "second": "segundo",
    "Pick a date": "Escolha uma data",
    "Blue": "Azul",
    "Edit Color": "Editar cor",
    "Green": "Verde",
    "Opacity": "Opacidade",
    "Red": "Vermelho",
    "Choose ": "Escolher ",
    "Custom color": "Cor personalizada",
    "Default color": "Cor padrão",
    "day": "dia",
    "month": "mês",
    "year": "ano",
    "Mo": "seg.",
    "Tu": "ter.",
    "We": "qua.",
    "Th": "qui.",
    "Fr": "sex.",
    "Sa": "sáb.",
    "Su": "dom.",
    "Jan": "jan.",
    "Feb": "fev.",
    "Mar": "mar.",
    "Apr": "abr.",
    "May": "mai.",
    "Jun": "jun.",
    "Jul": "jul.",
    "Aug": "ago.",
    "Sep": "set.",
    "Oct": "out.",
    "Nov": "nov.",
    "Dec": "dez.",
    "January": "janeiro",
    "February": "fevereiro",
    "March": "março",
    "April": "abril",
    "May": "maio",
    "June": "junho",
    "July": "julho",
    "August": "agosto",
    "September": "setembro",
    "October": "outubro",
    "November": "novembro",
    "December": "dezembro",
    " folder and remove it from the list, the folder will no longer appear in the list, but will not be deleted.": " e removê-la da lista, ela deixará de aparecer, mas não será excluída do computador.",
    "Are you sure you want to delete the folder?": "Tem certeza de que deseja remover a pasta?",
    "Done": "Concluído",
    "If you delete the ": "Se você remover a pasta ",
    "Add folder": "Adicionar pasta",
    "Back": "Voltar",
    "Close Navigation": "Fechar navegação",
    "Open Navigation": "Abrir navegação",
    "Next Page": "Próxima página",
    "Previous Page": "Página anterior",
    "Pause": "Pausar",
    "Play": "Reproduzir",
    "Mute": "Silenciar",
    "Unmute": "Ativar som",
}


# These values are translated dynamically by the GUI and therefore do not
# appear as literal ``tr()`` arguments in the Python syntax tree.
TRANSLATIONS.update({
    "Auto": "Automático",
    "Close": "Desativado",
    "CPU": "CPU",
    "GPU": "GPU",
    "无妄者": "Insone",
    "无归的谬误": "Falácia Irreversível",
    "辉萤军势": "Miríade Lampilúmen",
    "鸣钟之龟": "Geobuti-sineiro",
    "燎照之骑": "Cavaleiro Infernal",
    "无常凶鹭": "Garça-cambiante",
    "聚械机偶": "Abominação Mecânica",
    "哀声鸷": "Aix Lamentoso",
    "朔雷之鳞": "Mefítico Tonitruante",
    "云闪之鳞": "Mefítico Tempestuoso",
    "飞廉之猩": "Beringal-feiliano",
    "无冠者": "Destronado",
    "角": "Jué",
    "异构武装": "Constructo de Sentinela",
    "赫卡忒": "Hécate",
    "罗蕾莱": "Lorelei",
    "叹息古龙": "Dragão Lamentoso",
    "梦魇飞廉之猩": "Pesadelo: Beringal-feiliano",
    "梦魇无常凶鹭": "Pesadelo: Garça-cambiante",
    "梦魇云闪之鳞": "Pesadelo: Mefítico Tempestuoso",
    "梦魇朔雷之鳞": "Pesadelo: Mefítico Tonitruante",
    "梦魇无冠者": "Pesadelo: Destronado",
    "梦魇燎照之骑": "Pesadelo: Cavaleiro Infernal",
    "梦魇哀声鸷": "Pesadelo: Aix Lamentoso",
    "梦魇辉萤军势": "Pesadelo: Miríade Lampilúmen",
    "芙露德莉斯": "Fleurdelys",
    "梦魇凯尔匹": "Pesadelo: Kelpie",
    "荣耀狮像": "Leoa da Glória",
    "梦魇赫卡忒": "Pesadelo: Hécate",
    "芬莱克": "Fenrico",
    "海之女": "Senhora do Mar",
    "伪作的神王": "Falso Soberano",
    "鸣式利维亚坦": "Leviatã trenodiano",
    "海维夏": "Hyvatia",
    "炉芯机骸": "Reator Deteriorado",
    "辛吉勒姆": "Sigillum",
    "无铭探索者": "Explorador Anônimo",
    "达妮娅": "Denia",
    "梦魇亚当·重锤": "Pesadelo: Adam Smasher",
    "万囮牢·朽躯（限时提前开放）": "Prisão de Miríades: Corpo Decadente (acesso antecipado por tempo limitado)",
    "万囮牢·朽躯": "Prisão de Miríades: Corpo Decadente",
    "失坠困咎之庭（限时提前开放）": "Corte das Almas Acorrentadas (acesso antecipado por tempo limitado)",
    "千傀重楼": "Pavilhão das Mil Marionetes",
})


DYNAMIC_BOSS_MESSAGES = (
        "无妄者", "无归的谬误", "辉萤军势", "鸣钟之龟", "燎照之骑", "无常凶鹭",
        "聚械机偶", "哀声鸷", "朔雷之鳞", "云闪之鳞", "飞廉之猩", "无冠者", "角",
        "异构武装", "赫卡忒", "罗蕾莱", "叹息古龙", "梦魇飞廉之猩", "梦魇无常凶鹭",
        "梦魇云闪之鳞", "梦魇朔雷之鳞", "梦魇无冠者", "梦魇燎照之骑", "梦魇哀声鸷",
        "梦魇辉萤军势", "芙露德莉斯", "梦魇凯尔匹", "荣耀狮像", "梦魇赫卡忒",
        "芬莱克", "海之女", "伪作的神王", "鸣式利维亚坦", "海维夏", "炉芯机骸",
        "辛吉勒姆", "无铭探索者", "达妮娅", "梦魇亚当·重锤",
        "万囮牢·朽躯（限时提前开放）", "万囮牢·朽躯", "失坠困咎之庭（限时提前开放）",
        "千傀重楼",
)


DYNAMIC_CONTEXT_MESSAGES = {
    "GamePathSettingCard": ("Auto",),
    "BossNameOptionsSettingCard": DYNAMIC_BOSS_MESSAGES,
    "BossRushWidget": DYNAMIC_BOSS_MESSAGES,
}


QFLUENT_MESSAGES = {
    "AMPMFormatter": ("AM", "PM"),
    "AMTimePicker": ("AM", "PM", "hour", "minute", "second"),
    "CalendarPicker": ("Pick a date",),
    "ColorDialog": ("Blue", "Cancel", "Edit Color", "Green", "OK", "Opacity", "Red"),
    "ColorPickerButton": ("Choose ",),
    "CustomColorSettingCard": ("Choose color", "Custom color", "Default color"),
    "DatePicker": ("day", "month", "year"),
    "DayScrollView": ("Fr", "Mo", "Sa", "Su", "Th", "Tu", "We"),
    "EditMenu": ("Cancel", "Copy", "Cut", "Paste", "Select all"),
    "FastDayScrollView": ("Fr", "Mo", "Sa", "Su", "Th", "Tu", "We"),
    "FastMonthScrollView": ("Apr", "Aug", "Dec", "Feb", "Jan", "Jul", "Jun", "Mar", "May", "Nov", "Oct", "Sep"),
    "FolderListDialog": (" folder and remove it from the list, the folder will no longer appear in the list, but will not be deleted.", "Are you sure you want to delete the folder?", "Choose folder", "Done", "If you delete the "),
    "FolderListSettingCard": (" folder and remove it from the list, the folder will no longer appear in the list, but will not be deleted.", "Add folder", "Are you sure you want to delete the folder?", "Choose folder", "If you delete the "),
    "LabelContextMenu": ("Copy", "Select all"),
    "MessageBoxBase": ("Cancel", "OK"),
    "MessageDialog": ("Cancel", "OK"),
    "MonthFormatter": ("April", "August", "December", "February", "January", "July", "June", "March", "May", "November", "October", "September"),
    "MonthScrollView": ("Apr", "Aug", "Dec", "Feb", "Jan", "Jul", "Jun", "Mar", "May", "Nov", "Oct", "Sep"),
    "NavigationPanel": ("Back", "Close Navigation", "Open Navigation"),
    "PipsPager": ("Next Page", "Previous Page"),
    "PlayButton": ("Pause", "Play"),
    "SwitchButton": ("Off", "On"),
    "SwitchSettingCard": ("Off", "On"),
    "TimePicker": ("hour", "minute", "second"),
    "Ui_MessageBox": ("Cancel", "OK"),
    "VolumeView": ("Mute", "Unmute"),
}


def literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = literal_string(node.left), literal_string(node.right)
        return left + right if left is not None and right is not None else None
    if isinstance(node, ast.JoinedStr):
        values = [literal_string(value) for value in node.values]
        return "".join(values) if all(value is not None for value in values) else None
    return None


def current_gui_messages() -> dict[tuple[str, str], list[tuple[str, int]]]:
    messages: dict[tuple[str, str], list[tuple[str, int]]] = defaultdict(list)

    class Visitor(ast.NodeVisitor):
        def __init__(self, path: Path):
            self.path = path
            self.classes: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.classes.append(node.name)
            self.generic_visit(node)
            self.classes.pop()

        def visit_Call(self, node: ast.Call) -> None:
            if not isinstance(node.func, ast.Attribute):
                self.generic_visit(node)
                return

            source = None
            context = self.classes[-1] if self.classes else self.path.stem
            if node.func.attr == "tr" and node.args:
                source = literal_string(node.args[0])
            elif node.func.attr == "translate" and len(node.args) >= 2:
                source = literal_string(node.args[1])
                context = literal_string(node.args[0]) or context

            if source is not None:
                relative = os.path.relpath(self.path, I18N_ROOT).replace("\\", "/")
                messages[(context, source)].append((relative, node.lineno))
            self.generic_visit(node)

    for path in sorted(GUI_ROOT.rglob("*.py")):
        if path.name == "resource.py":
            continue
        Visitor(path).visit(ast.parse(path.read_text(encoding="utf-8"), filename=str(path)))

    return messages


def translation_for(source: str) -> str:
    if source in KEEP_SOURCE:
        return source
    try:
        return TRANSLATIONS[source]
    except KeyError as error:
        raise KeyError(f"Missing reviewed pt-BR translation for {source!r}") from error


def build_catalog() -> str:
    root = copy.deepcopy(ET.parse(BASE_CATALOG).getroot())
    root.set("language", "pt_BR")
    root.set("sourcelanguage", "en_US")

    contexts: dict[str, ET.Element] = {}
    messages: dict[tuple[str, str], ET.Element] = {}
    for context in root.findall("context"):
        name = context.findtext("name") or ""
        contexts[name] = context
        for message in context.findall("message"):
            source = message.findtext("source") or ""
            messages[(name, source)] = message

    extracted = current_gui_messages()
    for (context_name, source), locations in extracted.items():
        context = contexts.get(context_name)
        if context is None:
            context = ET.SubElement(root, "context")
            ET.SubElement(context, "name").text = context_name
            contexts[context_name] = context
        message = messages.get((context_name, source))
        if message is None:
            message = ET.SubElement(context, "message")
            ET.SubElement(message, "source").text = source
            ET.SubElement(message, "translation")
            messages[(context_name, source)] = message
        existing_locations = {
            (location.get("filename"), location.get("line"))
            for location in message.findall("location")
        }
        for filename, line in locations:
            if (filename, str(line)) not in existing_locations:
                location = ET.Element("location", filename=filename, line=str(line))
                message.insert(0, location)

    for context_name, sources in (QFLUENT_MESSAGES | DYNAMIC_CONTEXT_MESSAGES).items():
        context = contexts.get(context_name)
        if context is None:
            context = ET.SubElement(root, "context")
            ET.SubElement(context, "name").text = context_name
            contexts[context_name] = context
        for source in sources:
            if (context_name, source) in messages:
                continue
            message = ET.SubElement(context, "message")
            ET.SubElement(message, "source").text = source
            ET.SubElement(message, "translation")
            messages[(context_name, source)] = message

    for (_context, source), message in messages.items():
        translation = message.find("translation")
        if translation is None:
            translation = ET.SubElement(message, "translation")
        translation.attrib.clear()
        translation.text = translation_for(source)

    ET.indent(root, space="    ")
    body = ET.tostring(root, encoding="unicode", short_empty_elements=False)
    return f'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>\n{body}\n'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the committed catalog is stale")
    args = parser.parse_args()

    catalog = build_catalog()
    if args.check:
        if not OUTPUT_CATALOG.exists() or OUTPUT_CATALOG.read_text(encoding="utf-8") != catalog:
            print(f"{OUTPUT_CATALOG.relative_to(ROOT)} is stale; rebuild it with {Path(__file__).name}")
            return 1
        return 0

    OUTPUT_CATALOG.write_text(catalog, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT_CATALOG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
