
# Configuración de paths
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

from Database.General.get_connection import DatabaseConnection

def select_header_data (clnt_id: int):
    
    header_data = []
    try:
        
        
        cursor = DatabaseConnection.get_conn()
        
        
        query = """
                    SELECT Client, Address_1, City, State_Prov, Postal_Code, Country, CompanyPhone
                    
                    FROM Clients WHERE Client_ID = ?
                    
                """
        
        
        client_id = clnt_id
        
        result = cursor.execute(query, (str(client_id),))
        
        result = list(result)
        
        #print(result)
        
        cursor.close()
        
    except Exception as ex:
        
        print(f"Error getting the header data {ex}")
        
