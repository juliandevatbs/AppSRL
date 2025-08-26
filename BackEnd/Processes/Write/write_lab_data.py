from Utils.merged_cell import merged_cell


def write_lab_data(wb, data: list, start_row, client_sample_id):
    sheet_to_write = wb["Reporte"]
    start_row = start_row + 2

    #print(f"START ROW PARA LAB DATA {start_row}")
    
    
    
    print(data)
    try:
        for row in data:
            important_data = row

            if len(important_data) > 0:
                # Generar el ID consecutivo
                
                item = important_data[0]
                formatted_id = important_data[2]
                client_sample_id = important_data[3]
                collected = important_data[4]
                sample_matrix = important_data[5]
                analysis_requested = important_data[-1]

                # Escribir cada dato en su columna correspondiente
                sheet_to_write[f"G{start_row}"].value = formatted_id  # ID consecutivo
                sheet_to_write[f"B{start_row}"].value = item
                sheet_to_write[f"K{start_row}"].value = client_sample_id
                sheet_to_write[f"Q{start_row}"].value = collected
                #sheet_to_write[f"U{start_row}"].value = collected_time
                sheet_to_write[f"X{start_row}"].value = sample_matrix
                sheet_to_write[f"AC{start_row}"].value = analysis_requested

                start_row += 1
        return start_row + 2

    except Exception as ex:
        print(f"Error: {ex}")