from BackEnd.Database.General.get_connection import DatabaseConnection


def select_last_labsampleid_by_wo(lab_reporting_batch_id: str, tbl: str):
    """
    Obtiene el último LabSampleID de un Work Order específico
    
    Args:
        lab_reporting_batch_id: ID del Work Order/Batch
        tbl: Nombre de la tabla (Samples o SampleTests)
        
    Returns:
        str: Último LabSampleID o None si no existe
    """
    connection = None
    cursor = None
    
    try:
        instance_db = DatabaseConnection()
        connection = DatabaseConnection.get_conn(instance_db)
    
        if connection is None:
            print("Error: No database connection")
            return None
        
        cursor = connection.cursor()
        
        allowed_tables = ['Samples', 'SampleTests']
        if tbl not in allowed_tables:
            print(f"Error: Invalid table name '{tbl}'")
            return None
        
        # Construir query con nombre de tabla (NO usar parámetro aquí)
        query = f"""
            SELECT TOP 1 LabSampleID 
            FROM {tbl}
            WHERE LabReportingBatchID = ?
            ORDER BY ItemID DESC
        """
        
        cursor.execute(query, (lab_reporting_batch_id,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            print(f"No samples found for batch: {lab_reporting_batch_id} in table {tbl}")
            return None
        
    except Exception as e:
        print(f"Error selecting last LabSampleID: {e}")
        return None
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()