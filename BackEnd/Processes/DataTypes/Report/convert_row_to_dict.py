def row_to_dicts(rows, columns):
    
    
    if not rows:
        
        return []
    
    result = []
    
    for row in rows:
        
        row_dict = {}
        
        
        if hasattr(row, 'keys') and callable(row.keys):
            
            for key in row.keys():
                
                row_dict[key] = row[key]
                
        else:
            
            for i, col in enumerate(columns):
                
                row_dict[col] = row[i] if i < len(row) else ''
            
            result.append(row_dict)
            
    return result           
                
        
        