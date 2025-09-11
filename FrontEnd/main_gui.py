from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.append(str(PROJECT_ROOT))
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_DIR))

from FrontEnd.Views.import_tab import ImportTab
 
from FrontEnd.Styles.config_styles import configure_styles
from FrontEnd.Views.loading_view import LoadingView
from FrontEnd.Views.report_tab import ReportTab

class Main_Gui:

    def __init__(self, root):

        BASE_DIR = Path(__file__).parent.resolve()
        
        self.root = root
        self.root.title("App")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.iconbitmap(BASE_DIR / "Assets" / "logos" / "LOGO_SRL_FINAL.ico")

        # Ocultar inicialmente la ventana principal
        self.root.withdraw()
        self.dark_color = '#1a202c'
        # Estilo ttk
        self.style = ttk.Style()
        configure_styles(self.style)  

        # Visibles para almacenar el batch ID actual
        self.current_batch_id = None

        self.file_path = BASE_DIR / "Assets" / "logos" / "LOGO_SRL_FINAL.png"

        self.initialize_with_loading()

        # Sección para controlar hilos de ejecución
        self.db_thread_pool = []
        self.is_loading = False

    def initialize_with_loading(self):
        self.loading_view = LoadingView(
            root=self.root,
            logo_path=self.file_path,
            app_instance=self
        )
        self.loading_view.create_splash_screen()
        self.loading_view.start_loading_sequence()

    def close_splash_and_show_main(self):
        """Cerrar splash y mostrar ventana principal"""
        if self.loading_view and self.loading_view.splash and self.loading_view.splash.winfo_exists():
            self.loading_view.splash.destroy()

        # Mostrar la ventana principal
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
    def setup_header(self):
        """Setup the header with logo and title"""
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10), ipady=10)
        
        # Logo with better sizing and padding
        try:
            BASE_DIR = Path(__file__).parent.resolve()

            original_image = Image.open(BASE_DIR / "assets" / "logos" / "LOGO_SRL_FINAL.png")
            resized_image = original_image.resize((50, 50), Image.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_image)
            
            logo_label = ttk.Label(header_frame, image=self.logo_image, background=self.dark_color)
            logo_label.image = self.logo_image
            logo_label.pack(side=tk.LEFT, padx=(15, 10))
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.logo_image = tk.PhotoImage(width=40, height=40)
            logo_label = ttk.Label(header_frame, image=self.logo_image, background=self.dark_color)
            logo_label.pack(side=tk.LEFT, padx=(15, 10))
        
        title_label = ttk.Label(header_frame, 
                              text="App", 
                              style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Spacer to push user info to the right
        ttk.Label(header_frame, 
                 text="", 
                 background=self.dark_color).pack(side=tk.LEFT, expand=True)

    def setup_main_interface(self):
        # Main container with subtle gradient background
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Setup header with logo
        self.setup_header()
        
        # Create notebook for tabs with modern styling
        self.notebook = ttk.Notebook(self.main_frame, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        
        # Create tabs
        self.report_tab = ReportTab(self.notebook)
        self.notebook.add(self.report_tab, text="Report")
        
        
        self.import_tab = ImportTab(self.notebook)
        self.notebook.add(self.import_tab, text="Import")

        # SECCION PARA CONTROLAR HILOS DE EJECUCIÓN
        self.db_thread_pool = []
        self.is_loading = False
    


def main():
    """Función principal para iniciar la aplicación"""
    root = tk.Tk()
    app = Main_Gui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
