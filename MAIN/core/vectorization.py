# core/vectorization.py
import numpy as np

def vectorize_from_contours(contours: list) -> list[list[tuple[int, int]]] | None:
    """
    Converte os contornos detectados pelo OpenCV em uma lista de caminhos vetoriais.

    Args:
        contours (list): A lista de contornos do OpenCV.
                         Cada contorno é um np.ndarray de formato (n, 1, 2).

    Returns:
        list[list[tuple[int, int]]] | None:
            Uma lista de caminhos. Cada caminho é uma lista de tuplas de coordenadas (x, y).
            Retorna None se a entrada for None ou vazia.
    """
    if contours is None or not contours:
        return None

    vectorized_paths = []
    for contour in contours:
        # Cada 'point' em 'contour' é como [[x, y]], então precisamos extrair x e y.
        # E converter para inteiros, pois as coordenadas de pixel são inteiras.
        path = [(int(point[0][0]), int(point[0][1])) for point in contour]
        vectorized_paths.append(path)

    print(f"Vetorização concluída: {len(vectorized_paths)} caminhos criados.")
    return vectorized_paths

if __name__ == '__main__':
    # Exemplo de teste
    # Simula um contorno do OpenCV
    # Formato: (número_de_pontos, 1, 2) onde o '1' é uma dimensão extra.
    mock_contour1 = np.array([[[10, 10]], [[20, 10]], [[20, 20]], [[10, 20]]], dtype=np.int32)
    mock_contour2 = np.array([[[30, 30]], [[40, 30]], [[35, 40]]], dtype=np.int32)
    mock_contours = [mock_contour1, mock_contour2]

    paths = vectorize_from_contours(mock_contours)
    if paths:
        for i, path_data in enumerate(paths):
            print(f"Caminho {i+1}: {path_data}")

    paths_vazio = vectorize_from_contours([])
    print(f"Teste com contornos vazios: {paths_vazio}")

    paths_none = vectorize_from_contours(None)
    print(f"Teste com contornos None: {paths_none}")