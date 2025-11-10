from pathlib import Path
import threading
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import math

from FrontEnd.Styles.config_styles import configure_styles
from BackEnd.Database.General.get_connection import DatabaseConnection


class LoadingView:
    def __init__(self, root, logo_path=None, app_instance=None):
        self.root = root
        self.file_path = logo_path
        self.app_instance = app_instance
        self.db_connection = None
        self.db_config = "DB_ACTIVE_CONFIG"

        self.style = ttk.Style()
        configure_styles(self.style)
        self.add_custom_styles()

        self.splash = None
        self.splash_logo_image = None
        self.splash_progress_bar = None
        self.splash_status_label = None
        self.logo_label = None
        self.animation_running = False

    def create_splash_screen(self):
        azul_fondo = "#1a365d"
        self.splash = tk.Toplevel(self.root)
        self.splash.title("SRL")
        self.splash.geometry("500x350")  # Aumentamos ligeramente el tamaño
        self.splash.configure(bg=azul_fondo)

        self.center_splash_window()
        self.splash.transient(self.root)
        self.splash.grab_set()
        self.splash.overrideredirect(True)

        # Añadir sombra sutil alrededor de la ventana
        self.splash.attributes('-alpha', 0.98)

        main_frame = tk.Frame(self.splash, bg=azul_fondo)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Frame para el logo con efecto de elevación
        logo_frame = tk.Frame(main_frame, bg=azul_fondo, highlightthickness=0)
        logo_frame.pack(pady=(10, 15))

        self.setup_splash_logo(logo_frame, azul_fondo)

        title_label = tk.Label(
            main_frame,
            text="SRL",
            fg="white",
            bg=azul_fondo,
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(5, 5))

        subtitle_label = tk.Label(
            main_frame,
            text="Data Management System",
            fg="#a0aec0",
            bg=azul_fondo,
            font=("Arial", 11)
        )
        subtitle_label.pack(pady=(0, 20))

        self.setup_splash_progress(main_frame)

        self.splash_status_label = tk.Label(
            main_frame,
            text="Initializing...",
            fg="#e2e8f0",
            bg=azul_fondo,
            font=("Arial", 10)
        )
        self.splash_status_label.pack(pady=(15, 5))

        bottom_frame = tk.Frame(main_frame, bg=azul_fondo)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))

        version_label = tk.Label(bottom_frame, text="Version 1.0.1", fg="#718096", bg=azul_fondo, font=("Arial", 8))
        version_label.pack(side=tk.LEFT)

        connection_label = tk.Label(bottom_frame, text="DB: SRLFLORIDA", fg="#718096", bg=azul_fondo, font=("Arial", 8))
        connection_label.pack(side=tk.RIGHT)

        # Iniciar animación del logo
        self.start_logo_animation()

    def start_logo_animation(self):
        """Inicia una animación sutil de flotación para el logo"""
        if not self.logo_label or not self.splash.winfo_exists():
            return

        self.animation_running = True
        self.animate_logo(0)

    def animate_logo(self, offset):
        """Anima el logo con un efecto de flotación suave"""
        if not self.animation_running or not self.splash.winfo_exists():
            return

        # Movimiento sinusoidal suave
        new_offset = math.sin(offset * 0.5) * 3

        if self.logo_label:
            self.logo_label.place(y=10 + new_offset)

        # Programar siguiente frame de animación
        if self.animation_running and self.splash.winfo_exists():
            self.splash.after(50, lambda: self.animate_logo(offset + 0.1))

    def stop_logo_animation(self):
        """Detiene la animación del logo"""
        self.animation_running = False

    def start_loading_sequence(self):
        def loading_thread():
            try:
                self.safe_update_progress(10, "Initializing system...")
                time.sleep(0.3)

                self.safe_update_progress(30, "Loading core modules...")
                time.sleep(0.4)

                self.safe_update_progress(50, "Testing database connection...")
                db = DatabaseConnection()
                success, message = db.test_connection()

                if not success:
                    self.safe_update_progress(50, "Database connection failed!")
                    time.sleep(0.8)
                    self.root.after(0, lambda: self.show_connection_error(message))
                    return

                self.db_connection = db.get_conn()
                self.safe_update_progress(70, "Database connection established!")
                time.sleep(0.3)

                self.safe_update_progress(85, "Setting up interface...")
                if self.app_instance:
                    self.root.after(0, lambda: configure_styles(self.app_instance.style))
                time.sleep(0.3)

                self.safe_update_progress(95, "Configuring components...")
                """if self.app_instance:
                    self.root.after(0, self.app_instance.setup_main_interface)"""
                time.sleep(0.3)

                # Efecto de completado con pausa
                self.safe_update_progress(100, "Ready!")
                time.sleep(0.8)

                self.root.after(0, self.app_instance.close_splash_and_show_main)

            except Exception as e:
                error_msg = f"Initialization error: {str(e)}"
                self.safe_update_progress(0, "Initialization failed!")
                self.root.after(0, lambda: self.show_connection_error(error_msg))

        thread = threading.Thread(target=loading_thread, daemon=True)
        thread.start()

    def safe_update_progress(self, progress, status_text):
        self.root.after(0, lambda: self.update_splash_progress(progress, status_text))

    def show_connection_error(self, error_message):
        self.stop_logo_animation()
        if hasattr(self, 'splash') and self.splash.winfo_exists():
            self.splash.destroy()

        self.root.deiconify()

        error_win = tk.Toplevel(self.root)
        error_win.title("Database Connection Error")
        error_win.geometry("500x300")  # Ajuste de tamaño
        error_win.configure(bg='#1a365d')
        error_win.transient(self.root)
        error_win.grab_set()
        error_win.attributes('-alpha', 0.98)  # Transparencia sutil

        self.center_window(error_win, 500, 300)

        main_frame = tk.Frame(error_win, bg='#1a365d')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        error_icon = tk.Label(main_frame, text="⚠️", fg="white", bg='#1a365d', font=("Arial", 32))
        error_icon.pack(pady=(10, 15))

        title_label = tk.Label(main_frame, text="Database Connection Failed",
                               fg="white", bg='#1a365d', font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))

        # Frame para el texto de error con scrollbar
        error_frame = tk.Frame(main_frame, bg='#1a365d')
        error_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        error_text = tk.Text(
            error_frame,
            height=6,
            width=55,
            bg="#2d4a66",
            fg='white',
            font=('Arial', 9),
            wrap=tk.WORD,
            relief="flat",
            bd=1,
            padx=10,
            pady=10,
            highlightthickness=0
        )
        error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(error_frame, orient=tk.VERTICAL, command=error_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        error_text.configure(yscrollcommand=scrollbar.set)

        error_text.insert(tk.END, error_message)
        error_text.configure(state=tk.DISABLED)

        btn_frame = tk.Frame(main_frame, bg='#1a365d')
        btn_frame.pack(pady=(10, 0))

        retry_btn = tk.Button(btn_frame, text="Retry Connection", bg="#4a90e2", fg="white",
                              font=("Arial", 10, "bold"), relief="flat", padx=20, pady=8,
                              command=lambda: self.retry_connection(error_win))
        retry_btn.pack(side=tk.LEFT, padx=8)

        config_btn = tk.Button(btn_frame, text="Change Config", bg="#f5a623", fg="white",
                               font=("Arial", 10, "bold"), relief="flat", padx=20, pady=8,
                               command=lambda: self.show_config_dialog(error_win))
        config_btn.pack(side=tk.LEFT, padx=8)

        exit_btn = tk.Button(btn_frame, text="Exit Application", bg="#d0021b", fg="white",
                             font=("Arial", 10, "bold"), relief="flat", padx=20, pady=8,
                             command=self.root.quit)
        exit_btn.pack(side=tk.LEFT, padx=8)

    def retry_connection(self, error_window):
        error_window.destroy()
        self.root.withdraw()
        self.create_splash_screen()
        self.start_loading_sequence()

    def show_config_dialog(self, error_window):
        config_win = tk.Toplevel(error_window)
        config_win.title("Database Configuration")
        config_win.geometry("350x250")
        config_win.configure(bg='#1a365d')
        config_win.transient(error_window)
        config_win.grab_set()
        config_win.attributes('-alpha', 0.98)

        self.center_window(config_win, 350, 250)

        frame = tk.Frame(config_win, bg='#1a365d')
        frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        tk.Label(frame, text="Select Database Configuration:",
                 fg="white", bg='#1a365d', font=("Arial", 12, "bold")).pack(pady=(0, 20))

        selected_config = tk.StringVar(value=self.db_config)

        # Aquí irían las opciones de configuración (simplificado)
        options_frame = tk.Frame(frame, bg='#1a365d')
        options_frame.pack(pady=(0, 25))

        # Simulamos opciones (deberías reemplazar esto con tus configuraciones reales)
        for i, config in enumerate(["DB_ACTIVE_CONFIG", "DB_BACKUP_CONFIG", "DB_TEST_CONFIG"]):
            rb = tk.Radiobutton(options_frame, text=config, variable=selected_config,
                                value=config, bg='#1a365d', fg='white',
                                selectcolor='#2d4a66', font=("Arial", 9))
            rb.pack(anchor=tk.W, pady=3)

        btn_frame = tk.Frame(frame, bg='#1a365d')
        btn_frame.pack(pady=(15, 0))

        apply_btn = tk.Button(btn_frame, text="Apply & Retry", bg="#4a90e2", fg="white",
                              font=("Arial", 10, "bold"), relief="flat", padx=15, pady=6,
                              command=lambda: self.apply_config_and_retry(selected_config.get(), config_win,
                                                                          error_window))
        apply_btn.pack(side=tk.LEFT, padx=8)

        cancel_btn = tk.Button(btn_frame, text="Cancel", bg="#7f8c8d", fg="white",
                               font=("Arial", 10, "bold"), relief="flat", padx=15, pady=6,
                               command=config_win.destroy)
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
        width, height = 500, 350
        screen_w = self.splash.winfo_screenwidth()
        screen_h = self.splash.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.splash.geometry(f"{width}x{height}+{x}+{y}")

    def setup_splash_logo(self, parent_frame, bg="#1a365d"):
        try:
            if self.file_path and Path(self.file_path).exists():
                original_image = Image.open(self.file_path)
                # Añadir un efecto de suavizado y resizing mejorado
                resized_image = original_image.resize((80, 80), Image.Resampling.LANCZOS)
                self.splash_logo_image = ImageTk.PhotoImage(resized_image)

                # Usar place para permitir animación
                self.logo_label = tk.Label(
                    parent_frame,
                    image=self.splash_logo_image,
                    bg=bg,
                    borderwidth=0,
                    highlightthickness=0
                )
                self.logo_label.place(x=0, y=10, width=80, height=80)
                parent_frame.configure(width=80, height=100)
            else:
                raise FileNotFoundError("Logo not found")
        except Exception:
            placeholder_label = tk.Label(parent_frame, text="🔬", fg="white", bg=bg, font=("Arial", 32))
            placeholder_label.pack(pady=(10, 10))
            self.logo_label = placeholder_label

    def setup_splash_progress(self, parent_frame):
        # Frame para la barra de progreso con sombra
        progress_container = tk.Frame(parent_frame, bg='#2d4a66', relief='flat',
                                      highlightthickness=0, height=14)
        progress_container.pack(pady=(5, 0), fill=tk.X)
        progress_container.pack_propagate(False)

        self.splash_progress_bar = ttk.Progressbar(
            progress_container,
            length=300,
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.splash_progress_bar.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def update_splash_progress(self, progress, status_text):
        if hasattr(self, 'splash') and self.splash and self.splash.winfo_exists():
            try:
                # Transición suave del progreso
                current_progress = self.splash_progress_bar['value']
                step = 2 if progress > current_progress else -2

                def animate_progress(target):
                    current = self.splash_progress_bar['value']
                    if (step > 0 and current < target) or (step < 0 and current > target):
                        self.splash_progress_bar['value'] = current + step
                        self.splash.after(10, lambda: animate_progress(target))
                    else:
                        self.splash_progress_bar['value'] = target

                animate_progress(progress)

                self.splash_status_label.config(text=status_text)
                self.splash.update()
            except tk.TclError:
                pass

    def close_splash_and_show_main(self):
        # Detener animación del logo
        self.stop_logo_animation()

        # Añadir efecto de desvanecimiento
        def fade_out():
            current_alpha = self.splash.attributes('-alpha')
            if current_alpha > 0:
                self.splash.attributes('-alpha', current_alpha - 0.05)
                self.splash.after(20, fade_out)
            else:
                if hasattr(self, 'splash') and self.splash and self.splash.winfo_exists():
                    try:
                        self.splash.grab_release()
                        self.splash.destroy()
                    except tk.TclError:
                        pass
                self.show_main_window()

        fade_out()

    def show_main_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()

    def add_custom_styles(self):
        base_blue = "#1a365d"
        dark_blue = "#2d4a66"
        light_blue = "#4a90e2"

        self.style.configure('Custom.Horizontal.TProgressbar',
                             troughcolor=dark_blue,
                             background=light_blue,
                             thickness=10,
                             bordercolor=base_blue,
                             lightcolor=light_blue,
                             darkcolor=light_blue)