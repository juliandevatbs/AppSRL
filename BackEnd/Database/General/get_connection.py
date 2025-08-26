import os
from pathlib import Path
from dotenv import load_dotenv
import pyodbc

class DatabaseConnection:
    """Manejo de conexión a la base de datos"""
    
    def __init__(self):
        #env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv()
        self.active_config = os.getenv("DB_ACTIVE_CONFIG", 'julian')
    
    def get_connection_string(self):
        """Obtiene el string de conexión desde variables de entorno"""
        config_name = self.active_config.upper()
        
        config = {
            'SERVER': os.getenv(f'DB_{config_name}_SERVER'),
            'DATABASE': os.getenv(f'DB_{config_name}_DATABASE'),
            'USERNAME': os.getenv(f'DB_{config_name}_USERNAME'),
            'PASSWORD': os.getenv(f'DB_{config_name}_PASSWORD')
        }
        
        
        print(config)
        
        
        
        
        # Validar que no falte ninguna
        missing_vars = [k for k, v in config.items() if not v and k not in ['USERNAME', 'PASSWORD']]
        if missing_vars:
            raise ValueError(f"Faltan variables de entorno: {', '.join(missing_vars)}")
        
        # Construir string de conexión
        if config['SERVER'].startswith('(localdb)'):
            # LocalDB con autenticación Windows
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config['SERVER']};"
                f"DATABASE={config['DATABASE']};"
                f"Trusted_Connection=yes;"
            )
        elif config['USERNAME'] and config['PASSWORD']:
            # SQL Server remoto con usuario/contraseña
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config['SERVER']};"
                f"DATABASE={config['DATABASE']};"
                f"UID={config['USERNAME']};"
                f"PWD={config['PASSWORD']};"
            )
        else:
            # SQL Server con autenticación Windows
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config['SERVER']};"
                f"DATABASE={config['DATABASE']};"
                f"Trusted_Connection=yes;"
            )
    
    def get_conn(self):
        """Retorna una conexión activa"""
        return pyodbc.connect(self.get_connection_string())
    
    def test_connection(self):
        """Prueba la conexión"""
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True, f"Conexión exitosa a {self.active_config}"
        except pyodbc.Error as e:
            return False, f"Error de conexión: {e.args}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def get_cursor(self):
        """Retorna cursor y conexión"""
        try:
            conn = self.get_conn()
            return conn.cursor(), conn
        except Exception as e:
            print(f"Error en get_cursor: {str(e)}")
            return None, None
