# core/node_optimization.py
import cv2
import numpy as np

def optimize_paths(vectorized_paths: list[list[tuple[int, int]]],
                   epsilon_factor: float = 0.005) -> list[list[tuple[int, int]]] | None:
    """
    Otimiza (simplifica) uma lista de caminhos vetoriais usando o algoritmo Ramer-Douglas-Peucker.

    Args:
        vectorized_paths (list[list[tuple[int, int]]]):
            Lista de caminhos, onde cada caminho é uma lista de tuplas de coordenadas (x, y).
        epsilon_factor (float): Fator para calcular o parâmetro epsilon para cv2.approxPolyDP.
                                O epsilon real será epsilon_factor * perímetro_do_contorno.
                                Um valor menor resulta em menos simplificação (mais pontos).
                                Um valor maior resulta em mais simplificação (menos pontos).
                                Valores típicos podem variar (ex: 0.001 a 0.05).

    Returns:
        list[list[tuple[int, int]]] | None:
            Lista de caminhos otimizados. Cada caminho é uma lista de tuplas (x,y).
            Retorna None se a entrada for None ou vazia.
    """
    if not vectorized_paths:
        print("Nenhum caminho vetorizado para otimizar.")
        return None

    optimized_paths_list = []
    total_original_points = 0
    total_optimized_points = 0

    for path in vectorized_paths:
        if not path or len(path) < 3: # Precisa de pelo menos 3 pontos para simplificação significativa
            optimized_paths_list.append(path) # Mantém caminhos curtos como estão
            total_original_points += len(path)
            total_optimized_points += len(path)
            continue

        # Converter o caminho para o formato NumPy (N, 1, 2) exigido por cv2.approxPolyDP
        np_path = np.array(path, dtype=np.int32).reshape((-1, 1, 2))
        total_original_points += len(np_path)

        # Calcular o perímetro do contorno para tornar o epsilon relativo ao tamanho do contorno
        perimeter = cv2.arcLength(np_path, closed=True)
        epsilon = epsilon_factor * perimeter

        print(f"  Path (primeiros 5 pts): {path[:5]}, Perímetro: {perimeter:.2f}, Epsilon_factor: {epsilon_factor:.5f}, Epsilon Calculado: {epsilon:.2f}, Pontos Originais: {len(np_path)}")
        # Aplicar o algoritmo Ramer-Douglas-Peucker
        # O parâmetro 'closed=True' indica que o contorno é fechado.
        simplified_np_path = cv2.approxPolyDP(np_path, epsilon, closed=True)

        # Converter o caminho simplificado de volta para lista de tuplas (x,y)
        simplified_path = [(int(point[0][0]), int(point[0][1])) for point in simplified_np_path]
        optimized_paths_list.append(simplified_path)
        total_optimized_points += len(simplified_path)

    reduction_percentage = 0
    if total_original_points > 0:
        reduction_percentage = ((total_original_points - total_optimized_points) / total_original_points) * 100

    print(f"Otimização de caminhos concluída.")
    print(f"  Pontos originais: {total_original_points}")
    print(f"  Pontos otimizados: {total_optimized_points}")
    print(f"  Redução: {reduction_percentage:.2f}%")

    return optimized_paths_list

if __name__ == '__main__':
    # Exemplo de teste
    mock_paths = [
        # Um caminho "quadrado" com pontos redundantes
        [(10, 10), (50, 10), (90, 10), (100, 10), (100, 50), (100, 90), (100, 100),
         (50, 100), (10, 100), (10, 50), (10,10)],
        # Um caminho mais simples
        [(120, 50), (150, 20), (180, 50), (150, 80), (120, 50)],
        # Um caminho muito curto
        [(200,200), (201,201)]
    ]

    print("Testando com epsilon_factor = 0.01 (menos simplificação):")
    optimized = optimize_paths(mock_paths, epsilon_factor=0.01)
    if optimized:
        for i, p_data in enumerate(optimized):
            print(f"  Caminho otimizado {i+1} ({len(p_data)} pontos): {p_data}")

    print("\nTestando com epsilon_factor = 0.03 (mais simplificação):")
    optimized_more = optimize_paths(mock_paths, epsilon_factor=0.03)
    if optimized_more:
        for i, p_data in enumerate(optimized_more):
            print(f"  Caminho otimizado {i+1} ({len(p_data)} pontos): {p_data}")

    # Teste com dados vazios ou None
    print(f"\nTeste com lista vazia: {optimize_paths([])}")
    print(f"Teste com None: {optimize_paths(None)}")
    print(f"Teste com caminho vazio interno: {optimize_paths([[]])}")