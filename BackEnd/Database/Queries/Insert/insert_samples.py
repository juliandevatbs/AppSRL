from BackEnd.Database.General.get_connection import DatabaseConnection
from BackEnd.Processes.samples.process_samples_to_create import process_samples_to_create


def insert_samples(samples: list[dict]) -> bool:
    """Inserta múltiples muestras en la BD usando diccionarios"""
    connection = None
    cursor = None
    
    try:
        if not samples:
            print("No data to insert")
            return False
        
        # Procesar muestras ANTES de insertar
        processed_samples = process_samples_to_create(samples)
        
        if not processed_samples:
            print("No valid samples to insert after processing")
            return False
        
        # Obtener conexión
        instance_db = DatabaseConnection()
        connection = DatabaseConnection.get_conn(instance_db)
        cursor = connection.cursor()
        
        if not cursor:
            print("Error: Connection could not be established")
            return False
        
        # Columnas
        columns = [
            'ItemID', 'LabSampleID', 'ClientSampleID', 'CollectMethod',
            'CollectionAgency', 'MatrixID', 'Sampler', 'DateCollected',
            'ResultComments', 'ShippingBatchID', 'CoolerNumber', 'Temperature',
            'AdaptMatrixID', 'TotalContainers', 'LabID', 'LabReportingBatchID'
        ]
        
        # Construir query
        column_names = ", ".join([f"[{col}]" for col in columns])
        placeholders = ", ".join(["?" for _ in columns])
        insert_query = f"INSERT INTO [dbo].[Samples] ({column_names}) VALUES ({placeholders})"
        
        samples_inserted = 0
        
        # Insertar cada muestra procesada
        for sample_dict in processed_samples:
            final_data = [sample_dict.get(col) for col in columns]
            
            print(f"Inserting: {sample_dict['LabSampleID']}")
            cursor.execute(insert_query, final_data)
            samples_inserted += 1
        
        connection.commit()
        print(f"SUCCESS! Total samples inserted: {samples_inserted}")
        return True
        
    except Exception as ex:
        print(f"Error inserting samples: {ex}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()