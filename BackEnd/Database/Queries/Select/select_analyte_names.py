from BackEnd.Database.General.get_connection import DatabaseConnection

def select_analyte_names(batch_id):
    """
    Seleccionar todas los analyte names de un batch id
    """
    analyte_names_list = []
    connection = None
    cursor = None
    
    try: 
        instance_db = DatabaseConnection()
        connection = DatabaseConnection.get_conn(instance_db)
        
        if connection is None:
            print("Error: No database connection")
            return analyte_names_list
    
        cursor = connection.cursor()
        
        query = """
            SELECT DISTINCT AnalyteName FROM Sample_Tests 
            WHERE LabReportingBatchID = ?
        """
        
        cursor.execute(query, (batch_id, ))
        results = cursor.fetchall()
        
        # Since we're selecting only one column, each result is a tuple with one element
        for result in results:
            analyte_names_list.append(result[0])  # This will be a tuple like ('AnalyteName1',)
            
    except Exception as e:
        print(f"Error fetching analyte names: {e}")
        
    finally: 
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
    return analyte_names_list