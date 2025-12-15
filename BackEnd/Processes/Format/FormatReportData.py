from collections import defaultdict


class FormatReportData:


    def __init__(self):
        pass


    def format_date(self, date_value):

        if date_value is None:

            return ""

        if isinstance(date_value, str):

            return date_value

        try:

            return date_value.strftime("%m/%d/%y %H:%M:%S")

        except:

            return str(date_value)


    def format_samples_summary(self, first_page_data):

        samples_summary = []

        for row in first_page_data:

            sample = {

                "labSampleId": row.LabSampleID or "",
                "clientSampleId": row.ClientSampleID or "",
                "collectedDateTime": self.format_date(row.DateCollected),
                "sampleMatrix": row.MatrixID or "",
                "analysisRequested": row.Methods or ""

            }

            samples_summary.append(sample)

        return samples_summary

    def format_sample_tests(self, analytical_results, filter_detected=False):

        tests_by_sample = defaultdict(list)

        for row in analytical_results:

            if filter_detected:

                try:

                    result = str(row.result)
                    reporting_limit = str(row.ReportingLimit) if row.ReportingLimit else " "

                    if float(result) <= float(reporting_limit):

                        continue
                except (ValueError, AttributeError):

                    if filter_detected:

                        continue

            sample_test = {
                "analyteName": row.AnalyteName or "",
                "results": str(row.Result) if row.Result is not None else "",
                "units": row.ResultUnits or "",
                "df": str(row.Dilution) if row.Dilution else "1",
                "mdl": str(row.DetectionLimit) if row.DetectionLimit else "",
                "pql": str(row.ReportingLimit) if row.ReportingLimit else "",
                "method": row.LabAnalysisRefMethodID or "",
                "analyzedDate": self.format_date(row.DateAnalyzed),
                "by": row.Analyst or "",
                "batch": row.MethodBatchID or "",
                "note": row.Notes or ""
            }

            lab_sample_id = row.LabSampleID
            tests_by_sample[lab_sample_id].append(sample_test)

        return tests_by_sample

    def format_samples_with_tests(self, first_page_data, tests_by_sample):

        samples = []

        for row in first_page_data:

            sample = {
                "clientSampleId": row.ClientSampleID or "",
                "labSampleId": row.LabSampleID or "",
                "dateCollected": self.format_date(row.DateCollected),
                "collectedBy": row.CollectedBy or "",
                "matrixId": row.MatrixID or "",
                "sampleTests": tests_by_sample.get(row.LabSampleID, [])
            }

            samples.append(sample)

        return samples

    def format_quality_controls(self, quality_controls_data):


        qc_data = []

        for row in quality_controls_data:

            qc = {
                "analyteName": row.AnalyteName or "",
                "clientSampleId": row.ClientSampleID or "",
                "labSampleId": row.LabSampleID or "",
                "dateCollected": self.format_date(row.DateCollected),
                "datePrepared": self.format_date(row.DatePrepared) if hasattr(row, 'DatePrepared') else "",
                "dateAnalyzed": self.format_date(row.DateAnalyzed),
                "result": str(row.Result) if row.Result is not None else "",
                "qcSpikeAdded": str(row.QCSpikeAdded) if hasattr(row, 'QCSpikeAdded') and row.QCSpikeAdded else "",
                "resultUnits": row.ResultUnits or "",
                "detectionLimit": str(row.DetectionLimit) if row.DetectionLimit else "",
                "percentRecovery": str(row.PercentRecovery) if hasattr(row,
                                                                       'PercentRecovery') and row.PercentRecovery else "",
                "analyst": row.Analyst or "",
                "methodBatchId": row.MethodBatchID or ""
            }
            qc_data.append(qc)

        return qc_data


    def format_complete_report(self, first_data, analytical_results, quality_controls, project_info=None):

        samples_summary = self.format_samples_summary(first_data)

        all_tests_by_sample = self.format_sample_tests(analytical_results, filter_detected=False)
        samples_all = self.format_samples_with_tests(first_data, all_tests_by_sample)

        detected_tests_by_sample = self.format_sample_tests(analytical_results, filter_detected=True)
        samples_detected =  self.format_samples_with_tests(first_data, detected_tests_by_sample)

        qc_data = self.format_quality_controls(quality_controls)

        report = {
            "projectData": project_info or {
                "projectName": "",
                "labReceivedDate": "",
                "companyName": "",
                "clientName": "",
                "clientAddress": "",
                "city": "",
                "state": "",
                "zip": "",
                "projectLocation": "",
                "clientPhone": "",
                "clientProjectNumber": "",
                "labReportingBatchID": ""
            },
            "samplesData": samples_summary,  # Resumen para primera página
            "samplesDataTW": samples_all,  # Todos los resultados analíticos
            "samplesDataDetected": samples_detected,  # Solo detectados
            "qualityControlData": qc_data
        }

        return report



