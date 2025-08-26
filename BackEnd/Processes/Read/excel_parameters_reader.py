









from datetime import date, datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utils.significant_digits import significant_digits
from openpyxl import load_workbook
from Read.excel_header_reader import excel_header_reader
from Utils.get_wchem_data import get_wchem_data

# Agrega el directorio padre al path


def format_date(date_value):
    """
    Función robusta para formatear fechas que maneja:
    - Objetos datetime (los formatea directamente)
    - Strings en formato '%Y-%m-%d %H:%M' o '%m/%d/%Y %H:%M'
    - Valores None o inválidos (los devuelve sin cambios)
    """
    if date_value is None:
        return None
        
    if isinstance(date_value, datetime):
        return date_value.strftime("%m/%d/%y %H:%M")
        
    if isinstance(date_value, str):
        try:
            # Primero intenta con formato ISO (de Excel)
            try:
                date_obj = datetime.strptime(date_value, "%Y-%m-%d %H:%M")
                return date_obj.strftime("%m/%d/%y %H:%M")
            except ValueError:
                # Si falla, intenta con formato americano
                date_obj = datetime.strptime(date_value, "%m/%d/%Y %H:%M")
                return date_obj.strftime("%m/%d/%y %H:%M")
        except ValueError:
            print(f"Formato de fecha no reconocido: {date_value}")
            return date_value  # Devuelve el valor original si no se puede parsear
            
    return date_value 

def determine_qc_type(client_sample_id):
    """
    Determina el tipo de QC basado en el client_sample_id
    """
    if client_sample_id is None:
        return "N"
    
    client_sample_str = str(client_sample_id).upper().strip()
    
    # Verificar los diferentes tipos de QC
    if "METHOD BLANK" in client_sample_str or client_sample_str.startswith("MB"):
        return "MB"
    elif "LABORATORY CONTROL STANDARD" in client_sample_str or client_sample_str.startswith("LCS"):
        return "LCS"
    elif "MATRIX SPIKE DUP" in client_sample_str or client_sample_str.startswith("MSD"):
        return "MSD"
    elif "MATRIX SPIKE" in client_sample_str or client_sample_str.startswith("MS"):
        return "MS"
    elif client_sample_str.startswith("QC"):
        return "QC"
    else:
        return "N"

def excel_parameters_reader(wb_to_read, code):
    print("STARTING")
    
    # Lista de hojas a excluir
    exceptions_sheets = [
        "Generate the report", "Chain of Custody", 
        "Chain of Custody 1", "WCHEM", "Cal_Curve COLOR", 
        "Cal-Curve-Nitrites", "Cal-CurveOP", "StandarizationTNK", 
        "Cal-Curve TP", "Sterilization", "1", ""
    ]
    
    PARAMETER_MAPPING = {
        'Be': 'Beryllium',
        'Cd': 'Cadmium',
        'Mn': 'Manganese',
        'Ag': 'Silver',
        'As': 'Arsenic',
        'Ba': 'Barium',
        'Co': 'Cobalt',
        'Cr': 'Chromium',
        'Cu': 'Copper',
        'Fe': 'Iron',
        'Ni': 'Nickel',
        'Pb': 'Lead',
        'Sb': 'Antimony',
        'Se': 'Selenium',
        'Sr': 'Strontium',
        'Tl': 'Thallium',
        'V': 'Vanadium',
        'Zn': 'Zinc',
        'Al': 'Aluminum',
        'Ca': 'Calcium',
        'Mg': 'Magnesium',
        'K': 'Potassium',
        'Na': 'Sodium',
        'Hg': 'Mercury',
        'N-NO3': 'Nitrogen, Nitrate (NO3)',
        'Nitrites': 'Nitrogen, Nitrite (NO2)',
        'OP': 'Ortho Phosphate',
        'SO4': 'Sulfate',
        'TDS': 'Total Dissolved Solids/Total Filterable Residue',
        'Total Hardness': 'Hardness, Total',
        'Hardness': 'Hardness, Total',
        'TP1': 'Phosphorus LL, Total'
    }
    
    # Obtener datos del encabezado
    print("Obteniendo datos del encabezado...")
    header_data = excel_header_reader(wb_to_read)
    print(f"Datos del encabezado obtenidos: {header_data}")
    
    project_name = header_data[7]
    print(f"Nombre del proyecto: {project_name}")
    
    # Filtrar hojas relevantes
    sheets = wb_to_read.sheetnames
    print(f"Hojas encontradas: {sheets}")
    
    sheets_filter = [sheet for sheet in sheets if sheet not in exceptions_sheets]
    print(f"Hojas después del filtro: {sheets_filter}")
    
    # Estructura para almacenar los resultados
    sample_tests = []
    start_row = 21
    
    try:
        for sheet in sheets_filter:
            print(f"\nProcesando hoja: {sheet}")
            try:
                parameter_name = PARAMETER_MAPPING.get(sheet, sheet)
                wchem_data = get_wchem_data(wb_to_read, parameter_name)
            except Exception as ex:
                print(f"Error en wchem {ex}")
            print(f"Datos wchem obtenidos: {wchem_data}")
            ws_to_read = wb_to_read[sheet]
            current_row = start_row
            counter = 1
            
            while True:
                
                print(ws_to_read[f"A{current_row}"].value)
                # Verificar si hay datos en la fila
                if ws_to_read[f"A{current_row}"].value is None or ws_to_read[f"A{current_row}"].value == '' or ws_to_read[f"A{current_row}"].value == 'No Aplica' or ws_to_read[f"A{current_row}"].value == '' or ws_to_read[f"A{current_row}"].value == 'Appoved by' or ws_to_read[f"A{current_row}"].value == 'APPROVED BY' :
                    break
                
                print(f"Procesando fila {current_row}...")
                temp_list = []
                
                # Valores comunes
                sample_test_id = str(code)
                method = wchem_data[0]
                lab_sample_id = f"{code}-{counter:03d}"
                analyte_name = sheet
                result_units = "mg/L"
                detection_limit = wchem_data[1]
                reporting_limit = wchem_data[2]
                matrix_id = "GroundWater"
                qc_type = "None"
                batch_id = code
                
                # Valores por defecto (hoja común)
                client_sample_id = ws_to_read[f"B{current_row}"].value
                result = ws_to_read[f"H{current_row}"].value
                date_collected = ws_to_read[f"A{current_row}"].value
                formatted_date = format_date(str(date_collected))
                notes = ws_to_read[f"J{current_row}"].value
                dilution = 1
                
                # Procesamiento especial por tipo de hoja
                if sheet in ['Chlorides', 'Nitrites', 'OP', 'SO4', 'TP1']:
                    print("Hoja identificada como: Chlorides/Nitrites/OP/SO4/TP1")
                    result = ws_to_read[f"G{current_row}"].value
                    print(f"DEBUG - Hoja: {sheet}, Fila: {current_row}")
                    print(f"  Valor en G{current_row}: '{result}' (tipo: {type(result)})")
                    notes = ws_to_read[f"I{current_row}"].value
                    
                    if sheet in ['SO4', 'TP1']:
                        print("ROW PARA TP1")
                        
                        dilution = ws_to_read[f"C{current_row+2}"].value
                        print(current_row)
                elif sheet in ['O&G', 'TDS', 'TSS']:
                    print("Hoja identificada como: O&G/TDS/TSS")
                    result = ws_to_read[f"J{current_row}"].value
                    notes = ws_to_read[f"L{current_row}"].value
                
                elif sheet in ['TKN', 'Total Hardness']:
                    print("Hoja identificada como: TKN/Total Hardness")
                    result = ws_to_read[f"I{current_row}"].value
                    notes = ws_to_read[f"K{current_row}"].value
                
                elif sheet == 'TS':
                    print("Hoja identificada como: TS")
                    result = ws_to_read[f"K{current_row}"].value
                    notes = ws_to_read[f"M{current_row}"].value
                
                elif sheet == 'Turbidity':
                    print("Hoja identificada como: Turbidity")
                    result = ws_to_read[f"E{current_row}"].value
                    notes = ws_to_read[f"G{current_row}"].value
                
                elif sheet == 'Chl-a':
                    print("Hoja identificada como: Chl-a")
                    result = ws_to_read[f"N{current_row}"].value
                    notes = ws_to_read[f"P{current_row}"].value
                
                elif sheet == 'Total Coliform, MF':
                    print("Hoja identificada como: Total Coliform, MF")
                    result = ws_to_read[f"G{current_row}"].value
                    notes = ws_to_read[f"H{current_row}"].value
                
                elif sheet == 'Hardness, Total':
                    print("Hoja identificada como: Hardness, Total")
                    result = ws_to_read[f"E{current_row}"].value
                    notes = ws_to_read[f"I{current_row}"].value
                    
                
                elif sheet in PARAMETER_MAPPING:
                    print("Hoja identificada como: Metal")
                    result = ws_to_read[f"L{current_row}"].value
                    notes = ws_to_read[f"N{current_row}"].value
                    client_sample_id = ws_to_read[f"D{current_row}"].value
                    dilution = ws_to_read[f"H{current_row}"].value
                
                else:
                    # Valores comunes
                    sample_test_id = str(code)
                    method = wchem_data[0]
                    lab_sample_id = f"{code}-{counter:03d}"
                    analyte_name = sheet
                    result_units = "mg/L"
                    detection_limit = wchem_data[1]
                    reporting_limit = wchem_data[2]
                    matrix_id = "GroundWater"
                    qc_type = "N"
                    batch_id = code
                    
                    # Valores por defecto (hoja común)
                    client_sample_id = ws_to_read[f"B{current_row}"].value
                    result = ws_to_read[f"H{current_row}"].value
                    date_collected = ws_to_read[f"A{current_row}"].value
                    formatted_date = format_date(str(date_collected))
                    print(date_collected)
                    notes = ws_to_read[f"J{current_row}"].value
                    dilution = 1
                    
                    
                    print("DATEEEEEEEEEEEEEEEEEEEEEEEEEEE")
                    print(date_collected)
                    
                    
                
                
                if notes is None:
                    notes = '-'
                
                # NUEVA FUNCIONALIDAD: Determinar el tipo de QC basado en client_sample_id
                qc_type_determined = determine_qc_type(client_sample_id)
                print(f"QC Type determinado para '{client_sample_id}': {qc_type_determined}")
                
                # Construir la lista de datos
                temp_list.extend([
                    client_sample_id,
                    method,
                    lab_sample_id,
                    analyte_name,
                    significant_digits(result if result is not None else 1),
                    result_units,
                    detection_limit,
                    dilution,
                    reporting_limit, 
                    project_name,
                    formatted_date,# 
                    matrix_id,
                    batch_id,
                    notes,
                    qc_type_determined  # NUEVO CAMPO AGREGADO AL FINAL
                ])
                
                sample_tests.append(temp_list)
                current_row += 1
                counter += 1
            
            print(f"Hoja {sheet} procesada correctamente. Filas procesadas: {counter-1}")
    
    except Exception as ex:
        print(f"ERROR en la hoja {sheet}: {ex}")
        print(f"Tipo de error: {type(ex)}")
        import traceback
        print(traceback.format_exc())
        
    print("\nProcesamiento de todas las hojas completado")
    print(f"Total de registros obtenidos: {len(sample_tests)}")
    return sample_tests
