# utils/exporter.py
import svgwrite
import os

def export_to_svg(structured_paths: list[list[tuple]], # MODIFICADO: Aceita nova estrutura
                  filepath: str,
                  image_width: int | None = None,
                  image_height: int | None = None,
                  stroke_color: str = 'black',
                  stroke_width: str = '1',
                  fill_color: str = 'none') -> bool:
    """
    Exporta os caminhos (agora com estrutura de segmentos) para um arquivo SVG.
    """
    if not structured_paths:
        print("Nenhum caminho estruturado para exportar.")
        return False

    try:
        # ... (lógica de tamanho e viewbox como antes) ...
        if image_width is not None and image_height is not None:
            dwg_size = (f"{image_width}px", f"{image_height}px")
            view_box_str = f"0 0 {image_width} {image_height}"
        else: # Fallback
            # Para calcular o fallback, precisamos extrair todos os pontos finais dos segmentos
            all_final_points = []
            for path in structured_paths:
                for seg in path:
                    if seg[0] == 'M' or seg[0] == 'L':
                        all_final_points.append(seg[1])
                    elif seg[0] == 'Q':
                        all_final_points.append(seg[2]) # Ponto final da quadrática
                    elif seg[0] == 'C':
                        all_final_points.append(seg[3]) # Ponto final da cúbica
            if not all_final_points: max_x, max_y = 100,100
            else:
                max_x = max(p[0] for p in all_final_points if p) + 10
                max_y = max(p[1] for p in all_final_points if p) + 10
            dwg_size = (f"{max_x}px", f"{max_y}px")
            view_box_str = f"0 0 {max_x} {max_y}"


        dwg = svgwrite.Drawing(filepath, size=dwg_size, profile='tiny')
        view_box_values = [float(v) for v in view_box_str.split()]
        dwg.viewbox(minx=view_box_values[0], miny=view_box_values[1], 
                    width=view_box_values[2], height=view_box_values[3])

        for path_segments in structured_paths:
            if not path_segments:
                continue

            d_cmds = []
            for segment_data in path_segments:
                cmd = segment_data[0]
                pts = segment_data[1:] # Resto são pontos ou tuplas de pontos

                if cmd == 'M' or cmd == 'L': # M x,y ou L x,y
                    d_cmds.append(f"{cmd}{pts[0][0]},{pts[0][1]}")
                elif cmd == 'Q': # Q cx,cy x,y
                    d_cmds.append(f"{cmd}{pts[0][0]},{pts[0][1]} {pts[1][0]},{pts[1][1]}")
                elif cmd == 'C': # C c1x,c1y c2x,c2y x,y
                    d_cmds.append(f"{cmd}{pts[0][0]},{pts[0][1]} {pts[1][0]},{pts[1][1]} {pts[2][0]},{pts[2][1]}")
                # O comando 'Z' será adicionado globalmente abaixo para cada path
            
            if d_cmds:
                d_cmds.append("Z") # Garante que cada path individual seja fechado
                path_element = dwg.path(
                    d=" ".join(d_cmds),
                    stroke=stroke_color,
                    stroke_width=stroke_width,
                    fill=fill_color
                )
                dwg.add(path_element)
        
        dwg.save()
        print(f"SVG (com estrutura de path) exportado com sucesso para: {filepath}")
        return True
    except Exception as e:
        print(f"Erro ao exportar SVG (com estrutura de path): {e}")
        import traceback
        print(traceback.format_exc()) # Imprime mais detalhes do erro
        return False

# ... (if __name__ == '__main__': para teste pode ser atualizado para usar a nova estrutura)