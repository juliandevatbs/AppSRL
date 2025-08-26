from Utils.copy_excel_range import copy_excel_range
from Utils.pagination import check_pagination_needed, pagination

def copy_table_final(source_wb, destiny_wb, source_sheet, last_row, WB_TO_FORMAT, WB_TO_READ):
    """
    Copia la tabla final desde el source sheet al reporte
    """
    range_table = "A1:AQ37"  # Rango de la tabla final (37 filas)
    
    try:
        # Obtener las hojas de trabajo
        src_sheet = source_wb[source_sheet] if isinstance(source_sheet, str) else source_sheet
        dest_sheet = destiny_wb['Reporte']
        
        # Calcular filas necesarias (37 filas de la tabla)
        total_rows_needed = 37
        
        # Verificar si necesita paginación
        if check_pagination_needed(last_row, total_rows_needed):
            last_row = pagination(destiny_wb, WB_TO_FORMAT, WB_TO_READ, last_row, total_rows_needed)
        
        # Definir celda destino
        table_cell_dest = f"A{last_row}"
        
        print(f"Copiando tabla final a {table_cell_dest}")
        
        # Copiar la tabla final
        copy_excel_range(src_sheet, dest_sheet, range_table, table_cell_dest)
        
        # Actualizar la fila actual
        new_last_row = last_row + 37
        
        print(f"✅ Tabla final copiada exitosamente. Nueva última fila: {new_last_row}")
        
        return new_last_row
        
    except Exception as e:
        print(f"❌ Error en copy_table_final: {str(e)}")
        return last_row  # Retornar la fila original si hay error