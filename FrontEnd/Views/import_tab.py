import os
import threading
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
from openpyxl import load_workbook

from BackEnd.Database.Queries.Insert.insert_sample_tests import insert_sample_tests
from BackEnd.Database.Queries.Insert.insert_samples import insert_samples
from BackEnd.Processes.DataTypes.process_data import process_main
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
        
        self.chain_of_custody_var = tk.BooleanVar(value=True)
        self.subcontracted_var = tk.BooleanVar()
        self._last_workflow = "chain_of_custody"
        
        self.WORKFLOW_CONFIG = {
            "chain_of_custody": {
                "samples": ('itemID', 'LabReportingBatchID', 'LabSampleID', 'ClientSampleID',
                           'Sampler', 'Datecollected', 'MatrixID', 'AnalysisMethodIDs', 'Temperature',
                           'ShippingBatchID', 'CollectMethod', 'CollectionAgency', 'AdaptMatrixID', 'LabID'),
                "tests": ("ClientSampleID", "LabAnalysisRefMethodID", "LabSampleID", "AnalyteName", 
                         "Result", "ResultUnits", "DetectionLimit", "Dilution", "ReportingLimit", 
                         "ProjectName", "DateCollected", "MatrixID", "LabReportingBatchID", 
                         "Notes", "AnalyteType", "Sampler", "Analyst")
            },
            "subcontracted": {
                "samples": ("ItemID", "LabReportingBatchID", "LabSampleId", "ClientSampleID", 
                           "MatrixID", "DateCollected", "Tag"),
                "tests": ("ClientSampleID", "LabAnalysisRefMethodID", "LabSampleID", "LabID", 
                         "ClientAnalyteID", "AnalyteName", "Result", "ResultUnits", 
                         "LabQualifiers", "ReportingLimit", "AnalyteType", "Dilution", 
                         "PercentMoisture", "PercentRecovery", "RelativePercentDifference", 
                         "ReportingQ", "DateCollected", "MatrixID", "QCType", "Notes", 
                         "PreparationType", "MethodBatchID")
            }
        }
        
        self._create_ui()
        self.setup_import_tables("chain_of_custody")

    def _create_ui(self):
        file_frame = ttk.LabelFrame(self, text="Excel File Import", padding=10)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(self, text="Ready")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Label(file_frame, text="Select Excel File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.file_path_entry = ttk.Entry(file_frame, width=50)
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Browse...", style='Primary.TButton',
                  command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(file_frame, text="Select Workflow:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        workflow_frame = ttk.Frame(file_frame)
        workflow_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Checkbutton(workflow_frame, text="Chain of Custody", 
                       variable=self.chain_of_custody_var,
                       command=self.on_workflow_change).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Checkbutton(workflow_frame, text="Subcontracted", 
                       variable=self.subcontracted_var,
                       command=self.on_workflow_change).pack(side=tk.LEFT)

        self._create_tables()
        self._create_bottom_controls()

    def _create_tables(self):
        self.import_notebook = ttk.Notebook(self)
        self.import_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.import_table1 = self._create_table_with_scroll("Samples")
        self.import_table2 = self._create_table_with_scroll("Sample Tests")

    def _create_table_with_scroll(self, tab_name):
        frame = ttk.Frame(self.import_notebook)
        self.import_notebook.add(frame, text=tab_name)
        
        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        table = ttk.Treeview(container, show='headings')
        
        scroll_v = ttk.Scrollbar(container, orient=tk.VERTICAL, command=table.yview)
        scroll_h = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=table.xview)
        
        table.configure(yscroll=scroll_v.set, xscroll=scroll_h.set)
        
        table.grid(row=0, column=0, sticky='nsew')
        scroll_v.grid(row=0, column=1, sticky='ns')
        scroll_h.grid(row=1, column=0, sticky='ew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        return table

    def _create_bottom_controls(self):
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_bar = ttk.Progressbar(bottom_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack(fill=tk.X, expand=True, pady=5)
        
        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Import Data", style='Success.TButton',
                  command=self.import_data).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(btn_frame, text="Clear", style='Danger.TButton',
                  command=self.clear_import).pack(side=tk.RIGHT, padx=5)

    def on_workflow_change(self):
        if self.chain_of_custody_var.get() and self.subcontracted_var.get():
            if hasattr(self, '_last_workflow') and self._last_workflow == 'chain_of_custody':
                self.chain_of_custody_var.set(False)
            else:
                self.subcontracted_var.set(False)
        
        if self.chain_of_custody_var.get():
            self._last_workflow = 'chain_of_custody'
        elif self.subcontracted_var.get():
            self._last_workflow = 'subcontracted'
        
        if not self.chain_of_custody_var.get() and not self.subcontracted_var.get():
            self.chain_of_custody_var.set(True)
            self._last_workflow = 'chain_of_custody'
            
        workflow = self.get_selected_workflow()
        self.setup_import_tables(workflow)

    def setup_import_tables(self, workflow):
        for table in [self.import_table1, self.import_table2]:
            table.delete(*table.get_children())
            for col in table["columns"]:
                table.heading(col, text="")
                table.column(col, width=0)
                
        columns1 = self.WORKFLOW_CONFIG[workflow]["samples"]
        columns2 = self.WORKFLOW_CONFIG[workflow]["tests"]
        
        self.import_table1["columns"] = columns1
        for col in columns1:
            self.import_table1.heading(col, text=col)
            self.import_table1.column(col, anchor=tk.W)
            
        self.import_table2["columns"] = columns2
        for col in columns2:
            self.import_table2.heading(col, text=col)
            self.import_table2.column(col, anchor=tk.W)

    def get_selected_workflow(self):
        if self.chain_of_custody_var.get():
            return "chain_of_custody"
        elif self.subcontracted_var.get():
            return "subcontracted"
        else:
            return "chain_of_custody"

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            self.update_status(f"Selected file: {os.path.basename(file_path)}")

    def import_data(self):
        try:
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

    def execute_import(self, file_path):
        try:
            self.root.after(0, lambda: self.update_progress(10, "Starting data import..."))
            
            wb_to_read = load_workbook(filename=file_path, data_only=True)
            self.root.after(0, lambda: self.update_progress(30, "Reading Excel file..."))
            
            workflow = self.get_selected_workflow()
            
            if workflow == 'chain_of_custody':
                samples_data = excel_chain_data_reader(wb_to_read, file_path)
                code = get_plus_code(wb_to_read)
                samples_tests = excel_parameters_reader(wb_to_read, code)
                self.root.after(0, self.update_import_tables, samples_data, samples_tests)
                
            elif workflow == 'subcontracted':
                registers_subcontracted = process_subcontracted(file_path, wb_to_read)
                samples_subcontracted = generate_samples_for_st(registers_subcontracted)
                self.root.after(0, self.update_import_tables, samples_subcontracted, registers_subcontracted)
                
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
        
        for sample in samples_data:
            data_to_print = process_main(sample, "sample")
            self.import_table1.insert('', tk.END, values=data_to_print)
        
        for test in samples_tests:
            data_to_print = process_main(test, "test")
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

    def clear_import(self):
        self.file_path_entry.delete(0, tk.END)
        self.progress_bar['value'] = 0
        
        for item in self.import_table1.get_children():
            self.import_table1.delete(item)
        for item in self.import_table2.get_children():
            self.import_table2.delete(item)
            
        self.update_status("Import fields cleared")

    def update_status(self, message, error=False):
        self.status_label.config(text=message)
        if error:
            self.status_label.config(foreground='#ff6b6b')
            self.root.after(5000, lambda: self.status_label.config(foreground='white'))
        else:
            self.status_label.config(foreground='white')