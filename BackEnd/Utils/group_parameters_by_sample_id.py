import re
import sys




def group_parameters_by_sample(parameters_data: list):
    """
    Agrupa los parámetros por sample_id, separando muestras normales de controles de calidad.
    
    Args:
        parameters_data (list): Lista de parámetros de la base de datos
        
    Returns:
        tuple: (grouped_parameters, quality_controls)
    """
    
    # Validación de entrada
    if parameters_data is None:
        print("❌ ERROR: parameters_data is None")
        return {}, {}
    
    if not isinstance(parameters_data, list):
        print(f"❌ ERROR: parameters_data debe ser una lista, recibido: {type(parameters_data)}")
        return {}, {}
    
    if len(parameters_data) == 0:
        print("⚠️ WARNING: parameters_data está vacía")
        return {}, {}
    
    grouped_parameters = {}
    quality_controls = {}
    
    # Patrón para identificar controles de calidad
    qc_pattern = re.compile(
        r'^(MB|LCSD|LCS|MS|MSD).*|.*(MB|LCSD|LCS|MS|MSD)$|.*Trip Blank-.*|.*method blank.*|.*qc.*', 
        re.IGNORECASE
    )
     
    for param in parameters_data:
        try:
            # Validar que param tenga al menos 2 elementos
            if not param or len(param) < 2:
                print(f"⚠️ WARNING: Parámetro inválido ignorado: {param}")
                continue
                
            sample_id = param[1]  # Asumiendo que sample_id está en el índice 1
            
            # Validar que sample_id no sea None
            if sample_id is None:
                print(f"⚠️ WARNING: sample_id es None en parámetro: {param}")
                continue
            
            # Convertir a string si no lo es
            sample_id = str(sample_id)
            
            if qc_pattern.match(sample_id):   
                # Es un control de calidad
                if sample_id in quality_controls:
                    quality_controls[sample_id].append(param)
                else:
                    # ✅ CORRECCIÓN: Crear una lista en lugar de asignar directamente
                    quality_controls[sample_id] = [param]
            else:
                # Es una muestra normal
                if sample_id in grouped_parameters:
                    grouped_parameters[sample_id].append(param)
                else:
                    grouped_parameters[sample_id] = [param]
                    
        except Exception as e:
            print(f"❌ ERROR procesando parámetro {param}: {str(e)}")
            continue
    
    print(f"✅ Procesamiento completado:")
    print(f"   - Muestras normales: {len(grouped_parameters)} grupos")
    print(f"   - Controles de calidad: {len(quality_controls)} grupos")
    
    return grouped_parameters, quality_controls


# Función de prueba para debugging
def test_group_parameters_by_sample():
    """Función de prueba para verificar el funcionamiento"""
    
    # Datos de prueba basados en tu paste-2.txt
    test_data = [
        [28103, 'SW-1', 'SM 4500 N-NH3 B, C', '2503014-006', 'Ammonia', 0.4, 'mg/L'],
        [28104, 'SW-2', 'SM 4500 N-NH3 B, C', '2503014-007', 'Ammonia', 0.53, 'mg/L'],
        [28105, 'MB-1', 'SM 4500 N-NH3 B, C', '2503014-008', 'Ammonia', 0.66, 'mg/L'],  # Control de calidad
        [28106, 'LCS-1', 'SM 4500 N-NH3 B, C', '2503014-009', 'Ammonia', 0.79, 'mg/L'],  # Control de calidad
    ]
    
    print("🧪 Ejecutando prueba...")
    samples, qc = group_parameters_by_sample(test_data)
    
    print(f"Muestras: {samples}")
    print(f"QC: {qc}")
    
    return samples, qc


