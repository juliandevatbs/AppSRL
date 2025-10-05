"""
This is the function to create quality controls
"""
# ==================================================================== #
#                     PROJECT ROOT CONFIGURATION
# ====================================================================

from pathlib import Path
import sys




def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.append(str(PROJECT_ROOT))
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_DIR))

# ==================================================================== #
#                     IMPORTS
# ====================================================================
from BackEnd.Processes.DataTypes.QC_creation.process_mb import process_mb

import tkinter as tk
from tkinter import ttk, messagebox

class CreateQc:
    def __init__(self, parent=None, work_order=None, lab_sample_id=None, 
                 analyte_name=None, analyte_group_id=None, client_sample_id=None):
        """
        Initialize QC creation window
        
        Args:
            parent: Parent window
            work_order: Work Order ID
            lab_sample_id: Lab Sample ID
            analyte_name: Analyte Name
            analyte_group_id: Analyte Group ID
        """
        BASE_DIR = Path(__file__).parent.resolve()
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        
        # Store received parameters
        self.work_order = work_order
        self.lab_sample_id = lab_sample_id
        self.analyte_name = analyte_name
        self.analyte_group_id = analyte_group_id
        self.client_sample_id =client_sample_id
        
        # Window configuration
        self.window.title("Create Quality Controls")
        self.window.geometry("550x700")
        self.window.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Configure colors and styles
        self.configure_styles()
        
        # Set icon
        try:
            self.window.iconbitmap(BASE_DIR / "assets" / "logos" / "LOGO_SRL_FINAL.ico")
        except:
            pass
        
        # QC types available
        self.controls = ["MB", "LCS", "LCSD", "MS", "MSD"]
        
        self.setup_ui()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def configure_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = "#f0f0f0"
        primary_color = "#2c3e50"
        accent_color = "#3498db"
        success_color = "#27ae60"
        
        self.window.configure(bg=bg_color)
        
        # Title style
        style.configure("Title.TLabel", 
                       font=("Century Gothic", 18, "bold"),
                       foreground=primary_color,
                       background=bg_color)
        
        # Subtitle style
        style.configure("Subtitle.TLabel",
                       font=("Century Gothic", 11, "bold"),
                       foreground=primary_color,
                       background=bg_color)
        
        # Info style
        style.configure("Info.TLabel",
                       font=("Century Gothic", 10),
                       foreground="#555555",
                       background=bg_color)
        
        # Button style
        style.configure("Accent.TButton",
                       font=("Century Gothic", 10, "bold"),
                       foreground="white",
                       background=accent_color)
        
        style.configure("Success.TButton",
                       font=("Century Gothic", 11, "bold"))
    
    def setup_ui(self):
        """Setup user interface"""
        # Main container with padding
        main_frame = tk.Frame(self.window, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header section
        self.create_header(main_frame)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Sample information section
        self.create_info_section(main_frame)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # QC selection section
        self.create_qc_selection(main_frame)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Buttons section
        self.create_buttons(main_frame)
    
    def create_header(self, parent):
        """Create header with title"""
        header_frame = tk.Frame(parent, bg="#f0f0f0")
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                               text="Create Quality Controls",
                               style="Title.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame,
                                   text="Select the quality control types to generate",
                                   style="Info.TLabel")
        subtitle_label.pack(pady=(5, 0))
    
    def create_info_section(self, parent):
        """Create sample information section"""
        info_frame = tk.Frame(parent, bg="#ffffff", relief=tk.RIDGE, bd=1)
        info_frame.pack(fill='x', pady=10)
        
        # Internal padding
        inner_frame = tk.Frame(info_frame, bg="#ffffff")
        inner_frame.pack(fill='x', padx=15, pady=15)
        
        ttk.Label(inner_frame, 
                 text="Sample Information",
                 style="Subtitle.TLabel",
                 background="#ffffff").pack(anchor='w', pady=(0, 10))
        
        # Create info grid
        info_data = [
            ("Work Order:", self.work_order or "Not specified"),
            ("Lab Sample ID:", self.lab_sample_id or "Not specified"),
            ("Analyte Name:", self.analyte_name or "Not specified"),
            ("Analyte Group ID:", self.analyte_group_id or "Not specified")
        ]
        
        for i, (label, value) in enumerate(info_data):
            row_frame = tk.Frame(inner_frame, bg="#ffffff")
            row_frame.pack(fill='x', pady=3)
            
            ttk.Label(row_frame, 
                     text=label,
                     font=("Century Gothic", 9, "bold"),
                     foreground="#2c3e50",
                     background="#ffffff").pack(side='left')
            
            ttk.Label(row_frame,
                     text=value,
                     font=("Century Gothic", 9),
                     foreground="#555555",
                     background="#ffffff").pack(side='left', padx=(5, 0))
    
    def create_qc_selection(self, parent):
        """Create QC type selection section"""
        qc_frame = tk.Frame(parent, bg="#ffffff", relief=tk.RIDGE, bd=1)
        qc_frame.pack(fill='both', expand=True, pady=10)
        
        # Internal padding
        inner_frame = tk.Frame(qc_frame, bg="#ffffff")
        inner_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        ttk.Label(inner_frame,
                 text="Select Quality Control Types:",
                 style="Subtitle.TLabel",
                 background="#ffffff").pack(anchor='w', pady=(0, 15))
        
        # Variables for checkboxes
        self.control_vars = {}
        
        # QC descriptions
        qc_descriptions = {
            "MB": "Method Blank - Blank sample to detect contamination",
            "LCS": "Laboratory Control Sample - Sample with known concentration",
            "LCSD": "Laboratory Control Sample Duplicate - Duplicate of LCS",
            "MS": "Matrix Spike - Sample with added analyte",
            "MSD": "Matrix Spike Duplicate - Duplicate of MS"
        }
        
        # Create checkboxes with descriptions
        for control in self.controls:
            # Container for each checkbox
            cb_frame = tk.Frame(inner_frame, bg="#ffffff")
            cb_frame.pack(fill='x', pady=5)
            
            var = tk.BooleanVar()
            
            # Checkbox with larger font
            cb = tk.Checkbutton(cb_frame,
                               text=control,
                               variable=var,
                               font=("Century Gothic", 10, "bold"),
                               bg="#ffffff",
                               activebackground="#ffffff",
                               fg="#2c3e50",
                               selectcolor="#ffffff")
            cb.pack(side='left', padx=5)
            
            # Description
            desc_label = ttk.Label(cb_frame,
                                  text=qc_descriptions.get(control, ""),
                                  font=("Century Gothic", 8),
                                  foreground="#777777",
                                  background="#ffffff")
            desc_label.pack(side='left', padx=(10, 0))
            
            self.control_vars[control] = var
    
    def create_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg="#f0f0f0")
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Cancel button
        cancel_btn = ttk.Button(button_frame,
                               text="Cancel",
                               command=self.window.destroy,
                               width=15)
        cancel_btn.pack(side='left', padx=(0, 5))
        
        # Preview button
        preview_btn = ttk.Button(button_frame,
                                text="Preview Selection",
                                command=self.show_preview,
                                style="Accent.TButton",
                                width=18)
        preview_btn.pack(side='left', padx=(0, 5))
        
        # Create button
        create_btn = ttk.Button(button_frame,
                               text="Create QC",
                               command=self.create_quality_controls,
                               style="Success.TButton",
                               width=18)
        create_btn.pack(side='right')
    
    def show_preview(self):
        """Show preview of selected QCs"""
        selected = [ctrl for ctrl, var in self.control_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("No Selection", 
                                  "Please select at least one Quality Control type.")
            return
        
        info = "═" * 50 + "\n"
        info += "QUALITY CONTROL PREVIEW\n"
        info += "═" * 50 + "\n\n"
        info += f"Work Order: {self.work_order or 'Not specified'}\n"
        info += f"Lab Sample ID: {self.lab_sample_id or 'Not specified'}\n"
        info += f"Analyte Name: {self.analyte_name or 'Not specified'}\n"
        info += f"Analyte Group ID: {self.analyte_group_id or 'Not specified'}\n\n"
        info += f"Selected QC Types: {', '.join(selected)}\n"
        info += "═" * 50
        
        messagebox.showinfo("Preview", info)
    
    def create_quality_controls(self):
        """Main function to create quality controls"""
        selected = [ctrl for ctrl, var in self.control_vars.items() if var.get()]
        
        # Validation
        if not selected:
            messagebox.showerror("Error", 
                               "Please select at least one Quality Control type.")
            return
        
        # Confirmation
        confirm_msg = f"Create the following Quality Controls?\n\n"
        confirm_msg += f"QC Types: {', '.join(selected)}\n"
        confirm_msg += f"Work Order: {self.work_order}\n"
        confirm_msg += f"Lab Sample ID: {self.lab_sample_id}\n"
        confirm_msg += f"Analyte: {self.analyte_name}\n"
        
        if messagebox.askyesno("Confirm Creation", confirm_msg):
            try:
                self.execute_qc_creation(selected)
                
                messagebox.showinfo("Success",
                                   f"Quality Controls created successfully!\n\n"
                                   f"Created: {', '.join(selected)}\n"
                                   f"For Sample: {self.lab_sample_id}")
                
                self.window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", 
                                   f"Failed to create Quality Controls:\n{str(e)}")
    
    def execute_qc_creation(self, control_types):
        """
        Execute QC creation in database
        
        Args:
            control_types: List of selected control types ['MB', 'LCS', etc.]
        """
        print(f"Creating QC:")
        print(f"  Control Types: {control_types}")
        print(f"  Work Order: {self.work_order}")
        print(f"  Lab Sample ID: {self.lab_sample_id}")
        print(f"  Analyte Name: {self.analyte_name}")
        print(f"  Analyte Group ID: {self.analyte_group_id}")
        
        
        
        send_data_to_process = {}
        
        
        send_data_to_process["control_type"] = control_types
        send_data_to_process["work_order"] = self.work_order
        send_data_to_process["lab_sample_id"] = self.lab_sample_id
        send_data_to_process["analyte_name"] = self.analyte_name
        send_data_to_process["analyte_group_id"] = self.analyte_group_id
        send_data_to_process["client_sample_id"] = self.client_sample_id
        
        process_mb(send_data_to_process)
        
        # TODO: Implement actual database insertion
        # conn = None
        # cursor = None
        # try:
        #     instance_db = DatabaseConnection()
        #     conn = DatabaseConnection.get_conn(instance_db)
        #     cursor = conn.cursor()
        #     
        #     for qc_type in control_types:
        #         query = """
        #             INSERT INTO QualityControls 
        #             (WorkOrder, LabSampleID, AnalyteName, AnalyteGroupID, QCType)
        #             VALUES (?, ?, ?, ?, ?)
        #         """
        #         cursor.execute(query, (self.work_order, self.lab_sample_id, 
        #                               self.analyte_name, self.analyte_group_id, qc_type))
        #     
        #     conn.commit()
        #     
        # except Exception as e:
        #     if conn:
        #         conn.rollback()
        #     raise e
        # finally:
        #     if cursor:
        #         cursor.close()
        #     if conn:
        #         conn.close()
        
        import time
        time.sleep(0.5)


def show_create_qc_view(parent=None, work_order=None, lab_sample_id=None,
                       analyte_name=None, analyte_group_id=None):
    """
    Function to open the QC creation view
    
    Args:
        parent: Parent window
        work_order: Work Order ID
        lab_sample_id: Lab Sample ID
        analyte_name: Analyte Name
        analyte_group_id: Analyte Group ID
    
    Example usage:
        show_create_qc_view(
            parent=main_window,
            work_order="WO-2024-001",
            lab_sample_id="LS-12345",
            analyte_name="Lead",
            analyte_group_id="METALS-01"
        )
    """
    qc_view = CreateQc(
        parent=parent,
        work_order=work_order,
        lab_sample_id=lab_sample_id,
        analyte_name=analyte_name,
        analyte_group_id=analyte_group_id
    )
    
    if parent:
        qc_view.window.grab_set()
        qc_view.window.focus_set()
    
    if parent is None:
        qc_view.window.mainloop()
    
    return qc_view


def create_qc(work_order=None, lab_sample_id=None, 
             analyte_name=None, analyte_group_id=None):
    """
    Helper function to create QC without parent window
    """
    show_create_qc_view(
        work_order=work_order,
        lab_sample_id=lab_sample_id,
        analyte_name=analyte_name,
        analyte_group_id=analyte_group_id
    )
    return True
