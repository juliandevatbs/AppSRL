import datetime

def process_main(data:list, data_type: str):

    if data_type == 'test':

        return process_tests(data)

    return process_samples(data)



def process_samples(data:list):


    print(f"Sample data {data}")

    date_time = data[5]

    if date_time is None or date_time == "" or str(date_time).lower() in ["nan", "null"]:
        processed_date = "No date provided"

    elif (isinstance(date_time, datetime.datetime)):
        processed_date = date_time.strftime("%d/%m/%Y %H:%M")

    elif (isinstance(date_time, str)):
        value = date_time.strip()
        date_formats = [
            "%m/%d/%Y %H:%M",  # 08/18/2025 10:15
            "%d/%m/%Y %H:%M",  # 18/08/2025 10:15
            "%Y-%m-%d %H:%M",  # 2025-08-18 10:15
            "%Y-%m-%d",  # 2025-08-30
            "%d/%m/%Y",  # 30/08/2025
            "%m/%d/%Y",  # 08/30/2025
            "%d-%m-%Y",  # 30-08-2025
            "%Y/%m/%d",
        ]

        processed_date = "No date provided"  # Cambiado aquí

        for fmt in date_formats:
            try:
                dt = datetime.datetime.strptime(value, fmt)
                processed_date = dt.strftime("%d/%m/%Y %H:%M")
                break
            except ValueError:
                continue

    else:
        processed_date = "No date provided"

    data[5] = processed_date
    return data



def process_tests(data: list):
    date_time = data[16]

    if date_time is None or date_time == "" or str(date_time).lower() in ["nan", "null"]:
        processed_date = "No date provided"

    elif (isinstance(date_time, datetime.datetime)):
        processed_date = date_time.strftime("%d/%m/%Y %H:%M")

    elif (isinstance(date_time, str)):
        value = date_time.strip()
        date_formats = [
            "%m/%d/%Y %H:%M",  # 08/18/2025 10:15
            "%d/%m/%Y %H:%M",  # 18/08/2025 10:15
            "%Y-%m-%d %H:%M",  # 2025-08-18 10:15
            "%Y-%m-%d",  # 2025-08-30
            "%d/%m/%Y",  # 30/08/2025
            "%m/%d/%Y",  # 08/30/2025
            "%d-%m-%Y",  # 30-08-2025
            "%Y/%m/%d",
        ]

        processed_date = "No date provided"  # Cambiado aquí

        for fmt in date_formats:
            try:
                dt = datetime.datetime.strptime(value, fmt)
                processed_date = dt.strftime("%d/%m/%Y %H:%M")
                break
            except ValueError:
                continue

    else:
        processed_date = "No date provided"

    data[16] = processed_date
    return data