import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor


class TapeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cells = []
        self.head_pos = 0
        self.visible_cells = 31
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.init_tape()

    def init_tape(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        self.cells = []
        for _ in range(self.visible_cells):
            cell = QLabel("_")
            cell.setAlignment(Qt.AlignCenter)
            cell.setFixedSize(40, 40)
            cell.setStyleSheet("""
                QLabel {
                    border: 1px solid #444;
                    background-color: #2d2d2d;
                    color: #fff;
                    font-weight: bold;
                    font-size: 16px;
                }
            """)
            self.cells.append(cell)

        self.head_indicator = QLabel("↓")
        self.head_indicator.setAlignment(Qt.AlignCenter)
        self.head_indicator.setFixedSize(40, 20)
        self.head_indicator.setStyleSheet("color: #ff5555; font-size: 16px;")

        head_row = QWidget()
        head_row_layout = QHBoxLayout()
        head_row_layout.setContentsMargins(0, 0, 0, 0)
        head_row_layout.setSpacing(0)
        for i in range(self.visible_cells):
            if i == self.visible_cells // 2:
                head_row_layout.addWidget(self.head_indicator)
            else:
                spacer = QLabel("")
                spacer.setFixedSize(40, 20)
                head_row_layout.addWidget(spacer)
        head_row.setLayout(head_row_layout)

        tape_row = QWidget()
        tape_row_layout = QHBoxLayout()
        tape_row_layout.setContentsMargins(0, 0, 0, 0)
        tape_row_layout.setSpacing(0)
        for cell in self.cells:
            tape_row_layout.addWidget(cell)
        tape_row.setLayout(tape_row_layout)

        self.layout.addWidget(head_row)
        self.layout.addWidget(tape_row)

    def update_tape(self, tape_data, head_pos, blank_symbol):
        center_pos = self.visible_cells // 2
        start_pos = head_pos - center_pos
        for i in range(self.visible_cells):
            pos = start_pos + i
            if pos in tape_data:
                self.cells[i].setText(tape_data[pos])
            else:
                self.cells[i].setText(blank_symbol)

        for i, cell in enumerate(self.cells):
            if i == center_pos:
                cell.setStyleSheet("""
                    QLabel {
                        border: 2px solid #ff5555;
                        background-color: #3d3d3d;
                        color: #fff;
                        font-weight: bold;
                        font-size: 16px;
                    }
                """)
            else:
                cell.setStyleSheet("""
                    QLabel {
                        border: 1px solid #444;
                        background-color: #2d2d2d;
                        color: #fff;
                        font-weight: bold;
                        font-size: 16px;
                    }
                """)


class TuringMachine:
    def __init__(self):
        self.tape = {}
        self.head_pos = 0
        self.rules = {}
        self.state = "q0"
        self.halting_states = set()
        self.halted = False
        self.history = []
        self.step_limit = 1000
        self.result = None  # Aceita, Rejeita ou None
        self.transition_history = []  # Histórico detalhado das transições
        self.states = set()
        self.tape_alphabet = set()
        self.initial_state = "q0"
        self.blank_symbol = "_"

    def reset(self):
        self.tape = {}
        self.head_pos = 0
        self.state = self.initial_state
        self.halted = False
        self.history = []
        self.result = None
        self.transition_history = []

    def load_machine_definition(self, states, tape_alphabet, initial_state, blank_symbol):
        self.states = set(states.split())
        self.tape_alphabet = set(tape_alphabet.split(','))
        self.initial_state = initial_state
        self.blank_symbol = blank_symbol
        
        # Adicionar símbolos especiais obrigatórios
        self.tape_alphabet.update(['⊳', '_', self.blank_symbol])
        
    def load_rules(self, rules_text, halting_states_str):
        self.rules = {}
        self.halting_states = set(halting_states_str.split())
        for line in rules_text.split('\n'):
            linha = line.strip()
            if not linha or linha.startswith('#'):
                continue
            parts = linha.split()
            if len(parts) != 5:
                continue
            e_from, sym_read, sym_write, move, e_to = parts
            move = move.upper()
            key = (e_from, sym_read)
            if key not in self.rules:
                self.rules[key] = []
            self.rules[key].append((sym_write, move, e_to))

    def step(self):
        if self.state in self.halting_states:
            self.halted = True
            return False

        current_symbol = self.tape.get(self.head_pos, self.blank_symbol)
        chave = (self.state, current_symbol)
        
        if chave not in self.rules:
            self.halted = True
            return False

        transitions = self.rules[chave]
        if len(transitions) > 1:
            # Não determinismo - usamos a primeira transição
            pass
        
        sym_write, move, next_state = transitions[0]

        # Salva histórico antes da transição
        min_pos = min(self.tape.keys()) if self.tape else 0
        max_pos = max(self.tape.keys()) if self.tape else 0
        fita_str = "".join(self.tape.get(i, self.blank_symbol) for i in range(min_pos, max_pos + 1))
        self.history.append((self.state, fita_str, self.head_pos))
        
        # Salva detalhes da transição para histórico
        trans_info = f"δ({self.state}, {current_symbol}) = {next_state}, {sym_write}, {move}"
        self.transition_history.append(trans_info)

        # Aplica a transição
        if sym_write != self.blank_symbol:
            self.tape[self.head_pos] = sym_write
        else:
            self.tape.pop(self.head_pos, None)

        # Trata os movimentos especiais
        if move == "Y":
            self.halted = True
            self.result = "Aceita"
        elif move == "N":
            self.halted = True
            self.result = "Rejeita"
        else:  # R ou L
            if move == "R":
                self.head_pos += 1
            elif move == "L":
                self.head_pos -= 1
            self.state = next_state

            if self.state in self.halting_states:
                self.halted = True

        return True

    def get_tape_content(self):
        if not self.tape:
            return ""
        min_pos = min(self.tape.keys())
        max_pos = max(self.tape.keys())
        return "".join(self.tape.get(i, self.blank_symbol) for i in range(min_pos, max_pos + 1))

    def load_content(self, input_str):
        self.tape = {}
        self.tape[0] = "⊳"
        self.tape[1] = "_"  # Símbolo de espaço
        
        start_idx = 2  # Posição após ⊳⊔
        for i, char in enumerate(input_str):
            pos = start_idx + i
            if char != self.blank_symbol:
                self.tape[pos] = char
                
        self.head_pos = 1  # Começa no ⊔ (posição 1)
        self.state = self.initial_state
        self.halted = False
        self.history = []
        self.result = None
        self.transition_history = []


class TuringMachineGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tm = TuringMachine()
        self.setup_done = False
        self.history_visible = True
        self.init_ui()
        self.setWindowTitle("Turing Machine Simulator")
        self.resize(1200, 650)

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel, 2)

        self.setStyleSheet("""
            QMainWindow { background-color: #252525; }
            QWidget { background-color: #252525; color: #fff; }
            QTextEdit, QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #444;
                color: #fff;
                padding: 5px;
                font-family: monospace;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #444;
                color: #fff;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #4d4d4d; }
            QPushButton:pressed { background-color: #2d2d2d; }
            QLabel { color: #fff; }
            QTextEdit#historyBox {
                background-color: #1e1e1e; 
                color: #dcdcdc; 
                font-family: monospace;
                border: 1px solid #444;
            }
        """)

        self.tape_widget = TapeWidget()
        self.tape_scroll = QScrollArea()
        self.tape_scroll.setFrameStyle(QFrame.NoFrame)
        self.tape_scroll.setWidgetResizable(True)
        self.tape_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tape_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tape_scroll.setWidget(self.tape_widget)
        left_layout.addWidget(self.tape_scroll)

        info_layout = QHBoxLayout()
        self.state_label = QLabel("Estado: q0")
        self.state_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.state_label)
        info_layout.addStretch()
        info_layout.addWidget(self.status_label)
        left_layout.addLayout(info_layout)

        control_layout = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_machine)
        self.step_button = QPushButton("Step")
        self.step_button.clicked.connect(self.step_machine)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_machine)
        self.toggle_hist_button = QPushButton("Mostrar/Esconder Histórico")
        self.toggle_hist_button.clicked.connect(self.toggle_history)
        control_layout.addWidget(self.run_button)
        control_layout.addWidget(self.step_button)
        control_layout.addWidget(self.reset_button)
        control_layout.addWidget(self.toggle_hist_button)
        left_layout.addLayout(control_layout)

        # Novo grupo para definição da máquina
        machine_group = QWidget()
        machine_layout = QVBoxLayout()
        machine_group.setLayout(machine_layout)
        
        # Campo para estados (K)
        states_layout = QHBoxLayout()
        self.states_field = QLineEdit()
        self.states_field.setPlaceholderText("Ex: q0 q1 q2 q3 q4")
        states_layout.addWidget(QLabel("Estados (K):"))
        states_layout.addWidget(self.states_field)
        machine_layout.addLayout(states_layout)
        
        # Campo para alfabeto da fita (Γ)
        tape_alphabet_layout = QHBoxLayout()
        self.tape_alphabet_field = QLineEdit()
        self.tape_alphabet_field.setPlaceholderText("Ex: a,b,c,_,⊳,⊔")
        tape_alphabet_layout.addWidget(QLabel("Alfabeto da Fita (Γ):"))
        tape_alphabet_layout.addWidget(self.tape_alphabet_field)
        machine_layout.addLayout(tape_alphabet_layout)
        
        # Campo para estado inicial (s)
        initial_state_layout = QHBoxLayout()
        self.initial_state_field = QLineEdit("q0")
        initial_state_layout.addWidget(QLabel("Estado Inicial (s):"))
        initial_state_layout.addWidget(self.initial_state_field)
        machine_layout.addLayout(initial_state_layout)
        
        # Campo para símbolo branco (□)
        blank_symbol_layout = QHBoxLayout()
        self.blank_symbol_field = QLineEdit("_")
        blank_symbol_layout.addWidget(QLabel("Símbolo Branco (□):"))
        blank_symbol_layout.addWidget(self.blank_symbol_field)
        machine_layout.addLayout(blank_symbol_layout)
        
        left_layout.addWidget(machine_group)

        config_group = QWidget()
        config_layout = QVBoxLayout()
        config_group.setLayout(config_layout)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Insira o conteúdo inicial da fita (w)")
        input_layout.addWidget(QLabel("Conteúdo Inicial:"))
        input_layout.addWidget(self.input_field)
        config_layout.addLayout(input_layout)

        halting_layout = QHBoxLayout()
        self.halting_field = QLineEdit()
        self.halting_field.setPlaceholderText("Ex: qH qf")
        halting_layout.addWidget(QLabel("Halting States:"))
        halting_layout.addWidget(self.halting_field)
        config_layout.addLayout(halting_layout)

        step_limit_layout = QHBoxLayout()
        self.step_limit_field = QLineEdit()
        self.step_limit_field.setPlaceholderText("Ex: 1000")
        step_limit_layout.addWidget(QLabel("Limite de etapas (válido apenas para 'Run'):"))
        step_limit_layout.addWidget(self.step_limit_field)
        config_layout.addLayout(step_limit_layout)

        rules_layout = QVBoxLayout()
        rules_layout.addWidget(QLabel("Regras: <estado> <read> <write> <move> <next>"))
        self.rules_edit = QTextEdit()
        self.rules_edit.setPlaceholderText(
            "Digite regras, uma por linha, no formato:\n"
            "q0 a x R q1\n"
            "q0 a x Y qH   # Aceita\n"
            "q0 b _ N qR   # Rejeita"
        )
        rules_layout.addWidget(self.rules_edit)
        config_layout.addLayout(rules_layout)

        # Botões para salvar/carregar configuração completa
        file_layout = QHBoxLayout()
        self.load_config_button = QPushButton("Load Config")
        self.load_config_button.clicked.connect(self.load_config_file)
        self.save_config_button = QPushButton("Save Config")
        self.save_config_button.clicked.connect(self.save_config_file)
        file_layout.addWidget(self.load_config_button)
        file_layout.addWidget(self.save_config_button)
        config_layout.addLayout(file_layout)

        left_layout.addWidget(config_group)

        self.history_box = QTextEdit()
        self.history_box.setObjectName("historyBox")  # Para aplicar o estilo CSS
        self.history_box.setReadOnly(True)
        self.history_box.setStyleSheet("""
            background-color: #1e1e1e; 
            color: #dcdcdc; 
            font-family: monospace;
            border: 1px solid #444;
        """)
        main_layout.addWidget(self.history_box, 1)

        self.update_display()

    def update_display(self):
        self.tape_widget.update_tape(self.tm.tape, self.tm.head_pos, self.tm.blank_symbol)
        self.state_label.setText(f"Estado: {self.tm.state}")

        if self.tm.halted:
            if self.tm.result:
                self.status_label.setText(f"Status: {self.tm.result}")
            else:
                self.status_label.setText("Status: Rejected")
        else:
            if not self.tm.tape and not self.setup_done:
                self.status_label.setText("Status: Ready")
            else:
                self.status_label.setText("Status: Running")

        cell_width = 40
        center_index = self.tape_widget.visible_cells // 2
        center_pixel = center_index * cell_width
        half_view = self.tape_scroll.viewport().width() // 2
        target = center_pixel - half_view + (cell_width // 2)
        if target < 0:
            target = 0
        max_scroll = self.tape_scroll.horizontalScrollBar().maximum()
        if target > max_scroll:
            target = max_scroll
        self.tape_scroll.horizontalScrollBar().setValue(target)

    def toggle_history(self):
        self.history_visible = not self.history_visible
        self.history_box.setVisible(self.history_visible)

    def confirm_continue(self, X):
        reply = QMessageBox.question(
            self,
            "Máquina em execução",
            f"A máquina não parou após {X} transições.\nDeseja continuar por mais {X}?",
            QMessageBox.Yes | QMessageBox.No
        )
        return (reply == QMessageBox.Yes)

    def validate_input(self, input_str):
        # Obter alfabeto da fita do campo Γ
        gamma = self.tape_alphabet_field.text().split(',')
        valid_symbols = set(gamma)
        
        # Adicionar símbolos especiais obrigatórios
        valid_symbols.update(['⊳', '_', self.blank_symbol_field.text()])
        
        # Validar entrada
        invalids = set()
        for ch in input_str:
            if ch not in valid_symbols:
                invalids.add(ch)

        if invalids:
            return False, invalids
        return True, None

    def validate_machine_definition(self):
        """Realiza validações avançadas na definição da máquina"""
        errors = []
        warnings = []

        # 1. Verificar se o estado inicial está definido
        initial_state = self.initial_state_field.text().strip()
        if not initial_state:
            errors.append("Estado inicial não definido")
        
        # 2. Verificar se o estado inicial está na lista de estados
        states = set(self.states_field.text().split())
        if initial_state and initial_state not in states:
            errors.append(f"Estado inicial '{initial_state}' não está na lista de estados definidos")
        
        # 3. Verificar estados de parada
        halting_states = set(self.halting_field.text().split())
        undefined_halting = halting_states - states
        if undefined_halting:
            errors.append(f"Estados de parada não definidos: {', '.join(undefined_halting)}")
        
        # 4. Verificar alfabeto da fita
        gamma = set(self.tape_alphabet_field.text().split(','))
        if not gamma:
            warnings.append("Alfabeto da fita está vazio")

        # 5. Verificar regras
        rules_text = self.rules_edit.toPlainText().strip()
        if rules_text:
            # Verificar estados usados nas regras
            used_states = set()
            undefined_states = set()
            undefined_symbols = set()
            
            for line in rules_text.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) != 5:
                    continue
                
                e_from, sym_read, sym_write, move, e_to = parts
                used_states.add(e_from)
                used_states.add(e_to)
                
                # Verificar se símbolos pertencem ao alfabeto
                if sym_read != '_' and sym_read not in gamma:
                    undefined_symbols.add(sym_read)
                if sym_write != '_' and sym_write not in gamma:
                    undefined_symbols.add(sym_write)
            
            # Estados usados mas não definidos
            undefined_states = used_states - states
            if undefined_states:
                errors.append(f"Estados usados nas regras mas não definidos: {', '.join(undefined_states)}")
            
            # Símbolos não pertencentes ao alfabeto
            if undefined_symbols:
                errors.append(f"Símbolos usados nas regras não pertencem ao alfabeto Γ: {', '.join(undefined_symbols)}")
        
        return errors, warnings

    def load_rules(self):
        # Carregar definição da máquina
        states = self.states_field.text().strip()
        tape_alphabet = self.tape_alphabet_field.text().strip()
        initial_state = self.initial_state_field.text().strip()
        blank_symbol = self.blank_symbol_field.text().strip()
        
        if not states or not tape_alphabet or not initial_state or not blank_symbol:
            QMessageBox.warning(self, "Warning", "Definição incompleta da máquina.")
            return False
            
        # Validar definição antes de carregar
        errors, warnings = self.validate_machine_definition()
        
        if warnings:
            QMessageBox.warning(self, "Avisos", "\n".join(warnings))
            
        if errors:
            QMessageBox.critical(self, "Erros de Validação", "\n".join(errors))
            return False
            
        self.tm.load_machine_definition(states, tape_alphabet, initial_state, blank_symbol)
        
        # Carregar regras de transição
        rules_text = self.rules_edit.toPlainText().strip()
        if not rules_text:
            QMessageBox.warning(self, "Warning", "Nenhuma regra foi carregada.")
            return False

        halting_text = self.halting_field.text().strip()
        step_text = self.step_limit_field.text().strip()
        
        try:
            self.tm.step_limit = int(step_text)
        except:
            self.tm.step_limit = 1000

        self.tm.load_rules(rules_text, halting_text)
        return True

    def save_config_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Salvar Configuração Completa", "", "Turing Machine Config (*.tmc);;All Files (*)"
        )
        if file_name:
            try:
                # Coletar todas as configurações
                config = {
                    "states": self.states_field.text().strip(),
                    "tape_alphabet": self.tape_alphabet_field.text().strip(),
                    "initial_state": self.initial_state_field.text().strip(),
                    "blank_symbol": self.blank_symbol_field.text().strip(),
                    "halting_states": self.halting_field.text().strip(),
                    "step_limit": self.step_limit_field.text().strip(),
                    "rules": self.rules_edit.toPlainText().strip(),
                    "input": self.input_field.text().strip()
                }
                
                with open(file_name, 'w') as f:
                    json.dump(config, f, indent=4)
                    
                QMessageBox.information(self, "Success", "Configuração completa salva com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Falha ao salvar configuração: {str(e)}")

    def load_config_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Carregar Configuração Completa", "", "Turing Machine Config (*.tmc);;All Files (*)"
        )
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    config = json.load(f)
                
                # Preencher todos os campos com a configuração carregada
                self.states_field.setText(config.get("states", ""))
                self.tape_alphabet_field.setText(config.get("tape_alphabet", ""))
                self.initial_state_field.setText(config.get("initial_state", "q0"))
                self.blank_symbol_field.setText(config.get("blank_symbol", "_"))
                self.halting_field.setText(config.get("halting_states", ""))
                self.step_limit_field.setText(config.get("step_limit", "1000"))
                self.rules_edit.setPlainText(config.get("rules", ""))
                self.input_field.setText(config.get("input", ""))
                
                QMessageBox.information(self, "Success", "Configuração completa carregada com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Falha ao carregar configuração: {str(e)}")

    def append_to_history(self, estado, fita_str, head_pos, trans_info=None, is_setup=False):
        # Formata a fita destacando a célula atual
        formatted_tape = ""
        for i, char in enumerate(fita_str):
            if i == head_pos:
                formatted_tape += f"[<b style='color: #ff5555'>{char}</b>]"
            else:
                formatted_tape += char
                
        # Adiciona detalhes da transição se disponível
        trans_details = f"<br><i style='color: #888'>{trans_info}</i>" if trans_info else ""
        
        if is_setup:
            # Passo de setup
            linha = (f"<b>Setup</b>: Estado = <b style='color: #55ff55'>{estado}</b>, "
                     f"Fita = {formatted_tape}{trans_details}")
        else:
            # Passo normal
            passo = len(self.tm.transition_history)
            linha = (f"<b>Passo {passo}</b>: Estado = <b style='color: #55ff55'>{estado}</b>, "
                     f"Fita = {formatted_tape}{trans_details}")
            
        self.history_box.append(linha)
        self.history_box.verticalScrollBar().setValue(self.history_box.verticalScrollBar().maximum())

    def run_machine(self):
        self.history_box.clear()
        self.setup_done = False

        if not self.load_rules():
            return

        w = self.input_field.text().strip()
        valid, invalids = self.validate_input(w)
        if not valid:
            symbols_str = ", ".join(sorted(invalids))
            QMessageBox.warning(self, "Símbolos inválidos",
                                f"Os símbolos '{symbols_str}' não fazem parte do alfabeto Γ definido.")
            return

        if w:
            self.tm.load_content(w)
        else:
            # Tratar entrada vazia como configuração (⊳⊔)
            self.tm.load_content("")
            
        estado0 = self.tm.state
        fita0 = self.tm.get_tape_content()
        head0 = self.tm.head_pos
        self.tm.history.append((estado0, fita0, head0))
        # Registro especial para o setup
        self.append_to_history(estado0, fita0, head0, "Configuração inicial", True)
        self.update_display()

        passos = 0
        while not self.tm.halted:
            if passos >= self.tm.step_limit:
                resp = self.confirm_continue(self.tm.step_limit)
                if not resp:
                    break
                passos = 0
            executou = self.tm.step()
            if not executou:
                break
            estado_atual, fita_atual, head_atual = self.tm.history[-1]
            trans_info = self.tm.transition_history[-1] if self.tm.transition_history else None
            self.append_to_history(estado_atual, fita_atual, head_atual, trans_info)
            self.update_display()
            passos += 1

        # Verificar se a máquina parou em estado não definido como de parada
        if self.tm.halted and not self.tm.result and self.tm.state not in self.tm.halting_states:
            self.tm.result = "Rejeita (sem transição)"
            QMessageBox.warning(self, "Parada não planejada", 
                                f"A máquina parou no estado '{self.tm.state}' que não é um estado de parada definido.")

        # Adiciona configuração final ao histórico
        estado_final = self.tm.state
        fita_final = self.tm.get_tape_content()
        head_final = self.tm.head_pos
        self.append_to_history(estado_final, fita_final, head_final, "Configuração final")

        # Exibe resultado com tipo de parada
        resultado = self.tm.result if self.tm.result else "Rejected"
        QMessageBox.information(
            self,
            "Resultado",
            f"<b>Resultado</b>: <span style='color: #ff5555'>{resultado}</span><br>"
            f"<b>Estado final</b>: {self.tm.state}<br>"
            f"<b>Fita final</b>: {fita_final}"
        )

    def step_machine(self):
        if not self.load_rules():
            return

        if self.tm.halted:
            resultado = self.tm.result if self.tm.result else "Rejected"
            QMessageBox.information(
                self,
                "Resultado",
                f"<b>Resultado</b>: <span style='color: #ff5555'>{resultado}</span><br>"
                f"<b>Estado final</b>: {self.tm.state}<br>"
                f"<b>Fita final</b>: {self.tm.get_tape_content()}"
            )
            return

        if not self.setup_done:
            w = self.input_field.text().strip()
            valid, invalids = self.validate_input(w)
            if not valid:
                symbols_str = ", ".join(sorted(invalids))
                QMessageBox.warning(self, "Símbolos inválidos",
                                    f"Os símbolos '{symbols_str}' não fazem parte do alfabeto Γ definido.")
                return
            if w:
                self.tm.load_content(w)
            else:
                # Tratar entrada vazia como configuração (⊳⊔)
                self.tm.load_content("")
                
            estado0 = self.tm.state
            fita0 = self.tm.get_tape_content()
            head0 = self.tm.head_pos
            self.tm.history.append((estado0, fita0, head0))
            self.append_to_history(estado0, fita0, head0, "Configuração inicial", True)
            self.update_display()
            self.setup_done = True
            return

        executou = self.tm.step()
        self.update_display()
        estado_atual, fita_atual, head_atual = self.tm.history[-1]
        trans_info = self.tm.transition_history[-1] if self.tm.transition_history else None
        self.append_to_history(estado_atual, fita_atual, head_atual, trans_info)

        if self.tm.halted:
            # Verificar se a máquina parou em estado não definido como de parada
            if not self.tm.result and self.tm.state not in self.tm.halting_states:
                self.tm.result = "Rejeita (sem transição)"
                QMessageBox.warning(self, "Parada não planejada", 
                                    f"A máquina parou no estado '{self.tm.state}' que não é um estado de parada definido.")
            
            # Adiciona configuração final ao histórico
            estado_final = self.tm.state
            fita_final = self.tm.get_tape_content()
            head_final = self.tm.head_pos
            self.append_to_history(estado_final, fita_final, head_final, "Configuração final")
            
            resultado = self.tm.result if self.tm.result else "Rejected"
            QMessageBox.information(
                self,
                "Resultado",
                f"<b>Resultado</b>: <span style='color: #ff5555'>{resultado}</span><br>"
                f"<b>Estado final</b>: {self.tm.state}<br>"
                f"<b>Fita final</b>: {fita_final}"
            )

    def reset_machine(self):
        self.tm.reset()
        self.history_box.clear()
        self.setup_done = False
        self.update_display()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(37, 37, 37))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = TuringMachineGUI()
    window.show()
    sys.exit(app.exec_())