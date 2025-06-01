# Simulador de Máquina de Turing com Interface Gráfica

Este é um simulador de Máquina de Turing desenvolvido em Python utilizando a biblioteca PyQt5 para a interface gráfica. O programa permite carregar regras, definir conteúdo inicial na fita, executar operações passo a passo ou até a parada total, e visualizar o estado atual da fita e do cabeçote.

---

## 🛠️ Análise do Código

### Classes Principais:
1. **`TapeWidget`**:
   - Representa a fita da Máquina de Turing em uma interface gráfica.
   - Exibe células com valores e destaca a posição atual do cabeçote (indicado por uma seta vermelha).
   - Atualiza dinamicamente os valores da fita conforme a simulação avança.

2. **`TuringMachine`**:
   - Lógica da Máquina de Turing.
   - Gerencia estados, regras, movimentos do cabeçote e conteúdo da fita.
   - Suporta execução contínua (`run_until_halt`) ou passo a passo (`step`).

3. **`TuringMachineGUI`**:
   - Interface gráfica principal.
   - Inclui campos para inserir conteúdo inicial da fita, regras, botões de controle (Executar, Passo, Reiniciar) e opções para carregar/salvar regras em arquivo.

### Funcionalidades:
- Visualização da fita com células dinâmicas.
- Carregamento e salvamento de regras em arquivo (extensão `.tm`).
- Feedback visual do status (Pronto, Executando, Parado).
- Mensagens de resultado ao final da execução.

---

## 📥 Instalação das Dependências

### Pré-requisitos:
- Python 3.x instalado ([Download Python](https://www.python.org/downloads/)).
- Gerenciador de pacotes `pip` (já incluso em instalações recentes do Python).

### Instale o PyQt5:
```bash
pip install PyQt5