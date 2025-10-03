from pathlib import Path
import sys
import threading
from tkinter import messagebox, ttk
import tkinter as tk


PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from BackEnd.Database.Queries.Select.select_work_orders import select_work_orders
from FrontEnd.Functions.sample_test_wizard import SampleTestsWizard
from FrontEnd.Functions.sample_wizard import SampleWizard
from FrontEnd.Views.create_qc_view import CreateQc
from BackEnd.Database.Queries.Filters.filter_queries import filter_queries
from BackEnd.Database.Queries.Select.select_parameters import select_parameters
from BackEnd.Database.Queries.Select.select_samples import select_samples
from BackEnd.Processes.execute_report_generation import execute_report_generation
from BackEnd.Database.Queries.Select.select_analyte_groups import select_analyte_groups
from BackEnd.Database.Queries.Select.select_analyte_names import select_analyte_names


class ReportTab(ttk.Frame):
    def __init__(self, parent):
        """Create the Report tab with data viewing functionality"""
        super().__init__(parent)

        # Variables de estado
        self.is_loading = False
        self.root = parent
        self.main_frame = self
        self.db_thread_pool = []
        self.current_batch_id = None
        self.current_lab_sample_id = None
        self.last_valid_batch_id = None
        self.data_loaded = False
        self.work_order_combobox = None

        # Configuración inicial
        self.setup_ui()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Estilo
        style = ttk.Style()
        style.configure("Excel.Treeview",
                        borderwidth=2,
                        relief="solid",
                        fieldbackground="white",
                        background="white",
                        foreground="black")

        # Barra de estado
        self.status_label = ttk.Label(self, text="Ready")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Marco de búsqueda
        search_frame = ttk.LabelFrame(self, text="Search Parameters", padding=10)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        # Configurar campos de búsqueda
        self.setup_search_fields(search_frame)

        # Configurar menú de acciones
        self.create_actions_menu(search_frame)

        # Marco de resultados
        results_frame = ttk.Frame(self)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Notebook para múltiples tablas
        results_notebook = ttk.Notebook(results_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)

        # Configurar tablas
        self.setup_tables(results_notebook)

        # Botones de acción
        self.setup_action_buttons()
    
    def reset_all_filters(self):
        
        self.analyte_name_combobox.set('')
        self.analyte_name_combobox['values'] = []
        self.analyte_name_combobox.config(state='disabled')
        
        self.analyte_group_combobox.set('')
        self.analyte_group_combobox['values'] = []
        self.analyte_group_combobox.config(state='disabled')
        
        self.lab_sample_id_entry.set('')
        self.lab_sample_id_entry['values'] = []
        self.lab_sample_id_entry.config(state='disabled')
        
        # Limpiar tablas
        self.clear_tables_gui()
        
        # Resetear variables de estado
        self.current_batch_id = None
        self.current_lab_sample_id = None
        self.data_loaded = False
        
        # Actualizar estado
        self.update_status("All filters reset")
        
        
        
    def load_work_orders(self):
        """Cargar work orders disponibles en el combobox"""
        try:
            work_orders = select_work_orders()
            if work_orders:
                # Extraer solo los IDs y eliminar duplicados
                unique_orders = sorted(set([str(wo[0]) for wo in work_orders]))
                self.work_order_combobox['values'] = unique_orders
            else:
                self.work_order_combobox['values'] = []
                self.update_status("No work orders found", error=True)
        except Exception as e:
            self.update_status(f"Error loading work orders: {str(e)}", error=True)
            print(f"Error loading work orders: {e}")
            
    def load_analyte_names(self):
        
        
        
        
        return True
    
    
    
    def load_analyte_id(self):
        
        
        
        return True
            
    def on_work_order_selected(self, event=None):
        """Manejar selección de work order"""
        
        selected_wo = self.work_order_combobox.get()
        
        if selected_wo:
            
            self.reset_all_filters()  

            self.update_status(f"Work Order {selected_wo} selected")
            
            self.load_analytes_async(selected_wo)
    
    def load_analytes_async(self, batch_id):
        
        if self.is_loading:
            return 
        
        thread = threading.Thread(target=self.execute_analytes_loading, args=(batch_id, ))
        thread.daemon = True
        self.db_thread_pool.append(thread)
        thread.start()
        
    def execute_analytes_loading(self, batch_id):
        
        try:
            
            
            analyte_names = select_analyte_names(batch_id)
            analyte_groups = select_analyte_groups(batch_id)
            
            self.root.after(0, self.update_analyte_comboboxes, analyte_names, analyte_groups)
            
        except Exception as ex:
            
            error_msg = f"Error loading analytes: {str(ex)}"
            self.root.after(0, self.update_status, error_msg, True)
    
    def update_analyte_comboboxes(self, analyte_names, analyte_groups):
        """Actualizar y habilitar comboboxes de analitos"""
        
        # If functions return flat lists (just the values)
        if analyte_names:
            self.analyte_name_combobox['values'] = analyte_names
            self.analyte_name_combobox.config(state='normal')
            self.analyte_name_combobox.set('')
        else:
            self.analyte_name_combobox['values'] = []
            self.analyte_name_combobox.config(state='disabled')
        
        if analyte_groups:
            self.analyte_group_combobox['values'] = analyte_groups
            self.analyte_group_combobox.config(state='normal')
            self.analyte_group_combobox.set('')
        else:
            self.analyte_group_combobox['values'] = []
            self.analyte_group_combobox.config(state='disabled')
            
    def on_analyte_name_selected(self, event=None):
        """Manejar selección de Analyte Name"""
        selected_analyte = self.analyte_name_combobox.get()
        if selected_analyte and self.data_loaded:
            self.filter_by_analyte_name(selected_analyte)

    def on_analyte_name_changed(self, event=None):
        """Manejar cambios en Analyte Name"""
        analyte_text = self.analyte_name_combobox.get().strip()
        if not analyte_text and self.data_loaded and self.current_batch_id:
            # Si se borra el filtro, recargar datos
            self.reload_batch_data()
    
    def on_analyte_group_selected(self, event=None):
        """Manejar selección de Analyte Group"""
        selected_group = self.analyte_group_combobox.get()
        if selected_group and self.data_loaded:
            self.filter_by_analyte_group(selected_group)

    def on_analyte_group_changed(self, event=None):
        """Manejar cambios en Analyte Group"""
        group_text = self.analyte_group_combobox.get().strip()
        if not group_text and self.data_loaded and self.current_batch_id:
            # Si se borra el filtro, recargar datos
            self.reload_batch_data()
    

    def setup_search_fields(self, search_frame):
        
        """Configurar campos de búsqueda"""
        
        # Work Order / LabReportingBatchID Selector
        ttk.Label(search_frame, text="Work Order:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.work_order_combobox = ttk.Combobox(search_frame, width=25, state="readonly")
        self.work_order_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.work_order_combobox.bind('<<ComboboxSelected>>', self.on_work_order_selected)
        
        # LabSampleID
        ttk.Label(search_frame, text="LabSampleID:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.lab_sample_id_entry = ttk.Combobox(search_frame, width=25, values=[], state="normal")
        self.lab_sample_id_entry.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        self.lab_sample_id_entry.bind('<<ComboboxSelected>>', self.on_sample_id_selected)
        self.lab_sample_id_entry.bind('<KeyRelease>', self.on_sample_id_changed)
        
        #AnalyteName
        ttk.Label(search_frame, text="Analyte Name:").grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        self.analyte_name_combobox = ttk.Combobox(search_frame, width=25, values=[], state="normal")
        self.analyte_name_combobox.grid(row=0, column=7, padx=5, pady=5, sticky=tk.W)
        self.analyte_name_combobox.bind('<<ComboboxSelected>>', self.on_analyte_name_selected)
        self.analyte_name_combobox.bind('<KeyRelease>', self.on_analyte_name_changed)
        
        #Analyte group ID
        ttk.Label(search_frame, text="Analyte group ID:").grid(row=0, column=8, padx=5, pady=5, sticky=tk.W)
        self.analyte_group_combobox = ttk.Combobox(search_frame, width=25, values=[], state="disabled")  # ¡CORRECTO!
        self.analyte_group_combobox.grid(row=0, column=9, padx=5, pady=5, sticky=tk.W)
        self.analyte_group_combobox.bind('<<ComboboxSelected>>', self.on_analyte_group_selected)  # Evento correcto
        self.analyte_group_combobox.bind('<KeyRelease>', self.on_analyte_group_changed)
        
        # Botón View Data
        self.view_data_btn = ttk.Button(search_frame, text="View Data", style='Primary.TButton',
                                        command=self.view_data_wrapper, cursor="hand2", width=20)
        self.view_data_btn.grid(row=0, column=10, padx=(25, 5), pady=5)
        
        # Cargar work orders al iniciar
        self.load_work_orders()

    def setup_tables(self, notebook):
        """Configurar las tablas de datos"""
        # Tabla 1 - Sample Data
        table1_frame = ttk.Frame(notebook)
        notebook.add(table1_frame, text="Sample Data")
        self.table1 = self.create_table(table1_frame,
                                        columns=(
                                        'Include', 'itemID', 'LabReportingBatchID', 'LabSampleID', 'ClientSampleID',
                                        'Sampler', 'Datecollected', 'MatrixID','Temperature',
                                        'ShippingBatchID', 'CollectMethod', 'CollectionAgency', 'AdaptMatrixID',
                                        'LabID'),
                                        select_all_var_name="select_all_var1")

        # Tabla 2 - Sample Tests
        table2_frame = ttk.Frame(notebook)
        notebook.add(table2_frame, text="Sample Tests")
        self.table2 = self.create_table(table2_frame,
                                        columns=("Include", "SampleTestsID", "ClientSampleID", "LabAnalysisRefMethodID",
                                                 "LabSampleID", "AnalyteName", "Result", "ResultUnits",
                                                 "DetectionLimit",
                                                 "Dilution", "ReportingLimit", "ProjectName", "DateCollected",
                                                 "MatrixID",
                                                 "AnalyteType", "LabReportingBatchID", "Notes", "Sampler", "Analyst"),
                                        select_all_var_name="select_all_var2")

    def create_table(self, parent, columns, select_all_var_name):
        """Crear una tabla con scrollbars y checkbox de selección múltiple"""
        # Frame para seleccionar todos
        select_all_frame = ttk.Frame(parent)
        select_all_frame.pack(fill=tk.X, padx=5, pady=2)

        # Variable y checkbox para seleccionar todos
        setattr(self, select_all_var_name, tk.BooleanVar())
        select_all_cb = ttk.Checkbutton(select_all_frame, text="Select All",
                                        variable=getattr(self, select_all_var_name),
                                        command=lambda: self.toggle_all_checkboxes(
                                            getattr(self, f"table{1 if '1' in select_all_var_name else '2'}")))
        select_all_cb.pack(side=tk.LEFT)

        # Contenedor para tabla y scrollbars
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)

        # Crear tabla
        table = ttk.Treeview(table_container, style="Bordered.Treeview",
                             columns=columns, show='headings', selectmode='extended')

        # Configurar columnas
        
        column_configs = {
            'Include': {'width': 80, 'anchor': tk.CENTER, 'text': 'Include'},
            'itemID': {'width': 80, 'anchor': tk.CENTER, 'text': 'itemID'},
            'LabReportingBatchID': {'width': 150, 'anchor': tk.CENTER, 'text': 'LabReportingBatchID'},
            'ClientSampleID': {'width': 120, 'anchor': tk.CENTER, 'text': 'ClientSampleID'},
            'LabSampleID': {'width': 120, 'anchor': tk.W, 'text': 'LabSampleID'},
            'Sampler': {'width': 100, 'anchor': tk.CENTER, 'text': 'Sampler'},
            'Datecollected': {'width': 120, 'anchor': tk.CENTER, 'text': 'Datecollected'},
            'MatrixID': {'width': 100, 'anchor': tk.CENTER, 'text': 'MatrixID'},
            'AnalysisMethodIDs': {'width': 200, 'anchor': tk.CENTER, 'text': 'AnalysisMethodIDs'},
            'Temperature': {'width': 80, 'anchor': tk.CENTER, 'text': 'Temperature'},
            'ShippingBatchID': {'width': 100, 'anchor': tk.CENTER, 'text': 'ShippingBatchID'},
            'CollectMethod': {'width': 100, 'anchor': tk.CENTER, 'text': 'CollectMethod'},
            'CollectionAgency': {'width': 100, 'anchor': tk.CENTER, 'text': 'CollectionAgency'},
            'AdaptMatrixID': {'width': 100, 'anchor': tk.CENTER, 'text': 'AdaptMatrixID'},
            'LabID': {'width': 100, 'anchor': tk.CENTER, 'text': 'LabID'},
            'SampleTestsID': {'width': 120, 'anchor': tk.CENTER, 'text': 'SampleTestsID'},
            'LabAnalysisRefMethodID': {'width': 250, 'anchor': tk.CENTER, 'text': 'LabAnalysisRefMethodID'},
            'AnalyteName': {'width': 200, 'anchor': tk.CENTER, 'text': 'AnalyteName'},
            'Result': {'width': 100, 'anchor': tk.CENTER, 'text': 'Result'},
            'ResultUnits': {'width': 100, 'anchor': tk.CENTER, 'text': 'ResultUnits'},
            'DetectionLimit': {'width': 120, 'anchor': tk.CENTER, 'text': 'DetectionLimit'},
            'Dilution': {'width': 80, 'anchor': tk.CENTER, 'text': 'Dilution'},
            'ReportingLimit': {'width': 120, 'anchor': tk.CENTER, 'text': 'ReportingLimit'},
            'ProjectName': {'width': 250, 'anchor': tk.CENTER, 'text': 'ProjectName'},
            'DateCollected': {'width': 200, 'anchor': tk.CENTER, 'text': 'DateCollected'},
            'AnalyteType': {'width': 100, 'anchor': tk.CENTER, 'text': 'AnalyteType'},
            'Notes': {'width': 350, 'anchor': tk.CENTER, 'text': 'Notes'},
            'Analyst': {'width': 100, 'anchor': tk.CENTER, 'text': 'Analyst'}
        }

        for col in columns:
            table.heading(col, text=column_configs[col]['text'])
            table.column(col, width=column_configs[col]['width'], anchor=column_configs[col]['anchor'])

        # Scrollbars
        scrollbar_v = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=table.yview)
        scrollbar_h = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=table.xview)
        table.configure(yscroll=scrollbar_v.set, xscroll=scrollbar_h.set)

        # Posicionamiento
        table.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')

        # Configurar expansión
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Bind eventos
        table.bind('<ButtonRelease-1>', self.handle_checkbox_click)

        return table

    def setup_action_buttons(self):
        """Configurar botones de acción"""
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        # Botón Generate Report
        self.report_btn = ttk.Button(action_frame, text="Generate Report", style='Success.TButton',
                                     command=self.generate_report_wrapper)
        self.report_btn.pack(side=tk.LEFT, padx=5)

        # Botón Clear Results
        clear_btn = ttk.Button(action_frame, text="Clear Results", style='Danger.TButton',
                               command=self.clear_results)
        clear_btn.pack(side=tk.RIGHT, padx=5)

    def on_batch_id_changed(self, event=None):
        """Manejar cambios en el campo de batch ID"""
        batch_id_text = self.lab_sample_id_entry.get().strip()

        if not batch_id_text:
            self.lab_sample_id_entry.config(state='disabled')
            self.lab_sample_id_entry.set('')
            self.lab_sample_id_entry['values'] = []
            return

        try:
            batch_id_int = int(batch_id_text)
            self.lab_sample_id_entry.config(state='normal')

            # Si el batch ID es válido y ha cambiado, cargar los sample IDs disponibles
            if batch_id_int != self.last_valid_batch_id:
                self.last_valid_batch_id = batch_id_int
                self.load_sample_ids_async(batch_id_int)

        except ValueError:
            self.lab_sample_id_entry.config(state='disabled')
            self.lab_sample_id_entry.set('')
            self.lab_sample_id_entry['values'] = []

    def load_sample_ids_async(self, batch_id):
        """Cargar sample IDs de forma asíncrona"""
        if self.is_loading:
            return

        thread = threading.Thread(target=self.execute_sample_ids_loading, args=(batch_id,))
        thread.daemon = True
        self.db_thread_pool.append(thread)
        thread.start()

    def execute_sample_ids_loading(self, batch_id):
        """Ejecutar carga de sample IDs en hilo separado"""
        try:
            sample_ids = filter_queries(batch_id)
            self.root.after(0, self.update_sample_ids_combobox, sample_ids)
        except Exception as ex:
            error_msg = f"Error loading sample IDs: {str(ex)}"
            self.root.after(0, self.update_status, error_msg, True)

    def update_sample_ids_combobox(self, sample_ids):
        """Actualizar combobox con sample IDs"""
        if sample_ids:
            self.lab_sample_id_entry['values'] = [str(x[0]) for x in sample_ids]
            self.lab_sample_id_entry.config(state='normal')
        else:
            self.lab_sample_id_entry['values'] = []
            self.lab_sample_id_entry.config(state='disabled')

    def on_sample_id_selected(self, event=None):
        """Manejar selección de sample ID"""
        selected_sample_id = self.lab_sample_id_entry.get()
        if selected_sample_id and self.data_loaded:
            self.filter_by_sample_id(selected_sample_id)
            self.update_analyte_combobox(selected_sample_id)

    def on_sample_id_changed(self, event=None):
        """Manejar cambios en el sample ID"""
        sample_id_text = self.lab_sample_id_entry.get().strip()

        # Si se borra el sample ID, recargar todos los datos del batch
        if not sample_id_text and self.data_loaded and self.current_batch_id:
            self.load_data_async(self.current_batch_id, None)

    def validate_batch_id(self, event=None):
        """Validar batch ID y cargar datos si es válido"""
        batch_id_text = self.lab_sample_id_entry.get().strip()

        if not batch_id_text:
            self.lab_sample_id_entry.config(state='disabled')
            self.lab_sample_id_entry.set('')
            self.lab_sample_id_entry['values'] = []
            return

        try:
            batch_id_int = int(batch_id_text)
            self.lab_sample_id_entry.config(state='normal')

            # Si el batch ID es válido y ha cambiado, cargar datos automáticamente
            if batch_id_int != self.current_batch_id:
                self.view_data_wrapper()

        except ValueError:
            self.lab_sample_id_entry.config(state='disabled')
            self.lab_sample_id_entry.set('')
            self.lab_sample_id_entry['values'] = []

    def update_status(self, message, error=False):
        """Actualizar mensaje de estado"""
        self.status_label.config(text=message)
        if error:
            self.status_label.config(foreground='#ff6b6b')
            self.root.after(5000, lambda: self.status_label.config(foreground='SystemWindowText'))
        else:
            self.status_label.config(foreground='SystemWindowText')

    def filter_by_sample_id(self, sample_id):
        """Filtrar datos por sample ID"""
        try:
            batch_id = self.current_batch_id
            if not batch_id:
                return

            self.load_filtered_data_async(batch_id, sample_id)

        except Exception as e:
            messagebox.showerror("Error", f"Error filtering by sample ID: {str(e)}")

    def update_analyte_comboboxes(self, analyte_names, analyte_groups):
        """Actualizar y habilitar comboboxes de analitos"""
        
        # Habilitar los combobox una vez que tenemos datos
        if analyte_names:
            self.analyte_name_combobox['values'] = [str(x[0]) for x in analyte_names]
            self.analyte_name_combobox.config(state='normal')
            self.analyte_name_combobox.set('')  # Limpiar selección
        else:
            self.analyte_name_combobox['values'] = []
            self.analyte_name_combobox.config(state='disabled')
        
        if analyte_groups:
            self.analyte_group_combobox['values'] = [str(x[0]) for x in analyte_groups]
            self.analyte_group_combobox.config(state='normal')
            self.analyte_group_combobox.set('')  # Limpiar selección
        else:
            self.analyte_group_combobox['values'] = []
            self.analyte_group_combobox.config(state='disabled')

    def reload_batch_data(self):
        """Recargar todos los datos del batch actual"""
        if hasattr(self, 'current_batch_id') and self.current_batch_id:
            self.load_data_async(self.current_batch_id, "")

    def load_filtered_data_async(self, batch_id, sample_id=None, analyte_name=None, analyte_group=None):
        """Cargar datos filtrados de forma asíncrona"""
        if self.is_loading:
            return
            
        self.is_loading = True
        
        # Mensaje descriptivo del filtro
        filter_text = f"Filtering data"
        if sample_id:
            filter_text += f" for Sample: {sample_id}"
        if analyte_name:
            filter_text += f", Analyte: {analyte_name}"
        if analyte_group:
            filter_text += f", Group: {analyte_group}"
        
        self.update_status(filter_text + "...")
        self.set_view_button_state('disabled', 'Filtering...')
        
        thread = threading.Thread(target=self.execute_filtered_data_loading, 
                                args=(batch_id, sample_id, analyte_name, analyte_group))
        thread.daemon = True
        self.db_thread_pool.append(thread)
        thread.start()

    def execute_filtered_data_loading(self, batch_id, sample_id=None, analyte_name=None, analyte_group=None):
        """Ejecutar carga de datos filtrados en hilo separado"""
        
        try:
            
            self.root.after(0, self.clear_tables_gui)
            
            # Consultar datos con filtros adicionales
            sample_data = select_samples(batch_id, [], sample_id, False)
            parameters_data = select_parameters(batch_id, [], sample_id, analyte_name, analyte_group)
            
            self.root.after(0, self.update_tables_with_data, sample_data, parameters_data)
            
        except Exception as ex:
            error_msg = f"Database error: {str(ex)}"
            self.root.after(0, self.handle_data_loading_error, error_msg)
    
    def clear_filters(self):
        """Limpiar todos los filtros"""
        self.analyte_name_combobox.set('')
        self.analyte_group_combobox.set('')
        if self.data_loaded and self.current_batch_id:
            self.reload_batch_data()
            
            
    def filter_by_analyte_name(self, analyte_name):
        """Filtrar datos por nombre de analito"""
        try:
            batch_id = self.current_batch_id
            sample_id = self.lab_sample_id_entry.get().strip() or None
            if not batch_id:
                return
            self.load_filtered_data_async(batch_id, sample_id, analyte_name=analyte_name)
        except Exception as e:
            messagebox.showerror("Error", f"Error filtering by analyte: {str(e)}")

    def filter_by_analyte_group(self, analyte_group):
        """Filtrar datos por grupo de analito"""
        try:
            batch_id = self.current_batch_id
            sample_id = self.lab_sample_id_entry.get().strip() or None
            if not batch_id:
                return
            self.load_filtered_data_async(batch_id, sample_id, analyte_group=analyte_group)
        except Exception as e:
            messagebox.showerror("Error", f"Error filtering by analyte group: {str(e)}")
            
            
    

    def create_actions_menu(self, parent_frame):
        """Crear menú desplegable con acciones adicionales"""
        import tkinter.font as tkFont
        
        # Botón principal del menú
        self.actions_button = ttk.Button(parent_frame, text="☰ Actions", style='Primary.TButton', cursor="hand2", width=20)
        self.actions_button.grid(row=0, column=11, padx=(40, 5), pady=5)
        
        # Crear menú desplegable
        self.actions_menu = tk.Menu(parent_frame, tearoff=0, font=tkFont.Font(size=9))
        
        # Agregar opciones al menú
        self.actions_menu.add_command(label="Create Sample", command=self.show_sample_wizard)
        self.actions_menu.add_command(label="Create Sample Tests", command=self.show_sample_test_wizard)
        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="Create QC", command=self.show_create_qc_view)
        self.actions_menu.add_command(label="Assign Data", command=self.show_assign_data_view)
        
        # Configurar evento para mostrar menú
        self.actions_button.configure(command=self.show_actions_menu)

    def show_actions_menu(self):
        """Mostrar el menú desplegable"""
        try:
            # Obtener posición del botón
            x = self.actions_button.winfo_rootx()
            y = self.actions_button.winfo_rooty() + self.actions_button.winfo_height()
            
            # Mostrar menú en la posición calculada
            self.actions_menu.post(x, y)
        except tk.TclError:
            # En caso de error, mostrar en posición del mouse
            self.actions_menu.tk_popup(self.actions_button.winfo_rootx(), 
                                    self.actions_button.winfo_rooty())

    def show_assign_data_view(self):
        try:
            from assign_data_view import AssignData
            assign_data_view = AssignData(self.root)
            self.root.wait_window(assign_data_view.window)
            self.update_status("Assign data view closed")
        except Exception as ex:
            print(f"Error {ex}")

    def show_create_qc_view(self):
        try:
            create_qc_view = CreateQc(self.root)
            self.root.wait_window(create_qc_view.window)
            self.update_status("Create QC view closed")
        except Exception as ex:
            print(f"Error {ex}")

    def clear_results(self):
        """Clear all search results"""
        for table in [self.table1, self.table2]:
            for item in table.get_children():
                table.delete(item)
        self.lab_sample_id_entry.delete(0, tk.END)
        self.current_batch_id = None
        self.update_status("Results cleared")

    def view_data_wrapper(self):
        """Wrapper para el botón View Data"""
        try:
            if self.is_loading:
                messagebox.showinfo("Info", "Data is already being loaded. Please wait...")
                return
                
            batch_id_text = self.work_order_combobox.get().strip()
            lab_sample_id = self.lab_sample_id_entry.get().strip() or None
            
            if not batch_id_text:
                messagebox.showwarning("Warning", "Please enter a Batch ID")
                return
            
            batch_id_int = int(batch_id_text)
            self.current_batch_id = batch_id_int
            self.current_lab_sample_id = lab_sample_id
            
            # Ejecutar consulta en hilo separado
            self.load_data_async(batch_id_int, lab_sample_id)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric Batch ID")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_data_async(self, batch_id, lab_sample_id):
        """Cargar datos de forma asíncrona"""
        self.is_loading = True
        self.update_status("Loading data... Please wait")
        self.set_view_button_state('disabled', 'Loading...')

        thread = threading.Thread(target=self.execute_data_loading, args=(batch_id, lab_sample_id))
        thread.daemon = True
        self.db_thread_pool.append(thread)
        thread.start()

    def execute_data_loading(self, batch_id, lab_sample_id):
        """Ejecutar carga de datos en hilo separado"""
        try:
            self.root.after(0, self.clear_tables_gui)

            sample_data = select_samples(batch_id, [], lab_sample_id, True)
            parameters_data = select_parameters(batch_id, [], lab_sample_id)

            if not sample_data and not parameters_data:
                self.root.after(0, self.handle_data_loading_error, "No data found for the id")
                return

            self.root.after(0, self.update_tables_with_data, sample_data, parameters_data)

            # Cargar sample IDs para el combobox
            sample_ids = filter_queries(batch_id)
            self.root.after(0, self.update_sample_ids_combobox, sample_ids)

        except Exception as ex:
            error_msg = f"Database error: {str(ex)}"
            self.root.after(0, self.handle_data_loading_error, error_msg)

    def clear_tables_gui(self):
        """Limpiar tablas en el main thread"""
        for table in [self.table1, self.table2]:
            for item in table.get_children():
                table.delete(item)

        # Reset checkboxes
        self.select_all_var1.set(False)
        self.select_all_var2.set(False)

    def update_tables_with_data(self, sample_data, parameters_data):
        """Actualizar tablas con datos"""
        try:
            for item in sample_data:
                self.table1.insert('', tk.END, values=(
                    '☐',
                    item[0],  # ItemID
                    item[1],  # LabReportingBatchID
                    item[2],  # LabSampleID
                    item[3],  # ClientSampleID
                    item[4],  # Sampler
                    item[5],  # DateCollected
                    item[6],  # MatrixID
                    #item[7],  # AnalysisMethodIDs
                    item[7],  # Temperature
                    item[8],  # ShippingBatchID
                    item[9],  # CollectMethod
                    item[10],  # CollectionAgency
                    item[11],  # AdaptMatrixID
                    item[12]  # LabID
                ))

            for item in parameters_data:
                self.table2.insert('', tk.END, values=(
                    '☐',
                    item[0],  # sampletestid
                    item[1],  # clientsampleid
                    item[2],  # method
                    item[3],  # labsampleid
                    item[4],  # analyte
                    item[5],  # result
                    item[6],  # resultunits
                    item[7],  # detection limit
                    item[8],  # dilution
                    item[9],  # reporting limit
                    item[10],  # projectname
                    item[11],  # datecollected
                    item[12],  # matrix
                    item[13],  # qctype
                    item[14],  # labreportingbatchid
                    item[15],  # notes
                    item[16],  # sampler
                    item[17]  # Analyst
                ))

            self.update_status(f"Found {len(sample_data)} samples and {len(parameters_data)} analyses")
            self.data_loaded = True
            
            if parameters_data:
                self.analyte_name_combobox.config(state='normal')
                self.analyte_group_combobox.config(state='normal')

        except Exception as ex:
            print(f"ERROR updating tables: {ex}")
        finally:
            self.set_view_button_state('normal', 'View Data')
            self.is_loading = False

    def handle_data_loading_error(self, error_msg):
        """Manejar errores en la carga de datos"""
        self.update_status(error_msg, error=True)
        messagebox.showerror("Data loading error", error_msg)
        self.set_view_button_state('normal', 'View Data')
        self.is_loading = False

    def set_view_button_state(self, state, text):
        """Establecer estado del botón View Data"""
        self.view_data_btn.config(state=state, text=text)

    def toggle_all_checkboxes(self, table):
        """Toggle all checkboxes in the given table"""
        is_table1 = (table == self.table1)
        select_all_var = self.select_all_var1 if is_table1 else self.select_all_var2

        new_state = '☑' if select_all_var.get() else '☐'
        action = "SELECTED" if select_all_var.get() else "DESELECTED"
        
        affected_samples = []
        
        for item_id in table.get_children():
            current_values = table.item(item_id, 'values')
            if current_values:
                new_values = list(current_values)
                lab_sample_id = current_values[3]  # LabSampleID
                new_values[0] = new_state
                table.item(item_id, values=new_values)
                affected_samples.append(lab_sample_id)
        
        # Imprimir todas las muestras afectadas
        if affected_samples:
            print(f"All samples {action}: {', '.join(affected_samples)}")
            self.update_status(f"All samples {action} ({len(affected_samples)} samples)")

    def handle_checkbox_click(self, event):
        """Handle clicks on the checkbox column"""
        rowid = event.widget.identify_row(event.y)
        column = event.widget.identify_column(event.x)

        if column == '#1':
            current_values = event.widget.item(rowid, 'values')
            if current_values:
                new_values = list(current_values)
                lab_sample_id = current_values[3]
                if new_values[0] == '☐':
                    new_values[0] = '☑'
                    action = "SELECTED"
                else:
                    new_values[0] = '☐'
                    action = "DESELECTED"
                    
                print(f"Sample {action} -> LabSampleID = {lab_sample_id}")
                
                 # Actualizar la fila en la tabla
                event.widget.item(rowid, values=new_values)
            
                # Opcional: Mostrar también en el status
                self.update_status(f"Sample {action}: {lab_sample_id}")

    def get_selected_data(self):
        """Extrae los batch IDs de las filas que tienen el checkbox marcado"""
        selected_sample_batch_ids = []
        selected_analysis_batch_ids = []

        for LabSampleID in self.table1.get_children():
            values = self.table1.item(LabSampleID, 'values')
            if values and values[0] == '☑':
                LabSampleID = values[3]
                selected_sample_batch_ids.append(LabSampleID)

        """for sampleTestsID in self.table2.get_children():
            values = self.table2.item(sampleTestsID, 'values')
            if values and values[0] == '☑':
                sampleTestsID = values[1]
                selected_analysis_batch_ids.append(sampleTestsID)"""

        print(f"Selected Sample Batch IDs: {selected_sample_batch_ids}")
        print(f"Selected Analysis Batch IDs: {selected_analysis_batch_ids}")
        self.update_status(
            f"Selected {len(selected_sample_batch_ids)} sample batches and {len(selected_analysis_batch_ids)} analysis batches")

        return selected_analysis_batch_ids, selected_sample_batch_ids

    def show_sample_wizard(self):
        try:
            wizard = SampleWizard(self.root)
            self.root.wait_window(wizard.window)
            self.update_status("Sample wizard closed")
        except Exception as ex:
            print(f"Error {ex}")

    def show_sample_test_wizard(self):
        try:
            wizard = SampleTestsWizard(self.root)
            self.root.wait_window(wizard.window)
            self.update_status("Sample Tests Wizard Closed")
        except Exception as ex:
            print(f"Error -> {ex}")

    def generate_report_wrapper(self):
        """Wrapper que ejecuta la generación del reporte en un hilo separado"""
        if self.current_batch_id is None:
            messagebox.showwarning("Warning", "Please search for data first using View Data button")
            return
        
        selected_samples, selected_analyses = self.get_selected_data()
        if not selected_samples and not selected_analyses:
            return
        
        self.disable_report_button()
        
        thread = threading.Thread(target=self.execute_report_generation)
        thread.daemon = True
        thread.start()
    
    def disable_report_button(self):
        """Deshabilita el botón de reporte durante la generación"""
        self.report_btn.config(state='disabled', text='Generating...')
    
    def enable_report_button(self):
        """Rehabilita el botón de reporte después de la generación"""
        self.report_btn.config(state='normal', text='Generate Report')
    
    def execute_report_generation(self):
        """Ejecuta la generación del reporte"""
        try:
            self.root.after(0, lambda: self.update_status("Starting report generation..."))
            selected_samples, selected_parameters = self.get_selected_data()
            
            if not selected_parameters and not selected_samples:
                self.root.after(0, lambda: self.update_status("No data selected for report", error=True))
                return
            
            success = self.generate_filtered_report(
                self.current_batch_id,
                selected_samples,
                selected_parameters
            )
            
            if success:
                self.root.after(0, lambda: self.update_status("Report generated successfully!"))
                self.root.after(0, lambda: messagebox.showinfo("Success", "Report generated successfully!"))
            else:
                self.root.after(0, lambda: self.update_status("Report generation failed", error=True))
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to generate report"))
                
        except Exception as ex:
            print(f"Error en la ejecución del reporte {ex}")
        finally:
            self.root.after(0, self.enable_report_button)
    
    def generate_filtered_report(self, batch_id, selected_samples, selected_parameters):
        if execute_report_generation(batch_id, [], []):
            return True
        else:
            return False