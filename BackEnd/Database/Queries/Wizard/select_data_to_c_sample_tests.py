from pathlib import Path
import sys

from BackEnd.Database.General.get_connection import DatabaseConnection

def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.insert(0, str(PROJECT_ROOT))  
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))


def get_all_sample_tests_data(batch_id=None):
    """
    Función unificada que obtiene todos los datos necesarios para el wizard de sample tests
    con una sola conexión a la base de datos.
    
    Args:
        batch_id: ID del batch para filtrar lab samples (opcional)
    
    Returns:
        dict: Diccionario con todas las listas de datos:
        {
            'last_sample_tests': int,
            'batchs_id': list,
            'lab_samples': list
        }
    """
    connection = None
    cursor = None
    
    # Estructura de datos a retornar
    result_data = {
        'last_sample_tests': None,
        'batchs_id': [],
        'lab_samples': [],
        'analyte_names' : [],
        'result_units': [],
        'matrix_ids': []
    }
    
    try:
        instance_db = DatabaseConnection()
        connection = DatabaseConnection.get_conn(instance_db)
        cursor = connection.cursor()
        
        # 1. Obtener último Sample Test ID
        query_last_sample_tests = """
            SELECT TOP 1 SampleTestsID FROM Sample_Tests ORDER BY SampleTestsID DESC;
        """
        cursor.execute(query_last_sample_tests)
        sample_result = cursor.fetchall()
        
        if sample_result:
            # Corregido: fetchall() retorna lista de tuplas
            result_data['last_sample_tests'] = int(sample_result[0][0])
            print(f"Last Sample Test ID: {result_data['last_sample_tests']}")
        else:
            print("No Sample Tests records found")
        
        # 2. Obtener batch IDs
        query_batch_ids = """
            SELECT DISTINCT TOP 100 LabReportingBatchID 
            FROM Samples 
            WHERE LabReportingBatchID IS NOT NULL
            ORDER BY LabReportingBatchID DESC;
        """
        cursor.execute(query_batch_ids)
        batch_results = cursor.fetchall()
        result_data['batchs_id'] = [str(row[0]) for row in batch_results]
        print(f"Found {len(result_data['batchs_id'])} batch IDs")
        
        # 3. Obtener lab samples si se proporciona batch_id
        if batch_id is not None:
            query_lab_samples = """
                SELECT DISTINCT LabSampleID 
                FROM Samples 
                WHERE LabReportingBatchID = ? AND LabSampleID IS NOT NULL
                ORDER BY LabSampleID
            """
            # Corregido: parámetro como tupla con coma
            cursor.execute(query_lab_samples, (batch_id,))
            lab_samples_results = cursor.fetchall()
            result_data['lab_samples'] = [str(row[0]) for row in lab_samples_results]
            print(f"Found {len(result_data['lab_samples'])} lab samples for batch {batch_id}")

        # 4. Obtener analitos
        query_analyte_names = """
            SELECT DISTINCT AnalyteName FROM Sample_Tests;
        """
        cursor.execute(query_analyte_names)
        analyte_names_results = cursor.fetchall()
        result_data['analyte_names'] = [str(row[0]) for row in analyte_names_results]
        #print(f"Found {len(result_data['batchs_id'])} batch IDs")
        
        
        # 5. Obtener medidas para resultados
        query_result_units = """
            SELECT DISTINCT ResultUnits FROM Sample_Tests;
        """
        cursor.execute(query_result_units)
        result_units_results = cursor.fetchall()
        result_data['result_units'] = [str(row[0]) for row in result_units_results]
        #print(f"Found {len(result_data['batchs_id'])} batch IDs")
        
        
        # 5. Obtener lab qualifiers
        query_lab_qualifiers = """
            SELECT DISTINCT LabQualifiers FROM Sample_Tests;
        """
        cursor.execute(query_lab_qualifiers)
        lab_qualifiers_results = cursor.fetchall()
        result_data['lab_qualifiers'] = [str(row[0]) for row in lab_qualifiers_results]
        #print(f"Found {len(result_data['batchs_id'])} batch IDs")
        
        
        # 6. Obtener analyte types
        analyte_types_qualifiers = """
            SELECT DISTINCT AnalyteType FROM Sample_Tests;
        """
        cursor.execute(analyte_types_qualifiers)
        analyte_types_results = cursor.fetchall()
        result_data['analyte_types'] = [str(row[0]) for row in analyte_types_results]
        #print(f"Found {len(result_data['batchs_id'])} batch IDs")
        
        
        # 7. Obtener matrix_ids
        matrix_ids_qualifiers = """
            SELECT DISTINCT MatrixID FROM Sample_Tests;
        """
        cursor.execute(matrix_ids_qualifiers)
        matrix_ids_results = cursor.fetchall()
        result_data['matrix_ids'] = [str(row[0]) for row in matrix_ids_results]
        #print(f"Found {len(result_data['batchs_id'])} batch IDs")
        
        return result_data
        
    except Exception as ex:
        print(f"Error getting sample data: {ex}")
        import traceback
        traceback.print_exc()
        return result_data  # Retorna estructura con valores por defecto en caso de error
        
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"Error closing cursor: {e}")

# Funciones individuales para compatibilidad con código existente
def select_last_sample():
    """Función de compatibilidad - usa get_all_sample_tests_data()"""
    data = get_all_sample_tests_data()
    return data['last_sample_tests']

def select_batchs():
    """Función de compatibilidad - usa get_all_sample_tests_data()"""
    data = get_all_sample_tests_data()
    return data['batchs_id']

def select_lab_samples(batch_id):
    """Función de compatibilidad - usa get_all_sample_tests_data()"""
    data = get_all_sample_tests_data(batch_id)
    return data['lab_samples']

def select_analyte_names():
    
    data = get_all_sample_tests_data()
    
    return data['analyte_names']

def execute_all_sc_optimized(batch_id=None):
    """Ejecuta todas las consultas de manera optimizada con una sola conexión"""
    return get_all_sample_tests_data(batch_id)

def execute_all_sc(batch_id=None):
    """Función original - ahora usa la versión optimizada"""
    return execute_all_sc_optimized(batch_id)

