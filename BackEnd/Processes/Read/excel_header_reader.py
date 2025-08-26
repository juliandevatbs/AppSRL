def excel_header_reader(wb_to_read):

    try:

        sheet_to_read = wb_to_read["Chain of Custody 1"]

        company_name = sheet_to_read["D4"].value
        addres = sheet_to_read["D5"].value
        city = sheet_to_read["D6"].value
        state = sheet_to_read["D7"].value
        phone = sheet_to_read["D8"].value
        zip = sheet_to_read["G7"].value
        code =  sheet_to_read["BA3"].value
        project_name = sheet_to_read["AY5"].value
        project_location = sheet_to_read["AY7"].value
        requested_due_date = sheet_to_read["AY11"].value
        sampled_by = sheet_to_read["B10"].value


        header_data = [company_name, addres, city, state, phone, zip, code, project_name, project_location, requested_due_date, sampled_by]

    except Exception as e:

        print(f"ERROR: {e}")


    return header_data







