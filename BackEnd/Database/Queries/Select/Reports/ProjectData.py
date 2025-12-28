from BackEnd.Database.General.get_connection import DatabaseConnection


class ProjectData:



    def __init__(self):

        return



    def project_data_query(self, lab_reporting_batch_id, cursor):


        qry = """
            SELECT 
                ProjectName,
                Contact,
                Address_1,
                City,
                State_Prov,
                Postal_Code,
                ProjectLocation,
                Phone,
                ClientProjectNumber,
                Postal_Code,
                LabReceiptDate
                LabReportingBatchID
            
            FROM Sample_Login
            WHERE LabReportingBatchID = ?

            """

        cursor.execute(qry, (lab_reporting_batch_id, ))


        data = cursor.fetchall()

        return data







