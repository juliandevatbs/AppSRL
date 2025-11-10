import threading
import tkinter as tk
from tkinter import ttk

from BackEnd.Config.fields import INITIAL_DATA_FILTERS
from BackEnd.Database.Queries.Select.SelectDataByWo import SelectDataByWo
from BackEnd.Database.Queries.Select.SelectInitialData import SelectInitialData
from BackEnd.Database.Queries.Select.select_work_orders import select_work_orders
from BackEnd.Database.Queries.Select.select_analyte_names import select_analyte_names
from BackEnd.Database.Queries.Select.select_analyte_groups import select_analyte_groups
from BackEnd.Database.Queries.Filters.filter_queries import filter_queries
from BackEnd.Processes.DataFormatters.data_formatter import tuple_to_readable, data_formatter


class FilterManager:


    def __init__(self, parent, status_callback):
        self.parent = parent
        self.status_callback = status_callback
        self.filters = {}
        self.widgets = {}
        self.view_data_callback = None


        # Instances
        self.select_data_by_wo_instance = SelectDataByWo()
        self.selecte_initial_data_instance = SelectInitialData()

        # Data
        self.filters_data = None
        self.work_orders = None
        self.latest_work_order = None


    def set_initial_data(self, filters_initial_data: dict):


        if not isinstance(filters_initial_data, dict):
            return

        for key, value in filters_initial_data.items():

            if key not in self.widgets:
                continue

            widget = self.widgets[key]

            if key == 'LabReportingBatchID':
                if isinstance(widget, ttk.Combobox):

                    current_state = widget['state']

                    widget.config(state='normal')

                    widget['values'] = self.work_orders


                    str_value = str(value) if value is not None else ''

                    if str_value:

                        widget.set(str_value)
                        widget.update_idletasks()

                    widget.config(state=current_state)


                elif isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value) if value is not None else '')
                    widget.update_idletasks()

                continue
            if isinstance(widget, ttk.Combobox):

                current_state = widget['state']
                widget.config(state='normal')

                str_value = str(value) if value is not None else ''

                if str_value:
                    current_values = list(widget['values']) if widget['values'] else []

                    if str_value not in current_values:
                        current_values.append(str_value)
                        widget['values'] = current_values

                    widget.set(str_value)
                    widget.update_idletasks()

                widget.config(state=current_state)

            elif isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, str(value) if value is not None else '')
                widget.update_idletasks()

    def create_filter_frame(self, parent):
        """Crear frame de filtros sin scroll"""
        # Container principal
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame interno para los filtros
        filter_frame = ttk.LabelFrame(container, text="Search Parameters", padding=(10, 20))
        filter_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar widgets de filtro
        self._create_filter_widgets(filter_frame)

        return container, filter_frame



    def _create_filter_widgets(self, parent):

        # BUTTONS AND INPUTS


        # FIRST ROW --------------------------------------------------------------------------------------

        col = 0

        # Work Order
        ttk.Label(parent, text="Work Order:").grid(row=0, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['LabReportingBatchID'] = ttk.Combobox(parent, width=15)
        self.widgets['LabReportingBatchID'].grid(row=1, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Lab Sample ID
        ttk.Label(parent, text="LabSampleID:").grid(row=0, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['LabSampleID'] = ttk.Combobox(parent, width=15)
        self.widgets['LabSampleID'].grid(row=1, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Project name
        ttk.Label(parent, text="Project Name:").grid(row=0, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['ProjectName'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['ProjectName'].grid(row=1, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Project location
        ttk.Label(parent, text="Project Location:").grid(row=0, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['ProjectLocation'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['ProjectLocation'].grid(row=1, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Required Turnaround
        ttk.Label(parent, text="Required Turnaround:").grid(row=0, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['Date_Due'] = ttk.Combobox(parent, width=30, state="disabled")
        self.widgets['Date_Due'].grid(row=1, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Datetime Received
        ttk.Label(parent, text="Datetime Received:").grid(row=0, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['LabReceiptDate'] = ttk.Combobox(parent, width=30, state="disabled")
        self.widgets['LabReceiptDate'].grid(row=1, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Client contact
        ttk.Label(parent, text="Client contact:").grid(row=0, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['Contact'] = ttk.Combobox(parent, width=25, state="disabled")
        self.widgets['Contact'].grid(row=1, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # SECOND ROW ---------------------------------------------------------------------------------------------------

        col = 0

        # Contact email
        ttk.Label(parent, text="Contact email:").grid(row=2, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['Email'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['Email'].grid(row=3, column=col, padx=5, pady=(0, 5), sticky=tk.EW)

        col += 1

        # Contact mailing address
        ttk.Label(parent, text="Contact Mailing Address:").grid(row=2, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['Address_1'] = ttk.Combobox(parent, width=30, state="disabled")
        self.widgets['Address_1'].grid(row=3, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Zip
        ttk.Label(parent, text="Zip:").grid(row=2, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['Postal_Code'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['Postal_Code'].grid(row=3, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Contact phone
        ttk.Label(parent, text="Contact Phone:").grid(row=2, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['Phone'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['Phone'].grid(row=3, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Contact city
        ttk.Label(parent, text="Contact City:").grid(row=2, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['City'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['City'].grid(row=3, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # State
        ttk.Label(parent, text="State:").grid(row=2, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['State_Prov'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['State_Prov'].grid(row=3, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Client project location
        ttk.Label(parent, text="Client Project Location:").grid(row=2, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['ClientProjectLocation'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['ClientProjectLocation'].grid(row=3, column=col, padx=5, pady=(0, 5), sticky=tk.EW)


        # THIRD ROW --------------------------------------------------------------------------------------------------------
        col = 0

        # Matrix
        ttk.Label(parent, text="Matrix:").grid(row=4, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['MatrixID'] = ttk.Combobox(parent, width=20)
        self.widgets['MatrixID'].grid(row=5, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1


        # Analyte Name
        ttk.Label(parent, text="Analyte Name:").grid(row=4, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['analyte_name'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['analyte_name'].grid(row=5, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1

        # Analyte Group
        ttk.Label(parent, text="Analyte Group:").grid(row=4, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['analyte_group'] = ttk.Combobox(parent, width=20, state="disabled")
        self.widgets['analyte_group'].grid(row=5, column=col, padx=5, pady=(0, 5), sticky=tk.EW)
        col += 1





        # Clear Button
        ttk.Label(parent, text="").grid(row=4, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['clear_btn'] = ttk.Button(parent, text="Clear Filters", command=self.clear_filters, width=12)
        self.widgets['clear_btn'].grid(row=5, column=col, padx=5, pady=(0, 5), sticky=tk.EW)

        # Create sample
        ttk.Label(parent, text="").grid(row=4, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['create_sample'] = ttk.Button(parent, text="Create sample", command=self.clear_filters, width=12)
        self.widgets['create_sample'].grid(row=5, column=col, padx=5, pady=(0, 5), sticky=tk.EW)

        col += 1

        # View Button
        ttk.Label(parent, text="").grid(row=4, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['view_btn'] = ttk.Button(parent, text="View Data", command=self.view_data, width=12)
        self.widgets['view_btn'].grid(row=5, column=col, padx=5, pady=(0, 5), sticky=tk.EW)






        col += 1





        # Create sample tests
        ttk.Label(parent, text="").grid(row=4, column=col, padx=5, pady=(5, 0), sticky=tk.EW)
        self.widgets['sample_tests_btn'] = ttk.Button(parent, text="Add Sample tests", command=self.view_data, width=12)
        self.widgets['sample_tests_btn'].grid(row=5, column=col, padx=5, pady=(0, 5), sticky=tk.EW)



        # Configurar el grid para que se expanda uniformemente
        for i in range(7):  # 7 columnas en total
            parent.columnconfigure(i, weight=1, uniform="col")

        # Bind events
        self.widgets['LabReportingBatchID'].bind('<<ComboboxSelected>>', self.on_work_order_selected)
        self.widgets['LabSampleID'].bind('<<ComboboxSelected>>', self.on_sample_id_selected)
        self.widgets['analyte_name'].bind('<<ComboboxSelected>>', self.on_analyte_name_selected)
        self.widgets['analyte_group'].bind('<<ComboboxSelected>>', self.on_analyte_group_selected)



    def load_work_orders(self):

        self.selecte_initial_data_instance.load_connection()


        self.work_orders = tuple_to_readable(self.selecte_initial_data_instance.select_work_orders())

        if self.work_orders:
            # Select the last work order
            self.latest_work_order = self.work_orders[-1]


        self.selecte_initial_data_instance.close_connection()


    def refresh_filter_options(self):

        try:

            print("Filter options refreshed")

        except Exception as e:

            print(f"Error refreshing filter options: {e}")


    def load_data_by_wo(self, wo):


        try:

            self.select_data_by_wo_instance.load_connection()

            self.filters_data = data_formatter(self.select_data_by_wo_instance.select_login_data(wo), INITIAL_DATA_FILTERS)

            self.select_data_by_wo_instance.close_connection()

        except Exception as ex:

            print(f"Error loading data for the wo {wo}, \nError info: {ex}")

    def on_work_order_selected(self, event=None):

        selected_wo = self.widgets['LabReportingBatchID'].get()

        if selected_wo:

            self.status_callback(f"Work Order {selected_wo} selected")

            self.clear_filters(keep_work_order=True)

            self.load_data_by_wo(selected_wo)

            if self.filters_data:

                self.set_initial_data(self.filters_data)

            else:

                print(f"ERROR LOADING DATA, NO DATA SELECTED")

        if self.view_data_callback:

            self.view_data_callback()


    def initialize_with_latest_wo(self):

        if not self.latest_work_order:

            return

        self.load_data_by_wo(self.latest_work_order)

        if self.filters_data:

            self.set_initial_data(self.filters_data)
            self.status_callback(f"Loaded latest work order: {self.latest_work_order}")

        self.load_analytes_async(self.latest_work_order)


    def load_analytes_async(self, batch_id):

        """Cargar analitos de forma asíncrona"""
        self.status_callback("Loading analytes...")

        def load_data():
            try:
                analyte_names = select_analyte_names(batch_id)
                analyte_groups = select_analyte_groups(batch_id)
                sample_ids = filter_queries(batch_id)

                self.parent.after(0, self.update_filter_widgets, analyte_names, analyte_groups, sample_ids)
            except Exception as ex:
                self.parent.after(0, self.status_callback, f"Error loading analytes: {str(ex)}", True)

        thread = threading.Thread(target=load_data)
        thread.daemon = True
        thread.start()

    def update_filter_widgets(self, analyte_names, analyte_groups, sample_ids):

        if sample_ids:
            sample_ids = [str(item[0]) if isinstance(item, (tuple, list)) else str(item)
                          for item in sample_ids if item]
            unique_sample_ids = sorted(set(sample_ids))
            self.widgets['LabSampleID']['values'] = unique_sample_ids
        else:
            self.widgets['LabSampleID']['values'] = []

        # Actualizar Analyte Names
        if analyte_names:
            analyte_names = [str(item[0]) if isinstance(item, (tuple, list)) else str(item)
                             for item in analyte_names if item]
            unique_analyte_names = sorted(set(analyte_names))
            self.widgets['analyte_name']['values'] = unique_analyte_names
            self.widgets['analyte_name'].config(state='readonly')
        else:
            self.widgets['analyte_name']['values'] = []
            self.widgets['analyte_name'].config(state='disabled')

        # Actualizar Analyte Groups
        if analyte_groups:
            analyte_groups = [str(item[0]) if isinstance(item, (tuple, list)) else str(item)
                              for item in analyte_groups if item]
            unique_analyte_groups = sorted(set(analyte_groups))
            self.widgets['analyte_group']['values'] = unique_analyte_groups
            self.widgets['analyte_group'].config(state='readonly')
        else:
            self.widgets['analyte_group']['values'] = []
            self.widgets['analyte_group'].config(state='disabled')

        self.status_callback("Analytes loaded successfully")

    def on_sample_id_selected(self, event=None):
        selected_id = self.widgets['LabSampleID'].get()
        if selected_id:
            self.filters['LabSampleID'] = selected_id
        elif 'sample_id' in self.filters:
            del self.filters['LabSampleID']

    def on_analyte_name_selected(self, event=None):
        selected_name = self.widgets['analyte_name'].get()
        if selected_name:
            self.filters['analyte_name'] = selected_name
        elif 'analyte_name' in self.filters:
            del self.filters['analyte_name']

    def on_analyte_group_selected(self, event=None):
        selected_group = self.widgets['analyte_group'].get()
        if selected_group:
            self.filters['analyte_group'] = selected_group
        elif 'analyte_group' in self.filters:
            del self.filters['analyte_group']

    def clear_filters(self, keep_work_order=False):
        """Limpiar todos los filtros"""
        if not keep_work_order:
            self.widgets['LabReportingBatchID'].set('')

        self.widgets['LabSampleID'].set('')
        self.widgets['analyte_name'].set('')
        self.widgets['analyte_group'].set('')
        self.filters = {}

        self.status_callback("Filters cleared")

    def view_data(self):
        """Obtener datos de filtros para la búsqueda"""
        work_order = self.widgets['LabReportingBatchID'].get().strip()
        if not work_order:
            return None, self.filters

        try:
            batch_id = int(work_order)
            return batch_id, self.filters.copy()
        except ValueError:
            return None, self.filters

    def set_view_data_callback(self, callback):
        """Configurar el callback para el botón View Data"""
        self.view_data_callback = callback
        self.widgets['view_btn'].config(command=callback)

    def set_view_button_state(self, state, text):
        """Establecer estado del botón View Data"""
        self.widgets['view_btn'].config(state=state, text=text)