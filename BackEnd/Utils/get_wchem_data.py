from openpyxl import load_workbook

def get_wchem_data(wb_to_read, parameter: str) -> list:
    """
    Obtiene datos específicos de la hoja WCHEM para un parámetro dado.
    
    Args:
        wb_to_read: Workbook de openpyxl
        parameter: Nombre del parámetro a buscar en la columna A
        
    Returns:
        Lista con los datos encontrados: [método, unidades, mdl, pql, límites, recuperación, rpd]
    """
    ws_WCHEM = wb_to_read["WCHEM"]
    wchem_data = []
    counter = 3  # Comenzar en la fila 3
    
    while True:
        cell_ref = f"A{counter}"
        cell_value = ws_WCHEM[cell_ref].value
        
        # Condición de salida si llegamos a una celda vacía
        if cell_value is None:
            break
            
        if cell_value == parameter:
            # Obtener todos los valores necesarios
            method_ref = ws_WCHEM[f"C{counter}"].value
            units = ws_WCHEM[f"D{counter}"].value
            mdl = ws_WCHEM[f"E{counter}"].value
            pql = ws_WCHEM[f"F{counter}"].value
            limits = ws_WCHEM[f"G{counter}"].value
            ms_msd_recovery = ws_WCHEM[f"H{counter}"].value
            rpd = ws_WCHEM[f"I{counter}"].value
            
            return [
                method_ref,
                mdl,
                pql,
                units,
            
                limits,
                ms_msd_recovery,
                rpd
            ]
        
        counter += 1
    
    # Si llegamos aquí, no se encontró el parámetro
    print(f"Advertencia: No se encontró el parámetro '{parameter}' en la hoja WCHEM")
    return [None] * 7  # Retorna lista de None para mantener consistencia