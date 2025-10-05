from BackEnd.Database.General.get_connection import DatabaseConnection


def insert_mb_tests(data_to_create: dict) -> bool:
    """
    Clona una muestra existente y la convierte en un QC (Method Blank)
    
    Args:
        data_to_create: dict con las claves:
            - inc_lab_sample_id: Nuevo LabSampleID para el QC
            - client_sample_id: Nuevo ClientSampleID para el QC
            - lab_sample_id_orig: LabSampleID original a clonar
    
    Returns:
        bool: True if insert correctly
    """
    connection = None
    cursor = None
    
    try:
        instance_db = DatabaseConnection()
        connection = DatabaseConnection.get_conn(instance_db)
    
        if connection is None:
            print("Error: No database connection")
            return False
        
        cursor = connection.cursor()
        
        # Query with params
        # Query with params
        query = """
            INSERT INTO Sample_Tests (
                ClientSampleID,
                LabAnalysisRefMethodID,
                LabSampleID,
                LabID,
                AnalyteName,
                AnalysisType,
                ReportableResult,
                TotalOrDissolved,
                PrepBatchID,
                MethodBatchID,
                PreservationIntact,
                LabReportingBatchID, 
                GroupLongName,
                TagMB,
                Preservative
            )
            VALUES
            
            (
            ?,    
            ?,
            ?,
            'E83484',
            ?,
            'RES',
            1,
            'TOT',
            'PB09222518',
            'MB09222518',
            1,
            ?,
            'Classical Chemistry Parameters',
            1,
            1
          
            )
            
            """
        
        # Ejecutar con parámetros
        cursor.execute(query, (
            data_to_create.get("ClientSampleID"),
            data_to_create.get("LabAnalysisRefMethodID"),
            data_to_create.get("LabSampleID"),
            data_to_create.get("AnalyteName"),
            data_to_create.get("LabReportingBatchID")
        ))
        
        # Confirmar cambios
        connection.commit()
        
        print("MB Sample tests created")
        return True
        
    except Exception as e:
        print(f"Error inserting MB sample tests: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()