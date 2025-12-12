from BackEnd.Database.General.get_connection import DatabaseConnection


class SelectNextWorkOrder:
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
    
    def get_next_work_order(self):
        """Obtiene el siguiente LabReportingBatchID disponible"""
        qry = """
            SELECT MAX(LabReportingBatchID) FROM Sample_Login
        """
        
        self.cursor.execute(qry)
        result = self.cursor.fetchone()
        
        if result and result[0]:
            return int(result[0]) + 1
        else:
            return 1 