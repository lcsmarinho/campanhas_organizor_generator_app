# Gerenciador de Campanhas D&D

Este aplicativo é uma ferramenta completa para mestres de jogo que desejam criar, editar e gerenciar campanhas de Dungeons & Dragons. Com uma interface intuitiva construída em Python (Tkinter), o app permite organizar campanhas seguindo uma formatação pré-definida, importar nomes de monstros e itens (a partir dos arquivos `monstros.json` e `itens.json`), e manter um histórico de campanhas criadas.

## Funcionalidades

- **Carregamento Automático de Dados:**
  - **Histórico de Campanhas:** Ao iniciar, o app procura pelo arquivo `campanhas_historico.json` e carrega as campanhas salvas. Caso o arquivo não exista, uma estrutura vazia é iniciada.
  - **Monstros e Itens:** Os dados dos arquivos `monstros.json` e `itens.json` são carregados automaticamente, possibilitando a visualização e importação dos registros para suas campanhas.

- **Formulário para Criação e Edição de Campanhas:**
  - Preencha os campos da campanha (como `id`, `titulo`, `imagem`, `dificuldade`, `grupoMinimo`, `localidade`, `corpo`, `monstros`, `chefões`, `recompensas` e `npcs`).
  - Utilize as checkboxes "Não tem" para preencher automaticamente com valores padrão (`0` para campos numéricos e `nenhum` para os demais).

- **Interface Multi-Aba (Notebook):**
  - **Campanhas do Arquivo:** Exibe as campanhas presentes em um arquivo selecionado (via botão de seleção).
  - **Campanhas Adicionadas:** Mostra as campanhas criadas na sessão atual.
  - **Histórico de Campanhas:** Lista as campanhas salvas no histórico (do arquivo `campanhas_historico.json`).
  - **Monstros:** Apresenta os registros de monstros carregados. Dê duplo clique para visualizar detalhes em um pop-up e importe os nomes para o campo "monstros" da campanha.
  - **Itens:** Exibe os registros de itens carregados. Assim como os monstros, você pode visualizar detalhes e importar os nomes para o campo "recompensas".

- **Importação Seletiva:**
  - Importe individualmente ou todos os nomes de monstros e itens para a campanha, facilitando a montagem rápida do cenário de jogo.

- **Geração de Novo Arquivo de Campanhas:**
  - Ao confirmar, o app gera um novo arquivo chamado `campanhas_novo.json` que reúne as campanhas do arquivo original com as alterações e adições feitas, mantendo o arquivo original intacto.

- **Salvamento do Histórico:**
  - Ao fechar o aplicativo, as campanhas criadas ou editadas são mescladas ao histórico e salvas no arquivo `campanhas_historico.json`.

## Requisitos

- **Python 3.x**
- **Tkinter** (normalmente incluído com o Python)
- Arquivos JSON para:
  - Campanhas (ex.: `campanhas.json`)
  - Monstros (ex.: `monstros.json`)
  - Itens (ex.: `itens.json`)
  - Histórico de Campanhas (`campanhas_historico.json` - será criado automaticamente se não existir)

## Como Usar

1. **Inicie o Aplicativo:**
   Execute o script principal:
   ```bash
   python main.py
