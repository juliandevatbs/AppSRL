from pathlib import Path
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from FrontEnd.Styles.config_styles import configure_styles
from BackEnd.Database.General.get_connection import DatabaseConnection


class LoadingView:
    def __init__(self, root, logo_path=None, app_instance=None):
        self.root = root
        self.file_path = logo_path

        self.app_instance = app_instance  # Referencia a la clase App
        self.db_connection = None
        self.connection_failed = False
        self.db_config = list("DB_ACTIVE_CONFIG")[0]  # Valor por defecto

        self.style = ttk.Style()
        configure_styles(self.style)

        # Variables para el splash
        self.splash = None
        self.splash_logo_image = None
        self.splash_progress_bar = None
        self.splash_status_label = None

        # Variables para la aplicación principal
        self.db_thread_pool = []
        self.is_loading = False

    def create_splash_screen(self):
        """Crear la pantalla splash con estilo moderno usando ttk."""
        self.splash = tk.Toplevel(self.root)
        self.splash.title("SRLIMS")
        self.splash.geometry("480x320")
        self.splash.configure(bg='#34495e')  # Fondo moderno azul grisáceo

        self.center_splash_window()
        self.splash.transient(self.root)
        self.splash.grab_set()
        self.splash.overrideredirect(True)

        main_frame = ttk.Frame(self.splash, style='Splash.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        self.setup_splash_logo(main_frame)

        title_label = ttk.Label(
            main_frame,
            text="SRLIMS",
            style='SplashTitle.TLabel'
        )
        title_label.pack(pady=(15, 5))

        subtitle_label = ttk.Label(
            main_frame,
            text="Data Management System",
            style='SplashSubtitle.TLabel'
        )
        subtitle_label.pack(pady=(0, 25))

        self.setup_splash_progress(main_frame)

        self.splash_status_label = ttk.Label(
            main_frame,
            text="Initializing...",
            style='SplashStatus.TLabel'
        )
        self.splash_status_label.pack(pady=(15, 10))

        bottom_frame = ttk.Frame(main_frame, style='Splash.TFrame')
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))

        version_label = ttk.Label(bottom_frame, text="Version 1.0.1", style='SplashFooter.TLabel')
        version_label.pack(side=tk.LEFT)

        connection_label = ttk.Label(bottom_frame, text="DB: SRLFLORIDA", style='SplashFooter.TLabel')
        connection_label.pack(side=tk.RIGHT)

    def start_loading_sequence(self):
        """Iniciar la secuencia de carga con validación de BD en hilo."""
        def loading_thread():
            try:
                self.safe_update_progress(10, "Initializing system...")
                time.sleep(0.5)

                self.safe_update_progress(30, "Loading core modules...")
                time.sleep(0.5)

                self.safe_update_progress(50, "Testing database connection...")
                db = DatabaseConnection()
                success, message= db.test_connection()

                if not success:
                    self.safe_update_progress(50, "Database connection failed!")
                    time.sleep(1)
                    self.root.after(0, lambda: self.show_connection_error(message))
                    return

                self.db_connection = db.get_conn()
                self.safe_update_progress(70, "Database connection established!")
                time.sleep(0.6)

                self.safe_update_progress(85, "Setting up interface...")
                if self.app_instance:
                    self.root.after(0, lambda: configure_styles(self.app_instance.style))
                time.sleep(0.5)

                self.safe_update_progress(95, "Configuring components...")
                if self.app_instance:
                    self.root.after(0, self.app_instance.setup_main_interface)
                time.sleep(0.6)

                self.safe_update_progress(100, "Ready!")
                time.sleep(0.7)

                self.root.after(0, self.close_splash_and_show_main)

            except Exception as e:
                error_msg = f"Initialization error: {str(e)}"
                self.safe_update_progress(0, "Initialization failed!")
                self.root.after(0, lambda: self.show_connection_error(error_msg))

        thread = threading.Thread(target=loading_thread, daemon=True)
        thread.start()

    def safe_update_progress(self, progress, status_text):
        """Actualizar barra y texto progreso desde hilo seguro."""
        self.root.after(0, lambda: self.update_splash_progress(progress, status_text))

    def show_connection_error(self, error_message):
        """Ventana error conexión DB con estilo moderno ttk."""
        if hasattr(self, 'splash') and self.splash.winfo_exists():
            self.splash.destroy()

        self.root.deiconify()

        error_win = tk.Toplevel(self.root)
        error_win.title("Database Connection Error")
        error_win.geometry("480x320")
        error_win.configure(bg='#e74c3c')
        error_win.transient(self.root)
        error_win.grab_set()

        self.center_window(error_win, 480, 320)

        main_frame = ttk.Frame(error_win, style='Error.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        error_icon = ttk.Label(main_frame, text="⚠️", style='ErrorIcon.TLabel')
        error_icon.pack(pady=(10, 15))

        title_label = ttk.Label(main_frame, text="Database Connection Failed", style='ErrorTitle.TLabel')
        title_label.pack(pady=(0, 10))

        error_text = tk.Text(main_frame, height=6, width=58, bg='#c0392b', fg='white', font=('Century Gothic', 10), wrap=tk.WORD, state=tk.NORMAL)
        error_text.pack(pady=(0, 15))
        error_text.insert(tk.END, error_message)
        error_text.configure(state=tk.DISABLED)

        btn_frame = ttk.Frame(main_frame, style='Error.TFrame')
        btn_frame.pack()

        retry_btn = ttk.Button(btn_frame, text="Retry Connection", style='Retry.TButton', command=lambda: self.retry_connection(error_win))
        retry_btn.pack(side=tk.LEFT, padx=10)

        config_btn = ttk.Button(btn_frame, text="Change Config", style='Config.TButton', command=lambda: self.show_config_dialog(error_win))
        config_btn.pack(side=tk.LEFT, padx=10)

        exit_btn = ttk.Button(btn_frame, text="Exit Application", style='Exit.TButton', command=self.root.quit)
        exit_btn.pack(side=tk.LEFT, padx=10)

    def retry_connection(self, error_window):
        error_window.destroy()
        self.root.withdraw()
        self.create_splash_screen()
        self.start_loading_sequence()

    def show_config_dialog(self, error_window):
        config_win = tk.Toplevel(error_window)
        config_win.title("Database Configuration")
        config_win.geometry("350x250")
        config_win.configure(bg='#34495e')
        config_win.transient(error_window)
        config_win.grab_set()

        self.center_window(config_win, 350, 250)

        frame = ttk.Frame(config_win, style='Splash.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        ttk.Label(frame, text="Select Database Configuration:", style='SplashSubtitle.TLabel').pack(pady=(0, 15))

        selected_config = tk.StringVar(value=self.db_config)

        

        btn_frame = ttk.Frame(frame, style='Splash.TFrame')
        btn_frame.pack(pady=(20, 0))

        apply_btn = ttk.Button(btn_frame, text="Apply & Retry", style='Success.TButton', command=lambda: self.apply_config_and_retry(selected_config.get(), config_win, error_window))
        apply_btn.pack(side=tk.LEFT, padx=8)

        cancel_btn = ttk.Button(btn_frame, text="Cancel", style='Cancel.TButton', command=config_win.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=8)

    def apply_config_and_retry(self, new_config, config_window, error_window):
        self.db_config = new_config
        config_window.destroy()
        self.retry_connection(error_window)

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def center_splash_window(self):
        self.splash.update_idletasks()
        width, height = 480, 320
        screen_w = self.splash.winfo_screenwidth()
        screen_h = self.splash.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.splash.geometry(f"{width}x{height}+{x}+{y}")

    def setup_splash_logo(self, parent_frame):
        try:
            if self.file_path and Path(self.file_path).exists():
                original_image = Image.open(self.file_path)
                resized_image = original_image.resize((90, 90), Image.Resampling.LANCZOS)
                self.splash_logo_image = ImageTk.PhotoImage(resized_image)

                logo_label = ttk.Label(parent_frame, image=self.splash_logo_image, style='SplashLogo.TLabel')
                logo_label.pack(pady=(10,15))
            else:
                raise FileNotFoundError("Logo not found")
        except Exception as e:
            print(f"Error loading splash logo: {e}")
            placeholder_label = ttk.Label(parent_frame, text="🔬", style='SplashLogo.TLabel')
            placeholder_label.pack(pady=(15,15))

    def setup_splash_progress(self, parent_frame):
        self.splash_progress_bar = ttk.Progressbar(parent_frame, length=280, mode='determinate', style='SplashProgress.Horizontal.TProgressbar')
        self.splash_progress_bar.pack(pady=(10, 10))

    def update_splash_progress(self, progress, status_text):
        if hasattr(self, 'splash') and self.splash and self.splash.winfo_exists():
            try:
                self.splash_progress_bar['value'] = progress
                self.splash_status_label.config(text=status_text)
                self.splash.update()
            except tk.TclError:
                pass  # Ventana ya destruida

    def close_splash_and_show_main(self):
        if hasattr(self, 'splash') and self.splash and self.splash.winfo_exists():
            try:
                self.splash.grab_release()
                self.splash.destroy()
            except tk.TclError:
                pass

        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        self.root.focus_force()

# Estilos adicionales para el splash y error
def add_custom_styles(style):
    style.configure('Splash.TFrame', background='#34495e')
    style.configure('SplashTitle.TLabel', font=('Century Gothic', 28, 'bold'), foreground='white', background='#34495e')
    style.configure('SplashSubtitle.TLabel', font=('Century Gothic', 12), foreground='#bdc3c7', background='#34495e')
    style.configure('SplashStatus.TLabel', font=('Century Gothic', 10), foreground='white', background='#34495e')
    style.configure('SplashFooter.TLabel', font=('Century Gothic', 9), foreground='#7f8c8d', background='#34495e')
    style.configure('SplashLogo.TLabel', background='#34495e')

    style.configure('SplashProgress.Horizontal.TProgressbar',
                    troughcolor='#2c3e50',
                    background='#3498db',
                    thickness=15,
                    bordercolor='#34495e')

    style.configure('Error.TFrame', background='#c0392b')
    style.configure('ErrorIcon.TLabel', font=('Century Gothic', 48, 'bold'), foreground='white', background='#c0392b')
    style.configure('ErrorTitle.TLabel', font=('Century Gothic', 16, 'bold'), foreground='white', background='#c0392b')

    style.configure('Retry.TButton', background='#2980b9', foreground='white')
    style.configure('Config.TButton', background='#f39c12', foreground='white')
    style.configure('Exit.TButton', background='#e74c3c', foreground='white')
    style.configure('Success.TButton', background='#27ae60', foreground='white')
    style.configure('Cancel.TButton', background='#95a5a6', foreground='white')

    style.configure('Config.TRadiobutton', font=('Century Gothic', 11), foreground='white', background='#34495e')
