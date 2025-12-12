from BackEnd.Database.General.get_connection import DatabaseConnection


class InsertSample:
 
    def __init__(self):
        self.instance_db = DatabaseConnection()
        self.conn = None
        self.cursor = None
        
    def load_connection(self):
        """Carga la conexión a la base de datos"""
        self.conn = DatabaseConnection.get_conn(self.instance_db)
        self.cursor = self.conn.cursor()
    
    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def get_next_lab_sample_id(self, work_order):
        """
        Obtiene el siguiente LabSampleID disponible para un Work Order
        
        Args:
            work_order (int): LabReportingBatchID
            
        Returns:
            str: Siguiente LabSampleID (ej: '2410001-002')
        """
        try:
            query = """
                SELECT MAX(LabSampleID)
                FROM Samples
                WHERE LabReportingBatchID = ?
            """
            
            self.load_connection()
            self.cursor.execute(query, (work_order,))
            result = self.cursor.fetchone()
            
            if result and result[0]:
                # Obtener el último ID (ej: '2410001-005')
                last_id = result[0]
                # Separar el número de secuencia
                parts = str(last_id).split('-')
                if len(parts) == 2:
                    sequence = int(parts[1]) + 1
                    next_id = f"{work_order}-{sequence:03d}"
                else:
                    next_id = f"{work_order}-001"
            else:
                # No hay samples para este WO, empezar en 001
                next_id = f"{work_order}-001"
            
            return next_id
            
        except Exception as e:
            print(f"Error getting next LabSampleID: {e}")
            import traceback
            traceback.print_exc()
            return f"{work_order}-001"
        finally:
            self.close_connection()
    
    def create_empty_sample(self, work_order):
        """
        Crea un sample básico/vacío que el usuario editará después
        
        Args:
            work_order (int): LabReportingBatchID
            
        Returns:
            str: LabSampleID del sample creado, o None si falla
        """
        try:
            # Generar el siguiente LabSampleID
            lab_sample_id = self.get_next_lab_sample_id(work_order)
            
            
            # Query de inserción con valores mínimos
            query = """
                INSERT INTO Samples (
                    LabReportingBatchID,
                    LabSampleID
                   
                ) VALUES (?, ?)
            """
            
            values = (
                work_order,
                lab_sample_id,
              
            )
            
            self.load_connection()
            self.cursor.execute(query, values)
            self.conn.commit()
            
            print(f"[DB] Sample created: {lab_sample_id}")
            return lab_sample_id
            
        except Exception as e:
            print(f"Error creating sample: {e}")
            import traceback
            traceback.print_exc()
            if self.conn:
                self.conn.rollback()
            return None
        finally:
            self.close_connection()
