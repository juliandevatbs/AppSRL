

from BackEnd.Utils.copy_excel_range import copy_excel_range


def lab_format_copy(source_wb, destiny_wb, source_sheet, last_row, times_to_print):
    """
    Versión corregida que maneja correctamente los valores de retorno
    """
    lab_header_range = "A1:AQ2"
    lab_block_range = "A3:AQ3"

    try:
        # Obtener las hojas correctamente
        src_sheet = source_wb[source_sheet] if isinstance(source_sheet, str) else source_sheet
        dest_sheet = destiny_wb['Reporte']  # O usa  si necesitas hoja específica

        # 1. Copiar cabecera
        header_dest = f"A{last_row + 1}"
        #print(f"Copiando cabecera en {header_dest}")

        # Modificado para manejar diferentes formas de retorno
        result = copy_excel_range(
            src_sheet,
            dest_sheet,
            lab_header_range,
            header_dest
        )

        # Manejo flexible del retorno
        if isinstance(result, tuple):
            success, message = result
        else:
            success = result
            message = "Operación completada"

        if not success:
            raise Exception(message)

        # 2. Copiar bloques
        start_row = last_row + 2

        for i in range(times_to_print):
            block_dest = f"A{start_row + i}"
            #f"Copiando formato {i}/{times_to_print} en {block_dest}")

            result = copy_excel_range(
                src_sheet,
                dest_sheet,
                lab_block_range,
                block_dest
            )

            if isinstance(result, tuple):
                success, message = result
            else:
                success = result

            if not success:
                raise Exception(message or "Error al copiar bloque")

        #"¡Formatos copiados exitosamente!")
        return start_row + 21

    except Exception as e:
        print(f"Error en lab_format_copy: {str(e)}")
        return False