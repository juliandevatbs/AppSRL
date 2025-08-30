# This function generates the sample for the sample tests readed of the subcontracted

from BackEnd.Database.Queries.Select.select_last_lab_reporting_batch_id import select_last_lab_reporting_batch_id


def generate_samples_for_st(sample_tests: list) -> list:
    
    samples_to_create = []
    
    lrbi = select_last_lab_reporting_batch_id()
    
    
    for row in sample_tests:
        
        sample_id_counter = 1
        
        sample = []
    
        # Data from the excel subcontrated
        
        lab_sample_id = f"{lrbi}-{sample_id_counter:03d}"

        client_sample_id = row[0]
        matrix_id = row[17]
        date_collected = row[16]
        lab_id = row[3]
        
        
        
        
        sample.append(lrbi)
        sample.append(client_sample_id)
        sample.append(matrix_id)
        sample.append(date_collected)
        sample.append(lab_id)
        
        sample_id_counter += 1
        

        samples_to_create.append(sample)
    
    return samples_to_create