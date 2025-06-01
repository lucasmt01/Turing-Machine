# 🧠 Simulador de Máquina de Turing com Interface Gráfica

Este é um simulador completo de Máquina de Turing desenvolvido em Python com PyQt5. O programa permite definir todas as componentes de uma máquina de Turing `M = (K, Γ, δ, s, H)`, simular computações para uma entrada `w`, e visualizar o histórico completo da execução desde a configuração inicial `(s, ⊳⊔ w)` até a configuração de parada.

---

## ✨ Novos Recursos e Melhorias

### Definição Completa da Máquina de Turing
- **K (Estados)**: Campo dedicado para lista de estados
- **Γ (Alfabeto da Fita)**: Definição dos símbolos permitidos na fita
- **δ (Regras de Transição)**: Suporte completo a regras determinísticas e não-determinísticas
- **s (Estado Inicial)**: Seleção do estado inicial
- **H (Estados de Parada)**: Definição de estados de aceitação/rejeição
- **Símbolo Branco (□)**: Personalização do símbolo de espaço vazio

### Fluxo de Trabalho Aprimorado
1. Configuração completa da máquina (K, Γ, s, □)
2. Definição das regras de transição (δ)
3. Especificação dos estados de parada (H)
4. Entrada do conteúdo inicial da fita (w)
5. Execução passo-a-passo ou contínua
6. Visualização do resultado e histórico completo

### Recursos de Visualização
- **Fita Virtual**: 
  - 31 células visíveis centradas na posição atual
  - Destaque na célula sendo lida
  - Símbolos especiais ⊳ (início) e ⊔ (espaço)
- **Histórico Detalhado**:
  - Todas as configurações desde o início
  - Transições aplicadas em cada passo
  - Botão para mostrar/esconder histórico
- **Status em Tempo Real**:
  - Estado atual
  - Status da máquina (Pronto, Executando, Aceita, Rejeita)
  - Posição do cabeçote

### Funcionalidades Avançadas
- **Validação de Entrada**:
  - Verificação de símbolos contra Γ
  - Alertas para estados/símbolos não definidos
- **Persistência**:
  - Salvar/carregar configuração completa (.tmc)
  - Formato JSON com todos os parâmetros
- **Controle de Execução**:
  - Limite configurável de passos
  - Confirmação para continuar após limite
  - Reinício completo da simulação
- **Tratamento de Resultados**:
  - Aceita (Y) e Rejeita (N) explícitos
  - Detecção de paradas não planejadas
  - Exibição de fita final e estado

---

## 📥 Instalação das Dependências

### Pré-requisitos:
- Python 3.x instalado ([Download Python](https://www.python.org/downloads/)).
- Gerenciador de pacotes `pip` (já incluso em instalações recentes do Python).

### Instale o PyQt5:
```bash
pip install PyQt5
