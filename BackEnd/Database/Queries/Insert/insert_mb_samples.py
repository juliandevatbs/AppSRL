from BackEnd.Database.General.get_connection import DatabaseConnection


def insert_mb_samples(data_to_create: dict) -> bool:
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
        
        
        
        
        query = """
            INSERT INTO Samples (
                LabReportingBatchID, LabSampleID, ClientSampleID,
                ResultComments, Temperature, ShippingBatchID,
                CollectMethod, MatrixID, DateCollected, Sampler,
                TotalContainers, CoolerNumber, PreservationIntact,
                CollectionAgency, CustodyIntactSeal, AdaptMatrixID,
                ProgramType, CollectionMethod, SamplingDepth, LocationCode,
                ProjectNumber, LabID, TagMB, PercentMositure, DateAnalyzed,
                QCSample
            )
            SELECT 
                LabReportingBatchID, 
                ?,  -- inc_lab_sample_id
                ?,  -- client_sample_id
                ResultComments, 
                Temperature, 
                ShippingBatchID,              
                CollectMethod, 
                MatrixID, 
                DateCollected, 
                'Lab QC',  -- Cambiar Sampler
                TotalContainers, 
                CoolerNumber, 
                PreservationIntact,
                CollectionAgency, 
                CustodyIntactSeal, 
                AdaptMatrixID,
                ProgramType, 
                CollectionMethod, 
                SamplingDepth, 
                LocationCode,
                ProjectNumber, 
                LabID, 
                1,  -- TagMB = 1 ( MB)
                PercentMositure, 
                DateAnalyzed,
                1   -- QCSample = 1 (is a QC)
            FROM Samples
            WHERE LabSampleID = ?  -- lab_sample_id_orig
        """
        
        # Ejecutar con parámetros
        cursor.execute(query, (
            data_to_create.get("inc_lab_sample_id"),
            data_to_create.get("client_sample_id"),
            data_to_create.get("lab_sample_id_orig")
        ))
        # Confirmar cambios
        connection.commit()
        
        return True
        
    except Exception as e:
        print(f"Error inserting MB tests: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()