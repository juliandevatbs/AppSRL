from BackEnd.Database.General.get_connection import DatabaseConnection


class QualityControlsQuery:

    def __init__(self):
        return

    def quality_controls_query(self, lab_reporting_batch_id, cursor):
        qry = """

            SELECT
                s.ClientSampleID,
                s.LabSampleID,
                s.DateCollected,
                s.Sampler,
                s.MatrixID,

                t.AnalyteName,
                t.Result,
                t.ResultUnits,
                t.Dilution,
                t.DetectionLimit,
                t.ReportingLimit,
                t.LabAnalysisRefMethodID,
                t.Analyst,
                t.MethodBatchID,
                t.Notes
                FROM Sample_Tests t
                JOIN Samples s ON s.LabSampleID = t.LabSampleID
				AND s.LabReportingBatchID = t.LabReportingBatchID
				AND s.QCSample = 1
                WHERE t.LabReportingBatchID = ?

            """

        cursor.execute(qry, (lab_reporting_batch_id,))

        data = cursor.fetchall()

        return data







