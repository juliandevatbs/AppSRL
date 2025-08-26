import re
from Utils.pagination import pagination
from Utils.write_cell import write_cell
from Format.footer_format_copy import footer_format_copy
from Format.header_format_copy import header_format_copy
from Read.excel_header_reader import excel_header_reader
from Write.write_header_data import write_header_data


def write_quality_control(controls, last_row: int, ws_to_print, wb_format, wb_to_print, wb_to_read, block_ranges: list):
    """
    Escribe los datos de controles de calidad usando rangos de bloques predefinidos
    
    Args:
        controls: Lista de controles a procesar
        last_row: Fila actual (se mantiene por compatibilidad)
        ws_to_print: Hoja de trabajo destino
        wb_format: Workbook de formato
        wb_to_print: Workbook destino
        wb_to_read: Workbook fuente
        specs_rows: Filas de especificaciones
        block_ranges: Lista de rangos [[inicio, fin], [inicio, fin], ...] donde escribir cada bloque
    """
    
    print(f"\n=== DEBUG: STARTING write_quality_control ===")
    print(f"Initial last_row: {last_row}")
    print(f"Number of controls to process: {len(controls)}")
    print(f"Block ranges received: {block_ranges}")
    
    
    
    # Verificar que tengamos rangos para todos los controles
    if len(block_ranges) != len(controls):
        print(f"WARNING: Mismatch between controls ({len(controls)}) and block ranges ({len(block_ranges)})")
        # Usar solo los rangos disponibles
        max_controls = min(len(controls), len(block_ranges))
        controls = controls[:max_controls]
        block_ranges = block_ranges[:max_controls]
    
    current_row = last_row  # Para mantener compatibilidad con el retorno
    
    for i, (control, block_range) in enumerate(zip(controls, block_ranges)):
        print(f"\n--- Processing control #{i+1} ---")
        print(f"Block range: {block_range}")
        
        
    
        
        # Usar el rango del bloque para calcular las posiciones
        block_start, block_end = block_range
        
        # Extraer datos del control
        client_sample_id = control[0]
        method = control[1]
        lab_sample_id = control[2]
        analyte_name = control[3]
        result = control[4]
        units = control[5]
        mdl = control[6]
        df = control[7]
        pql = control[8]
        project_name = control[9]
        prep = control[10]
        analyzed = control[11]
        matrix_id = control[12]
        qc_type = control[13]
        batch_id = control[14]
        notes = control[15]
        by = control[16]
        analyst = control[17]
        rec = control[18]
        rpd = control[19]
        spk = control[20]
        limits = control[21]
        date_collected = control[22]
        
        # Normalizar tipo de control
        normalized_control_type = re.sub(r'[()]', '', str(qc_type)).upper() if qc_type is not None else ""
        control_code = control[13].upper() if len(control) > 13 and control[13] is not None else ""
        
        # Calcular posiciones relativas dentro del bloque (8 filas por bloque)
        # Estas posiciones deben coincidir exactamente con el formato copiado
        header_row_1 = block_start + 3  # Fila 3 del bloque (índice 2)
        header_row_2 = block_start + 4  # Fila 4 del bloque (índice 3)
        results_row = block_start + 7   # Fila 7 del bloque (índice 6)
        
        print(f"Block start: {block_start}, Block end: {block_end}")
        print(f"Header row 1: {header_row_1}")
        print(f"Header row 2: {header_row_2}")
        print(f"Results row: {results_row}")
        
        # Escribir datos según el tipo de control
        if re.search(r'\bLCS\b|\bLCSD\b', normalized_control_type) or control_code in ['LCS', 'LCSD']:
            print("Processing LCS/LCSD control")
            
            # Primera línea de encabezado
            write_cell(ws_to_print, f"L{header_row_1}", client_sample_id)
            write_cell(ws_to_print, f"AD{header_row_1}", analyzed)
            write_cell(ws_to_print, f"AI{header_row_1}", matrix_id)
            
            # Segunda línea de encabezado
            write_cell(ws_to_print, f"L{header_row_2}", lab_sample_id)
            
            # Línea de resultados
            write_cell(ws_to_print, f"B{results_row}", analyte_name)
            write_cell(ws_to_print, f"K{results_row}", result)
            write_cell(ws_to_print, f"T{results_row}", units)
            write_cell(ws_to_print, f"V{results_row}", df)
            write_cell(ws_to_print, f"Y{results_row}", mdl)
            write_cell(ws_to_print, f"AB{results_row}", pql)
            write_cell(ws_to_print, f"AD{results_row}", by)
            write_cell(ws_to_print, f"AH{results_row}", batch_id)
            write_cell(ws_to_print, f"Q{results_row}", spk)
            write_cell(ws_to_print, f"AC{results_row}", rec)
            write_cell(ws_to_print, f"AK{results_row}", limits)
            
        elif (re.search(r'\bMB\b|\bMETHOD BLANK\b', normalized_control_type) or 
              control_code in ['MB']):
            print("Processing MB control")
            
            # Primera línea de encabezado
            write_cell(ws_to_print, f"L{header_row_1}", client_sample_id)
            write_cell(ws_to_print, f"AI{header_row_1}", matrix_id)
            write_cell(ws_to_print, f"X{header_row_1}", date_collected)
            write_cell(ws_to_print, f"AD{header_row_1}", analyzed)
            
            # Segunda línea de encabezado
            write_cell(ws_to_print, f"L{header_row_2}", lab_sample_id)
            write_cell(ws_to_print, f"X{header_row_2}", prep)
            
            # Línea de resultados
            write_cell(ws_to_print, f"B{results_row}", analyte_name)
            write_cell(ws_to_print, f"K{results_row}", result)
            write_cell(ws_to_print, f"T{results_row}", units)
            write_cell(ws_to_print, f"V{results_row}", df)
            write_cell(ws_to_print, f"Y{results_row}", mdl)
            write_cell(ws_to_print, f"AB{results_row}", pql)
            write_cell(ws_to_print, f"AC{results_row}", by)
            write_cell(ws_to_print, f"AI{results_row}", batch_id)
            write_cell(ws_to_print, f"AK{results_row}", notes)
                
        elif control_code in ["MS"]:
            print("Processing MS control")
            
            # Primera línea de encabezado
            write_cell(ws_to_print, f"L{header_row_1}", client_sample_id)
            write_cell(ws_to_print, f"AD{header_row_1}", analyzed)
            write_cell(ws_to_print, f"AI{header_row_1}", matrix_id)
            write_cell(ws_to_print, f"X{header_row_1}", date_collected)
            
            # Segunda línea de encabezado
            write_cell(ws_to_print, f"L{header_row_2}", lab_sample_id)
            write_cell(ws_to_print, f"X{header_row_2}", prep)
            
            # Línea de resultados
            write_cell(ws_to_print, f"B{results_row}", analyte_name)
            write_cell(ws_to_print, f"K{results_row}", result)
            write_cell(ws_to_print, f"T{results_row}", units)
            write_cell(ws_to_print, f"V{results_row}", df)
            write_cell(ws_to_print, f"Y{results_row}", mdl)
            write_cell(ws_to_print, f"AB{results_row}", pql)
            write_cell(ws_to_print, f"AC{results_row}", rec)
            write_cell(ws_to_print, f"AD{results_row}", '-')
            write_cell(ws_to_print, f"AE{results_row}", by)
            write_cell(ws_to_print, f"AI{results_row}", batch_id)
            write_cell(ws_to_print, f"AN{results_row}", notes)
            write_cell(ws_to_print, f"Q{results_row}", spk)
            write_cell(ws_to_print, f"AC{results_row}", rec)  # ⚠️ Nota: Esto sobrescribe AC - revisar si es correcto
            write_cell(ws_to_print, f"AK{results_row}", limits)
        
        elif control_code in ["MSD"]:
            print("Processing MSD control")
            
            # Primera línea de encabezado
            write_cell(ws_to_print, f"L{header_row_1}", client_sample_id)
            write_cell(ws_to_print, f"AD{header_row_1}", analyzed)
            write_cell(ws_to_print, f"AI{header_row_1}", matrix_id)
            write_cell(ws_to_print, f"X{header_row_1}", date_collected)
            
            # Segunda línea de encabezado
            write_cell(ws_to_print, f"L{header_row_2}", lab_sample_id)
            write_cell(ws_to_print, f"X{header_row_2}", prep)
            
            # Línea de resultados
            write_cell(ws_to_print, f"B{results_row}", analyte_name)
            write_cell(ws_to_print, f"K{results_row}", result)
            write_cell(ws_to_print, f"T{results_row}", units)
            write_cell(ws_to_print, f"V{results_row}", df)
            write_cell(ws_to_print, f"Y{results_row}", mdl)
            write_cell(ws_to_print, f"AB{results_row}", pql)
            write_cell(ws_to_print, f"AC{results_row}", rpd)
            write_cell(ws_to_print, f"AD{results_row}", rec)
            write_cell(ws_to_print, f"AE{results_row}", '-')
            write_cell(ws_to_print, f"AG{results_row}", by)
            write_cell(ws_to_print, f"AI{results_row}", batch_id)
            write_cell(ws_to_print, f"AN{results_row}", notes)
            write_cell(ws_to_print, f"Q{results_row}", spk)
            write_cell(ws_to_print, f"AK{results_row}", limits)
            
        elif re.search(r'\bQC\b', normalized_control_type) or control_code == 'QC':
            print("Processing QC control")
            
            # Primera línea de encabezado
            write_cell(ws_to_print, f"L{header_row_1}", client_sample_id)
            write_cell(ws_to_print, f"AD{header_row_1}", analyzed)
            write_cell(ws_to_print, f"AI{header_row_1}", matrix_id)
            
            # Segunda línea de encabezado
            write_cell(ws_to_print, f"L{header_row_2}", lab_sample_id)
            write_cell(ws_to_print, f"X{header_row_2}", prep)
            
            # Línea de resultados
            write_cell(ws_to_print, f"B{results_row}", analyte_name)
            write_cell(ws_to_print, f"K{results_row}", result)
            write_cell(ws_to_print, f"T{results_row}", units)
            write_cell(ws_to_print, f"V{results_row}", df)
            write_cell(ws_to_print, f"Y{results_row}", mdl)
            write_cell(ws_to_print, f"AB{results_row}", pql)
            write_cell(ws_to_print, f"AC{results_row}", by)
            write_cell(ws_to_print, f"AI{results_row}", batch_id)
            write_cell(ws_to_print, f"AK{results_row}", notes)
            
        elif re.search(r'\bDUP\b|\bDUPLICATE\b', normalized_control_type) or control_code == 'DUP':
            print("Processing DUP control")
            
            # Primera línea de encabezado
            write_cell(ws_to_print, f"L{header_row_1}", client_sample_id)
            write_cell(ws_to_print, f"AD{header_row_1}", analyzed)
            write_cell(ws_to_print, f"AI{header_row_1}", matrix_id)
            write_cell(ws_to_print, f"X{header_row_1}", date_collected)
            
            # Segunda línea de encabezado
            write_cell(ws_to_print, f"L{header_row_2}", lab_sample_id)
            write_cell(ws_to_print, f"X{header_row_2}", prep)
            
            # Línea de resultados
            write_cell(ws_to_print, f"B{results_row}", analyte_name)
            write_cell(ws_to_print, f"K{results_row}", result)
            write_cell(ws_to_print, f"T{results_row}", units)
            write_cell(ws_to_print, f"V{results_row}", df)
            write_cell(ws_to_print, f"Y{results_row}", mdl)
            write_cell(ws_to_print, f"AB{results_row}", pql)
            write_cell(ws_to_print, f"AC{results_row}", by)
            write_cell(ws_to_print, f"AI{results_row}", batch_id)
            write_cell(ws_to_print, f"AK{results_row}", notes)
            write_cell(ws_to_print, f"AN{results_row}", rpd)
            
        else:
            print(f"Unknown control type: {control_code} / {normalized_control_type}")
            # Formato genérico para controles no reconocidos
            write_cell(ws_to_print, f"L{header_row_1}", client_sample_id)
            write_cell(ws_to_print, f"AD{header_row_1}", analyzed)
            write_cell(ws_to_print, f"AI{header_row_1}", matrix_id)
            write_cell(ws_to_print, f"L{header_row_2}", lab_sample_id)
            write_cell(ws_to_print, f"B{results_row}", analyte_name)
            write_cell(ws_to_print, f"K{results_row}", result)
            write_cell(ws_to_print, f"T{results_row}", units)
        
        print(f"Control #{i+1} written to block range [{block_start}, {block_end}]")
        
        # Actualizar current_row para mantener compatibilidad
        current_row = max(current_row, block_end + 1)
    
    print(f"\n=== DEBUG: FINISHED write_quality_control ===")
    print(f"Final current_row: {current_row}")
    return current_row


