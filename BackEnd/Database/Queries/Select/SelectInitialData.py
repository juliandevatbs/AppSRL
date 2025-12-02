from BackEnd.Database.General.get_connection import DatabaseConnection


class SelectInitialData:

    def __init__(self):


        self.connection = None
        self.cursor = None

        self.filters_inital_data = None
        self.sample_initial_data = None



        self.filters_inital_data_query = """
        
        
                                            SELECT TOP 1
                                            
                                                S.LabReportingBatchID,
                                                S.LabSampleID,
                                                SL.ProjectName,
                                                SL.ProjectLocation,
                                                SL.Date_Due,
                                                SL.LabReceiptDate,
                                                SL.Contact,
                                                SL.Email,
                                                SL.Address_1,
                                                SL.City,
                                                SL.Postal_Code,
                                                SL.Phone,
                                                SL.State_Prov,
                                                SL.ClientProjectLocation,
                                                S.MatrixID

                                            FROM Samples S 
                                            LEFT JOIN Sample_Login SL ON S.LabReportingBatchID = SL.LabReportingBatchID 
                                            ORDER BY S.LabReportingBatchID DESC;
        
                                        
                                        
                                        """

        self.sample_initial_data_query = """
    
                                        SELECT TOP 1  
                                            
		
                                            ItemID,
                                            LabReportingBatchID,
                                            LabSampleID,
                                            ClientSampleID,
                                            Sampler,
                                            DateCollected,
                                            MatrixID,
                                            Temperature,
                                            ShippingBatchID,
                                            CollectionMethod,
                                            CollectionAgency,
                                            AdaptMatrixID,
                                            LabID
                                    
                                    FROM Samples 
                                    ORDER BY LabReportingBatchID DESC; 
        
    
    
    
                                    """

        self.work_orders_query = """
        
                
                SELECT 
                    DISTINCT TOP 300 LabReportingBatchID 
                FROM Samples
                ORDER BY LabReportingBatchID DESC;
        
        
        
        
        
        """

    def load_connection(self):

        try:


            instance_db = DatabaseConnection()
            self.connection = instance_db.get_conn()

            if self.connection:

                self.cursor = self.connection.cursor()

            else:

                print("No database connection")

        except Exception as e:
            print(f"Error in the database connection: {e}")


    def close_connection(self):


        if self.cursor:

            self.cursor.close()

        if self.connection:

            self.connection.close()


    def select_work_orders(self):

        self.cursor.execute(self.work_orders_query)

        results = self.cursor.fetchall()

        return results


    def select_initial_data(self):



        self.cursor.execute(self.filters_inital_data_query)

        results = self.cursor.fetchall()

        return results



    def select_sample_initial_data(self):

        self.cursor.execute(self.sample_initial_data_query)

        results = self.cursor.fetchall()

        return results










