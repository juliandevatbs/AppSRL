from BackEnd.Database.General.get_connection import DatabaseConnection


def insert_lcs_samples(data_to_create: dict) :

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

                    ItemID, LabReportingBatchID, LabSampleID, ClientSampleID,
                    ResultComments, Temperature, ShippingBatchID,
                    CollectMethod, MatrixID, DateCollected, Sampler,
                    TotalContainers, CoolerNumber, PreservationIntact,
                    CollectionAgency, CustodyIntactSeal, AdaptMatrixID,
                    ProgramType, CollectionMethod, SamplingDepth, LocationCode,
                    ProjectNumber, LabID, TagMB, PercentMositure, DateAnalyzed,
                    QCSample
                )
                SELECT 
                    (SELECT MAX(ItemID) +1 FROM Samples
                    WHERE LabReportingBatchID = ?
                    ),
                    s.LabReportingBatchID, 
                    ?,  -- inc_lab_sample_id
                    ?,  -- client_sample_id
                    s.ResultComments, 
                    s.Temperature, 
                    s.ShippingBatchID,              
                    s.CollectMethod, 
                    s.MatrixID, 
                    s.DateCollected, 
                    'Lab QC',  -- Cambiar Sampler
                    s.TotalContainers, 
                    s.CoolerNumber, 
                    s.PreservationIntact,
                    s.CollectionAgency, 
                    s.CustodyIntactSeal, 
                    s.AdaptMatrixID,
                    s.ProgramType, 
                    s.CollectionMethod, 
                    s.SamplingDepth, 
                    s.LocationCode,
                    s.ProjectNumber, 
                    s.LabID, 
                    1,  -- TagLCS = 1 (LCS)
                    s.PercentMositure, 
                    s.DateAnalyzed,
                    1   -- QCSample = 1 (is a QC)
                FROM Samples s
                WHERE s.LabSampleID = ?  -- lab_sample_id_orig
            """

        # Ejecutar con parámetros
        cursor.execute(query, (
            data_to_create.get("work_order"),
            data_to_create.get("inc_lab_sample_id"),
            data_to_create.get("client_sample_id"),
            data_to_create.get("lab_sample_id_orig")
        ))
        # Confirmar cambios
        connection.commit()

        return True

    except Exception as e:
        print(f"Error inserting LCS tests: {e}")
        if connection:
            connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()