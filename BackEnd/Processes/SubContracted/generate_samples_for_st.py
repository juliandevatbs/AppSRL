# This function generates the sample for the sample tests readed of the subcontracted

from BackEnd.Database.Queries.Select.select_last_lab_reporting_batch_id import select_last_lab_reporting_batch_id


def detect_sample_type(client_sample_id: str) -> str:
    
    id_upper = client_sample_id.upper()
    
    if "BLANK" in id_upper:
        return "MB"
    if "LCS" in id_upper:
        return "LCS"
    if id_upper.endswith("MSD"):
        return "MSD"
    if id_upper.endswith("MS"):
        return "MS"
    if "DUP" in id_upper:
        return "DUP"
    return "N"



def generate_samples_for_st(sample_tests: list) -> list:

    print(sample_tests)

    samples_to_create = []
    
    lrbi = select_last_lab_reporting_batch_id() + 1
    
    sample_id_counter = 0
    
    for row in sample_tests:
        
        sample_id_counter += 1
        
        item_id = sample_id_counter
        
        lab_sample_id = f"{lrbi}-{sample_id_counter:03d}"
        
        client_sample_id = row[0]
        matrix_id = row[17]
        date_collected = row[19]
        lab_id = row[3]
        
        sample_type = detect_sample_type(str(client_sample_id))
        
        
        
        sample = [
            item_id,          # consecutivo interno
            lrbi,             # batch id
            lab_sample_id,    # SampleNumber (ej: 2508039-001)
            client_sample_id, # ID crudo del Excel
            matrix_id,        # matriz
            date_collected,   # fecha de colección
            sample_type,      # NORMAL / MB / LCS / MS / MSD / DUP
            lab_id            # opcional si lo quieres guardar
        ]

        
        
        
        
        
        
        
    

        samples_to_create.append(sample)
    print(samples_to_create)
    return samples_to_create