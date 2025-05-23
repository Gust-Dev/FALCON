# gui/main_window.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QVBoxLayout, QWidget, QFileDialog, QMessageBox, QHBoxLayout,
                             QCheckBox, QDoubleSpinBox, QFormLayout)
from PyQt5.QtGui import (QPixmap, QImage, QPaintEvent, # QMouseEvent, QWheelEvent, QCursor são usados por ClickableImageLabel
                          QPainter)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import cv2
import numpy as np

# Assumindo que clickable_image_label.py está na mesma pasta 'gui/'
from .clickable_image_label import ClickableImageLabel

# Importe as funções dos seus módulos
try:
    from utils import image_loader, exporter, file_manager
    from core import contour_detection, vectorization, node_optimization, curve_fitter

except ModuleNotFoundError:
    # Bloco de fallback para o path (mantido como no seu original)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path: sys.path.append(project_root)
    from utils import image_loader, exporter, file_manager
    from core import contour_detection, vectorization, node_optimization, curve_fitter


class MainWindow(QMainWindow):
    preview_needs_update = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("F.A.L.C.O.N - Vetorizador Interativo") # Título atualizado
        self.setGeometry(100, 100, 1200, 750) # Ajuste o tamanho inicial da janela

        # --- 1. WIDGET CENTRAL E LAYOUT PRINCIPAL (HORIZONTAL) ---
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget") # Para QSS, se necessário
        self.setCentralWidget(self.central_widget)
        # O layout principal agora é HORIZONTAL
        self.main_app_layout = QHBoxLayout(self.central_widget)
        self.main_app_layout.setContentsMargins(9, 9, 9, 9) # Margens para o layout principal
        self.main_app_layout.setSpacing(7) # Espaçamento entre painel de controle e imagem

        # --- 2. PAINEL DE CONTROLES (LADO ESQUERDO) ---
        self.controls_panel_widget = QWidget()
        self.controls_panel_widget.setObjectName("controlsPanel") # Para estilizar com QSS
        self.controls_panel_widget.setFixedWidth(300) # Largura do painel de controles

        self.controls_panel_layout = QVBoxLayout(self.controls_panel_widget) # Layout vertical para os controles
        self.controls_panel_layout.setAlignment(Qt.AlignTop) # Alinha conteúdo ao topo
        self.controls_panel_layout.setContentsMargins(0, 0, 0, 0) # Sem margens internas no layout do painel
        self.controls_panel_layout.setSpacing(15) # Espaçamento entre os grupos de widgets no painel

        # --- Grupo: Botões de Ação ---
        self.action_buttons_group_container = QWidget() # Container para este grupo
        self.action_button_layout = QHBoxLayout(self.action_buttons_group_container) # Botões lado a lado
        self.action_button_layout.setContentsMargins(0,0,0,0)

        self.load_button = QPushButton("Carregar Imagem")
        self.load_button.setObjectName("load_button")
        self.load_button.setToolTip("Abrir um arquivo de imagem para vetorização.")
        self.load_button.clicked.connect(self.open_image_dialog)
        self.action_button_layout.addWidget(self.load_button)

        self.process_selected_button = QPushButton("Processar Seleção")
        self.process_selected_button.setObjectName("process_selected_button")
        self.process_selected_button.setToolTip("Gera os vetores e aplica simplificação (se habilitada).")
        self.process_selected_button.clicked.connect(self.process_selected_action)
        self.process_selected_button.setEnabled(False)
        self.action_button_layout.addWidget(self.process_selected_button)

        self.save_svg_button = QPushButton("Salvar SVG")
        self.save_svg_button.setObjectName("save_svg_button")
        self.save_svg_button.setToolTip("Salvar os vetores processados como um arquivo SVG.")
        self.save_svg_button.clicked.connect(self.save_svg_dialog)
        self.save_svg_button.setEnabled(False)
        self.action_button_layout.addWidget(self.save_svg_button)
        
        self.controls_panel_layout.addWidget(self.action_buttons_group_container)

        # --- Grupo: Controles Gerais ---
        self.general_controls_group_container = QWidget() # Container para este grupo
        self.general_controls_layout = QHBoxLayout(self.general_controls_group_container)
        self.general_controls_layout.setContentsMargins(0,0,0,0)

        self.reset_button = QPushButton("Resetar Imagem")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.setToolTip("Recarrega a imagem original e reseta o processo.")
        self.reset_button.clicked.connect(self.reset_image_processing_action)
        self.reset_button.setEnabled(False)
        self.general_controls_layout.addWidget(self.reset_button)
        
        self.show_bw_checkbox = QCheckBox("Mostrar Imagem P&B")
        self.show_bw_checkbox.setToolTip("Alterna a visualização para a imagem limiarizada em preto e branco.")
        self.show_bw_checkbox.stateChanged.connect(self.preview_needs_update.emit)
        self.show_bw_checkbox.setEnabled(False)
        self.general_controls_layout.addWidget(self.show_bw_checkbox)
        self.general_controls_layout.addStretch(1) # Empurra os controles gerais para a esquerda dentro do seu QHBoxLayout

        self.controls_panel_layout.addWidget(self.general_controls_group_container)

        # --- Grupo: Controles de Simplificação Customizada ---
        self.simplification_controls_layout = QFormLayout()
        self.simplification_controls_layout.setSpacing(8)

        self.enable_custom_simplification_checkbox = QCheckBox("Habilitar Simplificação RDP")
        self.enable_custom_simplification_checkbox.setToolTip("Ativa/Desativa o algoritmo de simplificação de Douglas-Peucker.")
        self.enable_custom_simplification_checkbox.setChecked(False)
        self.enable_custom_simplification_checkbox.stateChanged.connect(self.trigger_reprocess_on_control_change)
        self.simplification_controls_layout.addRow(self.enable_custom_simplification_checkbox)

        self.custom_epsilon_input = QDoubleSpinBox()
        self.custom_epsilon_input.setToolTip("Define o valor de tolerância (epsilon) para o algoritmo RDP.")
        self.custom_epsilon_input.setSuffix(" (ε)")
        self.custom_epsilon_input.setMinimum(0.00)
        self.custom_epsilon_input.setMaximum(50.0)
        self.custom_epsilon_input.setSingleStep(0.01)
        self.custom_epsilon_input.setValue(1.0)
        self.custom_epsilon_input.setDecimals(2)
        self.custom_epsilon_input.setEnabled(False)
        self.enable_custom_simplification_checkbox.toggled.connect(self.custom_epsilon_input.setEnabled)
        self.custom_epsilon_input.valueChanged.connect(self.trigger_reprocess_on_control_change)
        self.simplification_controls_layout.addRow("Tolerância (ε):", self.custom_epsilon_input)

        self.controls_panel_layout.addLayout(self.simplification_controls_layout)

        # Adiciona um espaçador para empurrar os controles para cima no painel esquerdo
        self.controls_panel_layout.addStretch(1)

        # --- 3. ÁREA DE VISUALIZAÇÃO DA IMAGEM (LADO DIREITO) ---
        self.image_preview_label = ClickableImageLabel()
        self.image_preview_label.setObjectName("imagePreview") # Para QSS
        self.image_preview_label.imageClicked.connect(self.handle_preview_image_click)
        self.image_preview_label.viewChanged.connect(self.preview_needs_update.emit)

        # --- 4. ADICIONAR PAINEL DE CONTROLES E IMAGEM AO LAYOUT PRINCIPAL ---
        self.main_app_layout.addWidget(self.controls_panel_widget)    # Painel da esquerda
        self.main_app_layout.addWidget(self.image_preview_label, 1) # Imagem à direita, com fator de stretch 1

        # --- 5. ESTADO INICIAL E VARIÁVEIS ---
        self.loaded_image_cv: np.ndarray | None = None
        self.threshold_image_for_preview: np.ndarray | None = None
        self.raw_contours: list | None = None
        self.raw_contour_selection_states: list[bool] = []
        self.vectorized_polylines_from_selection: list[list[tuple[int, int]]] | None = None
        self.final_renderable_paths: list[list[tuple]] | None = None
        self._current_image_filepath: str | None = None
        self.preview_mode = "idle"
        
        self.preview_needs_update.connect(self.update_preview_display)
        self.reset_ui_states_for_new_image()

    # --- Outros Métodos da Classe MainWindow ---
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
        self.reset_button.setEnabled(bool(self._current_image_filepath))

    def reset_image_processing_action(self):
        current_fp = self._current_image_filepath
        if current_fp:
            QMessageBox.information(self, "Resetar", f"Resetando imagem: {os.path.basename(current_fp)}")
            self.full_image_processing_pipeline(current_fp)
        else:
            self.loaded_image_cv = None
            self._current_image_filepath = None
            self.reset_ui_states_for_new_image()
            QMessageBox.information(self, "Resetar", "Nenhuma imagem para resetar.")

    def handle_preview_image_click(self, image_click_pos: QPoint):
        if self.preview_mode != "selecting_contours" or not self.raw_contours or \
           not self.raw_contour_selection_states or \
           len(self.raw_contours) != len(self.raw_contour_selection_states):
            return

        click_pt = (image_click_pos.x(), image_click_pos.y())
        best_match_index, min_area_for_match = -1, float('inf')

        for i, contour in enumerate(self.raw_contours):
            distance = cv2.pointPolygonTest(contour, click_pt, False) 
            if distance >= 0: 
                area = cv2.contourArea(contour)
                if area < min_area_for_match: 
                    min_area_for_match = area
                    best_match_index = i
        
        if best_match_index != -1:
            self.raw_contour_selection_states[best_match_index] = not self.raw_contour_selection_states[best_match_index]
            self.preview_needs_update.emit()

    def open_image_dialog(self):
        last_input_dir = file_manager.get_last_input_directory() or os.path.expanduser("~")
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo de Imagem", last_input_dir,
                                                   "Arquivos de Imagem (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos os Arquivos (*)",
                                                   options=options)
        if file_path:
            current_dir = os.path.dirname(file_path)
            file_manager.set_last_input_directory(current_dir)
            self.full_image_processing_pipeline(file_path)

    def full_image_processing_pipeline(self, file_path: str):
        self.loaded_image_cv = image_loader.load_image(file_path)
        self._current_image_filepath = file_path
        self.reset_ui_states_for_new_image() 

        if self.loaded_image_cv is None:
            QMessageBox.warning(self, "Erro ao Carregar", f"Não foi possível carregar a imagem de: {file_path}")
            self._current_image_filepath = None
            self.reset_button.setEnabled(False)
            return

        self.reset_button.setEnabled(True)

        detection_result = contour_detection.detect_contours(self.loaded_image_cv, blur_ksize_val=5)
        if detection_result:
            self.raw_contours, self.threshold_image_for_preview = detection_result
        else:
            self.raw_contours, self.threshold_image_for_preview = None, None
        
        if self.threshold_image_for_preview is not None:
            self.show_bw_checkbox.setEnabled(True)

        if not self.raw_contours:
            QMessageBox.information(self, "Resultado da Detecção", "Nenhum contorno foi detectado na imagem.")
            self.preview_mode = "idle"
            self.process_selected_button.setEnabled(False)
        else:
            self.raw_contour_selection_states = [True] * len(self.raw_contours)
            self.preview_mode = "selecting_contours"
            self.process_selected_button.setEnabled(True)

        self.preview_needs_update.emit()
        
    def process_selected_action(self):
        if not self.raw_contours or not any(self.raw_contour_selection_states):
            print("Processar Ação: Nenhum contorno selecionado para processar.")
            return
        
        selected_raw_contours = [
            self.raw_contours[i] for i, is_selected in enumerate(self.raw_contour_selection_states) if is_selected]
        
        if not selected_raw_contours:
            print("Processar Ação: Nenhum contorno efetivamente selecionado após filtragem.")
            return

        polylines_base = vectorization.vectorize_from_contours(selected_raw_contours)
        if not polylines_base:
            QMessageBox.warning(self, "Erro de Vetorização", "Falha ao vetorizar os contornos selecionados.")
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
                if simplified_polylines is None or not simplified_polylines:
                    print("Aviso: Simplificação Customizada resultou em dados vazios ou falhou. Usando vetores detalhados.")
                else:
                    polylines_para_finalizar = simplified_polylines
            except ImportError:
                QMessageBox.warning(self, "Erro de Módulo", "Módulo 'node_optimization' não pôde ser importado. Simplificação não aplicada.")
            except Exception as e:
                QMessageBox.warning(self, "Erro de Simplificação", f"Ocorreu um erro durante a simplificação customizada: {e}")
        else:
            print("Simplificação Customizada DESABILITADA.")
        
        self.vectorized_polylines_from_selection = polylines_para_finalizar
            
        self.final_renderable_paths = curve_fitter.fit_curves_to_paths(self.vectorized_polylines_from_selection)
        
        if self.final_renderable_paths is not None:
            self.preview_mode = "showing_processed"
            self.save_svg_button.setEnabled(True)
            print(f"Processamento concluído: {len(selected_raw_contours)} contornos originais -> {len(self.final_renderable_paths)} caminhos finais.")
        else:
            QMessageBox.warning(self, "Erro Pós-Processamento", "Falha ao converter caminhos para a estrutura final SVG.")
            self.save_svg_button.setEnabled(False)
        
        self.preview_needs_update.emit()

    def trigger_reprocess_on_control_change(self):
        """ Chamado quando o checkbox de simplificação ou o valor de epsilon mudam. """
        # Debug prints (opcional, pode remover depois)
        print("--- Debug: trigger_reprocess_on_control_change ---")
        # try:
        #     print(f"  self.loaded_image_cv is not None? {self.loaded_image_cv is not None}")
        #     print(f"  self.raw_contours? {bool(self.raw_contours)}")
        #     if hasattr(self, 'raw_contour_selection_states'):
        #         print(f"  any(self.raw_contour_selection_states)? {any(self.raw_contour_selection_states)}")
        # except Exception as e_debug:
        #     print(f"  ERRO no debug print: {e_debug}")

        # Condição corrigida para evitar ValueError com NumPy array
        if (self.loaded_image_cv is not None and
            self.raw_contours and # self.raw_contours é None ou lista, bool(None) é False, bool([]) é False
            self.raw_contour_selection_states and # Verifica se a lista não é None (deve ser inicializada como [])
            any(self.raw_contour_selection_states)):
            
            if self.preview_mode == "selecting_contours" or self.preview_mode == "showing_processed":
                print(f"Controle de simplificação mudou. Re-processando automaticamente.")
                self.process_selected_action()
            # else:
            #     print("  Condição de preview_mode não atendida para reprocessar.")
        # else:
        #     print("  Condição principal para reprocessar NÃO atendida.")
        #     if self.loaded_image_cv is None: print("    Motivo: self.loaded_image_cv é None")
        #     if not self.raw_contours: print("    Motivo: self.raw_contours é Falsy (None ou lista vazia)")
        #     if hasattr(self, 'raw_contour_selection_states') and not any(self.raw_contour_selection_states):
        #          print("    Motivo: any(self.raw_contour_selection_states) é False (lista vazia ou todos False)")


    def update_preview_display(self):
        current_base_image_for_drawing = None
        display_original_w, display_original_h = 0, 0

        if self.show_bw_checkbox.isChecked() and self.threshold_image_for_preview is not None:
            if len(self.threshold_image_for_preview.shape) == 2:
                 current_base_image_for_drawing = cv2.cvtColor(self.threshold_image_for_preview, cv2.COLOR_GRAY2BGR)
            else:
                 current_base_image_for_drawing = self.threshold_image_for_preview.copy()
            display_original_h, display_original_w = self.threshold_image_for_preview.shape[:2]
        elif self.loaded_image_cv is not None:
            current_base_image_for_drawing = self.loaded_image_cv.copy()
            display_original_h, display_original_w, _ = self.loaded_image_cv.shape
        else:
            self.image_preview_label.setText("Nenhuma imagem carregada.")
            self.image_preview_label.setPixmap(QPixmap())
            self.image_preview_label.clearOriginalImageSize()
            return

        if self.preview_mode == "selecting_contours" and self.raw_contours:
            if len(self.raw_contours) == len(self.raw_contour_selection_states):
                for i, contour in enumerate(self.raw_contours):
                    color = (0, 255, 0) if self.raw_contour_selection_states[i] else (0, 0, 255)
                    cv2.drawContours(current_base_image_for_drawing, [contour], -1, color, 1)
        
        elif self.preview_mode == "showing_processed" and self.vectorized_polylines_from_selection:
            for path_polyline in self.vectorized_polylines_from_selection:
                if len(path_polyline) > 1:
                    np_path = np.array(path_polyline, dtype=np.int32).reshape((-1, 1, 2))
                    # Cor alterada para os vetores processados para melhor distinção
                    cv2.polylines(current_base_image_for_drawing, [np_path], False, (255, 128, 0), 1) 

        try:
            q_image = QImage(current_base_image_for_drawing.data,
                             current_base_image_for_drawing.shape[1], 
                             current_base_image_for_drawing.shape[0], 
                             current_base_image_for_drawing.strides[0],
                             QImage.Format_BGR888)
            pixmap_to_set_on_label = QPixmap.fromImage(q_image)

            self.image_preview_label.setOriginalImageSize(display_original_w, display_original_h)
            self.image_preview_label.setPixmap(pixmap_to_set_on_label)
        except Exception as e:
            print(f"Erro ao converter imagem para display: {e}")
            self.image_preview_label.setText("Erro ao exibir imagem.")


    def draw_original_image_on_preview(self): 
        if self.loaded_image_cv is None:
            self.image_preview_label.setText("Nenhuma imagem.")
            self.image_preview_label.setPixmap(QPixmap())
            self.image_preview_label.clearOriginalImageSize()
            return
        
        h_orig, w_orig, _ = self.loaded_image_cv.shape
        q_image = QImage(self.loaded_image_cv.data, w_orig, h_orig, self.loaded_image_cv.strides[0], QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_preview_label.setOriginalImageSize(w_orig, h_orig)
        self.image_preview_label.setPixmap(pixmap)

    def save_svg_dialog(self):
        if not self.final_renderable_paths:
            QMessageBox.information(self, "Salvar SVG", "Nenhum dado vetorial finalizado para salvar.")
            return

        img_h, img_w = (None, None)
        if self.loaded_image_cv is not None:
            img_h, img_w, _ = self.loaded_image_cv.shape
        
        last_output_dir = file_manager.get_last_output_directory() or os.path.expanduser("~")
        suggested_filename_base = "vetorizado_falcon"
        
        if self._current_image_filepath:
            base = os.path.basename(self._current_image_filepath)
            name, _ = os.path.splitext(base)
            suggested_filename_base = f"{name}_vetorizado_falcon" 
            if self.enable_custom_simplification_checkbox.isChecked():
                suggested_filename_base += "_simplificado"
        
        suggested_filepath = os.path.join(last_output_dir, f"{suggested_filename_base}.svg")
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Arquivo SVG", suggested_filepath,
                                                   "Arquivos SVG (*.svg);;Todos os Arquivos (*)",
                                                   options=options)
        if file_path:
            if not file_path.lower().endswith(".svg"):
                file_path += ".svg"
            
            current_dir = os.path.dirname(file_path)
            file_manager.set_last_output_directory(current_dir)
            
            success = exporter.export_to_svg(self.final_renderable_paths, file_path,
                                             image_width=img_w, image_height=img_h)
            if success:
                QMessageBox.information(self, "Sucesso!", f"Arquivo SVG salvo em:\n{file_path}")
            else:
                QMessageBox.critical(self, "Erro ao Salvar", "Ocorreu um erro ao tentar salvar o arquivo SVG.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Bloco de teste para carregar QSS se este arquivo for executado diretamente
    # qss_file_to_load = None
    # path_to_qss = os.path.join(os.path.dirname(__file__), "style", "style.qss") # Caminho relativo à pasta gui
    # if os.path.exists(path_to_qss):
    #     qss_file_to_load = path_to_qss
    # if qss_file_to_load:
    #     try:
    #         with open(qss_file_to_load, "r", encoding='utf-8') as f:
    #             style_sheet_content = f.read()
    #             app.setStyleSheet(style_sheet_content)
    #             print(f"Estilo QSS carregado (teste direto main_window.py): {qss_file_to_load}")
    #     except Exception as e:
    #         print(f"ERRO ao carregar QSS (teste direto main_window.py): {e}")
    # else:
    #     print(f"AVISO: Arquivo de estilo (teste direto main_window.py) '{path_to_qss}' não encontrado.")

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())