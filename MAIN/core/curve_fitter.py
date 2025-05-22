import numpy as np

def fit_curves_to_paths(polylines: list[list[tuple[int, int]]]) -> list[list[tuple]] | None:
    """
    Converte polilinhas simplificadas em uma estrutura de caminho mais rica,
    potencialmente pronta para ajuste de curvas de Bézier.

    Versão Inicial: Apenas converte para uma sequência de 'M' e 'L'.
    Futuramente, esta função implementará o ajuste de Bézier.

    Args:
        polylines (list[list[tuple[int, int]]]): 
            Lista de caminhos (polilinhas), onde cada caminho é uma lista de tuplas (x,y).
            Tipicamente, o resultado da otimização RDP.

    Returns:
        list[list[tuple]] | None:
            Lista de caminhos no novo formato de segmento [('CMD', pt1, pt2...), ...],
            ou None se a entrada for inválida.
    """
    if not polylines:
        return None

    structured_paths = []
    for polyline in polylines:
        if not polyline or len(polyline) < 1: # Precisa de pelo menos um ponto para M
            continue

        path_segments = []
        # Ponto inicial com 'M'
        path_segments.append(('M', polyline[0]))

        # Segmentos de linha 'L' para os pontos restantes
        for point in polyline[1:]:
            path_segments.append(('L', point))
        
        # Adicionamos um 'Z' para garantir o fechamento no exportador, 
        # mas a estrutura pode ou não incluir explicitamente.
        # Para esta estrutura, vamos omitir o 'Z' aqui e deixar o exportador tratar.

        if path_segments: # Garante que temos pelo menos o 'M'
            structured_paths.append(path_segments)
            
    print(f"Curve_fitter: Convertidos {len(structured_paths)} polilinhas para estrutura de segmentos.")
    return structured_paths

# --- Exemplo de como um futuro ajuste de Bézier PODE começar (MUITO SIMPLIFICADO) ---
# NÃO USE ISTO EM PRODUÇÃO AINDA - É APENAS UMA ILUSTRAÇÃO CONCEITUAL
def fit_naive_bezier_to_paths(polylines: list[list[tuple[int, int]]]) -> list[list[tuple]] | None:
    if not polylines: return None
    structured_paths = []
    for polyline in polylines:
        if not polyline or len(polyline) < 2: continue # Precisa de pelo menos 2 pontos

        path_segments = [('M', polyline[0])]
        
        # Tenta agrupar pontos para formar Béziers cúbicas (ingênuo)
        i = 1
        while i < len(polyline):
            if i + 2 < len(polyline): # Temos P_i, P_i+1, P_i+2 para P_end, cp1, cp2
                # (P_i-1) é o start, P_i é cp1, P_i+1 é cp2, P_i+2 é end
                # O ponto final do segmento anterior é o início deste Bézier.
                # O ponto final deste Bézier será polyline[i+2]
                # Pontos de controle serão polyline[i] e polyline[i+1]
                path_segments.append(('C', polyline[i], polyline[i+1], polyline[i+2]))
                i += 3 # Avança 3 pontos
            elif i + 1 < len(polyline): # Temos P_i para P_end (cp1 = P_i-1, cp2=P_i) - Quadrática?
                 # Para simplificar, apenas adiciona como linha
                path_segments.append(('L', polyline[i]))
                i += 1
            else: # Último ponto como linha
                path_segments.append(('L', polyline[i]))
                i += 1
        
        if path_segments and len(path_segments) > 1: # Garante que temos mais que apenas 'M'
             structured_paths.append(path_segments)
    print(f"Curve_fitter (naive_bezier): Processados {len(structured_paths)} caminhos.")
    return structured_paths

if __name__ == '__main__':
    test_polylines = [
        [(10,10), (20,20), (30,10), (40,20), (50,10)],
        [(100,100), (110,110), (120,100), (130,110), (140,100), (150,110), (160,100)]
    ]
    print("--- Teste com fit_curves_to_paths (Linhas) ---")
    structured = fit_curves_to_paths(test_polylines)
    if structured:
        for i, p in enumerate(structured):
            print(f"Caminho {i}: {p}")

    print("\n--- Teste com fit_naive_bezier_to_paths (Bézier Cúbico Ingênuo) ---")
    naive_bezier = fit_naive_bezier_to_paths(test_polylines)
    if naive_bezier:
        for i, p in enumerate(naive_bezier):
            print(f"Caminho Bézier Ingênuo {i}: {p}")