from BackEnd.Database.Queries.Insert.mb_qc.insert_mb_samples import insert_mb_samples
from BackEnd.Database.Queries.Insert.mb_qc.insert_mb_tests import insert_mb_tests
from BackEnd.Database.Queries.Select.select_last_labsampleid_by_wo import select_last_labsampleid_by_wo


def process_mb_samples(data_to_process: dict) :
    
    
    processed_data = {}
    
    # get the last labsampleid from the wo
    
    work_order = data_to_process.get("work_order")
    lab_sample_id = data_to_process.get("lab_sample_id")
    
    if (type(work_order) == str):
    
        last_lbid = select_last_labsampleid_by_wo(work_order, 'Samples')
    
    else:
        
        last_lbid = select_last_labsampleid_by_wo(str(work_order), 'Samples')
        


    print(f"ULTOMO LAST LAB SAMPLE ID PARA INCREMENTAR {last_lbid}")

       
    #client_sample_id -> fixed lbid with mb 
    lbid_parts = last_lbid.split('-')
    wo = lbid_parts[0]
    consec = int(lbid_parts[1])   
    inc_lbid = f"{wo}-{consec+1:03d}"
    processed_data["inc_lab_sample_id"] = inc_lbid

    # inc_lab_sample_id -> new lab sample id

    last_lbid_proc = f"{wo}-{consec+1:03d} MB"
    processed_data["client_sample_id"] = last_lbid_proc

    
    #lab_sample_id_orig -> lbid original to filter
    processed_data["lab_sample_id_orig"] =lab_sample_id
    processed_data["work_order"] = work_order


    return processed_data
    
        
    


def process_mb_tests(data_to_process: dict):
    
    
    work_order = data_to_process.get("work_order")
    lab_sample_id = data_to_process.get("lab_sample_id")
    
    if (type(work_order) == str):
    
        last_lbid = select_last_labsampleid_by_wo(work_order, 'Samples')
    
    else:
        
        last_lbid = select_last_labsampleid_by_wo(str(work_order), 'Samples')
        





    lbid_parts = last_lbid.split('-')
    wo = lbid_parts[0]
    consec = int(lbid_parts[1])
    inc_lbid = f"{wo}-{consec + 1:03d}"

    fixed_csid = f"{inc_lbid} MB"



        
    tests_mb_processed = {}
    
    
    tests_mb_processed["work_order"] = work_order
    tests_mb_processed["ClientSampleID"] = fixed_csid
    tests_mb_processed["LabAnalysisRefMethodID"] = data_to_process.get("analyte_group_id")
    tests_mb_processed["LabSampleID"] = inc_lbid
    tests_mb_processed["AnalyteName"] = data_to_process.get("analyte_name")
    tests_mb_processed["LabReportingBatchID"] = data_to_process.get("work_order")


    return tests_mb_processed
    

    
    
def process_mb(data_to_process: dict):
    
    
    samples_to_create = process_mb_samples(data_to_process)
    tests_to_create = process_mb_tests(data_to_process)

    insert_mb_samples(samples_to_create)
    insert_mb_tests(tests_to_create)
    
    
    
    
    
    
    