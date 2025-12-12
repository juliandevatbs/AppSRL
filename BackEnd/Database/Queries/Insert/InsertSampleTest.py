from datetime import datetime

from BackEnd.Database.General.get_connection import DatabaseConnection


class InsertSampleTest:
    """
    Clase para insertar nuevos sample tests básicos en SampleTests
    El usuario editará los campos después en la tabla
    """
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
    
    def get_samples_for_work_order(self, work_order):
        """
        Obtiene los samples disponibles para un Work Order
        
        Args:
            work_order (int): LabReportingBatchID
            
        Returns:
            list: Lista de tuplas (LabSampleID, ClientSampleID, MatrixID)
        """
        try:
            query = """
                SELECT LabSampleID, ClientSampleID, MatrixID
                FROM Samples
                WHERE LabReportingBatchID = ?
                ORDER BY LabSampleID
            """
            
            self.load_connection()
            self.cursor.execute(query, (work_order,))
            results = self.cursor.fetchall()
            
            return results if results else []
            
        except Exception as e:
            print(f"Error getting samples: {e}")
            return []
        finally:
            self.close_connection()
    
    def create_empty_test(self, work_order, lab_sample_id=None):
        """
        Crea un sample test básico/vacío que el usuario editará después
        
        Args:
            work_order (int): LabReportingBatchID
            lab_sample_id (str): LabSampleID opcional. Si es None, usa el primero disponible
            
        Returns:
            int: SampleTestsID del test creado, o None si falla
        """
        try:
            # Si no se proporciona LabSampleID, obtener el primero disponible
            if not lab_sample_id:
                samples = self.get_samples_for_work_order(work_order)
                if not samples:
                    print("Error: No samples available for this Work Order")
                    return None
                lab_sample_id = samples[0][0]  # Primer LabSampleID
                client_sample_id = samples[0][1]
                matrix_id = samples[0][2]
            else:
                # Obtener datos del sample
                query = """
                    SELECT ClientSampleID, MatrixID
                    FROM Samples
                    WHERE LabSampleID = ? AND LabReportingBatchID = ?
                """
                self.load_connection()
                self.cursor.execute(query, (lab_sample_id, work_order))
                result = self.cursor.fetchone()
                self.close_connection()
                
                if result:
                    client_sample_id = result[0]
                    matrix_id = result[1]
                else:
                    client_sample_id = lab_sample_id
            
            # Fecha actual
            now = datetime.now().strftime('%m/%d/%y %H:%M')
            
            # Query de inserción con valores mínimos
            query = """
                INSERT INTO Sample_Tests (
                    LabReportingBatchID,
                    LabSampleID,
                    ClientSampleID
                    
                ) VALUES (?, ?, ?)
            """
            
            values = (
                work_order,
                lab_sample_id,
                client_sample_id
               
            )
            
            self.load_connection()
            self.cursor.execute(query, values)
            self.conn.commit()
            
            # Obtener el ID generado
            self.cursor.execute("SELECT @@IDENTITY")
            new_id = self.cursor.fetchone()[0]
            
            print(f"[DB] Sample Test created: {new_id} for {lab_sample_id}")
            return new_id
            
        except Exception as e:
            print(f"Error creating sample test: {e}")
            import traceback
            traceback.print_exc()
            if self.conn:
                self.conn.rollback()
            return None
        finally:
            self.close_connection()
    
    def create_multiple_tests_for_sample(self, work_order, lab_sample_id, count=1):
        """
        Crea múltiples tests para un sample
        
        Args:
            work_order (int): LabReportingBatchID
            lab_sample_id (str): LabSampleID
            count (int): Cantidad de tests a crear
            
        Returns:
            list: Lista de IDs creados
        """
        created_ids = []
        for _ in range(count):
            test_id = self.create_empty_test(work_order, lab_sample_id)
            if test_id:
                created_ids.append(test_id)
        return created_ids