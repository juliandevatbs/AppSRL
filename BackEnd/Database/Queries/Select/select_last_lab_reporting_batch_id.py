


from pathlib import Path
import sys



def get_project_root():
    """Retorna el directorio raíz del proyecto"""
    return Path(__file__).parent.parent.absolute()

# Configurar paths
PROJECT_ROOT = get_project_root()
sys.path.append(str(PROJECT_ROOT))
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_DIR))

from BackEnd.Database.General.get_connection import DatabaseConnection

# This function gets the last labreportingbatch id from de database

def select_last_lab_reporting_batch_id():
    
    
    try:
    
        instance_db = DatabaseConnection()
        conn = DatabaseConnection.get_conn(instance_db)
        cursor = conn.cursor()
        
        
        query = """

            SELECT TOP 1 LabReportingBatchID FROM dbo.Samples ORDER BY LabReportingBatchID DESC;  
        
        """
        
        cursor.execute(query)
        row = cursor.fetchone()
     
        
        last_llrbi = row[0]
        
        cursor.close()
        
        return last_llrbi
    
    except Exception as ex:
        
        print(f"Error getting the last lab reporting batch id {ex}")