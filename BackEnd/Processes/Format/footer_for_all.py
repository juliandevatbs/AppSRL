from Utils.copy_excel_range import copy_excel_range


def footer_for_all(source_wb, destiny_wb, source_sheet_name, last_row_to):
    
    footer_range = "A1:AQ2"
    destination_cell = f"A{last_row_to + 1}"  # Colocamos el footer justo después del último renglón de datos
    last_row = last_row_to + 2
    
    
    try:
        
         # Asegurarnos de tener los objetos Worksheet correctos
        if isinstance(source_sheet_name, str):
            source_sheet = source_wb[source_sheet_name]
        else:
            source_sheet = source_sheet_name 
        
        # Manejar la hoja destino
        if "Reporte" not in destiny_wb.sheetnames:
            destiny_ws = destiny_wb.create_sheet("Reporte")
            #print("Hoja 'Reporte' creada en el archivo destino")
        else:
            destiny_ws = destiny_wb["Reporte"]
        
        # Llamar a la función de copia
        success = copy_excel_range(
            src_ws=source_sheet,  # Objeto Worksheet de origen
            dst_ws=destiny_ws,  # Objeto Worksheet de destino
            src_range=footer_range,  # String con el rango ("A1:AQ4")
            dst_cell=destination_cell  # String con celda destino (ej. "A101")
        )
        
        if not success:
            raise Exception("Error al copiar el rango del footer")
        
        
        
    except Exception as ex:
        
        print(f"Error formatting format for all {ex}")
    