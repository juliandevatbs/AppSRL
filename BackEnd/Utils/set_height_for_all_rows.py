def set_height_for_all_rows(worksheet, height, start_row = 1, end_row = None):
    """
        Establece la altura para todas las filas en una hoja Excel.

        Args:
            worksheet: Objeto worksheet de openpyxl
            height: Altura deseada en puntos
            start_row: Fila inicial (por defecto 1)
            end_row: Fila final (por defecto None, lo que significa hasta el límite de datos)
        """
    # Si end_row no se especifica, calculamos hasta dónde hay datos
    if end_row is None:
        # Obtenemos la fila máxima que contiene datos
        if worksheet.max_row > 0:
            end_row = worksheet.max_row + 100  # Añadimos 100 filas extra para futuros datos
        else:
            end_row = 1000  # Un valor razonable si la hoja está vacía

    # Establecer la altura predeterminada de la hoja
    worksheet.sheet_format.defaultRowHeight = height

    # Aplicar la altura a cada fila individualmente para asegurar consistencia
    for row_idx in range(start_row, end_row + 1):
        worksheet.row_dimensions[row_idx].height = height

    print(f"Se ha establecido una altura de {height} puntos para {end_row - start_row + 1} filas")


