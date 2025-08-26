from pathlib import Path
import sys
import threading
from tkinter import messagebox, ttk
import tkinter as tk

from FrontEnd.Functions.sample_test_wizard import SampleTestsWizard
from FrontEnd.Functions.sample_wizard import SampleWizard


PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


from BackEnd.Database.Queries.Filters.filter_queries import filter_queries
from BackEnd.Database.Queries.Select.select_parameters import select_parameters
from BackEnd.Database.Queries.Select.select_samples import select_samples
from BackEnd.Processes.execute_report_generation import execute_report_generation


class ReportTab(ttk.Frame):


    def __init__(self, parent):
        """Create the Report tab with data viewing functionality"""
        super().__init__(parent)
        
        style = ttk.Style()
        
        style.configure("Excel.Treeview",
                borderwidth=2,
                relief="solid",
                fieldbackground="white",
                background="white",
                foreground="black")

        # Search frame
        search_frame = ttk.LabelFrame(self, text="Search Parameters", padding=10)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Primera fila: Entry fields y botones principales
        ttk.Label(search_frame, text="LabReportingBatchID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.batch_id_entry = ttk.Entry(search_frame, width=25)
        self.batch_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Event for validate batchid in real time
        self.batch_id_entry.bind('<KeyRelease>', self.validate_batch_id)
        self.batch_id_entry.bind('<FocusOut>', self.validate_batch_id)
        
        
        ttk.Label(search_frame, text="LabSampleID:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.sample_id_entry = ttk.Combobox(search_frame, width=25, values=[])
        self.sample_id_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        #Event for validate sampleid filter in realtime
        self.sample_id_entry.bind('<<ComboboxSelected>>', self.on_sample_id_selected)
        self.sample_id_entry.bind('<KeyRelease>', self.on_sample_id_changed)
        
        # Botón View Data
        search_btn = ttk.Button(search_frame, text="View Data", style='Primary.TButton', 
                            command=self.view_data_wrapper, cursor="hand2", width=20)
        search_btn.grid(row=0, column=6, padx=(25, 5), pady=5)
        
        # Botón desplegable para acciones adicionales
        self.create_actions_menu(search_frame)
        
        # Results frame
        results_frame = ttk.Frame(self)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for multiple tables
        results_notebook = ttk.Notebook(results_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Table 1 - MODIFICADO PARA INCLUIR SCROLL HORIZONTAL
        table1_frame = ttk.Frame(results_notebook)
        results_notebook.add(table1_frame, text="Sample Data")
        
        # Add Select All checkbox for Table 1
        select_all_frame1 = ttk.Frame(table1_frame)
        select_all_frame1.pack(fill=tk.X, padx=5, pady=2)
        
        self.select_all_var1 = tk.BooleanVar()
        self.select_all_cb1 = ttk.Checkbutton(select_all_frame1, text="Select All", 
                                        variable=self.select_all_var1,
                                        command=lambda: self.toggle_all_checkboxes(self.table1))
        self.select_all_cb1.pack(side=tk.LEFT)
        
        # CREAR FRAME PARA CONTENER TABLA Y SCROLLBARS
        table1_container = ttk.Frame(table1_frame)
        table1_container.pack(fill=tk.BOTH, expand=True)



        
        self.table1 = ttk.Treeview(table1_container, 
                                style="Bordered.Treeview", 
                                columns=('Include', 'itemID', 'LabReportingBatchID', 'LabSampleID', 'ClientSampleID', 'Sampler', 'Datecollected', 'MatrixID'), 
                                show='headings', selectmode='extended')
        
        # Configure columns
        self.table1.heading('Include', text='Include')
        self.table1.heading('itemID', text='itemID')
        self.table1.heading('LabReportingBatchID', text='LabReportingBatchID')
        self.table1.heading('ClientSampleID', text='ClientSampleID')
        self.table1.heading('LabSampleID', text='LabSampleID')  
        self.table1.heading('Sampler', text='Sampler')
        self.table1.heading('Datecollected', text='Datecollected')
        self.table1.heading('MatrixID', text='MatrixID')
        #self.table1.heading('LabAnalysisRefMethodID', text='LabAnalysisRefMethodID')

        self.table1.column('Include', width=80, anchor=tk.CENTER)
        self.table1.column('itemID', width=80, anchor=tk.CENTER)
        self.table1.column('LabReportingBatchID', width=150, anchor=tk.CENTER)
        self.table1.column('ClientSampleID', width=120, anchor=tk.CENTER)
        self.table1.column('LabSampleID', width=120, anchor=tk.W)
        self.table1.column('Sampler', width=100, anchor=tk.CENTER)
        self.table1.column('Datecollected', width=120, anchor=tk.CENTER)
        self.table1.column('MatrixID', width=100, anchor=tk.CENTER)
        #self.table1.column('LabAnalysisRefMethodID', width=180, anchor=tk.CENTER)

        # AGREGAR SCROLLBARS VERTICAL Y HORIZONTAL PARA TABLA 1
        scrollbar1_v = ttk.Scrollbar(table1_container, orient=tk.VERTICAL, command=self.table1.yview)
        scrollbar1_h = ttk.Scrollbar(table1_container, orient=tk.HORIZONTAL, command=self.table1.xview)
        
        # CONFIGURAR LA TABLA PARA USAR AMBOS SCROLLBARS
        self.table1.configure(yscroll=scrollbar1_v.set, xscroll=scrollbar1_h.set)
        
        # POSICIONAR TABLA Y SCROLLBARS USANDO GRID
        self.table1.grid(row=0, column=0, sticky='nsew')
        scrollbar1_v.grid(row=0, column=1, sticky='ns')
        scrollbar1_h.grid(row=1, column=0, sticky='ew')
        
        # CONFIGURAR PESOS DE GRID PARA EXPANSIÓN
        table1_container.grid_rowconfigure(0, weight=1)
        table1_container.grid_columnconfigure(0, weight=1)
        
        # Bind checkbox click event
        self.table1.bind('<ButtonRelease-1>', self.handle_checkbox_click)
        
        # Table 2 - MODIFICADO PARA INCLUIR SCROLL HORIZONTAL
        table2_frame = ttk.Frame(results_notebook)
        results_notebook.add(table2_frame, text="Analysis Data")
        
        # Add Select All checkbox for Table 2
        select_all_frame2 = ttk.Frame(table2_frame)
        select_all_frame2.pack(fill=tk.X, padx=5, pady=2)
        
        self.select_all_var2 = tk.BooleanVar()
        self.select_all_cb2 = ttk.Checkbutton(select_all_frame2, text="Select All", 
                                        variable=self.select_all_var2,
                                        command=lambda: self.toggle_all_checkboxes(self.table2))
        self.select_all_cb2.pack(side=tk.LEFT)
        
        # CREAR FRAME PARA CONTENER TABLA Y SCROLLBARS
        table2_container = ttk.Frame(table2_frame)
        table2_container.pack(fill=tk.BOTH, expand=True)
        
        self.table2 = ttk.Treeview(table2_container, 
                                   style="Bordered.Treeview",
                                columns=("Include", "SampleTestsID", "ClientSampleID", "LabAnalysisRefMethodID", "LabSampleID", "AnalyteName", 
                                        "Result", "ResultUnits", "DetectionLimit", "Dilution", "ReportingLimit", 
                                        "ProjectName", "DateCollected", "MatrixID", "AnalyteType", "LabReportingBatchID", "Notes", "Sampler", "Analyst"), 
                                show='headings', selectmode='extended')
    
        # Configure headers
        self.table2.heading('Include', text='Include')
        self.table2.heading('SampleTestsID', text='SampleTestsID')
        self.table2.heading('ClientSampleID', text='ClientSampleID')
        self.table2.heading('LabAnalysisRefMethodID', text='LabAnalysisRefMethodID')        
        self.table2.heading('LabSampleID', text='LabSampleID')     
        self.table2.heading('AnalyteName', text='AnalyteName')  
        self.table2.heading('Result', text='Result')
        self.table2.heading('ResultUnits', text='ResultUnits')
        self.table2.heading('DetectionLimit', text='DetectionLimit')
        self.table2.heading('Dilution', text='Dilution')
        self.table2.heading('ReportingLimit', text='ReportingLimit')
        self.table2.heading('ProjectName', text='ProjectName')  
        self.table2.heading('DateCollected', text='DateCollected')
        self.table2.heading('MatrixID', text='MatrixID')
        self.table2.heading('AnalyteType', text='AnalyteType')
        self.table2.heading('LabReportingBatchID', text='LabReportingBatchID')
        self.table2.heading('Notes', text='Notes')
        self.table2.heading('Sampler', text='Sampler')
        self.table2.heading("Analyst", text="Analyst")
        
        # Configure column widths
        self.table2.column('Include', width=80, anchor=tk.CENTER)
        self.table2.column('SampleTestsID', width=120, anchor=tk.CENTER)
        self.table2.column('ClientSampleID', width=150, anchor=tk.W)
        self.table2.column('LabAnalysisRefMethodID', width=250, anchor=tk.CENTER)       
        self.table2.column('LabSampleID', width=120, anchor=tk.CENTER)        
        self.table2.column('AnalyteName', width=200, anchor=tk.CENTER)      
        self.table2.column('Result', width=100, anchor=tk.CENTER)  
        self.table2.column('ResultUnits', width=100, anchor=tk.CENTER)
        self.table2.column('DetectionLimit', width=120, anchor=tk.CENTER)   
        self.table2.column('Dilution', width=80, anchor=tk.CENTER)
        self.table2.column('ReportingLimit', width=120, anchor=tk.CENTER)  
        self.table2.column('ProjectName', width=250, anchor=tk.CENTER)
        self.table2.column('DateCollected', width=200, anchor=tk.CENTER)
        self.table2.column('MatrixID', width=100, anchor=tk.CENTER)       
        self.table2.column('AnalyteType', width=100, anchor=tk.CENTER)
        self.table2.column('LabReportingBatchID', width=150, anchor=tk.CENTER)
        self.table2.column('Notes', width=350, anchor=tk.CENTER)
        self.table2.column('Sampler', width=100, anchor=tk.CENTER)
        self.table2.column("Analyst", width=100, anchor=tk.CENTER)
        
        # AGREGAR SCROLLBARS VERTICAL Y HORIZONTAL PARA TABLA 2
        scrollbar2_v = ttk.Scrollbar(table2_container, orient=tk.VERTICAL, command=self.table2.yview)
        scrollbar2_h = ttk.Scrollbar(table2_container, orient=tk.HORIZONTAL, command=self.table2.xview)
        
        # CONFIGURAR LA TABLA PARA USAR AMBOS SCROLLBARS
        self.table2.configure(yscroll=scrollbar2_v.set, xscroll=scrollbar2_h.set)
        
        # POSICIONAR TABLA Y SCROLLBARS USANDO GRID
        self.table2.grid(row=0, column=0, sticky='nsew')
        scrollbar2_v.grid(row=0, column=1, sticky='ns')
        scrollbar2_h.grid(row=1, column=0, sticky='ew')
        
        # CONFIGURAR PESOS DE GRID PARA EXPANSIÓN
        table2_container.grid_rowconfigure(0, weight=1)
        table2_container.grid_columnconfigure(0, weight=1)
        
        # Bind checkbox click event for table 2
        self.table2.bind('<ButtonRelease-1>', self.handle_checkbox_click)
        
        # Action buttons
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Report Data button - ahora integrado con la función de reporte
        report_btn = ttk.Button(action_frame, text="Generate Report", style='Success.TButton',
                            command=self.generate_report_wrapper)
        report_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(action_frame, text="Clear Results", style='Danger.TButton',
                            command=self.clear_results)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        
    def on_sample_id_selected(self, event=None):
        
        selected_sample_id = self.sample_id_entry.get()
        if selected_sample_id:
            self.filter_by_sample_id(selected_sample_id)
            self.update_analyte_combobox(selected_sample_id)
        
        
    def on_sample_id_changed(self, event=None):
        
        sample_id_text = self.sample_id_entry.get().strip()
        if not sample_id_text:
            self.reload_batch_data()
           

    def filter_by_sample_id(self, sample_id):
        
        try: 
            batch_id = self.current_batch_id
            if not batch_id:
                return
            
            self.load_filtered_data_async(batch_id, sample_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error filtering by sample ID: {str(e)}")
            
    def update_analyte_combobox(self, sample_id):
        
        print("HI")
    
    
    def load_filtered_data_async(self, batch_id, sample_id):
        """Cargar datos filtrados de forma asíncrona"""
        if self.is_loading:
            return
            
        self.is_loading = True
        self.update_status(f"Filtering data for Sample ID: {sample_id}...")
        self.disable_view_button()
        
        thread = threading.Thread(target=self.execute_filtered_data_loading, args=(batch_id, sample_id))
        thread.daemon = True
        self.db_thread_pool.append(thread)
        thread.start()
    
    
    def execute_filtered_data_loading(self, batch_id, sample_id):
        """Ejecutar carga de datos filtrados en hilo separado"""
        try:
            self.root.after(0, self.clear_tables_gui)
            
            # Consultar datos filtrados por batch_id Y sample_id
            sample_data = select_samples(batch_id, [], sample_id, False)  # Pasar sample_id como filtro
            parameters_data = select_parameters(batch_id, [], sample_id)
            
            self.root.after(0, self.update_tables_with_data, sample_data, parameters_data)
            
        except Exception as ex:
            error_msg = f"Database error: {str(ex)}"
            self.root.after(0, self.handle_data_loading_error, error_msg)


    def reload_batch_data(self):
        """Recargar todos los datos del batch actual"""
        if hasattr(self, 'current_batch_id') and self.current_batch_id:
            self.load_data_async(self.current_batch_id, "")

   

    def validate_batch_id(self, event=None):
        
        batch_id_text = self.batch_id_entry.get().strip()
        
        if not batch_id_text:
            
            self.sample_id_entry.config(state='disabled')
            #self.analyte_name_entry.config(state='disabled')
            self.sample_id_entry.set('')
            #self.analyte_name_entry.set('')
            self.sample_id_entry['values'] = []
            #self.analyte_name_entry['values'] = []
            return

        try:
            
            batch_id_int = int(batch_id_text)
            
            self.sample_id_entry.config(state='normal')
        
        except ValueError:
            
            self.sample_id_entry.config(state='disabled')
            #self.analyte_name_entry.config(state='disabled')
            self.sample_id_entry.set('')
            #self.analyte_name_entry.set('')
            self.sample_id_entry['values'] = []
            #self.analyte_name_entry['values'] = []



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



    def create_actions_menu(self, parent_frame):
        """Crear menú desplegable con acciones adicionales"""
        import tkinter.font as tkFont
        
        # Botón principal del menú
        self.actions_button = ttk.Button(parent_frame, text="☰ Actions", style='Primary.TButton', cursor="hand2", width=20)
        self.actions_button.grid(row=0, column=7, padx=(40, 5), pady=5)
        
        # Crear menú desplegable
        self.actions_menu = tk.Menu(parent_frame, tearoff=0, font=tkFont.Font(size=9))
        
        # Agregar opciones al menú
        self.actions_menu.add_command(label="Create Sample", command=self.show_sample_wizard)
        self.actions_menu.add_command(label="Create Sample Tests", command=self.show_sample_test_wizard)
        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="Create QC", command=self.show_create_qc_view)
        self.actions_menu.add_command(label="Assign Data", command=self.show_assign_data_view)
        """self.actions_menu.add_separator()
        self.actions_menu.add_command(label="Upload subcontracted", command= lambda: print("BUTTON SUBCONTRACTED"))"""
        
        # Configurar evento para mostrar menú
        self.actions_button.configure(command=self.show_actions_menu)
    
    
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
        self.sample_id_entry.delete(0, tk.END)
        self.current_batch_id = None  # Limpiar también el batch ID
        self.update_status("Results cleared")

    def view_data_wrapper(self):
        """Wrapper mejorado para el botón View Data"""
        try:
            # Prevenir múltiples consultas simultáneas
            if self.is_loading:
                messagebox.showinfo("Info", "Data is already being loaded. Please wait...")
                return
                
            batch_id_text = self.batch_id_entry.get().strip()
            lab_sample_id = self.sample_id_entry.get()
            if not batch_id_text:
                messagebox.showwarning("Warning", "Please enter a Sample ID")
                self.sample_id_entry['state'] = 'disabled'
                return
            
            
            batch_id_int = int(batch_id_text)
        
            self.current_batch_id = batch_id_int
            self.current_lab_sample_id = lab_sample_id
            
            
            
            
            # Ejecutar consulta en hilo separado
            if lab_sample_id is not None or lab_sample_id != '':
                self.load_data_async(batch_id_int, lab_sample_id)
            else:
                self.load_data_async(batch_id_int, None)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric Sample ID")
            
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    # ====================================================================
    #                    METODO PARA CARGAR ASINCRONAMENTE DATOS DE LA BD
    #                    -> ESTO EVITA QUE LA APP SE QUEDE EN BLANCO MIENTRAS SE HACEN CONSULTAS PESADAS               
    # ====================================================================
      
    def load_data_async(self, sample_id, lab_sample_id):
        
        self.is_loading = True
        self.update_status("Loading data .... Please wait")
        
        
        # Deshabilitar boton durante el cargue
        self.disable_view_button() 
            
            
        #Creación y ejecución del hilo
        thread = threading.Thread(target=self.execute_data_loading, args=(sample_id, lab_sample_id, ))
        thread.daemon = True
        self.db_thread_pool.append(thread)
        thread.start()
    
    # ====================================================================
    #                    METODO PARA EJECUTAR CONSULTAS EN HILOS SEPARADOS
    # ====================================================================
    def execute_data_loading(self, sample_id, lab_sample_id):
        
        try:
            
            self.root.after(0, self.clear_tables_gui)
            
            print(sample_id)
            
            
            

            sample_data = select_samples(sample_id, [], lab_sample_id, True)
            lab_sample_id_per_batch = filter_queries(sample_id)
            
            
            parameters_data = select_parameters(sample_id, [], lab_sample_id)
            
            self.root.after(0, self.update_tables_with_data, sample_data, parameters_data)
            self.root.after(0, self.update_filters_combobox, lab_sample_id_per_batch)
            

            
        except Exception as ex:
            
            error_msg = f"Database error: {str(ex)}"
            self.root.after(0, self.handle_data_loading_error, error_msg)
    
    def update_filters_combobox(self, sample_ids: list):
        
        if sample_ids:
            
            self.sample_id_entry['values'] = [str(x[0]) for x in sample_ids]
            self.sample_id_entry.config(state='normal')
        
        else:
            
            self.sample_id_entry['values'] = []
            self.sample_id_entry.config(state='disabled')
        
        return True
    
    # ====================================================================
    #                    METODO PARA LIMPIAR TABLAS EN EL MAIN THREAD
    # ====================================================================
    
    def clear_tables_gui(self):
        
        for table in [self.table1, self.table2]:
            for item in table.get_children():
                table.delete(item)
        
        # Reset checkboxes
        self.select_all_var1.set(False)
        self.select_all_var2.set(False)
    
    
    # ====================================================================
    #             ACTUALIZAR TABLAS CON DATOS            
    # ====================================================================
    
    
    def update_tables_with_data(self, sample_data, parameters_data):
        
        try:
            for item in sample_data:
                    
                
                self.table1.insert('', tk.END, values=(
                        '☐',
                        item[0],  # ItemID
                        item[1],  # LabReportingBatchID
                        item[2],  # LabSampleID
                        item[3],  # ClientSampleID
                        item[4],  # DateCollected
                        item[5],  # Matrix
                        item[6]   # Method
                ))
                
            for item in parameters_data:
                
                    self.table2.insert('', tk.END, values = (
                        '☐',
                        item[0],  #sampletestid
                        item[1],  # clientsampleid
                        item[2],  # method
                        item[3],  # labsampleid
                        item[4],  # analyte
                        item[5],  # result
                        item[6],  # resultunits
                        item[7],  # detection limit
                        item[8],  # dilution
                        item[9],  # reporting limit
                        item[10], #projectname
                        item[11], #datecollected
                        item[12], #matrix
                        item[13], # qctype
                        item[14], #labreportingbatchid
                        item[15], #notes
                        item[16], #sampler
                        item[17], #Analyst  
                    ))
            
            self.update_status(f"Found {len(sample_data)} samples and {len(parameters_data)} analyses")
            self.enable_view_button()
            self.is_loading = False
          
            
        except Exception as ex:
                
            print(f"ERROR ->  {ex}")
            
    # ====================================================================
    #             MANEJA POSIBLES ERRORES EN LA CARGA DE DATOS            
    # ====================================================================
    def handle_data_loading_error(self, error_msg):
        
        self.update_status(error_msg, error= True)
        messagebox.showerror("Data loading error", error_msg)
        self.enable_view_button()
        self.is_loading = False
        
    # ====================================================================
    #            DESHABILITA EL BOTON VIEW DATA DURANTE LA CARGA           
    # ====================================================================
    def disable_view_button(self):
        
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab_frame in widget.winfo_children():
                    for child in tab_frame.winfo_children():
                        if isinstance(child, ttk.LabelFrame) and "Search Parameters" in str(child.cget('text')):
                            for button in child.winfo_children():
                                if isinstance(button, ttk.Button) and "View Data" in str(button.cget('text')):
                                    button.config(state='disabled', text='Loading...')
    
    
    # ====================================================================
    #            Rehabilita el botón View Data después de la carga           
    # ====================================================================  
    def enable_view_button(self):
        
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab_frame in widget.winfo_children():
                    for child in tab_frame.winfo_children():
                        if isinstance(child, ttk.LabelFrame) and "Search Parameters" in str(child.cget('text')):
                            for button in child.winfo_children():
                                if isinstance(button, ttk.Button) and "Loading..." in str(button.cget('text')):
                                    button.config(state='normal', text='View Data')
    
    def generate_report_wrapper(self):
        """Wrapper que ejecuta la generación del reporte en un hilo separado"""
        if self.current_batch_id is None:
            messagebox.showwarning("Warning", "Please search for data first using View Data button")
            return
        
        # Verificar si hay datos seleccionados
        selected_samples, selected_analyses = self.get_selected_data()
        if not selected_samples and not selected_analyses:
            return  # El método get_selected_data ya muestra el warning
        
        """# Preguntar al usuario si quiere continuar
        response = messagebox.askyesno("Generate Report", 
                                     f"Generate report for Batch ID {self.current_batch_id}?\n"
                                     f"Selected: {len(selected_samples)} samples, {len(selected_analyses)} analyses")
        if not response:
            return"""
        
        # Deshabilitar el botón durante la generación
        self.disable_report_button()
        
        # Ejecutar en hilo separado para no bloquear la GUI
        thread = threading.Thread(target=self.execute_report_generation)
        thread.daemon = True
        thread.start()
    
    def disable_report_button(self):
        """Deshabilita el botón de reporte durante la generación"""
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab_frame in widget.winfo_children():
                    for child in tab_frame.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for button in child.winfo_children():
                                if isinstance(button, ttk.Button) and "Generate Report" in str(button.cget('text')):
                                    button.config(state='disabled', text='Generating...')
    
    def enable_report_button(self):
        """Rehabilita el botón de reporte después de la generación"""
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab_frame in widget.winfo_children():
                    for child in tab_frame.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for button in child.winfo_children():
                                if isinstance(button, ttk.Button) and "Generating..." in str(button.cget('text')):
                                    button.config(state='normal', text='Generate Report')
    
    def execute_report_generation(self):
        """Ejecuta la generación del reporte usando la función main_format"""
        
        
        try:
            self.root.after(0, lambda: self.update_status("Starting report generation..."))
            selected_samples, selected_parameters = self.get_selected_data()
            
            if not selected_parameters and not select_samples:
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
            
        
    
    
    def toggle_all_checkboxes(self, table):
        """Toggle all checkboxes in the given table"""
        # Determine which "Select All" was clicked
        is_table1 = (table == self.table1)
        select_all_var = self.select_all_var1 if is_table1 else self.select_all_var2
        
        # Get the new state (checked or unchecked)
        new_state = '☑' if select_all_var.get() else '☐'
        
        # Update all checkboxes in the table
        for item_id in table.get_children():
            current_values = table.item(item_id, 'values')
            if current_values:
                new_values = list(current_values)
                new_values[0] = new_state
                table.item(item_id, values=new_values)
    
    def handle_checkbox_click(self, event):
        """Handle clicks on the checkbox column"""
        rowid = event.widget.identify_row(event.y)
        column = event.widget.identify_column(event.x)
        
        # Only handle clicks in the first column '#1' ("Include")
        if column == '#1':
            current_values = event.widget.item(rowid, 'values')
            if current_values:
                new_values = list(current_values)
                if new_values[0] == '☐':
                    new_values[0] = '☑'
                else:
                    new_values[0] = '☐'
                event.widget.item(rowid, values=new_values)
    
    def get_samples(self, sample_id_int):
        
        try:
            if not isinstance(sample_id_int, int) or sample_id_int <= 0:
                raise ValueError("Sample ID must be a positive integer")
            return True
        except Exception as e:
            self.update_status(f"Validation error: {str(e)}", error=True)
            return False
    
    def get_selected_data(self):
        """
        Extrae los batch IDs de las filas que tienen el checkbox marcado
        Retorna dos listas: una con batch IDs de samples y otra con batch IDs de analyses
        """
        # Listas para almacenar los batch IDs seleccionados
        selected_sample_batch_ids = []
        selected_analysis_batch_ids = []
        
        
        #TABLE SAMPLES
        for LabSampleID in self.table1.get_children():
            values = self.table1.item(LabSampleID, 'values')
            if values and values[0] == '☑': 
                
                LabSampleID = values[3] 
                selected_sample_batch_ids.append(LabSampleID)
        
        #TABLE SAMPLE TESTS
        for sampleTestsID in self.table2.get_children():
            values = self.table2.item(sampleTestsID, 'values')
            if values and values[0] == '☑':  # Si el checkbox está marcado

                
                sampleTestsID = values[1]  
                selected_analysis_batch_ids.append(sampleTestsID)
        
        print(f"Selected Sample Batch IDs: {selected_sample_batch_ids}")
        print(f"Selected Analysis Batch IDs: {selected_analysis_batch_ids}")
        self.update_status(f"Selected {len(selected_sample_batch_ids)} sample batches and {len(selected_analysis_batch_ids)} analysis batches")

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