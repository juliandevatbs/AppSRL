from openpyxl.styles import Font


def apply_font_to_worksheet(ws, font_name='Calibri', font_size=25):
    """
    Aplica una fuente y tamaño consistentes a todas las celdas de una hoja de cálculo.

    Args:
        ws (Worksheet): La hoja de cálculo a modificar.
        font_name (str): Nombre de la fuente (ej: 'Arial', 'Calibri', 'Times New Roman').
        font_size (int): Tamaño de la fuente.
    """
    font_style = Font(name=font_name, size=font_size)

    for row in ws.iter_rows():
        for cell in row:
            cell.font = font_style