
from pathlib import Path
import sys


def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.insert(0, str(PROJECT_ROOT))  
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))


from BackEnd.Database.General.get_connection import DatabaseConnection


def select_last_samples():
    
    try:
        instance_db = DatabaseConnection()
        connection = DatabaseConnection.get_conn(instance_db)
        cursor = connection.cursor()
        
        if cursor:
            
            query = """
                            SELECT  TOP 10
                                S.ItemID, 
                                S.LabReportingBatchID, 
                                S.LabSampleID, 
                                S.ClientSampleID,
                                S.DateCollected, 
                                S.MatrixID
                            
                            FROM Samples AS S
                            ORDER BY LabReportingBatchID DESC;
                            
                    """
            
            cursor.execute(query)
            
            sample_top_results = cursor.fetchall()
            samples_top_results_list = [list(x) for x in sample_top_results]
            print(samples_top_results_list)
            
        else:
            
            print("Failed connection")
        
    except Exception as ex:
        
        print(f"Error -> {ex}")
        
