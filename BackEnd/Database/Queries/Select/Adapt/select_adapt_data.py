from BackEnd.Database.General.get_connection import DatabaseConnection


class SelectAdaptData:

    def __init__(self, cursor, wo):
        self.wo = wo
        self.cursor = cursor
        pass

    def select_adapt_data(self):
        qry = """
                SELECT 
                    st.ClientSampleID, 
                    st.LabAnalysisRefMethodID, 
                    st.LabSampleID, 
                    st.LabID, 
                    st.ClientAnalyteID, 
                    st.AnalyteName, 
                    st.Result, 
                    st.Error, 
                    st.ResultUnits, 
                    st.LabQualifiers, 
                    st.DetectionLimit, 
                    st.AnalyteType, 
                    st.Dilution, 
                    st.PercentMoisture, 
                    st.PercentRecovery, 
                    st.RelativePercentDifference, 
                    st.ReportingLimit, 
                    st.ProjectNumber, 
                    st.ProjectName, 
                    st.DateCollected, 
                    st.MatrixID, 
                    st.QCType, 
                    st.ShippingBatchID, 
                    st.Temperature, 
                    st.PreparationType, 
                    st.AnalysisType, 
                    CASE WHEN st.ReportableResult = -1 THEN 'Yes' ELSE 'No' END AS Reportable,
                    st.DatePrepared, 
                    st.DateAnalyzed, 
                    st.TotalOrDissolved, 
                    st.PrepBatchID, 
                    st.MethodBatchID, 
                    CASE WHEN st.PreservationIntact = -1 THEN 'Yes' ELSE 'No' END AS Preservation,
                    st.QCSpikeAdded, 
                    st.ResultComments, 
                    st.LabReportingBatchID,
                    st.GroupLongName,
                    st.High_Limit,
                    st.Low_Limit,
                    st.[Order],
                    st.Analyst,
                    st.Limits
                FROM Sample_Tests st
                INNER JOIN Samples s ON st.LabSampleID = s.LabSampleID
                WHERE st.LabReportingBatchID = ?
                ORDER BY st.LabAnalysisRefMethodID, st.LabSampleID, st.[Order];
            """

        self.cursor.execute(qry, (self.wo, ))
        data = self.cursor.fetchall()
        return [tuple(row) for row in data]

    def select_epp_data(self):
        qry = """
                SELECT DISTINCT 
                    fdd.WACS_Testsite_ID, 
                    fdd.WACS_Testsite_Name, 
                    fdd.WACS_Facility_ID, 
                    fdd.WACS_Facility_Name, 
                    CASE 
                        WHEN fdd.Matrix LIKE '%S%' THEN 'E'
                        WHEN fdd.WACS_Report_Type LIKE '%LP%' THEN 'E'
                        WHEN UPPER(fdd.WACS_Testsite_Name) LIKE '%BLANK%' THEN 'E'
                        ELSE ''
                    END AS Sample_Type,
                    fdd.Matrix, 
                    CASE 
                        WHEN fdd.WACS_Report_Type LIKE '%LP%' THEN ''
                        WHEN UPPER(fdd.WACS_Testsite_Name) LIKE '%BLANK%' THEN ''
                        ELSE fmp.Field_Measurement_Method
                    END AS Field_Measurement_Method,
                    CASE 
                        WHEN fdd.WACS_Report_Type LIKE '%LP%' THEN ''
                        WHEN UPPER(fdd.WACS_Testsite_Name) LIKE '%BLANK%' THEN ''
                        ELSE fmp.Field_Parameter_NameAnalyteName
                    END AS Field_Parameter_Name,
                    fdd.Result, 
                    CASE 
                        WHEN fdd.WACS_Report_Type LIKE '%LP%' THEN ''
                        WHEN UPPER(fdd.WACS_Testsite_Name) LIKE '%BLANK%' THEN ''
                        ELSE fmp.Result_Units
                    END AS Result_Units,
                    CASE 
                        WHEN fdd.WACS_Report_Type LIKE '%LP%' THEN ''
                        WHEN UPPER(fdd.WACS_Testsite_Name) LIKE '%BLANK%' THEN ''
                        ELSE fmp.Field_Parameter_Qualifier_Code
                    END AS Field_Parameter_Qualifier_Code,
                    fdd.Field_Comments, 
                    fdd.Sampler, 
                    fdd.CollectionAgency, 
                    fdd.Date_Sampled, 
                    fdd.Shipping_Batch_ID, 
                    fdd.Well_Purged_Flag, 
                    fdd.WACS_Report_Type
                FROM FDD_Elements_From_LDD fdd
                INNER JOIN Field_Measured_Parameters fmp 
                    ON fdd.Matrix = fmp.Matrix
                ORDER BY 
                    fdd.WACS_Testsite_Name, 
                    CASE 
                        WHEN fdd.WACS_Report_Type LIKE '%LP%' THEN ''
                        WHEN UPPER(fdd.WACS_Testsite_Name) LIKE '%BLANK%' THEN ''
                        ELSE fmp.Field_Parameter_NameAnalyteName
                    END;
            """

        self.cursor.execute(qry)
        data = self.cursor.fetchall()
        return [tuple(row) for row in data]