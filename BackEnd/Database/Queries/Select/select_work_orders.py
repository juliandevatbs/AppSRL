from BackEnd.Database.General.get_connection import DatabaseConnection


def select_work_orders():
    
    
    
    
    
    """
    
    Seleccionar todas las w.o para msotrar un desplegable
    en el front para que el usuario seleccione la que quiere
    trabajr
    
    
    
    """
    
    
    # Storage for the w.os    
    workdrs_list = []
    
    
    # Connection to the db 
    connection = None
    cursor = None
    
    
    try: 
        
        
        
        instance_db = DatabaseConnection()
        
        
        connection = DatabaseConnection.get_conn(instance_db)
        
        
        if connection is None:
            
            print("Error: No database connection")
            
            return workdrs_list
    
        cursor = connection.cursor()
        
        
        
        query = """
        

            SELECT TOP 200 LabReportingBatchID FROM Samples ORDER BY LabReportingBatchID DESC;
        
        
        
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        
        for i in results:
            
            workdrs_list.append(i)
            
            
    except Exception as e:
        
        print(f"Error al traer w.os")
        
    finally: 
        
        
        if cursor:
            
            cursor.close()
        
        if connection:
            
            connection.close()
            
    return workdrs_list
    
    
    
