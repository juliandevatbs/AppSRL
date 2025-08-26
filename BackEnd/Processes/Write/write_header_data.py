from Utils.merged_cell import merged_cell


def write_header_data(wb_destiny, header_data, n_row: int):

    sheet_to_write = wb_destiny["Reporte"]

    try:

        company_name= header_data[0]
        client_name = header_data[0]
        client_addres = header_data[1]
        lab_received_date = header_data[9]
        project_location = header_data[8]
        client_phone = header_data[4]


        first_line_to_print = n_row + 6
        second_line_to_print = n_row + 7
        third_line_to_print = n_row + 8
        fourth_line_to_print = n_row + 9
        

        merged_cell(sheet_to_write, f"K{second_line_to_print}", company_name)
        merged_cell(sheet_to_write, f"K{third_line_to_print}", client_name)
        merged_cell(sheet_to_write, f"K{fourth_line_to_print}", client_addres)
        merged_cell(sheet_to_write, f"AK{first_line_to_print}", lab_received_date)
        merged_cell(sheet_to_write, f"AK{third_line_to_print}", project_location)
        merged_cell(sheet_to_write, f"AK{fourth_line_to_print}", client_phone)


    except Exception as ex:

        print(f"ERROR: {ex}")


