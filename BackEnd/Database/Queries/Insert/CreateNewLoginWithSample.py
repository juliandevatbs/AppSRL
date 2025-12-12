
from BackEnd.Database.Queries.Insert.Login.InsertNewLogin import InsertNewLogin
from BackEnd.Database.Queries.Insert.Samples.InsertNewSample import InsertNewSample
from BackEnd.Database.Queries.Select.SelectNextWorkOrder import SelectNextWorkOrder


class CreateNewLoginWithSample:
    """
    Coordina la creación de un nuevo Sample_Login y su Sample asociado
    """
    
    def __init__(self):
        self.next_wo_instance = SelectNextWorkOrder()
        self.insert_login_instance = InsertNewLogin()
        self.insert_sample_instance = InsertNewSample()
    
    def create_login_and_sample(self, login_data: dict):
        """
        Crea un nuevo Login y Sample en una transacción
        Retorna el nuevo LabReportingBatchID
        """
        new_work_order = None
        
        try:
            # 1. Obtener el próximo Work Order
            self.next_wo_instance.load_connection()
            new_work_order = self.next_wo_instance.get_next_work_order()
            self.next_wo_instance.close_connection()
            
            # 2. Insertar el Sample_Login
            self.insert_login_instance.load_connection()
            self.insert_login_instance.insert_new_login(login_data, new_work_order)
            self.insert_login_instance.close_connection()
            
            # 3. Insertar el Sample asociado
            self.insert_sample_instance.load_connection()
            self.insert_sample_instance.insert_new_sample(new_work_order)
            self.insert_sample_instance.close_connection()
            
            return new_work_order
            
        except Exception as e:
            print(f"Error creating login and sample: {e}")
            raise e