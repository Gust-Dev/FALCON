# No início de gui/main_window.py, após as importações de PyQt
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QMouseEvent, QPixmap

class ClickableImageLabel(QLabel):
    # Sinal que emitirá as coordenadas do clique *na imagem original*
    imageClicked = pyqtSignal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_pixmap = None # O pixmap atualmente exibido (já escalado)
        self._original_image_width = 0
        self._original_image_height = 0

    def setPixmap(self, pixmap: QPixmap):
        self._current_pixmap = pixmap
        super().setPixmap(pixmap) # Chama o método original

    def setOriginalImageSize(self, width: int, height: int):
        self._original_image_width = width
        self._original_image_height = height

    def mousePressEvent(self, event: QMouseEvent):
        if not self._current_pixmap or self._current_pixmap.isNull() or \
           self._original_image_width == 0 or self._original_image_height == 0:
            super().mousePressEvent(event)
            return

        widget_click_pos = event.pos() # Posição do clique no widget

        # Dimensões do widget QLabel
        label_w = self.width()
        label_h = self.height()

        # Dimensões do QPixmap exibido (que já foi escalado para caber no QLabel)
        pixmap_w = self._current_pixmap.width()
        pixmap_h = self._current_pixmap.height()

        if pixmap_w == 0 or pixmap_h == 0:
            super().mousePressEvent(event)
            return

        # Calcula o offset se o pixmap estiver centralizado (devido ao KeepAspectRatio)
        offset_x = (label_w - pixmap_w) / 2.0
        offset_y = (label_h - pixmap_h) / 2.0

        # Verifica se o clique foi dentro da área do pixmap exibido
        if not (offset_x <= widget_click_pos.x() < offset_x + pixmap_w and \
                offset_y <= widget_click_pos.y() < offset_y + pixmap_h):
            # Clique fora do pixmap (na "borda" do QLabel)
            super().mousePressEvent(event)
            return

        # Coordenadas do clique relativas ao canto superior esquerdo do pixmap exibido
        pixmap_click_x = widget_click_pos.x() - offset_x
        pixmap_click_y = widget_click_pos.y() - offset_y

        # Mapeia as coordenadas do clique no pixmap para as coordenadas da imagem original
        original_x = (pixmap_click_x / pixmap_w) * self._original_image_width
        original_y = (pixmap_click_y / pixmap_h) * self._original_image_height

        self.imageClicked.emit(QPoint(int(original_x), int(original_y)))
        super().mousePressEvent(event)