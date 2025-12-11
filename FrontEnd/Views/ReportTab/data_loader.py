import threading
from BackEnd.Database.Queries.Select.select_samples import select_samples
from BackEnd.Database.Queries.Select.select_parameters import select_parameters


class DataLoader:
    def __init__(self, parent, status_callback):
        self.parent = parent
        self.status_callback = status_callback
        self.is_loading = False

    def load_data_async(self, batch_id, filters, callback):

        # Charge data asincronously

        if self.is_loading:

            return

        self.is_loading = True

        self.status_callback("Loading data... Please wait")

        def load_data():

            try:

                sample_id = filters.get('LabSampleID')

                analyte_name = filters.get('analyte_name')

                analyte_group = filters.get('analyte_group')

                sample_data = select_samples(batch_id, [], sample_id, True)

                parameters_data = select_parameters(batch_id, [], sample_id, analyte_name, analyte_group)

                self.parent.after(0, callback, sample_data, parameters_data, None)

            except Exception as ex:

                error_msg = f"Database error: {str(ex)}"

                self.parent.after(0, callback, None, None, error_msg)

            finally:

                self.is_loading = False

        thread = threading.Thread(target=load_data)

        thread.daemon = True

        thread.start()
