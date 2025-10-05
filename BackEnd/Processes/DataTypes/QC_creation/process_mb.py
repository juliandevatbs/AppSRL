from BackEnd.Database.Queries.Insert.insert_mb_samples import insert_mb_samples
from BackEnd.Database.Queries.Insert.insert_mb_tests import insert_mb_tests
from BackEnd.Database.Queries.Select.MB.select_last_labsampleid_by_wo import select_last_labsampleid_by_wo


def process_mb_samples(data_to_process: dict) :
    
    
    processed_data = {}
    
    # get the last labsampleid from the wo
    
    work_order = data_to_process.get("work_order")
    lab_sample_id = data_to_process.get("lab_sample_id")
    
    if (type(work_order) == str):
    
        last_lbid = select_last_labsampleid_by_wo(work_order, 'Samples')
    
    else:
        
        last_lbid = select_last_labsampleid_by_wo(str(work_order), 'Samples')
        
    
    #inc_lab_sample_id -> new lab sample id
    last_lbid_proc = f"{last_lbid} MB"
    processed_data["client_sample_id"] = last_lbid_proc
       
    #client_sample_id -> fixed lbid with mb 
    lbid_parts = lab_sample_id.split('-')
    wo = lbid_parts[0]
    consec = int(lbid_parts[1])   
    inc_lbid = f"{wo}-{consec+1:03d}"
    processed_data["inc_lab_sample_id"] = inc_lbid
    
    #lab_sample_id_orig -> lbid original to filter
    processed_data["lab_sample_id_orig"] =lab_sample_id
    
        
    
    insert_mb_samples(processed_data)
    

def process_mb_tests(data_to_process: dict):
    
    
    work_order = data_to_process.get("work_order")
    lab_sample_id = data_to_process.get("lab_sample_id")
    
    if (type(work_order) == str):
    
        last_lbid = select_last_labsampleid_by_wo(work_order, 'Sample_Tests')
    
    else:
        
        last_lbid = select_last_labsampleid_by_wo(str(work_order), 'Sample_Tests')
        
    fixed_csid = f"{lab_sample_id} MB"
        
        
    tests_mb_processed = {}
    
    
    tests_mb_processed["ClientSampleID"] = fixed_csid
    tests_mb_processed["LabAnalysisRefMethodID"] = data_to_process.get("analyte_group_id")
    tests_mb_processed["LabSampleID"] = data_to_process.get("lab_sample_id")
    tests_mb_processed["AnalyteName"] = data_to_process.get("analyte_name")
    tests_mb_processed["LabReportingBatchID"] = data_to_process.get("work_order")
    
    insert_mb_tests(tests_mb_processed)
    
    
    
def process_mb(data_to_process: dict):
    
    
    process_mb_samples(data_to_process)
    process_mb_tests(data_to_process)
    
    
    
    
    
    
    