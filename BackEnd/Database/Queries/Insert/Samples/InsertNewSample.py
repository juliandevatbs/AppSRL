from BackEnd.Database.General.get_connection import DatabaseConnection


class InsertNewSample:
    
    def __init__(self):
        self.instance_db = DatabaseConnection()
        self.conn = None
        self.cursor = None
        
    def load_connection(self):
        self.conn = DatabaseConnection.get_conn(self.instance_db)
        self.cursor = self.conn.cursor()

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def insert_new_sample(self, work_order: int, lab_sample_id: str = None):
        """
        Crea un nuevo Sample asociado a un LabReportingBatchID
        Si no se proporciona LabSampleID, se genera automáticamente
        """
        
        # Si no hay LabSampleID, generar uno basado en el work order
        if not lab_sample_id:
            lab_sample_id = f"{work_order}-001"  # Primer sample del WO
        
        qry = """
            INSERT INTO Samples
                (
                LabReportingBatchID,
                LabSampleID
                )
            VALUES 
                (?, ?)
        """
        
        try:
            self.cursor.execute(qry, (work_order, lab_sample_id))
            self.conn.commit()
            
            # Obtener el itemID insertado
            self.cursor.execute("SELECT @@IDENTITY")  # SQL Server
            item_id = self.cursor.fetchone()[0]
            
            return item_id
            
        except Exception as e:
            self.conn.rollback()
            raise e