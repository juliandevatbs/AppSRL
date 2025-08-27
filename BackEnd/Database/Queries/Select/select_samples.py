

from BackEnd.Database.General.get_connection import DatabaseConnection


def select_samples(batch_id: int, samples_filtered: list, sample_id, is_view: bool) -> list:
    """
    Selecciona las muestras asociadas con batch_id específicos y agrega los análisis concatenados.
    
    Args:
        batch_id (int): El ID del lote de muestras a consultar (usado solo si samples_filtered está vacío)
        samples_filtered (list): Lista de batch IDs para filtrar (opcional)
        sample_id: ID de muestra específica para filtrar (opcional)
        is_view (bool): Si es True, incluye muestras QC (QCSample = 0 o 1). Si es False, solo muestras normales (QCSample = 0)
        
    Returns:
        list: Lista de muestras encontradas con análisis concatenados
    """
    results_list = []
    connection = None
    cursor = None
    
    try:
        
        instance_db = DatabaseConnection()
        # Obtener conexión y crear cursor 
        connection = DatabaseConnection.get_conn(instance_db)
        
        if connection is None:
            print("Error: No database connection"
                  )
            return results_list
        cursor = connection.cursor()
        
        # Construir la consulta base con subconsulta para concatenar análisis
        base_query = """
            SELECT 
                S.ItemID, 
                S.LabReportingBatchID, 
                S.LabSampleID, 
                S.ClientSampleID,
                S.Sampler,
                S.DateCollected, 
                S.MatrixID,
                ISNULL(
                    STUFF(
                        (SELECT DISTINCT ',' + CAST(ST.LabAnalysisRefMethodID AS VARCHAR)
                         FROM Sample_Tests ST 
                         WHERE ST.LabReportingBatchID = S.LabReportingBatchID
                         ORDER BY ',' + CAST(ST.LabAnalysisRefMethodID AS VARCHAR)
                         FOR XML PATH('')), 1, 1, ''
                    ), ''
                ) AS AnalysisMethodIDs
            FROM Samples S
            WHERE 1=1
        """
        
        # Agregar filtro QCSample basado en is_view
        if not is_view:
            base_query += " AND S.QCSample = 0"
        # Si is_view es True, no agregamos filtro QCSample (permite 0 y 1)
        
        #print("EJECUTANDO SELECT SAMPLEEEEEEEEEEEEEEEES")
        
        if len(samples_filtered) > 0:
            # Si hay batch IDs para filtrar, usar esos IDs
            placeholders = ','.join(['?' for _ in samples_filtered])
            query = f"{base_query} AND S.LabReportingBatchID IN ({placeholders})"
            params = samples_filtered
            #print(query)
        else:
            #print("NO HAY MAS FILTROS")
            # Si no hay filtros, solo usar el batch_id proporcionado
            query = f"{base_query} AND S.LabReportingBatchID = ?"
            params = [batch_id]
            #print(query)
        
        # Agregar filtro por LabSampleID si se proporciona
        if sample_id is not None and sample_id != '' and sample_id.strip() != '':
            query += " AND S.LabSampleID = ?"
            params.append(sample_id)
        

        cursor.execute(query, params)
        results = cursor.fetchall() 
        
        # Convertir resultados a lista
        for row in results:
            results_list.append(list(row))
            
        #print(f"Se encontraron {len(results_list)} muestras para los batch IDs consultados")
        print("QUERY USADO")
        print(query)
        
    except Exception as e:
        print(f"Error al seleccionar muestras: {e}")
    
    finally:
        # Cerrar cursor y conexión apropiadamente
        if cursor:
            cursor.close()
        if connection:
            connection.close()
   
    return results_list


def get_analysis_methods_for_batch(batch_id: int) -> str:
    """
    Función auxiliar para obtener solo los LabAnalysisRefMethodID únicos concatenados por comas.
    
    Args:
        batch_id (int): El ID del lote
        
    Returns:
        str: String con los análisis separados por comas
    """
    conn = None
    cursor = None
    
    try:
        instance_db = DatabaseConnection()
        
        conn = DatabaseConnection.get_conn(instance_db)
        cursor = conn.cursor()
        
        query = """
            SELECT DISTINCT LabAnalysisRefMethodID 
            FROM Sample_Tests 
            WHERE LabReportingBatchID = ?
            ORDER BY LabAnalysisRefMethodID
        """
        
        cursor.execute(query, [batch_id])
        results = cursor.fetchall()
        analysis_methods = [str(row[0]) for row in results if row[0] is not None]
        
        return ','.join(analysis_methods)
        
    except Exception as e:
        print(f"Error al obtener métodos de análisis: {e}")
        return ""
    
    finally:
        # Cerrar cursor y conexión apropiadamente
        if cursor:
            cursor.close()
        if conn:
            conn.close()