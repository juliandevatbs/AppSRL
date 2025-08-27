import sys
import os

from BackEnd.Database.General.get_connection import DatabaseConnection


def select_quality(batch_id: int, batches_filtered: list = []) -> list:
    """
    Selecciona los parámetros asociados con batch_id específicos.
    
    Args:
        batch_id (int): El ID del lote a consultar (usado solo si batches_filtered está vacío)
        batches_filtered (list): Lista de batch IDs para filtrar (opcional)
        
    Returns:
        list: Lista de parámetros encontrados
    """
    parameters_data = []
    
    try:
        instance_db = DatabaseConnection()
        conn = DatabaseConnection.get_conn(instance_db)
        cursor = conn.cursor()
        
        # Construir la consulta base (SIN el WHERE final)
        base_query = """
            SELECT ST.ClientSampleID, ST.LabAnalysisRefMethodID, ST.LabSampleID, ST.AnalyteName,
                   ST.Result, ST.ResultUnits, ST.DetectionLimit, ST.Dilution, ST.ReportingLimit,
                   ST.ProjectName, ST.DatePrepared, ST.DateAnalyzed, ST.MatrixID, ST.QCType, ST.LabReportingBatchID,
                   ST.Notes, S.Sampler, ST.Analyst, ST.PercentRecovery, ST.RelativePercentDifference, 
                   ST.QCSpikeAdded, ST.Limits, ST.Datecollected
            FROM Sample_Tests AS ST
            LEFT JOIN Samples AS S ON ST.LabSampleID = S.LabSampleID 
            WHERE ST.QCType != 'N' AND ST.LabReportingBatchID"""
        
        if len(batches_filtered) > 0:
            # Si hay batch IDs para filtrar, usar esos IDs
            placeholders = ','.join(['?' for _ in batches_filtered])
            query = f"{base_query} IN ({placeholders})"
            params = batches_filtered
            print(f"Filtrando parámetros por batch IDs: {batches_filtered}")
        else:
            # Si no hay filtros, solo usar el batch_id proporcionado
            query = f"{base_query} = ?"
            params = [batch_id]
            print(f"Usando batch ID único: {batch_id}")
        
        print(f"Ejecutando consulta: {query}")
        print(f"Parámetros: {params}")
        
        # Ejecutar la consulta
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        print(f"Resultados obtenidos: {len(results)}")
        
        # Convertir resultados a lista
        for row in results:
            parameters_data.append(list(row))
        
        cursor.close()
        print(f"Se encontraron {len(parameters_data)} parámetros para los batch IDs consultados")
        
        return parameters_data
        
    except Exception as ex:
        print(f"Error en select_quality: {ex}")
        import traceback
        traceback.print_exc()
        if 'cursor' in locals():
            cursor.close()
        return []

# Función de prueba para debug
def test_query_manually(batch_id):
    """
    Función para probar la consulta manualmente y ver qué está pasando
    """
    try:
        instance_db = DatabaseConnection()
        conn = DatabaseConnection.get_conn(instance_db)
        cursor = conn.cursor()
        
        # Probar primero si hay registros con ese batch_id
        test_query = "SELECT COUNT(*) FROM Sample_Tests WHERE LabReportingBatchID = ?"
        cursor.execute(test_query, [batch_id])
        count_result = cursor.fetchone()
        print(f"Total de registros con batch_id {batch_id}: {count_result[0]}")
        
        # Probar si hay registros con QCType != 'N'
        test_query2 = "SELECT COUNT(*) FROM Sample_Tests WHERE LabReportingBatchID = ? AND QCType != 'N'"
        cursor.execute(test_query2, [batch_id])
        count_result2 = cursor.fetchone()
        print(f"Registros con batch_id {batch_id} y QCType != 'N': {count_result2[0]}")
        
        # Ver qué valores de QCType existen
        test_query3 = "SELECT DISTINCT QCType FROM Sample_Tests WHERE LabReportingBatchID = ?"
        cursor.execute(test_query3, [batch_id])
        qc_types = cursor.fetchall()
        print(f"Tipos de QC encontrados para batch_id {batch_id}: {[row[0] for row in qc_types]}")
        
        cursor.close()
        
    except Exception as ex:
        print(f"Error en test: {ex}")
        if 'cursor' in locals():
            cursor.close()

# Ejemplo de uso:
# test_query_manually(2506011)
# result = select_quality(2506011)