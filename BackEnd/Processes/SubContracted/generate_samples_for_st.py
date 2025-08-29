# This function generates the sample for the sample tests readed of the subcontracted

def generate_samples_for_st(sample_tests: list) -> list:
    
    samples_to_create = []
    
    for row in sample_tests:
        
        sample = []
    
        # Data from the excel subcontrated
        client_sample_id = row[0]
        matrix_id = row[17]
        date_collected = row[16]
        lab_id = row[3]
        
        
        
        sample.append(client_sample_id)
        sample.append(matrix_id)
        sample.append(date_collected)
        sample.append(lab_id)
        

        samples_to_create.append(sample)
    
    return samples_to_create