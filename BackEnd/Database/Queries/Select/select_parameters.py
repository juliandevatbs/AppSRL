import sys
import os

from Database.General.get_connection import DatabaseConnection

def select_parameters(batch_id: int, batches_filtered: list, samples_ids=None) -> list:
    """
    Selecciona los parámetros asociados con batch_id específicos.
    
    Args:
        batch_id (int): El ID del lote a consultar (usado solo si batches_filtered está vacío)
        batches_filtered (list): Lista de batch IDs para filtrar (opcional)
        samples_ids (str or list, optional): LabSampleID específico o lista de IDs para filtrar
        
    Returns:
        list: Lista de parámetros encontrados
    """
    parameters_data = []
    
    try: 
        connection = DatabaseConnection.get_conn()
        cursor = connection.cursor()
        
        # Construir la consulta base
        base_query = """
        SELECT ST.SampleTestsID, ST.ClientSampleID, ST.LabAnalysisRefMethodID, ST.LabSampleID, ST.AnalyteName, 
        ST.Result, ST.ResultUnits, ST.DetectionLimit, ST.Dilution, ST.ReportingLimit, 
        ST.ProjectName, ST.DateCollected, ST.MatrixID, ST.QCType, ST.LabReportingBatchID, 
        ST.Notes, S.Sampler, ST.Analyst 
        FROM Sample_Tests AS ST
        LEFT JOIN Samples AS S ON ST.LabSampleID = S.LabSampleID 
        WHERE ST.QCType = 'N' AND ST.LabReportingBatchID"""
        
        # Construir la condición para batch IDs
        if len(batches_filtered) > 0:
            # Si hay batch IDs para filtrar, usar esos IDs
            placeholders = ','.join(['?' for _ in batches_filtered])
            query = f"{base_query} IN ({placeholders})"
            params = batches_filtered
        else:
            # Si no hay filtros, solo usar el batch_id proporcionado
            query = f"{base_query} = ?"
            params = [batch_id]
        
        # Agregar filtro por LabSampleID si se proporciona
        if samples_ids is not None and samples_ids != '' and samples_ids.strip() != '':
           
            query += " AND ST.LabSampleID = ?"
            params.append(samples_ids)
            # Si samples_ids está vacío o es None, no agregamos filtro
        
        """ print(f"Ejecutando consulta: {query}")
        print(f"Parámetros: {params}")"""
        
        results = cursor.execute(query, params)
        
        for row in results:
            parameters_data.append(list(row))
        
        cursor.close()
        print(f"Se encontraron {len(parameters_data)} parámetros para los batch IDs consultados")
        print(query)
        print(parameters_data)
        return parameters_data
    
        
    
    except Exception as ex:
        print(f"Error: {ex}")
        return []