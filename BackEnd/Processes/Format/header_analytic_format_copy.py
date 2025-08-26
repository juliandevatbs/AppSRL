from Utils.copy_excel_range import copy_excel_range


def header_analitic_format_copy(source_wb, destiny_wb, source_sheet_name, destination_row):
    header_range = "A1:AQ1"
    destination_cell = f"A{destination_row}"
    last_row = destination_row + 4

    try:
        # Asegurarnos de tener los objetos Worksheet correctos
        if isinstance(source_sheet_name, str):
            source_sheet = source_wb[source_sheet_name]
        else:
            source_sheet = source_sheet_name  # Asumimos que ya es un objeto Worksheet

        # Manejar la hoja destino
        if "Reporte" not in destiny_wb.sheetnames:
            destiny_ws = destiny_wb.create_sheet("Reporte")
            print("Hoja 'Reporte' creada en el archivo destino")
        else:
            destiny_ws = destiny_wb["Reporte"]

        # Llamar a la función de copia
        success = copy_excel_range(
            src_ws=source_sheet,  # Objeto Worksheet de origen
            dst_ws=destiny_ws,  # Objeto Worksheet de destino
            src_range=header_range,  # String con el rango ("A1:AQ9")
            dst_cell=destination_cell  # String con celda destino ("A1")
        )

        if not success:
            raise Exception("Error al copiar el rango")

    except Exception as e:
        print(f"ERROR en header_format_copy: {e}")
        raise

    return last_row