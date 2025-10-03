from BackEnd.Database.General.get_connection import DatabaseConnection


def select_parameters(batch_id: int, batches_filtered: list, samples_ids=None, analyte_groups=None, analyte_names=None) -> list:
    parameters_data = []
    
    try: 
        instance_db = DatabaseConnection()
        connection = DatabaseConnection.get_conn(instance_db)
        cursor = connection.cursor()
        
        base_query = """
            SELECT ST.SampleTestsID, ST.ClientSampleID, ST.LabAnalysisRefMethodID, ST.LabSampleID, ST.AnalyteName, 
            ST.Result, ST.ResultUnits, ST.DetectionLimit, ST.Dilution, ST.ReportingLimit, 
            ST.ProjectName, ST.DateCollected, ST.MatrixID, ST.QCType, ST.LabReportingBatchID, 
            ST.Notes, S.Sampler, ST.Analyst 
            FROM Sample_Tests AS ST
            INNER JOIN Samples AS S ON ST.LabSampleID = S.LabSampleID 
                AND ST.LabReportingBatchID
            """
        
        # Construir la condición para batch IDs
        if len(batches_filtered) > 0:
            placeholders = ','.join(['?' for _ in batches_filtered])
            query = f"{base_query} IN ({placeholders})"
            params = batches_filtered
        else:
            query = f"{base_query} = ?"
            params = [batch_id]
        
        # Agregar filtros adicionales
        if samples_ids:
            query += " AND ST.LabSampleID = ?"
            params.append(samples_ids)
        
        if analyte_names:
            query += " AND ST.LabAnalysisRefMethodID = ?"
            params.append(analyte_names)
        
        if analyte_groups:
            query += " AND ST.AnalyteName = ?"
            params.append(analyte_groups)
        
        query += " ORDER BY ST.LabSampleID, ST.AnalyteName"
        
        print(f"Ejecutando consulta: {query}")
        print(f"Parámetros: {params}")
        
        results = cursor.execute(query, params)
        
        for row in results:
            parameters_data.append(list(row))
        
        cursor.close()
        print(f"Se encontraron {len(parameters_data)} parámetros")
        return parameters_data
    
    except Exception as ex:
        print(f"Error: {ex}")
        return []