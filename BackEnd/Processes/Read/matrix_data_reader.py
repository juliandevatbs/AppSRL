from os.path import samefile
import re
from difflib import get_close_matches
from openpyxl.utils import get_column_letter


def normalize_sheet_name(name):
    """Normaliza el nombre de la hoja eliminando espacios extra y convirtiendo a minúsculas"""
    if not name:
        return ""
    return re.sub(r'\s+', ' ', str(name).strip()).lower()


def find_best_matching_sheet(search_name, available_sheets):
    """
    Encuentra la mejor coincidencia para un nombre de hoja utilizando coincidencia aproximada
    """
    if not search_name:
        return None
    
    # Normalizar nombres para comparación
    normalized_search = normalize_sheet_name(search_name)
    normalized_sheets = {normalize_sheet_name(s): s for s in available_sheets}
    
    # Primero buscar coincidencia exacta
    if normalized_search in normalized_sheets:
        return normalized_sheets[normalized_search]
    
    # Buscar coincidencia parcial (comenzando con)
    partial_matches = [s for s in normalized_sheets if s.startswith(normalized_search) or normalized_search.startswith(s)]
    if partial_matches:
        return normalized_sheets[partial_matches[0]]
    
    # Usar coincidencia difusa como último recurso
    matches = get_close_matches(normalized_search, normalized_sheets.keys(), n=1, cutoff=0.6)
    if matches:
        return normalized_sheets[matches[0]]
    
    return None


def is_matching_sample(target_id, cell_value):
    """Verifica si el ID de muestra coincide, con tolerancia para variantes y espacios"""
    if not target_id or not cell_value:
        return False
        
    # Convertir a string y limpiar espacios
    target_id = str(target_id).strip()
    current_id = str(cell_value).strip()
    
    # Coincidencia exacta después de normalizar
    if target_id.lower() == current_id.lower():
        return True
    
    # Crear patrón regex para coincidir con ID base y variantes permitidas
    pattern = re.compile(rf'^{re.escape(target_id)}(?:\s+[A-Z]+)?$', re.IGNORECASE)
    
    # Permitir variantes como "SW-1" vs "SW-01"
    numeric_pattern = re.compile(r'(\D+)[-_]?(\d+)(.*)$')
    target_match = numeric_pattern.match(target_id)
    current_match = numeric_pattern.match(current_id)
    
    if target_match and current_match:
        # Comparar prefijos y sufijos
        if target_match.group(1).lower() == current_match.group(1).lower() and target_match.group(3).lower() == current_match.group(3).lower():
            # Comparar números sin ceros a la izquierda
            if int(target_match.group(2)) == int(current_match.group(2)):
                return True
    
    return bool(pattern.fullmatch(current_id))


def find_data_range(sheet, start_row=21, id_column="B"):
    """
    Determina el rango de datos en una hoja, identificando automáticamente 
    dónde comienzan y terminan los datos relevantes
    """
    # Encontrar la primera fila vacía después de start_row
    row = start_row
    last_data_row = None
    
    while True:
        cell_value = sheet[f"{id_column}{row}"].value
        if cell_value is not None:
            last_data_row = row
        elif last_data_row and row > last_data_row + 10:  # Terminar búsqueda si hay 10 filas vacías consecutivas
            break
        
        row += 1
        if row > 1000:  # Límite de seguridad
            break
    
    return start_row, last_data_row if last_data_row else start_row


def get_metadata_values(sheet):
    """
    Busca y extrae metadatos relevantes de la hoja (DF, MDL, PQL)
    con manejo mejorado de errores
    """
    # Posibles ubicaciones para metadatos
    metadata_locations = {
        "df": ["N19", "N18", "O19", "M19"],
        "mdl": ["N20", "N19", "O20", "M20"],
        "pql": ["N21", "N20", "O21", "M21"]
    }
    
    results = {}
    
    # Buscar en múltiples ubicaciones para cada valor
    for key, locations in metadata_locations.items():
        for loc in locations:
            try:
                value = sheet[loc].value
                if value is not None:
                    results[key] = value
                    break
            except:
                continue
        
        # Si no se encuentra, usar valor predeterminado
        if key not in results:
            results[key] = None
    
    return results.get("df"), results.get("mdl"), results.get("pql")


def find_value_in_row(sheet, row, possible_columns, default=None):
    """
    Busca un valor en una fila probando múltiples columnas posibles
    """
    for col in possible_columns:
        try:
            value = sheet[f"{col}{row}"].value
            if value is not None:
                return value
        except:
            continue
    return default


def matrix_data_reader(wb_to_read, chain_data):
    """
    Versión mejorada para leer datos de matrices con mejor manejo de errores,
    coincidencia flexible de nombres y estructura de datos más robusta
    """
    # Matrix name mappings como diccionario para búsqueda más rápida y bidireccional
    matrix_aliases = {
        "Be": "Beryllium", "Cd": "Cadmium", "Mn": "Manganese", "Ag": "Silver",
        "As": "Arsenic", "Ba": "Barium", "Co": "Cobalt", "Cr": "Chromium",
        "Cu": "Copper", "Fe": "Iron", "Ni": "Nickel", "Pb": "Lead",
        "Sb": "Antimony", "Se": "Selenium", "Sr": "Strontium", "Tl": "Thallium",
        "V": "Vanadium", "Zn": "Zinc", "Al": "Aluminum", "Ca": "Calcium",
        "Mg": "Magnesium", "K": "Potassium", "Na": "Sodium", "Hg": "Mercury"
    }
    
    # Agregar mapeo inverso
    reverse_aliases = {v: k for k, v in matrix_aliases.items()}
    matrix_aliases.update(reverse_aliases)
    
    # Agregar más variantes comunes con espacios y mayúsculas/minúsculas
    variants = {}
    for short, long in matrix_aliases.items():
        variants[short.lower()] = long
        variants[short + " "] = long
        variants[short.lower() + " "] = long
        variants[long.lower()] = long
        variants[long + " "] = long
    matrix_aliases.update(variants)
    
    # Obtener todas las hojas disponibles en el workbook
    available_sheets = wb_to_read.sheetnames
    
    # Limpiar datos incompletos
    cleaned_chain_data = []
    for row in chain_data:
        if row and isinstance(row, list) and len(row) > 1 and row[0]:
            cleaned_chain_data.append(row)
    
    if not cleaned_chain_data:
        print("Advertencia: No se encontraron datos válidos en chain_data")
        return []
    
    # Procesar cada fila en los datos limpios
    for row_index, row in enumerate(cleaned_chain_data):
        try:
            # Verificar estructura básica
            if len(row) < 2 or not row[0] or len(row[0]) < 2:
                print(f"Advertencia: Fila {row_index} mal formada: {row}")
                continue
            
            sample_id = str(row[0][1]).strip()  # ID de muestra normalizado
            
            # Verificar que tengamos una lista de hojas a buscar
            if not isinstance(row[1], list) or not row[1]:
                print(f"Advertencia: Lista de hojas vacía para muestra {sample_id}")
                row[1] = []  # Asegurar que sea una lista aunque esté vacía
            
            matrix_list = row[1]
            
            # Inicializar lista de datos de matriz (posición 2 en fila)
            if len(row) < 3:
                row.append([])
            else:
                row[2] = []  # Reemplazar la lista existente con una nueva
            
            print(f"\nBuscando muestra: {sample_id}")
            
            # Buscar en cada hoja especificada para esta muestra
            for matrix_name in matrix_list:
                if not matrix_name:
                    continue
                    
                matrix_name = matrix_name.strip()
                print(f"\nProcesando matriz: {matrix_name}")
                
                # 1. Buscar directamente por nombre exacto
                if matrix_name in available_sheets:
                    sheet_name = matrix_name
                
                # 2. Buscar a través de alias conocidos
                elif matrix_name in matrix_aliases and matrix_aliases[matrix_name] in available_sheets:
                    sheet_name = matrix_aliases[matrix_name]
                
                # 3. Intentar buscar por coincidencia aproximada
                else:
                    sheet_name = find_best_matching_sheet(matrix_name, available_sheets)
                
                if not sheet_name:
                    print(f"Advertencia: No se encontró hoja para matriz '{matrix_name}'")
                    continue
                
                print(f"Usando hoja: {sheet_name}")
                sheet_to_read = wb_to_read[sheet_name]
                
                # Obtener valores de DF, MDL y PQL con manejo mejorado
                df_value, mdl_value, pql_value = get_metadata_values(sheet_to_read)
                
                # Determinar el rango de datos en la hoja
                start_row, end_row = find_data_range(sheet_to_read)
                
                # Buscar ID_muestra en la hoja
                found_any = False
                
                for row_num in range(start_row, end_row + 1):
                    # Buscar en múltiples columnas donde podría estar el ID
                    possible_id_columns = ["B", "C", "A"]
                    
                    for id_col in possible_id_columns:
                        cell_value = sheet_to_read[f"{id_col}{row_num}"].value
                        
                        if cell_value is None:
                            continue
                        
                        # Usar función de comparación precisa
                        if is_matching_sample(sample_id, cell_value):
                            found_any = True
                            print(f"Coincidencia encontrada en fila {row_num}:")
                            print(f"ID en hoja: {cell_value} | ID buscado: {sample_id}")
                            
                            # Recopilar datos de las columnas especificadas como una lista
                            # Buscar resultados en múltiples columnas posibles
                            date_value = find_value_in_row(sheet_to_read, row_num, ["A", "D", "E"], None)
                            sample_id_value = cell_value
                            result_value = find_value_in_row(sheet_to_read, row_num, ["H", "G", "F", "I"], None)
                            notes = find_value_in_row(sheet_to_read, row_num, ["I", "J", "K"], None)
                            notes2 = find_value_in_row(sheet_to_read, row_num, ["J", "K", "L"], None)
                            
                            # Crear estructura de datos
                            matrix_data = [
                                sheet_name,             # nombre_matriz
                                row_num,                # número_fila
                                df_value,               # df
                                mdl_value,              # mdl
                                pql_value,              # pql
                                [                       # lista de datos
                                    date_value,         # Fecha
                                    sample_id_value,    # ID de muestra
                                    result_value,       # Resultado
                                    notes,              # Nota
                                    notes2              # Nota 1
                                ]
                            ]
                            
                            row[2].append(matrix_data)
                            break  # Salir del bucle de columnas de ID
                
                if not found_any:
                    print(f"No se encontraron datos para {sample_id} en la hoja {sheet_name}")
            
            # Si no se encontraron datos en ninguna hoja para este parámetro, registrarlo
            if not row[2]:
                print(f"Advertencia: No se encontraron datos para ningún parámetro de la muestra {sample_id}")
        
        except Exception as e:
            print(f"Error procesando fila {row_index}: {str(e)}")
    
    # Eliminar filas vacías al final del resultado
    while cleaned_chain_data and not cleaned_chain_data[-1]:
        cleaned_chain_data.pop()
    
    return cleaned_chain_data