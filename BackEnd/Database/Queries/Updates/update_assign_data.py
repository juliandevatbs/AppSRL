import sys
import os
from Database.General.get_connection import DatabaseConnection

def update_assign_data(field_name, lab_sample_ids: list, new_data):
    """
    Actualiza un campo específico para una lista de muestras
    
    Args:
        field_name (str): Nombre del campo a actualizar
        lab_sample_ids (list): Lista de LabSampleIDs a actualizar
        new_data: Nuevo valor para el campo
    
    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario
    """
    
    # Validar que los parámetros no sean None o vacíos
    if not field_name or not lab_sample_ids or new_data is None:
        print("Error: field_name, lab_sample_ids, or new_data is None/empty. Please review.")
        return False
    
    # Validar que field_name sea un campo válido (seguridad)
    valid_fields = [
        "ClientSampleID", "Sampler", "DateCollected", "MatrixID", 
        "LabAnalysisRefMethodID", "Temperature", "CollectMethod", 
        "TotalContainers", "CoolerNumber"
    ]
    
    if field_name not in valid_fields:
        print(f"Error: '{field_name}' no es un campo válido. Campos permitidos: {valid_fields}")
        return False
    
    conn = None
    cursor = None
    
    try:
        conn = DatabaseConnection.get_conn()
        cursor = conn.cursor()
        
        # Construir la consulta con el nombre del campo directamente
        if len(lab_sample_ids) > 1:
            placeholders = ','.join(['?' for _ in lab_sample_ids])
            query = f"UPDATE Samples SET {field_name} = ? WHERE LabSampleID IN ({placeholders})"
            # new_data va primero, luego los IDs
            params = [new_data] + lab_sample_ids
        else:
            query = f"UPDATE Samples SET {field_name} = ? WHERE LabSampleID = ?"
            params = [new_data, lab_sample_ids[0]]
        
        print(f"Ejecutando consulta: {query}")
        print(f"Parámetros: {params}")
        
        # Ejecutar la consulta UPDATE
        cursor.execute(query, params)
        
        # Obtener el número de filas afectadas
        rows_affected = cursor.rowcount
        
        # Confirmar los cambios (CORREGIDO)
        conn.commit()  # ✅ La conexión hace commit, no el cursor
        
        print(f"Se actualizaron {rows_affected} registros exitosamente")
        
        # Verificar si se actualizaron las filas esperadas
        if rows_affected == 0:
            print("⚠️  Advertencia: No se actualizó ningún registro. Verifique que los LabSampleIDs existan.")
            return False
        elif rows_affected != len(lab_sample_ids):
            print(f"⚠️  Advertencia: Se esperaba actualizar {len(lab_sample_ids)} registros, pero se actualizaron {rows_affected}")
        
        return True
        
    except Exception as ex:
        print(f"Error al actualizar datos: {ex}")
        print(f"Tipo de error: {type(ex).__name__}")
        
        # Rollback en caso de error
        if conn:
            try:
                conn.rollback()
                print("Rollback ejecutado debido al error")
            except:
                pass
        
        return False
        
    finally:
        # Cerrar cursor y conexión
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def update_assign_data_with_validation(field_name, lab_sample_ids: list, new_data):
    """
    Versión mejorada con validación adicional y mejor manejo de errores
    """
    
    # Validaciones iniciales
    if not field_name or not lab_sample_ids or new_data is None:
        print("Error: Parámetros inválidos")
        return False
    
    # Validar que field_name sea seguro
    valid_fields = [
        "ClientSampleID", "Sampler", "DateCollected", "MatrixID", 
        "LabAnalysisRefMethodID", "Temperature", "CollectMethod", 
        "TotalContainers", "CoolerNumber"
    ]
    
    if field_name not in valid_fields:
        print(f"Error: Campo '{field_name}' no válido")
        return False
    
    conn = None
    cursor = None
    
    try:
        conn = DatabaseConnection.get_conn()
        cursor = conn.cursor()
        
        # Primero verificar que los LabSampleIDs existen
        if len(lab_sample_ids) > 1:
            check_placeholders = ','.join(['?' for _ in lab_sample_ids])
            check_query = f"SELECT LabSampleID FROM Samples WHERE LabSampleID IN ({check_placeholders})"
            cursor.execute(check_query, lab_sample_ids)
        else:
            check_query = "SELECT LabSampleID FROM Samples WHERE LabSampleID = ?"
            cursor.execute(check_query, [lab_sample_ids[0]])
        
        existing_ids = [row[0] for row in cursor.fetchall()]
        missing_ids = [id for id in lab_sample_ids if id not in existing_ids]
        
        if missing_ids:
            print(f"⚠️  Advertencia: Los siguientes LabSampleIDs no existen: {missing_ids}")
            if len(missing_ids) == len(lab_sample_ids):
                print("Error: Ninguno de los LabSampleIDs proporcionados existe en la base de datos")
                return False
        
        # Proceder con la actualización solo para IDs existentes
        valid_ids = existing_ids
        
        if len(valid_ids) > 1:
            placeholders = ','.join(['?' for _ in valid_ids])
            query = f"UPDATE Samples SET {field_name} = ? WHERE LabSampleID IN ({placeholders})"
            params = [new_data] + valid_ids
        else:
            query = f"UPDATE Samples SET {field_name} = ? WHERE LabSampleID = ?"
            params = [new_data, valid_ids[0]]
        
        print(f"Ejecutando consulta: {query}")
        print(f"Parámetros: {params}")
        print(f"Actualizando {len(valid_ids)} registros")
        
        # Ejecutar la consulta UPDATE
        cursor.execute(query, params)
        
        # Obtener el número de filas afectadas
        rows_affected = cursor.rowcount
        
        # Confirmar los cambios
        conn.commit()
        
        print(f"✅ Se actualizaron {rows_affected} registros exitosamente")
        
        return True
        
    except Exception as ex:
        print(f"❌ Error al actualizar datos: {ex}")
        print(f"Tipo de error: {type(ex).__name__}")
        
        # Información adicional para debugging
        import traceback
        print("Traceback completo:")
        traceback.print_exc()
        
        # Rollback en caso de error
        if conn:
            try:
                conn.rollback()
                print("Rollback ejecutado")
            except:
                pass
        
        return False
        
    finally:
        # Cerrar conexiones
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass
