import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow # Certifique-se que esta importação está correta

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # --- CÓDIGO PARA CARREGAR O ARQUIVO QSS ---
    qss_file_to_load = None
    path_to_qss = os.path.join(os.path.dirname(__file__), "gui", "style", "style.qss")

    if os.path.exists(path_to_qss):
        qss_file_to_load = path_to_qss
    
    if qss_file_to_load:
        try:
            # MODIFICAÇÃO AQUI vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
            with open(qss_file_to_load, "r", encoding='utf-8') as f:
            # MODIFICAÇÃO AQUI ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                style_sheet_content = f.read()
                app.setStyleSheet(style_sheet_content)
                print(f"Estilo QSS carregado com sucesso de: {qss_file_to_load}")
        except Exception as e:
            print(f"ERRO ao carregar o arquivo de estilo '{qss_file_to_load}': {e}")
    else:
        print(f"AVISO: Arquivo de estilo '{path_to_qss}' não encontrado.")
    # --- FIM DO CÓDIGO QSS ---

    main_window_instance = MainWindow()
    main_window_instance.show()
    sys.exit(app.exec_())