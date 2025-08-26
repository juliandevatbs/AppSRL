import sys
from pathlib import Path

from BackEnd.Database.General.get_connection import DatabaseConnection

def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.insert(0, str(PROJECT_ROOT))  
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))

import pyodbc

def insert_sample_tests(sample_tests: list, columns):
    """
    Inserta múltiples registros de pruebas de muestras en la base de datos.
    
    Args:
        sample_tests: Una lista de listas, donde cada lista interna contiene los datos de un registro
        columns: Lista de nombres de columnas
    
    Returns:
        bool: True si la inserción fue exitosa, False en caso contrario
    """
    
    if not sample_tests or not columns:
        print("No hay datos para insertar")
        return False

    try:
        # Obtener conexión activa
        cursor = DatabaseConnection.get_conn()
        if not cursor:
            print("Error: No se pudo establecer conexión")
            return False
            
        samples_inserted = 0
        table_name = "Sample_Tests"

        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join([f"[{col}]" for col in columns])
        insert_query = f"INSERT INTO [dbo].[{table_name}] ({column_names}) VALUES ({placeholders})"

        # Insert each data row
        for row_dict in sample_tests:
            print("ROW DICTTTTTTTTTTTTTTTTTTTTTT")
            print(row_dict)
            
            # Convert to list for modification
            row_data = list(row_dict)
            
            # Fix the type checking - check actual type, not string comparison
            # Assuming index 4 is the Result column based on your test_columns
            if row_data[4] is not None:
                # Try to convert to float if it's not already a number
                try:
                    if isinstance(row_data[4], str):
                        # Remove any non-numeric characters and convert
                        cleaned_value = str(row_data[4]).strip()
                        if cleaned_value and cleaned_value.replace('.', '').replace('-', '').isdigit():
                            row_data[4] = float(cleaned_value)
                        else:
                            print(f"Warning: Non-numeric result value: {row_data[4]}")
                            row_data[4] = 0.0
                    elif not isinstance(row_data[4], (int, float)):
                        print(f"Warning: Unexpected result type: {type(row_data[4])}, value: {row_data[4]}")
                        row_data[4] = 0.0
                except (ValueError, TypeError) as e:
                    print(f"Error converting result to float: {e}, value: {row_data[4]}")
                    row_data[4] = 0.0
            else:
                row_data[4] = 0.0
            
            cursor.execute(insert_query, row_data)
            samples_inserted += 1
            
        cursor.commit()
        print(f"PROCESS SUCCESSFULLY! Total rows inserted: {samples_inserted}")
        return True
        
    except Exception as ex:
        print(f"Error: {ex}")
        try:
            cursor.rollback()
        except:
            pass
        return False
    
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass