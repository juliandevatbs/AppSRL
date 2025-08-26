
from Database.General.get_connection import DatabaseConnection

def get_last_sample_test_id ():
    
    try:
        cursor = DatabaseConnection.get_conn()

        query = "SELECT TOP 1 SampleTestsID FROM Sample_Tests ORDER BY id DESC"
        
        
        return True
    
    except Exception as ex:
        
        print(f"Error {ex}")
        #cursor.rollback()
        return False