from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading


def get_project_root():
    """Obtiene la raíz del proyecto de manera más eficiente"""
    return Path(__file__).parent.parent.absolute()


# Configuración de paths del proyecto
PROJECT_ROOT = get_project_root()
sys.path.append(str(PROJECT_ROOT))

# Importaciones después de configurar el path
from FrontEnd.Views.import_tab import ImportTab
from FrontEnd.Styles.config_styles import configure_styles
from FrontEnd.Views.loading_view import LoadingView
from FrontEnd.Views.report_tab import ReportTab


class Main_Gui:
    def __init__(self, root):
        self.root = root
        self.setup_window_properties()

        # Variables de estado
        self.current_batch_id = None
        self.db_thread_pool = []
        self.is_loading = False

        # Configurar estilos
        self.style = ttk.Style()
        configure_styles(self.style)
        self.dark_color = '#1a202c'

        # Inicializar con pantalla de carga
        self.initialize_with_loading()

    def setup_window_properties(self):
        """Configura las propiedades de la ventana principal"""
        self.root.title("App")

        # Obtener dimensiones de pantalla con márgenes
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Usar ventana maximizada en lugar de dimensiones fijas
        self.root.state('zoomed')  # Esto funciona mejor en Windows
        # Alternativa para todos los sistemas:
        # self.root.attributes('-zoomed', True)  # Para sistemas Unix/Linux

        # Configurar icono
        BASE_DIR = Path(__file__).parent.resolve()
        icon_path = BASE_DIR / "Assets" / "logos" / "LOGO_SRL_FINAL.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"Error loading icon: {e}")

        # Ocultar inicialmente la ventana principal
        self.root.withdraw()

    def initialize_with_loading(self):
        """Inicializa la aplicación con pantalla de carga"""
        BASE_DIR = Path(__file__).parent.resolve()
        logo_path = BASE_DIR / "Assets" / "logos" / "LOGO_SRL_FINAL.png"

        self.loading_view = LoadingView(
            root=self.root,
            logo_path=logo_path,
            app_instance=self
        )
        self.loading_view.create_splash_screen()
        self.loading_view.start_loading_sequence()

    def close_splash_and_show_main(self):
        """Cierra la pantalla de carga y muestra la interfaz principal"""
        if (hasattr(self, 'loading_view') and
                self.loading_view and
                hasattr(self.loading_view, 'splash') and
                self.loading_view.splash and
                self.loading_view.splash.winfo_exists()):

            # Destruir splash de forma segura
            try:
                self.loading_view.splash.destroy()
            except tk.TclError:
                pass  # La ventana ya fue destruida

        # Mostrar la ventana principal
        self.root.deiconify()
        self.setup_main_interface()
        self.root.lift()
        self.root.focus_force()

    def setup_main_interface(self):
        """Configura la interfaz principal de la aplicación"""
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Configurar header
        self.setup_header()

        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        # Crear pestañas
        self.create_tabs()

    def setup_header(self):
        """Configura el encabezado con logo y título"""
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10), ipady=10)

        # Logo con mejor manejo de tamaño y espaciado
        try:
            BASE_DIR = Path(__file__).parent.resolve()
            logo_path = BASE_DIR / "Assets" / "logos" / "LOGO_SRL_FINAL.png"

            if logo_path.exists():
                original_image = Image.open(logo_path)
                # Redimensionar manteniendo relación de aspecto
                original_image.thumbnail((50, 50), Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(original_image)

                logo_label = ttk.Label(header_frame, image=self.logo_image,
                                       background=self.dark_color)
                logo_label.image = self.logo_image  # Guardar referencia
                logo_label.pack(side=tk.LEFT, padx=(15, 10))
            else:
                self.create_placeholder_logo(header_frame)

        except Exception as e:
            print(f"Error loading logo: {e}")
            self.create_placeholder_logo(header_frame)

        # Título de la aplicación
        title_label = ttk.Label(header_frame,
                                text="App",
                                style='Header.TLabel')
        title_label.pack(side=tk.LEFT)

        # Espaciador para alinear a la derecha información de usuario
        ttk.Label(header_frame, text="", background=self.dark_color).pack(
            side=tk.LEFT, expand=True)

    def create_placeholder_logo(self, parent):
        """Crea un logo de marcador de posición si no se encuentra el original"""
        placeholder = tk.PhotoImage(width=40, height=40)
        logo_label = ttk.Label(parent, image=placeholder, background=self.dark_color)
        logo_label.image = placeholder  # Guardar referencia
        logo_label.pack(side=tk.LEFT, padx=(15, 10))

    def create_tabs(self):
        """Crea y configura las pestañas de la aplicación"""
        # Pestaña de Reportes
        self.report_tab = ReportTab(self.notebook)
        self.notebook.add(self.report_tab, text="Report")

        # Pestaña de Importación
        self.import_tab = ImportTab(self.notebook)
        self.notebook.add(self.import_tab, text="Import")

    def safe_destroy(self):
        """Destruye la aplicación de manera segura, cerrando todos los hilos"""
        # Cerrar todos los hilos activos
        for thread in self.db_thread_pool:
            if thread.is_alive():
                # Marcar para terminación (depende de tu implementación)
                pass

        if self.root.winfo_exists():
            self.root.quit()
            self.root.destroy()


def main():
    """Función principal para iniciar la aplicación"""
    root = tk.Tk()
    app = Main_Gui(root)

    # Asegurar que la aplicación se cierre correctamente
    root.protocol("WM_DELETE_WINDOW", app.safe_destroy)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.safe_destroy()


if __name__ == "__main__":
    main()