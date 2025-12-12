from BackEnd.Database.General.get_connection import DatabaseConnection


class InsertNewLogin:
    
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
    
    def insert_new_login(self, data_to_create: dict, new_work_order: int):
        
        
        # Unzip data
        project_name = data_to_create.get('ProjectName', '')
        lab_receipt_date = data_to_create.get('LabReceiptDate', '')
        entered_by = data_to_create.get('Entered_By', '')
        date_due = data_to_create.get('Date_Due', '')
        priority = data_to_create.get('Priority', '')
        project_location = data_to_create.get('ProjectLocation', '')
        contact = data_to_create.get('Contact', '')
        phone = data_to_create.get('Phone', '')
        email = data_to_create.get('Email', '')
        address_1 = data_to_create.get('Address_1', '')
        city = data_to_create.get('City', '')
        state_prov = data_to_create.get('State_Prov', '')
        postal_code = data_to_create.get('Postal_Code', '')
        
        qry = """
            INSERT INTO Sample_Login 
                (
                LabReportingBatchID,
                ProjectName,
                LabReceiptDate, 
                Entered_By, 
                Date_Due, 
                Priority, 
                ProjectLocation, 
                Contact, 
                Phone, 
                Email, 
                Address_1,
                City, 
                State_Prov, 
                Postal_Code
                )
            VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(
                qry,
                (
                    new_work_order,
                    project_name,
                    lab_receipt_date,
                    entered_by,
                    date_due,
                    priority,
                    project_location,
                    contact,
                    phone,
                    email,
                    address_1,
                    city,
                    state_prov,
                    postal_code
                )
            )
            
            self.conn.commit()
            return new_work_order
            
        except Exception as e:
            self.conn.rollback()
            raise e