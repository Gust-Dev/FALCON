# gui/main_window.py
import sys
import os 
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QVBoxLayout, QWidget, QFileDialog, QMessageBox, QHBoxLayout,
                             QCheckBox, QDoubleSpinBox, QFormLayout) # Adicionado QDoubleSpinBox, QFormLayout
from PyQt5.QtGui import (QPixmap, QImage, QMouseEvent, QPaintEvent,
                         QPainter, QWheelEvent, QCursor)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import cv2
import numpy as np


from gui.clickable_image_label import ClickableImageLabel

# Importe as funções dos seus módulos
try:
    from utils import image_loader, exporter, file_manager
    from core import contour_detection, vectorization, node_optimization, curve_fitter 
    
except ModuleNotFoundError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path: sys.path.append(project_root)
    from utils import image_loader, exporter, file_manager
    from core import contour_detection, vectorization, node_optimization, curve_fitter



class MainWindow(QMainWindow):
    preview_needs_update = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("F.A.L.C.ON")
        self.setGeometry(100, 100, 800, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Botões de Ação
        self.action_button_layout = QHBoxLayout()
        self.load_button = QPushButton("Carregar Imagem")
        self.load_button.clicked.connect(self.open_image_dialog)
        self.action_button_layout.addWidget(self.load_button)
        self.process_selected_button = QPushButton("Processar Vetores Selecionados")
        self.process_selected_button.setToolTip("Gera os vetores e aplica simplificação (se habilitada).")
        self.process_selected_button.clicked.connect(self.process_selected_action)
        self.process_selected_button.setEnabled(False)
        self.action_button_layout.addWidget(self.process_selected_button)
        self.save_svg_button = QPushButton("Salvar SVG")
        self.save_svg_button.clicked.connect(self.save_svg_dialog)
        self.save_svg_button.setEnabled(False)
        self.action_button_layout.addWidget(self.save_svg_button)
        self.main_layout.addLayout(self.action_button_layout)
        
        # Controles Gerais
        self.general_controls_layout = QHBoxLayout()
        self.reset_button = QPushButton("Resetar Imagem")
        self.reset_button.clicked.connect(self.reset_image_processing_action)
        self.reset_button.setEnabled(False)
        self.general_controls_layout.addWidget(self.reset_button)
        self.show_bw_checkbox = QCheckBox("Mostrar Imagem P&B")
        self.show_bw_checkbox.stateChanged.connect(self.preview_needs_update.emit)
        self.show_bw_checkbox.setEnabled(False)
        self.general_controls_layout.addWidget(self.show_bw_checkbox)
        self.main_layout.addLayout(self.general_controls_layout)

        # Controles de Simplificação Customizada
        self.simplification_controls_layout = QFormLayout()
        self.enable_custom_simplification_checkbox = QCheckBox("Habilitar Simplificação")
        self.enable_custom_simplification_checkbox.setChecked(False) 
        self.enable_custom_simplification_checkbox.stateChanged.connect(self.trigger_reprocess_on_control_change)
        self.simplification_controls_layout.addRow(self.enable_custom_simplification_checkbox)

        self.custom_epsilon_input = QDoubleSpinBox()
        self.custom_epsilon_input.setSuffix("")
        self.custom_epsilon_input.setMinimum(0.0)
        self.custom_epsilon_input.setMaximum(50.0) 
        self.custom_epsilon_input.setSingleStep(0.1)
        self.custom_epsilon_input.setValue(1.0) # Valor padrão para epsilon
        self.custom_epsilon_input.setDecimals(2)
        self.custom_epsilon_input.setEnabled(False)
        self.enable_custom_simplification_checkbox.toggled.connect(self.custom_epsilon_input.setEnabled)
        self.custom_epsilon_input.valueChanged.connect(self.trigger_reprocess_on_control_change)
        self.simplification_controls_layout.addRow("Tolerância RDP:", self.custom_epsilon_input)
        self.main_layout.addLayout(self.simplification_controls_layout)

        self.image_preview_label = ClickableImageLabel()
        self.image_preview_label.setMinimumSize(1000, 800)
        self.image_preview_label.setStyleSheet("border: 1px solid black;")
        self.image_preview_label.imageClicked.connect(self.handle_preview_image_click)
        self.image_preview_label.viewChanged.connect(self.preview_needs_update.emit)
        self.main_layout.addWidget(self.image_preview_label)

        self.loaded_image_cv: np.ndarray | None = None
        self.threshold_image_for_preview: np.ndarray | None = None
        self.raw_contours: list | None = None
        self.raw_contour_selection_states: list[bool] = []
        self.vectorized_polylines_from_selection: list[list[tuple[int, int]]] | None = None
        self.final_renderable_paths: list[list[tuple]] | None = None
        self._current_image_filepath: str | None = None
        self.preview_mode = "idle"
        self.preview_needs_update.connect(self.update_preview_display)

    def reset_ui_states_for_new_image(self):
        self.raw_contours = None; self.raw_contour_selection_states = []
        self.threshold_image_for_preview = None
        self.vectorized_polylines_from_selection = None
        self.final_renderable_paths = None
        self.preview_mode = "idle"
        if self.image_preview_label:
            self.image_preview_label.clearOriginalImageSize()
            self.image_preview_label.setPixmap(QPixmap()) 
            self.image_preview_label.setText("Nenhuma imagem." if not self._current_image_filepath else "Processando...")
        self.process_selected_button.setEnabled(False)
        self.save_svg_button.setEnabled(False)
        self.show_bw_checkbox.setEnabled(False); self.show_bw_checkbox.setChecked(False)
        self.enable_custom_simplification_checkbox.setChecked(False)
        self.custom_epsilon_input.setEnabled(False)
        self.reset_button.setEnabled(bool(self._current_image_filepath))

    def reset_image_processing_action(self):
        # ... (como antes) ...
        current_fp = self._current_image_filepath 
        if current_fp: QMessageBox.information(self, "Resetar", f"Resetando: {os.path.basename(current_fp)}"); self.full_image_processing_pipeline(current_fp)
        else: self.loaded_image_cv = None; self._current_image_filepath = None; self.reset_ui_states_for_new_image(); QMessageBox.information(self, "Resetar", "Nenhuma imagem.")

    def handle_preview_image_click(self, image_click_pos: QPoint):
        # ... (como antes) ...
        if self.preview_mode != "selecting_contours" or not self.raw_contours or \
           not self.raw_contour_selection_states or \
           len(self.raw_contours) != len(self.raw_contour_selection_states): return
        click_pt = (image_click_pos.x(), image_click_pos.y()); best_match_index, min_area_for_match = -1, float('inf')
        for i, contour in enumerate(self.raw_contours):
            distance = cv2.pointPolygonTest(contour, click_pt, False)
            if distance >= 0:
                area = cv2.contourArea(contour)
                if area < min_area_for_match: min_area_for_match, best_match_index = area, i
        if best_match_index != -1:
            self.raw_contour_selection_states[best_match_index] = not self.raw_contour_selection_states[best_match_index]
            self.preview_needs_update.emit()

    def open_image_dialog(self):
        # ... (como antes) ...
        last_input_dir = file_manager.get_last_input_directory() or ""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Imagem", last_input_dir, "Imagens (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)", options=options)
        if file_path:
            current_dir = os.path.dirname(file_path); file_manager.set_last_input_directory(current_dir)
            self.full_image_processing_pipeline(file_path)

    def full_image_processing_pipeline(self, file_path: str):
        # ... (como antes) ...
        self.loaded_image_cv = image_loader.load_image(file_path)
        self._current_image_filepath = file_path 
        self.reset_ui_states_for_new_image() 
        if self.loaded_image_cv is None:
            QMessageBox.warning(self, "Erro", f"Não carregou: {file_path}"); self._current_image_filepath = None
            self.reset_button.setEnabled(False); return
        self.reset_button.setEnabled(True)
        detection_result = contour_detection.detect_contours(self.loaded_image_cv, blur_ksize_val=5) 
        if detection_result: self.raw_contours, self.threshold_image_for_preview = detection_result
        else: self.raw_contours, self.threshold_image_for_preview = None, None
        if self.threshold_image_for_preview is not None: self.show_bw_checkbox.setEnabled(True)
        if not self.raw_contours:
            QMessageBox.information(self, "Resultado", "Nenhum contorno detectado."); self.preview_mode = "idle"
            self.process_selected_button.setEnabled(False)
        else:
            self.raw_contour_selection_states = [True] * len(self.raw_contours)
            self.preview_mode = "selecting_contours"; self.process_selected_button.setEnabled(True)
        self.preview_needs_update.emit()
        
    def process_selected_action(self): 
        if not self.raw_contours or not any(self.raw_contour_selection_states):
            print("Processar Ação: Nenhum contorno selecionado para processar.")
            # QMessageBox.information(self, "Processar", "Nenhum contorno selecionado."); # REMOVIDO/COMENTADO
            return
        
        selected_raw_contours = [
            self.raw_contours[i] for i, is_selected in enumerate(self.raw_contour_selection_states) if is_selected]
        if not selected_raw_contours:
            print("Processar Ação: Nenhum contorno efetivamente selecionado.")
            # QMessageBox.information(self, "Processar", "Nenhum contorno efetivamente selecionado."); # REMOVIDO/COMENTADO
            return

        polylines_base = vectorization.vectorize_from_contours(selected_raw_contours)
        if not polylines_base:
            QMessageBox.warning(self, "Erro de Vetorização", "Falha ao vetorizar contornos selecionados."); # Erro importante, pode manter
            return

        polylines_para_finalizar = polylines_base

        if self.enable_custom_simplification_checkbox.isChecked():
            epsilon_val = self.custom_epsilon_input.value()
            print(f"Simplificação RDP Customizada HABILITADA com epsilon: {epsilon_val}")
            try:
                simplified_polylines = node_optimization.apply_custom_rdp_simplification(
                    polylines_base, 
                    epsilon=epsilon_val
                )
                if simplified_polylines is None:
                     print("Aviso: Falha na Simplificação Customizada. Usando vetores detalhados.")
                     # QMessageBox.warning(self, "Simplificação Customizada", "Falha ao simplificar. Usando vetores detalhados."); # REMOVIDO/COMENTADO
                     # polylines_para_finalizar continua sendo polylines_base
                else:
                    polylines_para_finalizar = simplified_polylines
            except ImportError: # Erro crítico de importação do módulo de otimização
                QMessageBox.warning(self, "Erro de Módulo", "Módulo 'node_optimization' não importado. Simplificação não aplicada.")
                # Continua com polylines_base
            except Exception as e: # Outro erro na simplificação
                QMessageBox.warning(self, "Erro de Simplificação", f"Erro na simplificação customizada: {e}")
                # Continua com polylines_base por segurança
        else:
            print("Simplificação Customizada DESABILITADA.")
        
        self.vectorized_polylines_from_selection = polylines_para_finalizar # Para o preview
            
        self.final_renderable_paths = curve_fitter.fit_curves_to_paths(self.vectorized_polylines_from_selection)
        
        if self.final_renderable_paths is not None:
            self.preview_mode = "showing_processed" 
            self.save_svg_button.setEnabled(True)
            print(f"Processamento concluído: {len(selected_raw_contours)} contornos originais -> {len(self.final_renderable_paths)} caminhos finais.")
            # QMessageBox.information(self, "Processado",  # REMOVIDO/COMENTADO
            #                         f"{len(selected_raw_contours)} contornos selecionados processados.")
        else:
            QMessageBox.warning(self, "Erro Pós-Processamento", "Falha ao converter para estrutura SVG final.") # Erro importante, pode manter
            self.save_svg_button.setEnabled(False)
        
        self.preview_needs_update.emit()

    def trigger_reprocess_on_control_change(self):
        """ Chamado quando o checkbox de simplificação ou o valor de epsilon mudam. """
        if self.process_selected_button.isEnabled() and \
           self.raw_contours and any(self.raw_contour_selection_states):
            print(f"Controle de simplificação mudou. Re-processando.")
            self.process_selected_action()

    def update_preview_display(self):
        # ... (como na sua última versão, desenhando self.vectorized_polylines_from_selection) ...
        current_base_image_for_drawing = None; display_original_w, display_original_h = 0,0
        if self.show_bw_checkbox.isChecked() and self.threshold_image_for_preview is not None:
            current_base_image_for_drawing = cv2.cvtColor(self.threshold_image_for_preview, cv2.COLOR_GRAY2BGR)
            display_original_h, display_original_w = self.threshold_image_for_preview.shape[:2]
        elif self.loaded_image_cv is not None:
            current_base_image_for_drawing = self.loaded_image_cv.copy()
            display_original_h, display_original_w, _ = self.loaded_image_cv.shape
        else: self.image_preview_label.setText("Nenhuma imagem."); self.image_preview_label.setPixmap(QPixmap()); self.image_preview_label.clearOriginalImageSize(); return
        if self.preview_mode == "selecting_contours" and self.raw_contours:
            if len(self.raw_contours) == len(self.raw_contour_selection_states):
                for i, contour in enumerate(self.raw_contours):
                    color = (0,255,0) if self.raw_contour_selection_states[i] else (0,0,255)
                    cv2.drawContours(current_base_image_for_drawing, [contour], -1, color, 1)
        elif self.preview_mode == "showing_processed" and self.vectorized_polylines_from_selection:
            for path_polyline in self.vectorized_polylines_from_selection: 
                if len(path_polyline) > 1:
                    np_path = np.array(path_polyline, dtype=np.int32).reshape((-1,1,2))
                    cv2.polylines(current_base_image_for_drawing, [np_path], True, (50,150,255), 1)
        q_image = QImage(current_base_image_for_drawing.data, current_base_image_for_drawing.shape[1], current_base_image_for_drawing.shape[0], current_base_image_for_drawing.strides[0], QImage.Format_BGR888)
        pixmap_to_set_on_label = QPixmap.fromImage(q_image)
        self.image_preview_label.setOriginalImageSize(display_original_w, display_original_h)
        self.image_preview_label.setPixmap(pixmap_to_set_on_label)

    def draw_original_image_on_preview(self):
        # ... (como na sua última versão) ...
        if self.loaded_image_cv is None: self.image_preview_label.setText("Nenhuma imagem."); self.image_preview_label.setPixmap(QPixmap()); self.image_preview_label.clearOriginalImageSize(); return
        h_orig, w_orig, _ = self.loaded_image_cv.shape
        q_image = QImage(self.loaded_image_cv.data, w_orig, h_orig, self.loaded_image_cv.strides[0], QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_preview_label.setOriginalImageSize(w_orig, h_orig); self.image_preview_label.setPixmap(pixmap)

    def save_svg_dialog(self):
        # ... (como na sua última versão, usando self.final_renderable_paths) ...
        if not self.final_renderable_paths: QMessageBox.information(self, "Salvar SVG", "Nenhum dado final para salvar."); return
        img_h, img_w = (None,None); 
        if self.loaded_image_cv is not None: img_h,img_w,_ = self.loaded_image_cv.shape
        last_output_dir = file_manager.get_last_output_directory() or ""
        suggested_filename_base = "vetorizado_final"
        if self._current_image_filepath:
            base = os.path.basename(self._current_image_filepath); name,_ = os.path.splitext(base)
            suggested_filename_base = f"{name}_final"
            if self.enable_custom_simplification_checkbox.isChecked(): suggested_filename_base += "_simplificado"
        suggested_filepath = os.path.join(last_output_dir, f"{suggested_filename_base}.svg")
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Arquivo SVG", suggested_filepath, "Arquivos SVG (*.svg);;Todos (*)", options=options)
        if file_path:
            if not file_path.lower().endswith(".svg"): file_path += ".svg"
            current_dir = os.path.dirname(file_path); file_manager.set_last_output_directory(current_dir)
            success = exporter.export_to_svg(self.final_renderable_paths, file_path, image_width=img_w, image_height=img_h)
            if success: QMessageBox.information(self, "Sucesso", f"SVG salvo em:\n{file_path}")
            else: QMessageBox.critical(self, "Erro", "Erro ao salvar o SVG.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())