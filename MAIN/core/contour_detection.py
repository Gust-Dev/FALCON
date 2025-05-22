# core/contour_detection.py
import cv2
import numpy as np

def detect_contours(color_image_cv: np.ndarray, 
                    blur_ksize_val: int = 5) -> tuple[list | None, np.ndarray | None]: # Modificado para retornar também threshold_image
    """
    Detecta contornos em uma imagem colorida.

    Args:
        color_image_cv (np.ndarray): A imagem carregada no formato OpenCV (BGR).
        blur_ksize_val (int): Tamanho do kernel para GaussianBlur (deve ser ímpar).

    Returns:
        tuple[list | None, np.ndarray | None]: 
            Uma tupla contendo (lista de contornos, imagem limiarizada).
            Retorna (None, None) se a imagem de entrada for None.
    """
    if color_image_cv is None:
        print("Erro: Imagem de entrada para detecção de contornos é None.")
        return None, None

    gray_image = cv2.cvtColor(color_image_cv, cv2.COLOR_BGR2GRAY)
    
    # Garante que o kernel de desfoque é ímpar e positivo
    if blur_ksize_val < 1: blur_ksize_val = 1
    if blur_ksize_val % 2 == 0: blur_ksize_val += 1
    blur_kernel_size = (blur_ksize_val, blur_ksize_val)
    
    blurred_image = cv2.GaussianBlur(gray_image, blur_kernel_size, 0)
    
    _, threshold_image = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    contours, hierarchy = cv2.findContours(threshold_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        print(f"Número de contornos detectados: {len(contours)}")
    else:
        print("Nenhum contorno detectado.")
    
    return contours, threshold_image # Retorna também a imagem limiarizada

# ... (bloco if __name__ == '__main__': pode ser atualizado para lidar com a tupla de retorno) ...
# Exemplo de atualização para o bloco de teste:
# if __name__ == '__main__':
#     test_image_path = "../test_image_badge.png"
#     try:
#         img_to_test = cv2.imread(test_image_path)
#         if img_to_test is not None:
#             # ...
#             detected_contours, thr_img = detect_contours(img_to_test) # Captura ambos os retornos
#             if detected_contours:
#                 # ... (desenha contornos) ...
#                 if thr_img is not None:
#                     cv2.imshow("Imagem Limiarizada (Teste)", thr_img) # Mostra imagem P&B
#                 cv2.waitKey(0)
#                 cv2.destroyAllWindows()
#     # ...

if __name__ == '__main__':
    # Teste rápido (requer uma imagem de exemplo)
    # Crie uma imagem 'test_image.png' ou similar na raiz do projeto ou ajuste o caminho.
    # Lembre-se que se este arquivo está em core/, "../test_image.png" refere-se à pasta MAIN/
    test_image_path = "../test_image_badge.png" # Use o caminho para sua imagem de distintivo para testar
    try:
        img_to_test = cv2.imread(test_image_path)
        if img_to_test is not None:
            print(f"Imagem de teste '{test_image_path}' carregada.")
            detected_contours = detect_contours(img_to_test)
            if detected_contours is not None and len(detected_contours) > 0:
                print(f"Total de {len(detected_contours)} contornos encontrados.")
                # Para visualizar (opcional):
                # Crie uma cópia da imagem original para desenhar os contornos
                contour_img_display = img_to_test.copy()
                # Desenha todos os contornos em cores diferentes para diferenciá-los
                for i, c in enumerate(detected_contours):
                    color = (np.random.randint(0,255), np.random.randint(0,255), np.random.randint(0,255)) # Cor aleatória
                    cv2.drawContours(contour_img_display, [c], -1, color, 1)
                cv2.imshow("Contornos Detectados (RETR_LIST)", contour_img_display)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            elif detected_contours is not None:
                print("Nenhum contorno foi detectado na imagem de teste.")
        else:
            print(f"Falha ao carregar a imagem de teste: {test_image_path}")
            print("Verifique se o caminho para a imagem de teste está correto e a imagem existe.")
    except Exception as e:
        print(f"Erro no teste de contour_detection.py: {e}")
    pass