from pathlib import Path
import sys

from BackEnd.Database.General.get_connection import DatabaseConnection

def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.insert(0, str(PROJECT_ROOT))  
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))


def get_all_sample_data():
    """
    Función unificada que obtiene todos los datos necesarios para el wizard de samples
    con una sola conexión a la base de datos.
    
    Returns:
        dict: Diccionario con todas las listas de datos:
        {
            'last_batch_id': int,
            'collect_methods': list,
            'collection_agencies': list,
            'matrices': list,
            'samplers': list,
            'lab_ids': list  # Si necesitas este campo específico
        }
    """
    connection = None
    cursor = None
    
    # Estructura de datos a retornar
    result_data = {
        'last_batch_id': None,
        'collect_methods': [],
        'collection_agencies': [],
        'matrices': [],
        'samplers': [],
        'lab_ids': [],
        'shipping_batchs': []
    }
    
    try:
        instance_db = DatabaseConnection()
        connection = DatabaseConnection.get_conn(instance_db)
        cursor = connection.cursor()
        # 1. Obtener último Batch ID
        query_last_batch = """
            SELECT TOP 1 LabReportingBatchID FROM Samples ORDER BY LabReportingBatchID DESC;
        """
        cursor.execute(query_last_batch)
        batch_result = cursor.fetchone()
        
        if batch_result:
            result_data['last_batch_id'] = int(batch_result[0]) + 1
            print(f"Last batch ID: {result_data['last_batch_id']}")
        else:
            print("No batch records found")
        
        # 2. Obtener Collect Methods
        query_collect_methods = """
            SELECT DISTINCT CollectMethod FROM Samples WHERE CollectMethod IS NOT NULL;
        """
        cursor.execute(query_collect_methods)
        collect_results = cursor.fetchall()
        result_data['collect_methods'] = [str(row[0]) for row in collect_results]
        print(f"Collect methods: {result_data['collect_methods']}")
        
        # 3. Obtener Collection Agencies
        query_collection_agencies = """
            SELECT DISTINCT CollectionAgency FROM Samples WHERE CollectionAgency IS NOT NULL;
        """
        cursor.execute(query_collection_agencies)
        agency_results = cursor.fetchall()
        result_data['collection_agencies'] = [str(row[0]) for row in agency_results]
        print(f"Collection agencies: {result_data['collection_agencies']}")
        
        # 4. Obtener Matrices
        query_matrices = """
            SELECT DISTINCT MatrixID FROM Samples WHERE MatrixID IS NOT NULL;
        """
        cursor.execute(query_matrices)
        matrix_results = cursor.fetchall()
        result_data['matrices'] = [str(row[0]) for row in matrix_results]
        print(f"Matrices: {result_data['matrices']}")
        
        # 5. Obtener Samplers
        query_samplers = """
            SELECT DISTINCT Sampler FROM Samples WHERE Sampler IS NOT NULL;
        """
        cursor.execute(query_samplers)
        sampler_results = cursor.fetchall()
        result_data['samplers'] = [str(row[0]) for row in sampler_results]
        print(f"Samplers: {result_data['samplers']}")
        
        # 6. Lab IDs (corregido - asumiendo que quieres LabID en lugar de CollectMethod)
        query_lab_ids = """
            SELECT DISTINCT LabID FROM Samples WHERE LabID IS NOT NULL;
        """
        cursor.execute(query_lab_ids)
        lab_results = cursor.fetchall()
        result_data['lab_ids'] = [str(row[0]) for row in lab_results]
        print(f"Lab IDs: {result_data['lab_ids']}")
        
        # 7. Adapt Matrix id
        
        query_adapt_matrix = """
            SELECT DISTINCT AdaptMatrixID FROM Samples WHERE AdaptMatrixID IS NOT NULL;
            """
        cursor.execute(query_adapt_matrix)
        adapt_results = cursor.fetchall()
        result_data['adapts_matrix'] = [str(row[0]) for row in adapt_results]
        
        
        # 8. Shipping batch id
        
        query_shipping_batch = """
            SELECT DISTINCT ShippingBatchID FROM Samples WHERE ShippingBatchID IS NOT NULL;
            """
        cursor.execute(query_shipping_batch)
        shipping_batch_results = cursor.fetchall()
        result_data['shipping_batchs'] = [str(row[0]) for row in shipping_batch_results]
        
        return result_data
        
    except Exception as ex:
        print(f"Error getting sample data: {ex}")
        return result_data  # Retorna estructura vacía en caso de error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Funciones individuales para compatibilidad con código existente
def select_last_batch():
    """Función de compatibilidad - usa get_all_sample_data()"""
    data = get_all_sample_data()
    return data['last_batch_id']

def select_collect_method():
    """Función de compatibilidad - usa get_all_sample_data()"""
    data = get_all_sample_data()
    return data['collect_methods']

def select_collection_agency():
    """Función de compatibilidad - usa get_all_sample_data()"""
    data = get_all_sample_data()
    return data['collection_agencies']

def select_matrix():
    """Función de compatibilidad - usa get_all_sample_data()"""
    data = get_all_sample_data()
    return data['matrices']

def select_sampler():
    """Función de compatibilidad - usa get_all_sample_data()"""
    data = get_all_sample_data()
    return data['samplers']

def select_lab_id():
    """Función de compatibilidad - usa get_all_sample_data()"""
    data = get_all_sample_data()
    return data['lab_ids']

# Función optimizada para ejecutar todo
def execute_all_sc_optimized():
    """Ejecuta todas las consultas de manera optimizada con una sola conexión"""
    data = get_all_sample_data()
    
    print("\n=== RESUMEN DE DATOS ===")
    print(f"Last Batch ID: {data['last_batch_id']}")
    print(f"Collect Methods: {len(data['collect_methods'])} items")
    print(f"Collection Agencies: {len(data['collection_agencies'])} items")
    print(f"Matrices: {len(data['matrices'])} items")
    print(f"Samplers: {len(data['samplers'])} items")
    print(f"Lab IDs: {len(data['lab_ids'])} items")
    
    return data

# Función original para compatibilidad
def execute_all_sc():
    """Función original - ahora usa la versión optimizada"""
    return execute_all_sc_optimized()

if __name__ == '__main__':
    # Ejecutar versión optimizada
    all_data = execute_all_sc_optimized()
    
    # Ejemplo de uso de los datos
    print("\n=== EJEMPLO DE USO ===")
    if all_data['last_batch_id']:
        next_batch = all_data['last_batch_id'] + 1
        print(f"Próximo Batch ID: {next_batch}")
    
    if all_data['collect_methods']:
        print(f"Primer método de recolección: {all_data['collect_methods'][0]}")