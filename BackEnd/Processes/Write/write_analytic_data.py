

from BackEnd.Utils import write_cell
from BackEnd.Utils.pagination import check_pagination_needed, pagination


def write_analitic_data(wb_to_read, ws_to_write, init_cell, dats, start_row, WB_TO_FORMAT=None, WB_TO_READ=None):
    """
    Escribe datos analíticos en una hoja de Excel con el formato específico y paginación automática.
    
    Parameters:
    - wb_to_read: Workbook de Excel de donde se leen datos adicionales
    - ws_to_write: Workbook donde se escribirán los datos
    - init_cell: Celda inicial (no se usa directamente en esta versión)
    - dats: Diccionario donde cada clave es un sample_id y su valor es una lista de parámetros
    - start_row: Fila inicial donde comenzar a escribir
    - WB_TO_FORMAT: Workbook de formato (para paginación)
    - WB_TO_READ: Workbook de lectura (para paginación)
    """
    # Verificamos que dats tenga contenido
    if not dats:
        print("Error: No hay datos para procesar")
        return False
    
    # Obtenemos la hoja de destino
    ws_to_write_sheet = ws_to_write["Reporte"]
    
    try:
        current_row = start_row
        
   
        
        # Procesamos cada muestra con sus parámetros
        for sample_id, parameters in dats.items():
            
            
         
            
            
            # Verificamos que la muestra tenga parámetros
            if not parameters:
                #print(f"Advertencia: No hay parámetros para la muestra {sample_id}")
                continue
            
            # Calculamos cuántas filas necesitamos para esta muestra completa
            # Header: 2 filas + espacios: 3 filas + parámetros: len(parameters) filas + espacio final: 1 fila
            total_rows_needed = 4 + len(parameters)
            
            
            
            # Verificamos si toda la muestra cabe en la página actual
            if WB_TO_FORMAT and WB_TO_READ and check_pagination_needed(current_row, total_rows_needed):
                print(f"Sample {sample_id} needs {total_rows_needed} rows, triggering pagination")
                current_row = pagination(ws_to_write, WB_TO_FORMAT, WB_TO_READ, current_row, total_rows_needed)
            
            
            
            #print("CURRENT ROW ARROJADA POR PAGINATION")
            #print(current_row)
            
            
            
            
            first_param = parameters[0]
            # Datos del encabezado (header)
            client_sample_id = first_param[1]
            lab_sample_id = first_param[3]
            date_collected = first_param[11]
            collected_by = first_param[16]
            by = first_param[17]
            matrix_id = first_param[12]
            
            # Escribimos el encabezado de la muestra
            first_line_block = current_row
            second_line_block = first_line_block + 1
            
            #print(first_param)
            #print("FIRST LINE BLOCK")
            #print(first_line_block)
            
            #print("SECOND LINE BLOCK")
            #print(second_line_block)
            
           
            
            
            write_cell(ws_to_write_sheet, f"L{first_line_block}", client_sample_id)
            write_cell(ws_to_write_sheet, f"Z{first_line_block}", date_collected)
            write_cell(ws_to_write_sheet, f"AI{first_line_block}", matrix_id)
            
            write_cell(ws_to_write_sheet, f"L{second_line_block}", lab_sample_id)
            write_cell(ws_to_write_sheet, f"Z{second_line_block}", collected_by)
            
            # La primera fila de datos de parámetros comienza después del encabezado
            param_row = second_line_block + 3
            
            #print("FILA DONDE ESCRIBE LOS RESULTADOS")
            #print(param_row)
            
            
            # Escribimos todos los parámetros de esta muestra
            for i, param in enumerate(parameters):
                #print(f"Writing parameter {i+1}/{len(parameters)} for sample {sample_id} at row {param_row}")
                
                # Datos del parámetro
                analyte_name = param[4]
                results = param[5]
                units = param[6]
                df = param[8]
                mdl = param[7]
                pql = param[9]
                method_analyzed = param[2]
                date_r = param[11]
                batch_id = param[14]
                notes = param[15]
                
                # Escribir los datos del parámetro
                write_cell(ws_to_write_sheet, f"B{param_row}", analyte_name)
                write_cell(ws_to_write_sheet, f"K{param_row}", results)
                write_cell(ws_to_write_sheet, f"T{param_row}", units)
                write_cell(ws_to_write_sheet, f"V{param_row}", df)
                write_cell(ws_to_write_sheet, f"Y{param_row}", mdl)
                write_cell(ws_to_write_sheet, f"AB{param_row}", pql)
                write_cell(ws_to_write_sheet, f"AC{param_row}", method_analyzed)
                write_cell(ws_to_write_sheet, f"AD{param_row}", date_collected)
                write_cell(ws_to_write_sheet, f"AH{param_row}", by)
                write_cell(ws_to_write_sheet, f"AI{param_row}", batch_id)
                write_cell(ws_to_write_sheet, f"AL{param_row}", notes)
                
                # Avanzamos a la siguiente fila para el próximo parámetro
                param_row += 1
            
            # La próxima muestra comienza después de todos los parámetros de la muestra actual
            # Añadimos un espacio adicional entre muestras
            current_row = param_row
        
            #print(f"TERMINO EL PRIMER ANALITO AHORA EMPIEZA OTRO ROW -> {current_row}")
            
            
        return current_row
        
    except Exception as ex:
        print(f"ERROR al escribir datos analíticos: {ex}")
        return False

