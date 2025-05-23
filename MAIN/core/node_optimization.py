import numpy as np
from typing import List # Necessário para List[complex] em Python mais antigo

# Sua implementação do RDP (adaptada para usar List em vez de np.ndarray para entrada/saída de pontos)
def rdp_custom(points_complex: List[complex], epsilon: float) -> List[complex]:
    if not points_complex or len(points_complex) < 3:
        return points_complex

    # Função interna para distância perpendicular
    def perpendicular_distance(pt: complex, line_start: complex, line_end: complex) -> float:
        if line_start == line_end:
            return abs(pt - line_start)
        
        # Usando a fórmula baseada em produto vetorial (equivalente à sua)
        # |Im( (line_end - line_start)^* * (pt - line_start) )| / |line_end - line_start|
        # onde ^* é o conjugado.
        # np.cross para vetores 2D (x1,y1), (x2,y2) é x1*y2 - x2*y1
        # Se (line_end - line_start) = dx + idy
        # Se (pt - line_start) = px + ipy
        # O numerador é |dx*py - dy*px|
        line_vec = line_end - line_start
        pt_vec = pt - line_start
        
        # Numerador: abs(line_vec.real * pt_vec.imag - line_vec.imag * pt_vec.real)
        # Denominador: abs(line_vec)
        numerator = abs(line_vec.real * pt_vec.imag - line_vec.imag * pt_vec.real)
        denominator = abs(line_vec)
        
        if denominator == 0: # line_start == line_end
             return abs(pt - line_start)
        return numerator / denominator

    max_dist = 0.0
    index = 0 # O RDP original usa o índice 1 como primeiro candidato válido se len > 2
              # Mas o loop range(1, len(points_complex)-1) cuida disso.
              # index=0 é um placeholder se nenhum ponto for encontrado com dist > max_dist.

    # Encontra o ponto mais distante do segmento entre o primeiro e o último ponto
    for i in range(1, len(points_complex) - 1):
        dist = perpendicular_distance(points_complex[i], points_complex[0], points_complex[-1])
        if dist > max_dist:
            index = i
            max_dist = dist

    # Se a distância máxima for maior que epsilon, simplifica recursivamente
    if max_dist > epsilon:
        # Chamada recursiva para a parte esquerda e direita do ponto de divisão
        left_simplified = rdp_custom(points_complex[:index + 1], epsilon)
        right_simplified = rdp_custom(points_complex[index:], epsilon)
        
        # Concatena os resultados, removendo o ponto de junção duplicado
        return left_simplified[:-1] + right_simplified
    else:
        # Se não, todos os pontos intermediários são removidos
        return [points_complex[0], points_complex[-1]]

def _convert_to_complex_points(polyline: list[tuple[int, int]]) -> List[complex]:
    """Converte [(x,y),...] para [complex(x,y),...]."""
    return [complex(p[0], p[1]) for p in polyline]

def _convert_from_complex_points(complex_polyline: List[complex]) -> list[tuple[int, int]]:
    """Converte [complex(x,y),...] para [(x,y),...]."""
    return [(int(round(p.real)), int(round(p.imag))) for p in complex_polyline]

def apply_custom_rdp_simplification(
        polylines_input: list[list[tuple[int, int]]], 
        epsilon: float = 1.0  # Tolerância para o RDP
    ) -> list[list[tuple[int, int]]] | None:
    """
    Aplica a simplificação RDP customizada a uma lista de polilinhas.
    """
    if not polylines_input:
        return None

    simplified_polylines_list = []
    total_points_before = 0
    total_points_after = 0

    for polyline in polylines_input:
        if not polyline or len(polyline) < 2: # RDP precisa de pelo menos 2, idealmente 3
            simplified_polylines_list.append(polyline) # Mantém polilinhas muito curtas
            total_points_before += len(polyline)
            total_points_after += len(polyline)
            continue

        total_points_before += len(polyline)
        complex_pts = _convert_to_complex_points(polyline)
        simplified_complex = rdp_custom(complex_pts, epsilon)
        simplified_output_polyline = _convert_from_complex_points(simplified_complex)
        
        # Garante que a polilinha simplificada não seja vazia se a original não era
        if not simplified_output_polyline and polyline:
            simplified_polylines_list.append([polyline[0]]) # Mantém pelo menos um ponto
        elif simplified_output_polyline:
            simplified_polylines_list.append(simplified_output_polyline)
        
        total_points_after += len(simplified_output_polyline)

    print(f"Simplificação RDP Customizada (epsilon={epsilon}): Processadas {len(polylines_input)} polilinhas.")
    if total_points_before > 0:
        reduction = ((total_points_before - total_points_after) / total_points_before) * 100 if total_points_before > 0 else 0
        print(f"  Pontos antes: {total_points_before}, Pontos depois: {total_points_after} (Redução: {reduction:.2f}%)")
    
    return simplified_polylines_list

# Para manter a compatibilidade se algum código ainda chama optimize_paths,
# ou simplesmente para ter um nome de função consistente.
optimize_paths = apply_custom_rdp_simplification

if __name__ == '__main__':
    # Exemplo de teste para rdp_custom
    test_line = [complex(0,0), complex(1,0.1), complex(2, -0.1), complex(3,0.2), complex(4,0), complex(5,0)]
    simplified_line = rdp_custom(test_line, epsilon=0.15)
    print(f"Linha original ({len(test_line)} pts): {test_line}")
    print(f"Linha simplificada ({len(simplified_line)} pts): {simplified_line}")

    test_poly_tuples = [(0,0),(1,1),(2,2),(2,3),(3,3),(4,4),(5,5),(6,5.1),(7,4.9),(8,5)]
    simplified_poly_tuples = apply_custom_rdp_simplification([test_poly_tuples], epsilon=0.2)
    print(f"\nPolilinha original: {test_poly_tuples}")
    if simplified_poly_tuples:
        print(f"Polilinha simplificada: {simplified_poly_tuples[0]}")