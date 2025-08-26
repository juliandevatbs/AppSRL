

from pathlib import Path
import sys




def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.append(str(PROJECT_ROOT))
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_DIR))

from BackEnd.Database.General.get_connection import DatabaseConnection



def filter_queries(batch_id: int) -> list:

   
    try:

        db = DatabaseConnection()
        conn = db.get_conn()
        cursor = db.cursor()
        
        base_query = """
            SELECT DISTINCT LabSampleID FROM Samples WHERE LabReportingBatchID = ?
        """

    
        cursor.execute(base_query, batch_id)
        results = cursor.fetchall() 
        
        results_list = []
        
        # Convertir resultados a lista
        for row in results:
            results_list.append(list(row))
            
        #print(results_list)
        
        
        
    except Exception as e:
        print(f"Error al seleccionar muestras: {e}")
    
    finally:
        # Cerrar cursor y conexión apropiadamente
        if cursor:
            cursor.close()
        if conn:
            conn.close()
   
    return results_list


