import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPalette

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(35) # Altura da barra de título
        self.setObjectName("CustomTitleBar")

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 5, 0) # Margens (esquerda, topo, direita, baixo)
        layout.setSpacing(5)

        self.title_label = QLabel(self.parent_window.windowTitle())
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0; /* Cor do texto do título */
                font-weight: bold;
                padding-left: 5px; /* Espaço para não colar no canto se não houver botões à esquerda */
            }
        """)

        btn_size = 25

        self.btn_minimize = QPushButton("—")
        self.btn_minimize.setFixedSize(btn_size, btn_size)
        self.btn_minimize.clicked.connect(self.parent_window.showMinimized)
        self.btn_minimize.setObjectName("MinimizeButton")
        self.btn_minimize.setStyleSheet("""
            #MinimizeButton {
                background-color: transparent; color: #E0E0E0;
                border: none; border-radius: 3px; font-weight: bold;
            }
            #MinimizeButton:hover { background-color: #4A4A4A; }
            #MinimizeButton:pressed { background-color: #3A3A3A; }
        """)

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(btn_size, btn_size)
        self.btn_close.clicked.connect(self.parent_window.close)
        self.btn_close.setObjectName("CloseButton")
        self.btn_close.setStyleSheet("""
            #CloseButton {
                background-color: transparent; color: #E0E0E0;
                border: none; border-radius: 3px; font-weight: bold;
            }
            #CloseButton:hover { background-color: #E81123; color: white; }
            #CloseButton:pressed { background-color: #B70013; color: white; }
        """)

        layout.addWidget(self.title_label)
        layout.addStretch() # Empurra os botões para a direita
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_close)
        self.setLayout(layout)

        # Para mover a janela
        self._mouse_pressed = False
        self._old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Verifica se o clique não foi em um botão da barra de título
            child_at_click = self.childAt(event.pos())
            if not child_at_click or child_at_click == self.title_label or child_at_click == self:
                self._mouse_pressed = True
                self._old_pos = event.globalPos()
                self._old_window_pos = self.parent_window.pos()
                event.accept()

    def mouseMoveEvent(self, event):
        if self._mouse_pressed and self._old_pos:
            delta = event.globalPos() - self._old_pos
            self.parent_window.move(self._old_window_pos + delta)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_pressed = False
            self._old_pos = None
            self._old_window_pos = None
            event.accept()

    def setTitle(self, title):
        self.title_label.setText(title)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("F.A.L.C.O.N Custom") # Seu título aqui
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window) # Permite minimizar corretamente
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Cor de fundo da janela e raio da borda
        self.background_color = "#2D2D2D"  # Um cinza escuro, mude conforme desejar
        self.border_radius = 10 # Raio dos cantos arredondados

        # Container principal que terá os cantos arredondados e a cor de fundo
        self.central_container = QWidget(self)
        self.central_container.setObjectName("CentralContainer")
        # Estilo para o container principal (fundo e bordas arredondadas)
        self.central_container.setStyleSheet(f"""
            #CentralContainer {{
                background-color: {self.background_color};
                border-radius: {self.border_radius}px;
                /* Você pode adicionar uma borda sutil se quiser */
                /* border: 1px solid #1C1C1C; */
            }}
        """)

        # Layout principal para o container (barra de título + conteúdo)
        main_layout = QVBoxLayout(self.central_container)
        main_layout.setContentsMargins(1, 1, 1, 1) # Pequena margem para a borda não cortar o conteúdo
        main_layout.setSpacing(0)

        # Barra de título customizada
        self.title_bar = CustomTitleBar(self)
        self.title_bar.setStyleSheet(f"""
            #CustomTitleBar {{
                background-color: #3C3C3C; /* Cor de fundo da barra de título */
                border-top-left-radius: {self.border_radius}px;
                border-top-right-radius: {self.border_radius}px;
            }}
        """)
        main_layout.addWidget(self.title_bar)

        # Conteúdo principal da sua aplicação (substitua pelo layout do seu app)
        # Este é o widget onde você colocará os elementos da sua UI (botões, etc.)
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget) # Use o layout apropriado para seu conteúdo

        # --- INÍCIO DO CONTEÚDO DA SUA APLICAÇÃO F.A.L.C.O.N ---
        # Adapte esta parte para recriar a interface da imagem que você forneceu
        # Por exemplo, um layout horizontal com um painel esquerdo e uma área principal
        app_main_area_layout = QHBoxLayout()
        app_main_area_layout.setContentsMargins(10, 10, 10, 10) # Margens internas para o conteúdo
        app_main_area_layout.setSpacing(10)

        # Painel Esquerdo (como na sua imagem)
        left_panel = QWidget()
        left_panel.setFixedWidth(200) # Largura do painel esquerdo
        # Você pode dar um estilo ao painel esquerdo também se desejar
        # left_panel.setStyleSheet("background-color: #333333; border-radius: 5px;")
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(10, 10, 10, 10)
        left_panel_layout.setSpacing(10)
        left_panel_layout.setAlignment(Qt.AlignTop) # Alinha widgets ao topo

        btn_carregar_imagem = QPushButton("Carregar Imagem")
        btn_carregar_imagem.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; color: white; padding: 8px;
                border: none; border-radius: 3px;
            }
            QPushButton:hover { background-color: #005A9E; }
        """)
        btn_processar_selecao = QPushButton("Processar Seleção")
        btn_processar_selecao.setStyleSheet("""
            QPushButton {
                background-color: #707070; color: white; padding: 8px;
                border: none; border-radius: 3px;
            }
            QPushButton:hover { background-color: #505050; }
        """)
        btn_salvar_svg = QPushButton("Salvar SVG")
        btn_salvar_svg.setStyleSheet("""
            QPushButton {
                background-color: #707070; color: white; padding: 8px;
                border: none; border-radius: 3px;
            }
            QPushButton:hover { background-color: #505050; }
        """)
        # Adicione outros widgets do painel esquerdo aqui (Resetar Imagem, Checkboxes, Tolerância)

        left_panel_layout.addWidget(btn_carregar_imagem)
        left_panel_layout.addWidget(btn_processar_selecao)
        left_panel_layout.addWidget(btn_salvar_svg)
        # ... Adicionar mais widgets ...
        left_panel_layout.addStretch() # Empurra para cima, se necessário

        # Área Principal (onde "Nenhuma imagem." aparece)
        right_area = QLabel("Nenhuma imagem.")
        right_area.setAlignment(Qt.AlignCenter)
        right_area.setStyleSheet("color: #CCCCCC; font-size: 16px;")
        right_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        app_main_area_layout.addWidget(left_panel)
        app_main_area_layout.addWidget(right_area, 1) # O '1' faz com que expanda

        content_layout.addLayout(app_main_area_layout)
        # --- FIM DO CONTEÚDO DA SUA APLICAÇÃO F.A.L.C.O.N ---

        main_layout.addWidget(self.content_widget)

        self.setCentralWidget(self.central_container)

        # Geometria inicial
        self.resize(800, 600)

    def setWindowTitle(self, title):
        super().setWindowTitle(title)
        if hasattr(self, 'title_bar'): # Garante que title_bar já existe
            self.title_bar.setTitle(title)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Opcional: Definir uma paleta de cores global para um look mais consistente
    # app_palette = QPalette()
    # app_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # app_palette.setColor(QPalette.WindowText, Qt.white)
    # # ... outras cores ...
    # app.setPalette(app_palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())