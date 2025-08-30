import os
import threading
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

from openpyxl import load_workbook

from BackEnd.Database.Queries.Insert.insert_sample_tests import insert_sample_tests
from BackEnd.Database.Queries.Insert.insert_samples import insert_samples
from BackEnd.Processes.DataTypes.process_datetime import process_datetime
from BackEnd.Processes.Read.excel_chain_data_reader import excel_chain_data_reader
from BackEnd.Processes.Read.excel_parameters_reader import excel_parameters_reader
from BackEnd.Processes.SubContracted.generate_samples_for_st import generate_samples_for_st
from BackEnd.Processes.SubContracted.process_subcontracted import process_subcontracted
from BackEnd.Utils.get_plus_code import get_plus_code

class ImportTab(ttk.Frame):
    
    
    def __init__(self, parent):
        
        super().__init__(parent)
        self.is_loading = False
        self.root = parent
        self.db_thread_pool = []
        
        style = ttk.Style()
        
        # Frame superior para selección de archivo
        file_frame = ttk.LabelFrame(self, text="Excel File Import", padding=10)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Var for checkboxes
        self.chain_of_custody_var = tk.BooleanVar(value=True)
        self.subcontracted_var = tk.BooleanVar()
        
        # Init workflow chain of custody by default
        self._last_workflow = "chain_of_custody"
        
        
        # Columns depending the selected workflow
        self.WORKFLOW_CONFIG =  {
            
            "chain_of_custody": {
                "samples" : ("ItemID", "LabReportingBatchID", "LabSampleId", "ClientSampleID", 
                    "LabAnalysisRefMethodID", "MatrixID", "DateCollected", "Sampler"),
                
                "tests": ("ClientSampleID", "LabAnalysisRefMethodID", "LabSampleID", "AnalyteName", 
                  "Result", "ResultUnits", "DetectionLimit", "Dilution", "ReportingLimit", 
                  "ProjectName", "DateCollected", "MatrixID", "LabReportingBatchID", 
                  "Notes","AnalyteType", "Sampler", "Analyst")
            },
            
            "subcontracted": {
                "samples" : ("ItemID", "LabReportingBatchID", "LabSampleId", "ClientSampleID", 
                   "MatrixID", "DateCollected"),
                
                
                
                "tests": ("ClientSampleID", "LabAnalysisRefMethodID", "LabSampleID", "LabID", 
                          "ClientAnalyteID", "AnalyteName", "Result", "ResultUnits", 
                          "LabQualifiers", "ReportingLimit", "AnalyteType", "Dilution", 
                          "PercentMoisture", "PercentRecovery", "RelativePercentDifference", 
                      "ReportingQ", "DateCollected", "MatrixID", "QCType", "Notes", 
                          "PreparationType", "MethodBatchID")
            }
        }
        
        
        
        
        self.status_label = ttk.Label(self, text="Ready")
        self.status_label.pack(side=tk.BOTTOM, fill = tk.X)
        
        
        # Primera fila: Selección de archivo
        ttk.Label(file_frame, text="Select Excel File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.file_path_entry = ttk.Entry(file_frame, width=50)
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5)
        
        browse_btn = ttk.Button(file_frame, text="Browse...", style='Primary.TButton',
                            command=self.browse_file)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)
        
        browse_parameters_excel_btn = ttk.Button(file_frame, text="Open excel to write data", style="Primary.TButton")
        browse_parameters_excel_btn.grid(row=0, column=3, padx=5, pady=5) 
        
        # Segunda fila: Selección de flujo de trabajo
        ttk.Label(file_frame, text="Select Workflow:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Frame para los checkboxes
        workflow_frame = ttk.Frame(file_frame)
        workflow_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Checkboxes
        chain_of_custody_cb = ttk.Checkbutton(workflow_frame, text="Chain of Custody", 
                                            variable=self.chain_of_custody_var,
                                            command=self.on_workflow_change)
        chain_of_custody_cb.pack(side=tk.LEFT, padx=(0, 20))
        
        subcontracted_cb = ttk.Checkbutton(workflow_frame, text="Subcontracted", 
                                        variable=self.subcontracted_var,
                                        command=self.on_workflow_change)
        subcontracted_cb.pack(side=tk.LEFT)
        
        # Notebook para las tablas de datos
        self.import_notebook = ttk.Notebook(self)
        self.import_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # TABLA 1 DE IMPORTACIÓN CON SCROLL HORIZONTAL
        table1_frame = ttk.Frame(self.import_notebook)
        self.import_notebook.add(table1_frame, text="Samples")
        
        # CREAR CONTAINER PARA TABLA 1 DE IMPORTACIÓN
        import_table1_container = ttk.Frame(table1_frame)
        import_table1_container.pack(fill=tk.BOTH, expand=True)
        
       
                
        self.import_table1 = ttk.Treeview(import_table1_container,show='headings')
        
        
        
        # SCROLLBARS PARA TABLA 1 DE IMPORTACIÓN
        import_scroll1_v = ttk.Scrollbar(import_table1_container, orient=tk.VERTICAL, command=self.import_table1.yview)
        import_scroll1_h = ttk.Scrollbar(import_table1_container, orient=tk.HORIZONTAL, command=self.import_table1.xview)
        
        self.import_table1.configure(yscroll=import_scroll1_v.set, xscroll=import_scroll1_h.set)
        
        # POSICIONAR CON GRID
        self.import_table1.grid(row=0, column=0, sticky='nsew')
        import_scroll1_v.grid(row=0, column=1, sticky='ns')
        import_scroll1_h.grid(row=1, column=0, sticky='ew')
        
        import_table1_container.grid_rowconfigure(0, weight=1)
        import_table1_container.grid_columnconfigure(0, weight=1)
        
        # TABLA 2 DE IMPORTACIÓN CON SCROLL HORIZONTAL
        table2_frame = ttk.Frame(self.import_notebook)
        self.import_notebook.add(table2_frame, text="Sample Tests")
        
        # CREAR CONTAINER PARA TABLA 2 DE IMPORTACIÓN
        import_table2_container = ttk.Frame(table2_frame)
        import_table2_container.pack(fill=tk.BOTH, expand=True)
        
        
        self.import_table2 = ttk.Treeview(import_table2_container, show='headings')
        
        
        # SCROLLBARS PARA TABLA 2 DE IMPORTACIÓN
        import_scroll2_v = ttk.Scrollbar(import_table2_container, orient=tk.VERTICAL, command=self.import_table2.yview)
        import_scroll2_h = ttk.Scrollbar(import_table2_container, orient=tk.HORIZONTAL, command=self.import_table2.xview)
        
        self.import_table2.configure(yscroll=import_scroll2_v.set, xscroll=import_scroll2_h.set)
        
        # POSICIONAR CON GRID
        self.import_table2.grid(row=0, column=0, sticky='nsew')
        import_scroll2_v.grid(row=0, column=1, sticky='ns')
        import_scroll2_h.grid(row=1, column=0, sticky='ew')
        
        import_table2_container.grid_rowconfigure(0, weight=1)
        import_table2_container.grid_columnconfigure(0, weight=1)
        
        # Frame inferior para progreso y botones
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_bar = ttk.Progressbar(bottom_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack(fill=tk.X, expand=True, pady=5)
        
        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.pack(fill=tk.X)
        
        import_btn = ttk.Button(btn_frame, text="Import Data", style='Success.TButton',
                            command=self.import_data)
        import_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="Clear", style='Danger.TButton',
                            command=self.clear_import)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        #Init configure for all tables
        
        self.setup_import_tables("chain_of_custody")
        
    
        
        
        
    # Method to control the worflow change
    def on_workflow_change(self):
        """Manejar cambios en la selección de workflow"""
        # Asegurar que solo uno esté seleccionado a la vez
        if self.chain_of_custody_var.get() and self.subcontracted_var.get():
            # Si ambos están seleccionados, desmarcar el que no fue el último clickeado
            
            if hasattr(self, '_last_workflow') and self._last_workflow == 'chain_of_custody':
                self.chain_of_custody_var.set(False)
            else:
                self.subcontracted_var.set(False)
        
        # Guardar el último workflow seleccionado
        if self.chain_of_custody_var.get():
            self._last_workflow = 'chain_of_custody'
        elif self.subcontracted_var.get():
            self._last_workflow = 'subcontracted'
        
        # Si ninguno está seleccionado, seleccionar Chain of Custody por defecto
        if not self.chain_of_custody_var.get() and not self.subcontracted_var.get():
            self.chain_of_custody_var.set(True)
            self._last_workflow = 'chain_of_custody'
            
        workflow = self.get_selected_workflow()
        self.setup_import_tables(workflow)
        
    # This method configures the tables depending the workflow selected       
    def setup_import_tables(self, workflow):
        
        
        # First delete the last table content
        for table in [self.import_table1, self.import_table2]:
            table.delete(*table.get_children())
            for col in table["columns"]:
                table.heading(col, text="")
                table.column(col, width=0)
                
        # Get the workflow columns
        columns1 = self.WORKFLOW_CONFIG[workflow]["samples"]
        columns2 = self.WORKFLOW_CONFIG[workflow]["tests"]
        
        # Reconfigure table 1
        self.import_table1["columns"] = columns1
        for col in columns1:
            self.import_table1.heading(col, text=col)
            self.import_table1.column(col, anchor= tk.W)
            
        # Reconfigure table 2
        self.import_table2["columns"] = columns2
        for col in columns2:
        
            self.import_table2.heading(col, text=col)
            self.import_table2.column(col, anchor= tk.W)
                
    #  Gets the selected workflow
    def get_selected_workflow(self):
        """Obtener el workflow seleccionado"""
        if self.chain_of_custody_var.get():
            return "chain_of_custody"
        elif self.subcontracted_var.get():
            return "subcontracted"
        else:
            return "chain_of_custody"  
        
    # Configure the status bar        
    def setup_status_bar(self):
        """Setup the status bar at the bottom with modern styling"""
        status_frame = ttk.Frame(self.main_frame, style='Status.TFrame')
        status_frame.pack(fill=tk.X, pady=(0, 0), ipady=3)
        
        # Status label with better padding
        self.status_label = ttk.Label(status_frame, 
                                    text="Ready", 
                                    style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Version info with subtle styling
        version_label = ttk.Label(status_frame, 
                                text="v1.0.1 | © 2025 App", 
                                style='Status.TLabel')
        version_label.pack(side=tk.RIGHT, padx=10)
        
    
    # This methods browse and open the file to get the data
    def browse_file(self):
        """Open file dialog to select Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            self.update_status(f"Selected file: {os.path.basename(file_path)}")
            
    
    # Call the code to read the uploaded excel
    def import_data(self):
        """Process the import of data from Excel"""
        try:
            # Verificar archivo seleccionado
            file_path = self.file_path_entry.get()
            if not file_path:
                messagebox.showwarning("Warning", "Please select an Excel file first!")
                return
                
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "The selected file does not exist!")
                return
            
            if self.is_loading:
                messagebox.showinfo("Info", "Import is already in progress. Please wait....")
                return
            
            
            self.is_loading = True
            thread = threading.Thread(target=self.execute_import, args=(file_path,))
            thread.daemon = True
            self.db_thread_pool.append(thread)
            thread.start()
            
                
            
            
        except Exception as e:
            error_msg = f"Import setup error: {str(e)}"
            self.update_status(error_msg, error=True)
            messagebox.showerror("Import Error", error_msg)
            
            
     
    # Call the import functions  
    def execute_import(self, file_path):
        
        try:
            self.root.after(0, lambda: self.update_progress(10, "Starting data import..."))
            
            # Cargar archivo Excel
            wb_to_read = load_workbook(filename=file_path, data_only=True)
            self.root.after(0, lambda: self.update_progress(30, "Reading Excel file..."))
            
            samples_data, samples_tests, registers_subcontracted = None, None, None
            
            
            # Verify selected workflow (chain of custody or subcontracted)
            workflow = self.get_selected_workflow()
            
            if workflow == 'chain_of_custody':
                
                # Read excel chain of custody
                samples_data = excel_chain_data_reader(wb_to_read, file_path)
                code = get_plus_code(wb_to_read)
                samples_tests = excel_parameters_reader(wb_to_read, code)
                
                
            
            elif workflow == 'subcontracted':
                
                # Subcontracted workflow
                #print(process_subcontracted)
                registers_subcontracted = process_subcontracted(file_path, wb_to_read)
                
                print(generate_samples_for_st(registers_subcontracted))
                
                #print("Registers to subcontracted")
                #print()
                #print(registers_subcontracted)
                
                self.root.after(0, self.update_import_tables, [], registers_subcontracted)
                
            else:
                
                raise Exception("Unknow workflow detected") 
            
            
            self.root.after(0, lambda: self.update_progress(60, "Processing data..."))
                
            # Actualizar GUI en hilo principal
            #self.root.after(0, self.update_import_tables, samples_data, samples_tests)
                
            # Insertar en BD
            #self.insert_data_to_db(samples_data, samples_tests)
                
            self.root.after(0, lambda: self.update_progress(100, "Import completed successfully!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Data import completed successfully!"))
            
            
        except Exception as e:
            error_msg = f"Import error: {str(e)}"
            self.root.after(0, lambda: self.handle_import_error(error_msg))
        finally:
            self.is_loading = False
         
           
    def update_progress(self, value, message):
        self.progress_bar['value'] = value
        self.update_status(message)
        self.root.update_idletasks()
    
    
    def update_import_tables(self, samples_data, samples_tests):

        for item in self.import_table1.get_children():
            self.import_table1.delete(item)
        for item in self.import_table2.get_children():
            self.import_table2.delete(item)
        
        # Insertar datos
        for sample in samples_data:
            current_sample = sample[0]
            if len(current_sample) > 3:
                self.import_table1.insert('', tk.END, values=current_sample)
        
        for test in samples_tests:
            data_to_print = process_datetime(test)
            self.import_table2.insert('', tk.END, values=data_to_print)


    def insert_data_to_db(self, samples_data, samples_tests):
        try:
            
            sample_columns = ["itemID", "LabReportingBatchID", "LabSampleID", "DateCollected",
                            "ClientSampleID", "CollectMethod", "MatrixID", "Sampler", "TotalContainers"]
            test_columns = ["ClientSampleID", "LabAnalysisRefMethodID", "LabSampleID", "AnalyteName", "Result", "ResultUnits", "DetectionLimit", "Dilution", "ReportingLimit", "ProjectName", "DateCollected", "MatrixID", "LabReportingBatchID", "Notes", "QCType"]
            
            insert_samples(samples_data, sample_columns)
            insert_sample_tests(samples_tests, test_columns)
            
        except Exception as e:
            raise Exception(f"Database insertion error: {str(e)}")
        
    
    
    def handle_import_error(self, error_msg):
        self.update_status(error_msg, error=True)
        messagebox.showerror("Import Error", error_msg)
        self.progress_bar['value'] = 0
        self.is_loading = False
    
    
    def clear_results(self):
        """Clear all search results"""
        for table in [self.table1, self.table2]:
            for item in table.get_children():
                table.delete(item)
        self.sample_id_entry.delete(0, tk.END)
        self.current_batch_id = None  # Limpiar también el batch ID
        self.update_status("Results cleared")
    
    def clear_import(self):
        """Clear import fields"""
        self.file_path_entry.delete(0, tk.END)
        
        self.progress_bar['value'] = 0
        
        # Limpiar también las tablas de importación
        for item in self.import_table1.get_children():
            self.import_table1.delete(item)
        for item in self.import_table2.get_children():
            self.import_table2.delete(item)
            
        self.update_status("Import fields cleared")
    
    def update_status(self, message, error=False):
        """Update the status bar message"""
        self.status_label.config(text=message)
        if error:
            self.status_label.config(foreground='#ff6b6b')
            self.root.after(5000, lambda: self.status_label.config(foreground='white'))
        else:
            self.status_label.config(foreground='white')
    
    def on_closing(self):
        """Limpia recursos al cerrar la aplicación"""
        try:
            # Esperar a que terminen los hilos de BD
            for thread in self.db_thread_pool:
                if thread.is_alive():
                    thread.join(timeout=2)  # Esperar máximo 2 segundos
            
            self.root.destroy()
        except:
            self.root.destroy()
        
        