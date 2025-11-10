from BackEnd.Database.General.get_connection import DatabaseConnection


def update_assign_data(table_name, field_name, lab_sample_ids: list, new_data):
    """
    Actualiza un campo en múltiples registros
    """
    if not table_name or not field_name or not lab_sample_ids or new_data is None:
        print("Error: Faltan parámetros")
        return False

    conn = None
    cursor = None

    try:
        instance_db = DatabaseConnection()
        conn = DatabaseConnection.get_conn(instance_db)
        cursor = conn.cursor()

        # Crear placeholders para IN clause
        placeholders = ','.join(['?' for _ in lab_sample_ids])
        query = f"UPDATE {table_name} SET {field_name} = ? WHERE SampleTestsID IN ({placeholders})"

        params = [new_data] + lab_sample_ids

        print(f"Ejecutando: {query}")
        print(f"Actualizando {len(lab_sample_ids)} registros")

        cursor.execute(query, params)
        conn.commit()

        print(f"✅ {cursor.rowcount} registros actualizados")
        return True

    except Exception as ex:
        print(f"❌ Error: {ex}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()