# utils/image_loader.py
import cv2
import numpy as np

def load_image(file_path: str) -> np.ndarray | None:
    """
    Carrega uma imagem de um arquivo usando OpenCV.

    Args:
        file_path (str): O caminho para o arquivo de imagem.

    Returns:
        np.ndarray | None: A imagem carregada como um array NumPy (formato BGR)
                           ou None se o carregamento falhar.
    """
    try:
        image = cv2.imread(file_path)
        if image is None:
            print(f"Erro: Não foi possível carregar a imagem de '{file_path}'. Verifique o caminho e o formato do arquivo.")
            return None
        return image
    except Exception as e:
        print(f"Erro ao tentar ler o arquivo de imagem '{file_path}': {e}")
        return None

if __name__ == '__main__':
    # Pequeno teste (opcional, execute python utils/image_loader.py com uma imagem de teste)
    # Crie uma imagem de teste chamada 'test_image.png' ou use uma existente
    # test_img_path = "caminho/para/sua/imagem_de_teste.png"
    # if test_img_path != "caminho/para/sua/imagem_de_teste.png":
    #     loaded_image = load_image(test_img_path)
    #     if loaded_image is not None:
    #         print(f"Imagem '{test_img_path}' carregada com sucesso. Dimensões: {loaded_image.shape}")
    #         cv2.imshow("Imagem de Teste", loaded_image)
    #         cv2.waitKey(0)
    #         cv2.destroyAllWindows()
    #     else:
    #         print(f"Falha ao carregar a imagem de teste: {test_img_path}")
    # else:
    #     print("Para testar 'image_loader.py' diretamente, defina 'test_img_path' com um caminho de imagem válido.")
    pass