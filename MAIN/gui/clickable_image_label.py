from PyQt5.QtWidgets import QLabel, QApplication # QApplication para keyboardModifiers
from PyQt5.QtGui import QPixmap, QImage, QMouseEvent, QPaintEvent, QPainter, QWheelEvent, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QPoint


class ClickableImageLabel(QLabel):
    imageClicked = pyqtSignal(QPoint); viewChanged = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap_unscaled: QPixmap | None = None; self._original_image_width = 0; self._original_image_height = 0
        self._zoom_factor = 1.0; self._pan_offset_x = 0.0; self._pan_offset_y = 0.0
        self._panning = False; self._pan_last_mouse_pos = QPoint()
        self.setAlignment(Qt.AlignCenter); self.setMinimumSize(200, 200); self.setMouseTracking(True)
    def setPixmap(self, pixmap: QPixmap | None):
        self._pixmap_unscaled = pixmap
        if pixmap and not pixmap.isNull(): self.setOriginalImageSize(pixmap.width(), pixmap.height())
        else: self.clearOriginalImageSize()
        self.update()
    def setOriginalImageSize(self, width: int, height: int):
        if self._original_image_width != width or self._original_image_height != height:
            self._original_image_width = width; self._original_image_height = height
            self._zoom_factor = 1.0; self._pan_offset_x = 0.0; self._pan_offset_y = 0.0
            self.viewChanged.emit() 
    def clearOriginalImageSize(self):
        self._original_image_width = 0; self._original_image_height = 0; self._pixmap_unscaled = None
        self._zoom_factor = 1.0; self._pan_offset_x = 0.0; self._pan_offset_y = 0.0; self.update()
    def wheelEvent(self, event: QWheelEvent):
        if not self._pixmap_unscaled or self._pixmap_unscaled.isNull(): super().wheelEvent(event); return
        delta = event.angleDelta().y(); zoom_speed_factor = 1.1; old_zoom_factor = self._zoom_factor
        if delta > 0: self._zoom_factor *= zoom_speed_factor
        elif delta < 0: self._zoom_factor /= zoom_speed_factor
        self._zoom_factor = max(0.05, min(self._zoom_factor, 20.0))
        if abs(old_zoom_factor - self._zoom_factor) > 1e-9: self.viewChanged.emit()
        self.update(); event.accept()
    def paintEvent(self, event: QPaintEvent):
        if not self._pixmap_unscaled or self._pixmap_unscaled.isNull() or \
           self._original_image_width == 0 or self._original_image_height == 0:
            painter = QPainter(self); painter.eraseRect(self.rect()); super().paintEvent(event); return
        painter = QPainter(self); painter.setRenderHint(QPainter.SmoothPixmapTransform)
        target_w_zoomed = self._original_image_width * self._zoom_factor
        target_h_zoomed = self._original_image_height * self._zoom_factor
        pixmap_to_draw = self._pixmap_unscaled.scaled(
            int(target_w_zoomed), int(target_h_zoomed), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        draw_x = (self.width() - pixmap_to_draw.width()) / 2.0 - self._pan_offset_x
        draw_y = (self.height() - pixmap_to_draw.height()) / 2.0 - self._pan_offset_y
        painter.drawPixmap(int(draw_x), int(draw_y), pixmap_to_draw)
    def _map_widget_to_image_coords(self, widget_pos: QPoint) -> tuple[int | None, int | None]:
        if not self._pixmap_unscaled or self._pixmap_unscaled.isNull() or \
           self._original_image_width == 0 or self._original_image_height == 0: return None, None
        target_w_zoomed = self._original_image_width * self._zoom_factor
        target_h_zoomed = self._original_image_height * self._zoom_factor
        painted_pixmap_scaled = self._pixmap_unscaled.scaled(
            int(target_w_zoomed), int(target_h_zoomed), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painted_w, painted_h = painted_pixmap_scaled.width(), painted_pixmap_scaled.height()
        draw_x = (self.width() - painted_w) / 2.0 - self._pan_offset_x
        draw_y = (self.height() - painted_h) / 2.0 - self._pan_offset_y
        if not (draw_x <= widget_pos.x() < draw_x + painted_w and \
                draw_y <= widget_pos.y() < draw_y + painted_h): return None, None
        on_painted_x = widget_pos.x() - draw_x; on_painted_y = widget_pos.y() - draw_y
        if painted_w == 0 or painted_h == 0: return None, None
        original_x = (on_painted_x / painted_w) * self._original_image_width
        original_y = (on_painted_y / painted_h) * self._original_image_height
        return int(original_x), int(original_y)
    def mousePressEvent(self, event: QMouseEvent):
        modifiers = QApplication.keyboardModifiers(); is_ctrl_pressed = bool(modifiers & Qt.ControlModifier)
        if is_ctrl_pressed and event.button() == Qt.LeftButton:
            if self._pixmap_unscaled and not self._pixmap_unscaled.isNull():
                self._panning = True; self._pan_last_mouse_pos = event.pos()
                self.setCursor(Qt.ClosedHandCursor); event.accept(); return
        self.unsetCursor()
        original_x, original_y = self._map_widget_to_image_coords(event.pos())
        if original_x is not None and original_y is not None:
            self.imageClicked.emit(QPoint(original_x, original_y)); event.accept(); return
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event: QMouseEvent):
        modifiers = QApplication.keyboardModifiers(); is_ctrl_pressed = bool(modifiers & Qt.ControlModifier)
        if self._panning and (event.buttons() & Qt.LeftButton):
            delta = event.pos() - self._pan_last_mouse_pos
            self._pan_offset_x -= delta.x(); self._pan_offset_y -= delta.y()
            self._pan_last_mouse_pos = event.pos(); self.update(); event.accept(); return
        if is_ctrl_pressed and not self._panning: self.setCursor(Qt.OpenHandCursor)
        elif not self._panning: self.unsetCursor()
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._panning and event.button() == Qt.LeftButton:
            self._panning = False; modifiers = QApplication.keyboardModifiers()
            if bool(modifiers & Qt.ControlModifier): self.setCursor(Qt.OpenHandCursor)
            else: self.unsetCursor()
            event.accept(); return
        super().mouseReleaseEvent(event)
    def enterEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if bool(modifiers & Qt.ControlModifier) and not self._panning: self.setCursor(Qt.OpenHandCursor)
        else: self.unsetCursor(); super().enterEvent(event)
    def leaveEvent(self, event):
        if not self._panning: self.unsetCursor()
        super().leaveEvent(event)
