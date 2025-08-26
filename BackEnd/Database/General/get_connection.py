import pyodbc

class DatabaseConnection:
    """Manejo de conexión a la base de datos"""
    
    ACTIVE_CONFIG = 'julian'  
    
    CONFIGS = {
        'orlando': {
            'SERVER': '192.168.0.121',
            'DATABASE': 'SRLSQL',
            'USERNAME': 'SRLADMIN',
            'PASSWORD': '$iZ42cU2$'
        },
        'julian': {
            'SERVER': '(localdb)\\MSSQLLocalDB',
            'DATABASE': 'local_srl',
            'USERNAME': 'JULIAN_SRL',
            'PASSWORD': 'IdeaTab2005@'
        },
        'chemilab': {
            'SERVER': '(localdb)\\SRLlOCAL',
            'DATABASE': 'LOCALSRL',
            'USERNAME': 'julianhomezdev',
            'PASSWORD': 'IdeaTab2005@'
        }
    }
    
    @staticmethod
    def get_connection_string():
        """Obtiene la cadena de conexión usando la configuración activa"""
        config = DatabaseConnection.CONFIGS.get(DatabaseConnection.ACTIVE_CONFIG)
        if not config:
            raise ValueError(f"Configuración '{DatabaseConnection.ACTIVE_CONFIG}' no encontrada")
        
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['SERVER']};"
            f"DATABASE={config['DATABASE']};"
            f"UID={config['USERNAME']};"
            f"PWD={config['PASSWORD']};"
            f"TrustServerCertificate=yes"
        )
    
    @staticmethod
    def test_connection():
        """Prueba la conexión usando la configuración activa"""
        try:
            connection_string = DatabaseConnection.get_connection_string()
            conn = pyodbc.connect(connection_string)
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            return True, f"Conexión exitosa a {DatabaseConnection.ACTIVE_CONFIG}", conn
            
        except pyodbc.Error as e:
            return False, f"Error de conexión: {str(e)}", None
        except Exception as e:
            return False, f"Error inesperado: {str(e)}", None
    
    @staticmethod
    def get_conn():
        """Retorna una conexión usando la configuración activa"""
        try:
            connection_string = DatabaseConnection.get_connection_string()
            conn = pyodbc.connect(connection_string)
            return conn
        except Exception as e:
            print(f"Error en get_conn: {str(e)}")
            return None
    
    @staticmethod
    def get_cursor():
        """Retorna un cursor usando la configuración activa"""
        try:
            conn = DatabaseConnection.get_conn()
            if conn:
                return conn.cursor(), conn
            return None, None
        except Exception as e:
            print(f"Error en get_cursor: {str(e)}")
            return None, None