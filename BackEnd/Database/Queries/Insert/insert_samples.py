from datetime import datetime, timedelta

from BackEnd.Database.General.get_connection import DatabaseConnection

def insert_samples(samples: list, columns):
    try:
        if not samples or not columns:
            print("There is no data to insert")
            return False
    
        # Obtener conexión activa
        instance_db = DatabaseConnection()
        conn = DatabaseConnection.get_conn(instance_db)
        cursor = conn.cursor()
        if not cursor:
            print("Error: Connection could not be established")
            return False
            
        samples_inserted = 0
        table_name = "Samples"
        
        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join([f"[{col}]" for col in columns])
        insert_query = f"INSERT INTO [dbo].[{table_name}] ({column_names}) VALUES ({placeholders})"
        
        # Insert each data row
        for original_data in samples:

            #original_data = row_dict[0]
            print("DATOS ORIGINALES")
            print(original_data)
            
            # Crear una copia de los datos para modificar
            to_insert = list(original_data)
            
            print(to_insert)
            
            if len(original_data) > 2 and len(to_insert):
            
                # Combinar fecha y hora
                # Posición 6 = hora ('12:45:00')
                # Posición 8 = fecha ('11-03-25')
                time_str = original_data[9]  # '12:45:00'
                date_str = original_data[8]  # '11-03-25'
                
                # Combinar fecha y hora en formato datetime
                datetime_combined = combine_date_time(date_str, time_str)
                
            
                
                # Reorganizar datos según las columnas esperadas
                final_data = [
                    original_data[0],  # ITEMID
                    original_data[1], #LABSAMPLEID
                    original_data[2],  # CLIENT SAMPLE ID
                    original_data[3],  # Collect Method
                    original_data[4],  # CollectionAgency
                    original_data[5],  # MATRIXID
                    original_data[6],  # Sampler
                    datetime_combined,
                    original_data[11], #COMMENTS
                    original_data[12], #SHIPPINGBATCHID
                    original_data[13], #COOLER NUMBER
                    original_data[14], #TEMPERATURE
                    original_data[15], #ADAPT MATRIX
                    original_data[16], #TOTAL CONTAINERS
                    original_data[17], #LABID
                    original_data[18]
                ]

                print(f" ESTA ES LOS DATOS FINALES PARA CREAR -> {final_data}")


                cursor.execute(insert_query, final_data)
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
        

def combine_date_time(date_str, time_str):
    """
    Combina fecha y hora en un objeto datetime
    date_str: '11-03-25' (formato dd-mm-yy)
    time_str: '12:45:00' pero puede tener horas > 23 (secuencial)
    """
    try:
        # Parsear la fecha asumiendo formato dd-mm-yy
        day, month, year = date_str.split('-')
        year = f"20{year}"  # Convertir 25 a 2025
        
        # Parsear la hora y corregir si es > 23
        hour_parts = time_str.split(':')
        original_hour = int(hour_parts[0])
        minutes = hour_parts[1] 
        seconds = hour_parts[2]
        
        # Si la hora es >= 24, convertir a formato válido
        if original_hour >= 24:
            # Opción 1: Usar módulo 24 para ciclar las horas
            valid_hour = original_hour % 24
            corrected_time = f"{valid_hour:02d}:{minutes}:{seconds}"
            
            # También podríamos añadir días si queremos ser más precisos
            extra_days = original_hour // 24
            base_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
            final_date = base_date + timedelta(days=extra_days)
            
            # Crear datetime final
            full_datetime_str = f"{final_date.strftime('%Y-%m-%d')} {corrected_time}"
        else:
            # Hora válida, usar tal como está
            full_datetime_str = f"{year}-{month}-{day} {time_str}"
        
        # Convertir a datetime
        datetime_obj = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M:%S")
        
        return datetime_obj
        
    except Exception as e:
        print(f"Error combining date and time: {e}")
        print(f"Trying to parse: date='{date_str}', time='{time_str}'")
        # Retornar datetime actual como fallback
        return datetime.now()

