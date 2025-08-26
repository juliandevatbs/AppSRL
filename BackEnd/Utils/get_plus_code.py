def get_plus_code (wb_to_read):
    
    
    ws_to_read = wb_to_read["Chain of Custody 1"]
    
    code = ws_to_read["BA3"].value
    
    if code:
        
        return code
    
    else:
        
        return False
    
    
    