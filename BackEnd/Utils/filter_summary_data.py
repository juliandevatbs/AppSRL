def filter_summary_data(data):
    filtered_samples = {}
    
    # Process samples
    for sample_id, param_list in data.items():
        #print(f"Processing sample_id: {sample_id}")
        
        filtered_params = []
        for param in param_list:
            try:
                # Handle case where param[4] or param[8] might be None
                value1 = float(param[5]) if param[5] is not None else 0.0
                value2 = float(param[9]) if param[9] is not None else 0.0
                print(f"  Comparing: {value1} > {value2}")
                
                if value1 > value2:
                    filtered_params.append(param)
            except (IndexError, ValueError, TypeError) as e:
                #print(f"  Error processing param: {param}")
                print(f"  Error details: {e}")
        
        if filtered_params:
            filtered_samples[sample_id] = filtered_params
            #print(f"  Added {len(filtered_params)} parameters for sample {sample_id}")
        else:
            print(f"  No parameters met the condition for sample {sample_id}")
            
    return filtered_samples