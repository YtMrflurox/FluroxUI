import os
import sys
import asyncio
import aiohttp
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext, colorchooser
import threading
import queue
import re
import json
from datetime import datetime
import random
import requests
from ttkbootstrap import Style, Window, Frame, Label, Button, Entry, Checkbutton, Combobox, Notebook, Progressbar, Scrollbar, Treeview, Labelframe, Spinbox
from PIL import Image, ImageTk
import jsbeautifier
import json

# ----------------- Common API/Backend Paths -----------------
COMMON_BACKEND_PATHS = [
    '/robots.txt',
    '/sitemap.xml',
    '/sitemap_index.xml',
    '/.well-known/security.txt',
    '/api',
    '/api/v1',
    '/api/v2',
    '/api/v3',
    '/graphql',
    '/swagger.json',
    '/openapi.json',
    '/api-docs',
    '/api/docs',
    '/wp-json',
    '/wp-json/wp/v2/posts',
    '/wp-json/wp/v2/pages',
    '/feed',
    '/feed/atom',
    '/rss',
    '/.env',
    '/config.json',
    '/manifest.json',
    '/package.json',
    '/composer.json',
    '/info',
    '/health',
    '/healthz',
    '/status',
    '/version',
    '/.git/config',
    '/.git/HEAD',
    '/server-status',
    '/server-info',
    '/debug',
    '/metrics',
    '/admin/config',
]

# ----------------- Website Copier Class -----------------
class WebsiteCopier:
    def __init__(self, root):
        self.root = root
        self.root.title("Darkmirror Pro - Advanced Website Copier")
        self.root.geometry("1200x800")
        
        # Set initial theme
        self.current_theme = "darkly"
        self.style = Style(theme=self.current_theme)
        
        # Enhanced attributes
        self.output_folder = None
        self.site_folder = None
        self.urls_to_download = set()
        self.downloaded_urls = set()
        self.failed_urls = set()
        self.session = None
        self.is_paused = False
        self.is_canceled = False
        self.download_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.start_time = None
        self.settings = {
            'max_concurrent': 10,
            'timeout': 30,
            'retry_count': 3,
            'delay': 0.5,
            'include_images': True,
            'include_css': True,
            'include_js': True,
            'include_media': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'depth_limit': 5,
            'exclude_patterns': [],
            'custom_headers': {},
            'use_proxy': False,
            'proxies': [],
            'current_proxy': None,
            'rotate_proxy': False,
            'speed_limit': 0,  # KB/s, 0 = no limit
            'theme': 'darkly',
            'log_level': 'INFO',
            'animations': True,
            'include_backend': True,
            'brute_api_paths': True,
            'extract_api_from_js': True,
            'save_api_responses': True,
            'custom_api_paths': []
        }
        self.stats = {
            'total_files': 0,
            'downloaded_files': 0,
            'failed_files': 0,
            'bytes_downloaded': 0
        }
        self.download_history = []
        self.proxy_list = []
        self.themes = [
            "darkly", "cyborg", "superhero", "solar", "vapor", 
            "minty", "lumen", "sandstone", "yeti", "pulse", 
            "flatly", "litera", "materia", "morph", "journal"
        ]
        self.current_tab = 0  # To store the current tab index
        
        self.create_gui()
        self.load_settings()
        self.update_log_display()

    # ----------------- GUI Layout -----------------
    def create_gui(self):
        # Create main container with gradient background
        self.main_container = Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create header with logo and title
        self.create_header()
        
        # Create notebook for tabs
        self.notebook = Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: Main Download
        self.main_tab = Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Download")
        
        # Tab 2: Proxies
        self.proxy_tab = Frame(self.notebook)
        self.notebook.add(self.proxy_tab, text="Proxies")
        
        # Tab 3: History
        self.history_tab = Frame(self.notebook)
        self.notebook.add(self.history_tab, text="History")
        
        # Tab 4: Settings
        self.settings_tab = Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Create content for each tab
        self.create_main_tab()
        self.create_proxy_tab()
        self.create_history_tab()
        self.create_settings_tab()
        
        # Create status bar
        self.create_status_bar()

    def create_header(self):
        header_frame = Frame(self.main_container, bootstyle="dark")
        header_frame.pack(fill=tk.X, padx=0, pady=0)

        left = Frame(header_frame, bootstyle="dark")
        left.pack(side=tk.LEFT, padx=15, pady=8)

        Label(left, text="DARKMIRROR", font=("Consolas", 22, "bold"),
              bootstyle="inverse-dark").pack(side=tk.LEFT)
        Label(left, text="  PRO", font=("Consolas", 12),
              foreground="#ff4444", bootstyle="inverse-dark").pack(side=tk.LEFT, pady=(6, 0))
        Label(left, text="  v2.0", font=("Consolas", 9),
              foreground="#666666", bootstyle="inverse-dark").pack(side=tk.LEFT, pady=(8, 0))

        self.phase_label = Label(left, text="", font=("Consolas", 10, "bold"),
                                 foreground="#00ff88", bootstyle="inverse-dark")
        self.phase_label.pack(side=tk.LEFT, padx=(20, 0), pady=(6, 0))

        right = Frame(header_frame, bootstyle="dark")
        right.pack(side=tk.RIGHT, padx=15, pady=8)

        Label(right, text="Theme", font=("Consolas", 9),
              bootstyle="inverse-dark").pack(side=tk.LEFT, padx=(0, 5))
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = Combobox(right, textvariable=self.theme_var, values=self.themes, width=12,
                               font=("Consolas", 9))
        theme_combo.pack(side=tk.LEFT)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

    def create_main_tab(self):
        main_container = Frame(self.main_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        # --- Top row: URL + Output + Start button, compact ---
        top = Frame(main_container)
        top.pack(fill=tk.X, pady=(0, 5))

        Label(top, text="URL", font=("Consolas", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.url_entry = Entry(top, width=55, font=("Consolas", 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.output_button = Button(top, text="Output Folder", command=self.select_output_folder,
                                    bootstyle="secondary-outline", width=14)
        self.output_button.pack(side=tk.LEFT, padx=(0, 5))

        self.start_button = Button(top, text="START", command=self.start_copy,
                                   bootstyle="success", width=10, padding=(12, 6))
        self.start_button.pack(side=tk.LEFT, padx=(0, 3))

        self.pause_button = Button(top, text="PAUSE", command=self.pause_download,
                                   state=tk.DISABLED, bootstyle="warning-outline", width=8)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 3))

        self.cancel_button = Button(top, text="STOP", command=self.cancel_download,
                                    state=tk.DISABLED, bootstyle="danger-outline", width=8)
        self.cancel_button.pack(side=tk.LEFT)

        # Output path label
        self.output_label = Label(main_container, text="No folder selected",
                                  font=("Consolas", 9), foreground="#888888")
        self.output_label.pack(fill=tk.X, pady=(0, 5))

        # --- Options: two groups side by side ---
        options_row = Frame(main_container)
        options_row.pack(fill=tk.X, pady=(0, 5))

        # Frontend options
        fe_frame = Labelframe(options_row, text="FRONTEND", bootstyle="success", padding=5)
        fe_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        fe_grid = Frame(fe_frame)
        fe_grid.pack(fill=tk.X)

        self.include_images_var = tk.BooleanVar(value=True)
        Checkbutton(fe_grid, text="Images", variable=self.include_images_var,
                    bootstyle="success-round-toggle").grid(row=0, column=0, sticky=tk.W, padx=4, pady=1)

        self.include_css_var = tk.BooleanVar(value=True)
        Checkbutton(fe_grid, text="CSS", variable=self.include_css_var,
                    bootstyle="success-round-toggle").grid(row=0, column=1, sticky=tk.W, padx=4, pady=1)

        self.include_js_var = tk.BooleanVar(value=True)
        Checkbutton(fe_grid, text="JavaScript", variable=self.include_js_var,
                    bootstyle="success-round-toggle").grid(row=0, column=2, sticky=tk.W, padx=4, pady=1)

        self.include_media_var = tk.BooleanVar(value=True)
        Checkbutton(fe_grid, text="Media", variable=self.include_media_var,
                    bootstyle="success-round-toggle").grid(row=0, column=3, sticky=tk.W, padx=4, pady=1)

        fe_params = Frame(fe_frame)
        fe_params.pack(fill=tk.X, pady=(4, 0))
        Label(fe_params, text="Depth:", font=("Consolas", 9)).pack(side=tk.LEFT, padx=(0, 3))
        self.depth_limit_var = tk.IntVar(value=3)
        Spinbox(fe_params, from_=1, to=10, textvariable=self.depth_limit_var, width=4,
                font=("Consolas", 9)).pack(side=tk.LEFT, padx=(0, 10))
        Label(fe_params, text="Speed (KB/s):", font=("Consolas", 9)).pack(side=tk.LEFT, padx=(0, 3))
        self.speed_limit_var = tk.IntVar(value=0)
        Spinbox(fe_params, from_=0, to=10000, increment=100, textvariable=self.speed_limit_var,
                width=6, font=("Consolas", 9)).pack(side=tk.LEFT)

        # Backend options
        be_frame = Labelframe(options_row, text="BACKEND / API", bootstyle="danger", padding=5)
        be_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        be_grid = Frame(be_frame)
        be_grid.pack(fill=tk.X)

        self.include_backend_var = tk.BooleanVar(value=True)
        Checkbutton(be_grid, text="Enable", variable=self.include_backend_var,
                    bootstyle="danger-round-toggle").grid(row=0, column=0, sticky=tk.W, padx=4, pady=1)

        self.brute_api_var = tk.BooleanVar(value=True)
        Checkbutton(be_grid, text="Brute Paths", variable=self.brute_api_var,
                    bootstyle="danger-round-toggle").grid(row=0, column=1, sticky=tk.W, padx=4, pady=1)

        self.extract_api_js_var = tk.BooleanVar(value=True)
        Checkbutton(be_grid, text="Extract from JS", variable=self.extract_api_js_var,
                    bootstyle="danger-round-toggle").grid(row=1, column=0, sticky=tk.W, padx=4, pady=1)

        self.save_api_responses_var = tk.BooleanVar(value=True)
        Checkbutton(be_grid, text="Save Responses", variable=self.save_api_responses_var,
                    bootstyle="danger-round-toggle").grid(row=1, column=1, sticky=tk.W, padx=4, pady=1)

        # --- Progress section: dual bars + stats cards ---
        progress_frame = Labelframe(main_container, text="PROGRESS", bootstyle="info", padding=5)
        progress_frame.pack(fill=tk.X, pady=(0, 5))

        # Frontend progress bar
        fe_prog = Frame(progress_frame)
        fe_prog.pack(fill=tk.X, pady=(0, 3))
        Label(fe_prog, text="Frontend", font=("Consolas", 9, "bold"), width=10).pack(side=tk.LEFT)
        self.progress_bar = Progressbar(fe_prog, mode="determinate", bootstyle="success-striped")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.progress_percent = Label(fe_prog, text="0%", font=("Consolas", 9, "bold"), width=6)
        self.progress_percent.pack(side=tk.LEFT)

        # Backend progress bar
        be_prog = Frame(progress_frame)
        be_prog.pack(fill=tk.X, pady=(0, 3))
        Label(be_prog, text="Backend", font=("Consolas", 9, "bold"), width=10).pack(side=tk.LEFT)
        self.backend_progress_bar = Progressbar(be_prog, mode="determinate", bootstyle="danger-striped")
        self.backend_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.backend_progress_percent = Label(be_prog, text="0%", font=("Consolas", 9, "bold"), width=6)
        self.backend_progress_percent.pack(side=tk.LEFT)

        # Stats cards row
        stats_row = Frame(progress_frame)
        stats_row.pack(fill=tk.X, pady=(3, 0))

        self.stat_files = self._create_stat_card(stats_row, "FILES", "0 / 0", "info")
        self.stat_failed = self._create_stat_card(stats_row, "FAILED", "0", "danger")
        self.stat_size = self._create_stat_card(stats_row, "SIZE", "0 B", "success")
        self.stat_speed = self._create_stat_card(stats_row, "SPEED", "0 B/s", "warning")
        self.stat_backend = self._create_stat_card(stats_row, "API HITS", "0", "danger")

        self.stats_label = Label(progress_frame, text="", font=("Consolas", 8))
        self.stats_label.pack()

        # --- Log panel ---
        log_frame = Labelframe(main_container, text="LOG", bootstyle="dark", padding=3)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        log_toolbar = Frame(log_frame)
        log_toolbar.pack(fill=tk.X, pady=(0, 3))

        Label(log_toolbar, text="Filter:", font=("Consolas", 9)).pack(side=tk.LEFT, padx=(0, 3))
        self.log_filter_var = tk.StringVar(value="ALL")
        log_filter_combo = Combobox(log_toolbar, textvariable=self.log_filter_var,
                                    values=["ALL", "INFO", "WARNING", "ERROR", "DEBUG"],
                                    width=8, font=("Consolas", 9))
        log_filter_combo.pack(side=tk.LEFT, padx=(0, 8))
        log_filter_combo.bind("<<ComboboxSelected>>", self.filter_log)

        Button(log_toolbar, text="Clear", command=self.clear_log,
               bootstyle="secondary-outline", width=6).pack(side=tk.LEFT)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, wrap=tk.WORD,
                                                  font=("Consolas", 9),
                                                  background="#1a1a2e", foreground="#eeeeee",
                                                  insertbackground="#ffffff")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.log_text.tag_configure("INFO", foreground="#00ff88")
        self.log_text.tag_configure("WARNING", foreground="#ffaa00")
        self.log_text.tag_configure("ERROR", foreground="#ff4444")
        self.log_text.tag_configure("DEBUG", foreground="#4488ff")
        self.log_text.tag_configure("PHASE", foreground="#ff44ff", font=("Consolas", 9, "bold"))

    def _create_stat_card(self, parent, title, value, style):
        card = Frame(parent, bootstyle=style, padding=4)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        lbl_title = Label(card, text=title, font=("Consolas", 8), bootstyle=f"inverse-{style}")
        lbl_title.pack()
        lbl_value = Label(card, text=value, font=("Consolas", 12, "bold"), bootstyle=f"inverse-{style}")
        lbl_value.pack()
        return lbl_value

    def create_proxy_tab(self):
        proxy_container = Frame(self.proxy_tab)
        proxy_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        # Top row: toggles + toolbar
        top = Frame(proxy_container)
        top.pack(fill=tk.X, pady=(0, 5))

        self.use_proxy_var = tk.BooleanVar(value=False)
        Checkbutton(top, text="Use Proxy", variable=self.use_proxy_var,
                    command=self.toggle_proxy_settings,
                    bootstyle="success-round-toggle").pack(side=tk.LEFT, padx=(0, 10))

        self.proxy_options_frame = Frame(top)
        self.proxy_options_frame.pack(side=tk.LEFT)

        self.rotate_proxy_var = tk.BooleanVar(value=False)
        Checkbutton(self.proxy_options_frame, text="Rotate Proxies",
                    variable=self.rotate_proxy_var,
                    bootstyle="warning-round-toggle").pack(side=tk.LEFT, padx=(0, 15))

        # Toolbar buttons
        toolbar = Frame(top)
        toolbar.pack(side=tk.RIGHT)

        Button(toolbar, text="+ Add", command=self.add_proxy_dialog,
               bootstyle="success-outline", width=7).pack(side=tk.LEFT, padx=2)
        Button(toolbar, text="Edit", command=self.edit_proxy,
               bootstyle="info-outline", width=6).pack(side=tk.LEFT, padx=2)
        Button(toolbar, text="Remove", command=self.remove_proxy,
               bootstyle="danger-outline", width=8).pack(side=tk.LEFT, padx=2)
        Button(toolbar, text="Test", command=self.test_proxy,
               bootstyle="warning-outline", width=6).pack(side=tk.LEFT, padx=2)
        Button(toolbar, text="Import", command=self.import_proxies,
               bootstyle="secondary-outline", width=8).pack(side=tk.LEFT, padx=2)
        Button(toolbar, text="Export", command=self.export_proxies,
               bootstyle="secondary-outline", width=8).pack(side=tk.LEFT, padx=2)

        # Proxy count label
        self.proxy_count_label = Label(proxy_container, text="0 proxies loaded",
                                       font=("Consolas", 9), foreground="#888888")
        self.proxy_count_label.pack(fill=tk.X, pady=(0, 3))

        # Proxy list treeview
        list_frame = Frame(proxy_container)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.proxy_tree = Treeview(list_frame,
                                   columns=("type", "host", "port", "username", "status"),
                                   show="headings", bootstyle="dark")
        self.proxy_tree.heading("type", text="Type")
        self.proxy_tree.heading("host", text="Host")
        self.proxy_tree.heading("port", text="Port")
        self.proxy_tree.heading("username", text="Username")
        self.proxy_tree.heading("status", text="Status")

        self.proxy_tree.column("type", width=80)
        self.proxy_tree.column("host", width=200)
        self.proxy_tree.column("port", width=80)
        self.proxy_tree.column("username", width=150)
        self.proxy_tree.column("status", width=100)

        proxy_scrollbar = Scrollbar(list_frame, orient=tk.VERTICAL, command=self.proxy_tree.yview)
        self.proxy_tree.configure(yscrollcommand=proxy_scrollbar.set)

        self.proxy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        proxy_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.proxy_tree.bind("<Double-1>", lambda e: self.edit_proxy())

    def create_history_tab(self):
        # History tab layout
        history_container = Frame(self.history_tab)
        history_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # History toolbar
        history_toolbar = Frame(history_container)
        history_toolbar.pack(fill=tk.X, pady=5)
        
        Button(history_toolbar, text="Refresh", command=self.refresh_history, bootstyle="primary").pack(side=tk.LEFT, padx=2)
        Button(history_toolbar, text="Clear History", command=self.clear_history, bootstyle="danger").pack(side=tk.LEFT, padx=2)
        Button(history_toolbar, text="Export Report", command=self.export_report, bootstyle="info").pack(side=tk.LEFT, padx=2)
        
        # History list
        history_list_container = Frame(history_container)
        history_list_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview for history with modern styling
        self.history_tree = Treeview(history_list_container, columns=("date", "url", "files", "size", "status"), show="headings", bootstyle="dark")
        self.history_tree.heading("date", text="Date")
        self.history_tree.heading("url", text="URL")
        self.history_tree.heading("files", text="Files")
        self.history_tree.heading("size", text="Size")
        self.history_tree.heading("status", text="Status")
        
        self.history_tree.column("date", width=150)
        self.history_tree.column("url", width=300)
        self.history_tree.column("files", width=80)
        self.history_tree.column("size", width=100)
        self.history_tree.column("status", width=100)
        
        # Scrollbar for history list
        history_scrollbar = Scrollbar(history_list_container, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view details
        self.history_tree.bind("<Double-1>", lambda e: self.view_history_details())

    def create_settings_tab(self):
        # Settings tab layout
        settings_container = Frame(self.settings_tab)
        settings_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for settings categories
        settings_notebook = Notebook(settings_container)
        settings_notebook.pack(fill=tk.BOTH, expand=True)
        
        # General settings tab
        general_tab = Frame(settings_notebook)
        settings_notebook.add(general_tab, text="General")
        
        # Connection settings tab
        connection_tab = Frame(settings_notebook)
        settings_notebook.add(connection_tab, text="Connection")
        
        # Appearance settings tab
        appearance_tab = Frame(settings_notebook)
        settings_notebook.add(appearance_tab, text="Appearance")
        
        # Advanced settings tab
        advanced_tab = Frame(settings_notebook)
        settings_notebook.add(advanced_tab, text="Advanced")
        
        # Create content for each settings tab
        self.create_general_settings(general_tab)
        self.create_connection_settings(connection_tab)
        self.create_appearance_settings(appearance_tab)
        self.create_advanced_settings(advanced_tab)

    def create_general_settings(self, parent):
        # General settings
        general_frame = Frame(parent)
        general_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Max Concurrent
        Label(general_frame, text="Max Concurrent Downloads:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_concurrent_var = tk.IntVar(value=self.settings['max_concurrent'])
        Spinbox(general_frame, from_=1, to=50, textvariable=self.max_concurrent_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Timeout
        Label(general_frame, text="Timeout (seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.timeout_var = tk.IntVar(value=self.settings['timeout'])
        Spinbox(general_frame, from_=5, to=120, textvariable=self.timeout_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Retry Count
        Label(general_frame, text="Retry Count:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.retry_var = tk.IntVar(value=self.settings['retry_count'])
        Spinbox(general_frame, from_=0, to=10, textvariable=self.retry_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Delay
        Label(general_frame, text="Delay Between Requests (seconds):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.delay_var = tk.DoubleVar(value=self.settings['delay'])
        Spinbox(general_frame, from_=0, to=5, increment=0.1, textvariable=self.delay_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # User Agent
        Label(general_frame, text="User Agent:").grid(row=4, column=0, sticky=tk.NW, padx=5, pady=5)
        self.user_agent_var = tk.StringVar(value=self.settings['user_agent'])
        user_agent_entry = Entry(general_frame, textvariable=self.user_agent_var, width=50)
        user_agent_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Exclude Patterns
        Label(general_frame, text="Exclude Patterns (one per line):").grid(row=5, column=0, sticky=tk.NW, padx=5, pady=5)
        self.exclude_patterns_text = scrolledtext.ScrolledText(general_frame, width=50, height=5)
        self.exclude_patterns_text.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.exclude_patterns_text.insert(tk.END, "\n".join(self.settings['exclude_patterns']))

    def create_connection_settings(self, parent):
        # Connection settings
        connection_frame = Frame(parent)
        connection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Custom Headers
        Label(connection_frame, text="Custom Headers (JSON format):").pack(anchor=tk.W, padx=5, pady=5)
        self.headers_text = scrolledtext.ScrolledText(connection_frame, width=70, height=15)
        self.headers_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.headers_text.insert(tk.END, json.dumps(self.settings['custom_headers'], indent=2))

    def create_appearance_settings(self, parent):
        # Appearance settings
        appearance_frame = Frame(parent)
        appearance_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Theme
        Label(appearance_frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.theme_var = tk.StringVar(value=self.settings['theme'])
        theme_combo = Combobox(appearance_frame, textvariable=self.theme_var, 
                                  values=self.themes, width=20)
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        # Log level
        Label(appearance_frame, text="Log Level:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.log_level_var = tk.StringVar(value=self.settings['log_level'])
        log_level_combo = Combobox(appearance_frame, textvariable=self.log_level_var, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"], width=20)
        log_level_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Animations
        self.animations_var = tk.BooleanVar(value=self.settings.get('animations', True))
        Checkbutton(appearance_frame, text="Enable Animations", variable=self.animations_var, bootstyle="info-round-toggle").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Color theme
        Label(appearance_frame, text="Custom Colors:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        color_frame = Frame(appearance_frame)
        color_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        Button(color_frame, text="Primary Color", command=self.choose_primary_color, bootstyle="primary").pack(side=tk.LEFT, padx=2)
        Button(color_frame, text="Secondary Color", command=self.choose_secondary_color, bootstyle="secondary").pack(side=tk.LEFT, padx=2)
        Button(color_frame, text="Reset Colors", command=self.reset_colors, bootstyle="warning").pack(side=tk.LEFT, padx=2)

    def create_advanced_settings(self, parent):
        # Advanced settings
        advanced_frame = Frame(parent)
        advanced_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File naming rules
        Label(advanced_frame, text="File Naming Rules:").pack(anchor=tk.W, padx=5, pady=5)
        
        naming_frame = Frame(advanced_frame)
        naming_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.preserve_structure_var = tk.BooleanVar(value=True)
        Checkbutton(naming_frame, text="Preserve Directory Structure", variable=self.preserve_structure_var, bootstyle="success-round-toggle").pack(anchor=tk.W, padx=5, pady=2)
        
        self.clean_filenames_var = tk.BooleanVar(value=True)
        Checkbutton(naming_frame, text="Clean Filenames (remove special chars)", variable=self.clean_filenames_var, bootstyle="success-round-toggle").pack(anchor=tk.W, padx=5, pady=2)
        
        self.add_index_var = tk.BooleanVar(value=True)
        Checkbutton(naming_frame, text="Add index.html to directories", variable=self.add_index_var, bootstyle="success-round-toggle").pack(anchor=tk.W, padx=5, pady=2)
        
        # Advanced options
        Label(advanced_frame, text="Advanced Options:").pack(anchor=tk.W, padx=5, pady=10)
        
        advanced_options_frame = Frame(advanced_frame)
        advanced_options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.follow_redirects_var = tk.BooleanVar(value=True)
        Checkbutton(advanced_options_frame, text="Follow Redirects", variable=self.follow_redirects_var, bootstyle="info-round-toggle").pack(anchor=tk.W, padx=5, pady=2)
        
        self.verify_ssl_var = tk.BooleanVar(value=True)
        Checkbutton(advanced_options_frame, text="Verify SSL Certificates", variable=self.verify_ssl_var, bootstyle="info-round-toggle").pack(anchor=tk.W, padx=5, pady=2)
        
        self.parse_javascript_var = tk.BooleanVar(value=False)
        Checkbutton(advanced_options_frame, text="Parse JavaScript for URLs", variable=self.parse_javascript_var, bootstyle="info-round-toggle").pack(anchor=tk.W, padx=5, pady=2)

        # Custom API paths for backend discovery
        Label(advanced_frame, text="Custom API Paths (one per line):").pack(anchor=tk.W, padx=5, pady=10)
        self.custom_api_paths_text = scrolledtext.ScrolledText(advanced_frame, width=60, height=6)
        self.custom_api_paths_text.pack(fill=tk.X, padx=5, pady=5)
        self.custom_api_paths_text.insert(tk.END, "\n".join(self.settings.get('custom_api_paths', [])))

    def create_status_bar(self):
        self.status_bar = Frame(self.root, bootstyle="dark")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = Label(self.status_bar, text="Ready", anchor=tk.W,
                                  font=("Consolas", 9), bootstyle="inverse-dark")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=4)

        self.progress_status = Label(self.status_bar, text="0 files",
                                     font=("Consolas", 9), bootstyle="inverse-dark")
        self.progress_status.pack(side=tk.RIGHT, padx=10, pady=4)

        self.elapsed_label = Label(self.status_bar, text="",
                                   font=("Consolas", 9), bootstyle="inverse-dark")
        self.elapsed_label.pack(side=tk.RIGHT, padx=10, pady=4)

    # ----------------- Theme Functions -----------------
    def change_theme(self, event=None):
        new_theme = self.theme_var.get()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            
            # Change theme with animation if enabled
            if self.animations_var.get():
                # Fade out effect
                self.root.attributes("-alpha", 0.8)
                self.root.update()
                
                # Change theme
                self.style.theme_use(new_theme)
                
                # Fade in effect
                for i in range(8, 11):
                    self.root.attributes("-alpha", i/10)
                    self.root.update()
                    time.sleep(0.05)
            else:
                # Change theme without animation
                self.style.theme_use(new_theme)
            
            # Update settings
            self.settings['theme'] = new_theme
            self.save_settings()

    # ----------------- Proxy Functions -----------------
    def toggle_proxy_settings(self):
        state = tk.NORMAL if self.use_proxy_var.get() else tk.DISABLED
        for child in self.proxy_options_frame.winfo_children():
            try:
                child.config(state=state)
            except tk.TclError:
                pass

    def add_proxy_dialog(self):
        # Create a dialog to add a proxy
        proxy_dialog = tk.Toplevel(self.root)
        proxy_dialog.title("Add Proxy")
        proxy_dialog.geometry("400x300")
        proxy_dialog.transient(self.root)
        proxy_dialog.grab_set()
        
        # Proxy type
        Label(proxy_dialog, text="Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        proxy_type_var = tk.StringVar(value="HTTP")
        Combobox(proxy_dialog, textvariable=proxy_type_var, values=["HTTP", "HTTPS", "SOCKS4", "SOCKS5"], width=15).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Host
        Label(proxy_dialog, text="Host:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        host_var = tk.StringVar()
        Entry(proxy_dialog, textvariable=host_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Port
        Label(proxy_dialog, text="Port:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        port_var = tk.IntVar(value=8080)
        Spinbox(proxy_dialog, from_=1, to=65535, textvariable=port_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Username
        Label(proxy_dialog, text="Username:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        username_var = tk.StringVar()
        Entry(proxy_dialog, textvariable=username_var, width=30).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Password
        Label(proxy_dialog, text="Password:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        password_var = tk.StringVar()
        Entry(proxy_dialog, textvariable=password_var, width=30, show="*").grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        button_frame = Frame(proxy_dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        def add_proxy():
            proxy = {
                'type': proxy_type_var.get(),
                'host': host_var.get(),
                'port': port_var.get(),
                'username': username_var.get(),
                'password': password_var.get(),
                'status': 'Untested'
            }
            
            self.proxy_list.append(proxy)
            self.update_proxy_tree()
            proxy_dialog.destroy()
        
        Button(button_frame, text="Add", command=add_proxy, bootstyle="success").pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Cancel", command=proxy_dialog.destroy, bootstyle="danger").pack(side=tk.LEFT, padx=5)

    def edit_proxy(self):
        # Get selected proxy
        selected_item = self.proxy_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a proxy to edit.")
            return
        
        # Get proxy index
        proxy_index = self.proxy_tree.index(selected_item[0])
        proxy = self.proxy_list[proxy_index]
        
        # Create a dialog to edit the proxy
        proxy_dialog = tk.Toplevel(self.root)
        proxy_dialog.title("Edit Proxy")
        proxy_dialog.geometry("400x300")
        proxy_dialog.transient(self.root)
        proxy_dialog.grab_set()

        # Proxy type
        Label(proxy_dialog, text="Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        proxy_type_var = tk.StringVar(value=proxy['type'])
        Combobox(proxy_dialog, textvariable=proxy_type_var, values=["HTTP", "HTTPS", "SOCKS4", "SOCKS5"], width=15).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Host
        Label(proxy_dialog, text="Host:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        host_var = tk.StringVar(value=proxy['host'])
        Entry(proxy_dialog, textvariable=host_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Port
        Label(proxy_dialog, text="Port:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        port_var = tk.IntVar(value=proxy['port'])
        Spinbox(proxy_dialog, from_=1, to=65535, textvariable=port_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Username
        Label(proxy_dialog, text="Username:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        username_var = tk.StringVar(value=proxy['username'])
        Entry(proxy_dialog, textvariable=username_var, width=30).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Password
        Label(proxy_dialog, text="Password:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        password_var = tk.StringVar(value=proxy['password'])
        Entry(proxy_dialog, textvariable=password_var, width=30, show="*").grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        button_frame = Frame(proxy_dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        def save_proxy():
            proxy['type'] = proxy_type_var.get()
            proxy['host'] = host_var.get()
            proxy['port'] = port_var.get()
            proxy['username'] = username_var.get()
            proxy['password'] = password_var.get()
            
            self.update_proxy_tree()
            proxy_dialog.destroy()
        
        Button(button_frame, text="Save", command=save_proxy, bootstyle="success").pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Cancel", command=proxy_dialog.destroy, bootstyle="danger").pack(side=tk.LEFT, padx=5)

    def remove_proxy(self):
        # Get selected proxy
        selected_item = self.proxy_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a proxy to remove.")
            return
        
        # Get proxy index
        proxy_index = self.proxy_tree.index(selected_item[0])
        
        # Remove proxy
        del self.proxy_list[proxy_index]
        self.update_proxy_tree()

    def test_proxy(self):
        # Get selected proxy
        selected_item = self.proxy_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a proxy to test.")
            return
        
        # Get proxy index
        proxy_index = self.proxy_tree.index(selected_item[0])
        proxy = self.proxy_list[proxy_index]
        
        # Test proxy in a separate thread
        def test_proxy_thread():
            try:
                # Create proxy URL
                if proxy['username'] and proxy['password']:
                    proxy_url = f"{proxy['type'].lower()}://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
                else:
                    proxy_url = f"{proxy['type'].lower()}://{proxy['host']}:{proxy['port']}"
                
                # Test with requests
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                
                response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
                
                if response.status_code == 200:
                    proxy['status'] = 'Working'
                    self.root.after(0, lambda: messagebox.showinfo("Proxy Test", "Proxy is working!"))
                else:
                    proxy['status'] = 'Failed'
                    self.root.after(0, lambda: messagebox.showerror("Proxy Test", f"Proxy test failed: {response.status_code}"))
            except Exception as e:
                proxy['status'] = 'Error'
                self.root.after(0, lambda: messagebox.showerror("Proxy Test", f"Proxy test failed: {str(e)}"))
            
            # Update proxy tree
            self.root.after(0, self.update_proxy_tree)
        
        # Start test thread
        threading.Thread(target=test_proxy_thread).start()

    def import_proxies(self):
        file_path = filedialog.askopenfilename(
            title="Import Proxies",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_path:
            return

        imported = 0
        current_type = "HTTP"

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Detect section headers like "# —— PAID SOCKS5 PROXIES ——"
                    if line.startswith('#'):
                        upper = line.upper()
                        if 'SOCKS5' in upper:
                            current_type = "SOCKS5"
                        elif 'SOCKS4' in upper:
                            current_type = "SOCKS4"
                        elif 'HTTPS' in upper:
                            current_type = "HTTPS"
                        elif 'HTTP' in upper:
                            current_type = "HTTP"
                        continue

                    parts = line.split(':')
                    if len(parts) < 2:
                        continue

                    # Detect format: if first part is a known type, use old format
                    if parts[0].upper() in ("HTTP", "HTTPS", "SOCKS4", "SOCKS5"):
                        proxy_type = parts[0].upper()
                        host = parts[1]
                        port = int(parts[2]) if len(parts) > 2 else 8080
                        username = parts[3] if len(parts) > 3 else ""
                        password = parts[4] if len(parts) > 4 else ""
                    else:
                        # Format: host:port or host:port:user:pass
                        proxy_type = current_type
                        host = parts[0]
                        port = int(parts[1]) if len(parts) > 1 else 8080
                        username = parts[2] if len(parts) > 2 else ""
                        password = parts[3] if len(parts) > 3 else ""

                    proxy = {
                        'type': proxy_type,
                        'host': host,
                        'port': port,
                        'username': username,
                        'password': password,
                        'status': 'Untested'
                    }

                    self.proxy_list.append(proxy)
                    imported += 1

            self.update_proxy_tree()
            messagebox.showinfo("Import Proxies", f"Imported {imported} proxies.")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import proxies: {str(e)}")

    def export_proxies(self):
        # Export proxies to file
        if not self.proxy_list:
            messagebox.showwarning("No Proxies", "No proxies to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Proxies",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as f:
                for proxy in self.proxy_list:
                    # Format: type:host:port:username:password
                    line = f"{proxy['type']}:{proxy['host']}:{proxy['port']}:{proxy['username']}:{proxy['password']}\n"
                    f.write(line)
            
            messagebox.showinfo("Export Proxies", f"Successfully exported {len(self.proxy_list)} proxies.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export proxies: {str(e)}")

    def update_proxy_tree(self):
        for item in self.proxy_tree.get_children():
            self.proxy_tree.delete(item)

        if hasattr(self, 'proxy_count_label'):
            socks = sum(1 for p in self.proxy_list if 'SOCKS' in p.get('type', ''))
            http = len(self.proxy_list) - socks
            self.proxy_count_label.config(
                text=f"{len(self.proxy_list)} proxies loaded  |  HTTP: {http}  |  SOCKS: {socks}")

        for proxy in self.proxy_list:
            # Set color based on status
            if proxy['status'] == 'Working':
                tag = 'success'
            elif proxy['status'] in ['Failed', 'Error']:
                tag = 'danger'
            else:
                tag = 'info'
            
            item = self.proxy_tree.insert("", "end", values=(
                proxy['type'],
                proxy['host'],
                proxy['port'],
                proxy['username'] if proxy['username'] else "",
                proxy['status']
            ), tags=(tag,))
            
            # Configure tag colors
            self.proxy_tree.tag_configure('success', foreground='green')
            self.proxy_tree.tag_configure('danger', foreground='red')
            self.proxy_tree.tag_configure('info', foreground='blue')

    # ----------------- History Functions -----------------
    def refresh_history(self):
        # Clear history tree
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add history items to tree
        for history in self.download_history:
            # Set color based on status
            if history['status'] == 'Completed':
                tag = 'success'
            elif history['status'] == 'Completed with errors':
                tag = 'warning'
            else:
                tag = 'danger'
            
            item = self.history_tree.insert("", "end", values=(
                history['date'],
                history['url'],
                f"{history['files']} files",
                self.format_bytes(history['size']),
                history['status']
            ), tags=(tag,))
            
            # Configure tag colors
            self.history_tree.tag_configure('success', foreground='green')
            self.history_tree.tag_configure('warning', foreground='orange')
            self.history_tree.tag_configure('danger', foreground='red')

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the download history?"):
            self.download_history = []
            self.refresh_history()

    def export_report(self):
        # Get selected history item
        selected_item = self.history_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a download to export.")
            return
        
        # Get history index
        history_index = self.history_tree.index(selected_item[0])
        history = self.download_history[history_index]
        
        # Export report
        file_path = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.html'):
                # HTML report with modern styling
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Download Report - {history['url']}</title>
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; color: #333; }}
                        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                        h2 {{ color: #3498db; }}
                        .container {{ max-width: 1000px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .info-box {{ background-color: #e8f4fc; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0; }}
                        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                        th {{ background-color: #3498db; color: white; }}
                        tr:nth-child(even) {{ background-color: #f2f2f2; }}
                        .status-completed {{ color: #27ae60; font-weight: bold; }}
                        .status-warning {{ color: #f39c12; font-weight: bold; }}
                        .status-error {{ color: #e74c3c; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Download Report</h1>
                        <h2>{history['url']}</h2>
                        
                        <div class="info-box">
                            <p><strong>Date:</strong> {history['date']}</p>
                            <p><strong>Status:</strong> <span class="status-{history['status'].lower().replace(' ', '-')}">{history['status']}</span></p>
                            <p><strong>Files Downloaded:</strong> {history['files']}</p>
                            <p><strong>Total Size:</strong> {self.format_bytes(history['size'])}</p>
                        </div>
                        
                        <h3>Downloaded Files</h3>
                        <table>
                            <tr>
                                <th>File</th>
                                <th>Size</th>
                                <th>Status</th>
                            </tr>
                """
                
                for file_info in history.get('file_list', []):
                    status_class = file_info['status'].lower().replace(' ', '-')
                    html_content += f"""
                        <tr>
                            <td>{file_info['path']}</td>
                            <td>{self.format_bytes(file_info['size'])}</td>
                            <td class="status-{status_class}">{file_info['status']}</td>
                        </tr>
                    """
                
                html_content += """
                        </table>
                    </div>
                </body>
                </html>
                """
                
                with open(file_path, 'w') as f:
                    f.write(html_content)
            else:
                # Text report
                with open(file_path, 'w') as f:
                    f.write(f"Download Report\n")
                    f.write(f"===============\n\n")
                    f.write(f"URL: {history['url']}\n")
                    f.write(f"Date: {history['date']}\n")
                    f.write(f"Status: {history['status']}\n")
                    f.write(f"Files Downloaded: {history['files']}\n")
                    f.write(f"Total Size: {self.format_bytes(history['size'])}\n\n")
                    f.write("Downloaded Files:\n")
                    f.write("----------------\n")
                    
                    for file_info in history.get('file_list', []):
                        f.write(f"File: {file_info['path']}\n")
                        f.write(f"Size: {self.format_bytes(file_info['size'])}\n")
                        f.write(f"Status: {file_info['status']}\n\n")
            
            messagebox.showinfo("Export Report", "Report exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

    def view_history_details(self):
        # Get selected history item
        selected_item = self.history_tree.selection()
        if not selected_item:
            return
        
        # Get history index
        history_index = self.history_tree.index(selected_item[0])
        history = self.download_history[history_index]
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title("Download Details")
        details_window.geometry("700x500")
        details_window.transient(self.root)

        # Details text
        details_text = scrolledtext.ScrolledText(details_window)
        details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add details
        details_text.insert(tk.END, f"URL: {history['url']}\n", "title")
        details_text.insert(tk.END, f"Date: {history['date']}\n", "info")
        details_text.insert(tk.END, f"Status: {history['status']}\n", "status")
        details_text.insert(tk.END, f"Files Downloaded: {history['files']}\n", "info")
        details_text.insert(tk.END, f"Total Size: {self.format_bytes(history['size'])}\n\n", "info")
        details_text.insert(tk.END, "Downloaded Files:\n", "title")
        details_text.insert(tk.END, "----------------\n", "separator")
        
        for file_info in history.get('file_list', []):
            details_text.insert(tk.END, f"File: {file_info['path']}\n", "file")
            details_text.insert(tk.END, f"Size: {self.format_bytes(file_info['size'])}\n", "info")
            details_text.insert(tk.END, f"Status: {file_info['status']}\n\n", "status")
        
        # Configure tags
        details_text.tag_configure("title", font=("Arial", 12, "bold"))
        details_text.tag_configure("info", foreground="blue")
        details_text.tag_configure("status", foreground="green")
        details_text.tag_configure("file", foreground="black")
        details_text.tag_configure("separator", foreground="gray")
        
        # Close button
        Button(details_window, text="Close", command=details_window.destroy, bootstyle="primary").pack(pady=10)

    # ----------------- Settings Functions -----------------
    def choose_primary_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            # Apply color to UI elements
            self.style.configure("TButton", background=color)
            self.style.configure("TLabel", background=color)

    def choose_secondary_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            # Apply color to UI elements
            self.style.configure("TFrame", background=color)

    def reset_colors(self):
        # Reset to default theme colors
        self.style.theme_use(self.current_theme)

    def save_settings(self):
        try:
            # Update settings from UI
            self.settings['max_concurrent'] = self.max_concurrent_var.get()
            self.settings['timeout'] = self.timeout_var.get()
            self.settings['retry_count'] = self.retry_var.get()
            self.settings['delay'] = self.delay_var.get()
            self.settings['user_agent'] = self.user_agent_var.get()
            self.settings['exclude_patterns'] = self.exclude_patterns_text.get("1.0", tk.END).strip().split("\n")
            self.settings['custom_headers'] = json.loads(self.headers_text.get("1.0", tk.END))
            self.settings['theme'] = self.theme_var.get()
            self.settings['log_level'] = self.log_level_var.get()
            self.settings['use_proxy'] = self.use_proxy_var.get()
            self.settings['proxies'] = self.proxy_list
            self.settings['rotate_proxy'] = self.rotate_proxy_var.get()
            self.settings['animations'] = self.animations_var.get()
            self.settings['include_backend'] = self.include_backend_var.get()
            self.settings['brute_api_paths'] = self.brute_api_var.get()
            self.settings['extract_api_from_js'] = self.extract_api_js_var.get()
            self.settings['save_api_responses'] = self.save_api_responses_var.get()

            # Save to file
            with open("darkmirror_settings.json", "w") as f:
                json.dump(self.settings, f)
            
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")

    # ----------------- Core Functions -----------------
    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_label.config(text=f"Output folder: {folder}")

    def load_settings(self):
        try:
            if os.path.exists("darkmirror_settings.json"):
                with open("darkmirror_settings.json", "r") as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
                    
                    # Update UI with loaded settings
                    self.include_images_var.set(self.settings['include_images'])
                    self.include_css_var.set(self.settings['include_css'])
                    self.include_js_var.set(self.settings['include_js'])
                    self.include_media_var.set(self.settings['include_media'])
                    self.depth_limit_var.set(self.settings['depth_limit'])
                    self.use_proxy_var.set(self.settings['use_proxy'])
                    self.rotate_proxy_var.set(self.settings['rotate_proxy'])
                    self.proxy_list = self.settings.get('proxies', [])
                    self.animations_var.set(self.settings.get('animations', True))
                    self.include_backend_var.set(self.settings.get('include_backend', True))
                    self.brute_api_var.set(self.settings.get('brute_api_paths', True))
                    self.extract_api_js_var.set(self.settings.get('extract_api_from_js', True))
                    self.save_api_responses_var.set(self.settings.get('save_api_responses', True))

                    # Update proxy tree
                    self.update_proxy_tree()
                    
                    # Update settings tab
                    if hasattr(self, 'max_concurrent_var'):
                        self.max_concurrent_var.set(self.settings['max_concurrent'])
                        self.timeout_var.set(self.settings['timeout'])
                        self.retry_var.set(self.settings['retry_count'])
                        self.delay_var.set(self.settings['delay'])
                        self.user_agent_var.set(self.settings['user_agent'])
                        self.theme_var.set(self.settings['theme'])
                        self.log_level_var.set(self.settings['log_level'])
                        
                        if hasattr(self, 'exclude_patterns_text'):
                            self.exclude_patterns_text.delete("1.0", tk.END)
                            self.exclude_patterns_text.insert(tk.END, "\n".join(self.settings['exclude_patterns']))
                        
                        if hasattr(self, 'headers_text'):
                            self.headers_text.delete("1.0", tk.END)
                            self.headers_text.insert(tk.END, json.dumps(self.settings['custom_headers'], indent=2))
        except Exception as e:
            self.log(f"Error loading settings: {str(e)}", "ERROR")

    def log(self, message, level="INFO"):
        if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "PHASE"]:
            level = "INFO"

        log_levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "PHASE": 1}
        current_level = log_levels.get(self.settings.get('log_level', 'INFO'), 1)
        message_level = log_levels.get(level, 1)

        if message_level >= current_level:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_queue.put(f"[{timestamp}] [{level}] {message}")

    def update_log_display(self):
        try:
            while not self.log_queue.empty():
                message = self.log_queue.get_nowait()
                
                # Apply log filter
                log_filter = self.log_filter_var.get()
                if log_filter == "ALL" or log_filter in message:
                    if "[PHASE]" in message:
                        tag = "PHASE"
                    elif "[ERROR]" in message:
                        tag = "ERROR"
                    elif "[WARNING]" in message:
                        tag = "WARNING"
                    elif "[INFO]" in message:
                        tag = "INFO"
                    elif "[DEBUG]" in message:
                        tag = "DEBUG"
                    else:
                        tag = "INFO"
                    
                    self.log_text.insert(tk.END, message + "\n", tag)
                    self.log_text.see(tk.END)
        except:
            pass
        self.root.after(100, self.update_log_display)

    def filter_log(self, event=None):
        # Clear and re-display log with filter
        self.log_text.delete("1.0", tk.END)
        # The log will be re-displayed with the filter applied in update_log_display

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)

    def update_stats(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            speed = self.stats['bytes_downloaded'] / elapsed if elapsed > 0 else 0
            speed_str = self.format_bytes(speed) + "/s"
            mins, secs = divmod(int(elapsed), 60)
            elapsed_str = f"{mins:02d}:{secs:02d}"
        else:
            speed_str = "0 B/s"
            elapsed_str = "00:00"

        backend_hits = self.stats.get('backend_hits', 0)

        self.stat_files.config(text=f"{self.stats['downloaded_files']} / {self.stats['total_files']}")
        self.stat_failed.config(text=str(self.stats['failed_files']))
        self.stat_size.config(text=self.format_bytes(self.stats['bytes_downloaded']))
        self.stat_speed.config(text=speed_str)
        self.stat_backend.config(text=str(backend_hits))

        self.progress_status.config(text=f"{self.stats['downloaded_files']} files")
        self.elapsed_label.config(text=elapsed_str)

    def format_bytes(self, bytes_value):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"

    # ----------------- Download Control -----------------
    def start_copy(self):
        url = self.url_entry.get().strip()
        if not url or not self.output_folder:
            messagebox.showwarning("Error", "Please enter a URL and select an output folder.")
            return
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        
        # Store current tab and switch to download tab
        self.current_tab = self.notebook.index(self.notebook.select())
        self.notebook.select(0)  # Switch to download tab
        
        # Reset state
        self.is_paused = False
        self.is_canceled = False
        self.urls_to_download = set()
        self.downloaded_urls = set()
        self.failed_urls = set()
        self.stats = {
            'total_files': 0,
            'downloaded_files': 0,
            'failed_files': 0,
            'bytes_downloaded': 0
        }
        self.current_file_list = []
        self.start_time = time.time()
        
        self.progress_bar["value"] = 0
        self.progress_percent.config(text="0%")
        self.backend_progress_bar["value"] = 0
        self.backend_progress_percent.config(text="0%")
        self.phase_label.config(text="STARTING...")
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)
        
        # Disable tabs but keep download tab active (index 0)
        for i in range(1, self.notebook.index("end")):
            self.notebook.tab(i, state=tk.DISABLED)
        
        # Create a subfolder for this website based on its domain
        domain = urlparse(url).netloc.replace(":", "_")
        self.site_folder = os.path.join(self.output_folder, domain)
        os.makedirs(self.site_folder, exist_ok=True)
        
        # Add the base URL to the download queue
        self.urls_to_download.add(url)
        self.stats['total_files'] = 1
        
        # Start download in a separate thread
        self.download_thread = threading.Thread(target=self.run_download, args=(url,))
        self.download_thread.daemon = True
        self.download_thread.start()
        
        self.log(f"Starting download of {url}", "INFO")
        self.status_label.config(text="Downloading...")

    def run_download(self, base_url):
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the download process
            loop.run_until_complete(self.download_website(base_url))
        except Exception as e:
            self.log(f"Download error: {str(e)}", "ERROR")
        finally:
            loop.close()
            
            # Update UI when download is complete
            self.root.after(0, self.download_complete)

    async def download_website(self, base_url):
        headers = {
            'User-Agent': self.settings['user_agent'],
            **self.settings['custom_headers']
        }

        connector = aiohttp.TCPConnector(
            limit=self.settings['max_concurrent'],
            force_close=True,
            enable_cleanup_closed=True,
            ssl=self.verify_ssl_var.get() if hasattr(self, 'verify_ssl_var') else True
        )

        timeout = aiohttp.ClientTimeout(total=self.settings['timeout'])

        proxy = None
        if self.settings['use_proxy'] and self.proxy_list:
            if self.settings['rotate_proxy']:
                proxy_info = random.choice(self.proxy_list)
            else:
                proxy_info = self.proxy_list[0]

            if proxy_info['username'] and proxy_info['password']:
                proxy = f"{proxy_info['type'].lower()}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
            else:
                proxy = f"{proxy_info['type'].lower()}://{proxy_info['host']}:{proxy_info['port']}"

            self.log(f"Using proxy: {proxy_info['host']}:{proxy_info['port']}", "INFO")

        async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
            self.session = session

            # Phase 1: Frontend crawl
            self.root.after(0, lambda: self.phase_label.config(text="PHASE 1: FRONTEND"))
            self.log("=== Phase 1: Frontend Crawl ===", "PHASE")
            while self.urls_to_download and not self.is_canceled:
                if self.is_paused:
                    await asyncio.sleep(0.5)
                    continue

                batch_size = min(self.settings['max_concurrent'], len(self.urls_to_download))
                batch = [self.urls_to_download.pop() for _ in range(batch_size)]

                tasks = [self.process_url(url, base_url, session, proxy) for url in batch]
                await asyncio.gather(*tasks, return_exceptions=True)

                progress = (self.stats['downloaded_files'] / max(1, self.stats['total_files'])) * 100
                self.root.after(0, lambda p=progress: self.progress_bar.config(value=p))
                self.root.after(0, lambda p=progress: self.progress_percent.config(text=f"{p:.1f}%"))
                self.root.after(0, self.update_stats)

            self.root.after(0, lambda: self.progress_bar.config(value=100))
            self.root.after(0, lambda: self.progress_percent.config(text="100%"))

            # Phase 2: Backend/API Discovery
            if self.include_backend_var.get() and not self.is_canceled:
                self.root.after(0, lambda: self.phase_label.config(text="PHASE 2: BACKEND"))
                self.root.after(0, lambda: self.status_label.config(text="Discovering backend..."))
                self.root.after(0, lambda: self.backend_progress_bar.config(mode="indeterminate"))
                self.root.after(0, lambda: self.backend_progress_bar.start(15))
                self.log("=== Phase 2: Backend/API Discovery ===", "PHASE")

                self.stats['backend_hits'] = 0

                if self.brute_api_var.get():
                    await self.discover_backend_paths(base_url, session, proxy)

                if self.extract_api_js_var.get():
                    await self.discover_api_from_downloaded_js(base_url, session, proxy)

                self.root.after(0, lambda: self.backend_progress_bar.stop())
                self.root.after(0, lambda: self.backend_progress_bar.config(mode="determinate", value=100))
                self.root.after(0, lambda: self.backend_progress_percent.config(text="100%"))
                self.root.after(0, self.update_stats)
                self.log("=== Backend discovery complete ===", "PHASE")

            self.root.after(0, lambda: self.phase_label.config(text="DONE"))

    async def process_url(self, url, base_url, session, proxy):
        if self.is_canceled:
            return
            
        try:
            # Check if URL should be excluded
            for pattern in self.settings['exclude_patterns']:
                if pattern and re.search(pattern, url):
                    self.log(f"Excluded by pattern: {url}", "DEBUG")
                    return
            
            # Add delay between requests
            if self.settings['delay'] > 0:
                await asyncio.sleep(self.settings['delay'])
            
            # Try to download the URL with retries
            for attempt in range(self.settings['retry_count'] + 1):
                if self.is_canceled:
                    return
                    
                try:
                    # Apply speed limit if set
                    speed_limit = self.speed_limit_var.get() if hasattr(self, 'speed_limit_var') else 0
                    
                    async with session.get(url, proxy=proxy) as response:
                        if response.status == 200:
                            content_type = response.headers.get('Content-Type', '')
                            
                            # Read data with speed limit
                            if speed_limit > 0:
                                # Calculate chunk size based on speed limit
                                chunk_size = max(1024, int(speed_limit * 1024 / 10))  # 10 chunks per second
                                data = b''
                                async for chunk in response.content.iter_chunked(chunk_size):
                                    data += chunk
                                    # Sleep to respect speed limit
                                    await asyncio.sleep(0.1)
                            else:
                                data = await response.read()
                            
                            # Save the file with the session for potential source map downloads
                            await self.save_file(url, data, response.headers.get('Content-Type', ''), session)
                            
                            # Update stats
                            file_size = len(data)
                            self.stats['bytes_downloaded'] += file_size
                            self.stats['downloaded_files'] += 1
                            
                            # Add to file list
                            self.current_file_list.append({
                                'url': url,
                                'path': self.get_local_path(url),
                                'size': file_size,
                                'status': 'Downloaded'
                            })
                            
                            # Extract links if it's an HTML page
                            if 'text/html' in content_type:
                                html = data.decode(errors='ignore')
                                links = self.extract_links(html, base_url, url)

                                for link in links:
                                    if link not in self.downloaded_urls and link not in self.urls_to_download:
                                        self.urls_to_download.add(link)
                                        self.stats['total_files'] += 1

                            # Extract API endpoints from JS files during crawl
                            if self.include_backend_var.get() and self.extract_api_js_var.get():
                                is_js = ('javascript' in content_type or url.endswith('.js'))
                                if is_js:
                                    try:
                                        js_text = data.decode(errors='ignore')
                                        api_urls = self.extract_api_endpoints_from_js(js_text, base_url)
                                        for api_url in api_urls:
                                            if api_url not in self.downloaded_urls and api_url not in self.urls_to_download:
                                                self.urls_to_download.add(api_url)
                                                self.stats['total_files'] += 1
                                                self.log(f"API endpoint found in JS: {api_url}", "DEBUG")
                                    except Exception:
                                        pass
                            
                            # Mark as downloaded
                            self.downloaded_urls.add(url)
                            self.log(f"Downloaded: {url} ({self.format_bytes(file_size)})", "INFO")
                            break
                        else:
                            self.log(f"HTTP Error {response.status}: {url}", "WARNING")
                            if attempt == self.settings['retry_count']:
                                self.failed_urls.add(url)
                                self.stats['failed_files'] += 1
                                
                                # Add to file list
                                self.current_file_list.append({
                                    'url': url,
                                    'path': self.get_local_path(url),
                                    'size': 0,
                                    'status': f'HTTP Error {response.status}'
                                })
                            else:
                                await asyncio.sleep(1)  # Wait before retry
                except Exception as e:
                    self.log(f"Attempt {attempt + 1} failed for {url}: {str(e)}", "WARNING")
                    if attempt == self.settings['retry_count']:
                        self.failed_urls.add(url)
                        self.stats['failed_files'] += 1
                        
                        # Add to file list
                        self.current_file_list.append({
                            'url': url,
                            'path': self.get_local_path(url),
                            'size': 0,
                            'status': f'Error: {str(e)}'
                        })
                    else:
                        await asyncio.sleep(1)  # Wait before retry
        except Exception as e:
            self.log(f"Error processing {url}: {str(e)}", "ERROR")
            self.failed_urls.add(url)
            self.stats['failed_files'] += 1
            
            # Add to file list
            self.current_file_list.append({
                'url': url,
                'path': self.get_local_path(url),
                'size': 0,
                'status': f'Error: {str(e)}'
            })

    def get_local_path(self, url, content_type=None):
        """
        Generate a local file path for the given URL, ensuring proper file extensions.
        For HTML files, always use .html extension.
        For JS files, preserve original path and filename.
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Get content type if not provided
        if content_type is None:
            content_type = self.get_content_type(url)
            
        is_html = 'text/html' in content_type
        is_js = 'application/javascript' in content_type or 'text/javascript' in content_type
        
        # Handle directory paths (URLs ending with /)
        if path.endswith('/') or path == '':
            return 'index.html' if is_html else 'index.html'
        
        # Split path into components
        dirname, filename = os.path.split(path)
        basename, ext = os.path.splitext(filename)
        
        # Handle HTML files - always ensure .html extension
        if is_html:
            ext = '.html'
        # Handle JavaScript files - preserve original extension or add .js if missing
        elif is_js:
            if not ext or ext.lower() != '.js':
                ext = '.js'
        # Handle other file types
        elif not ext or not filename:
            if 'text/css' in content_type:
                ext = '.css'
            elif 'image/jpeg' in content_type:
                ext = '.jpg'
            elif 'image/png' in content_type:
                ext = '.png'
            elif 'image/gif' in content_type:
                ext = '.gif'
            elif 'image/svg+xml' in content_type:
                ext = '.svg'
            elif 'image/webp' in content_type:
                ext = '.webp'
            elif 'video/mp4' in content_type:
                ext = '.mp4'
            elif 'audio/mpeg' in content_type:
                ext = '.mp3'
            elif 'application/pdf' in content_type:
                ext = '.pdf'
            elif 'application/json' in content_type:
                ext = '.json'
            elif 'application/xml' in content_type:
                ext = '.xml'
            elif 'text/plain' in content_type:
                ext = '.txt'
            else:
                ext = '.bin'  # Default extension for unknown types
        
        # Handle empty filenames
        if not basename:
            basename = 'index' if is_html else 'file'
        
        # Reconstruct the filename with proper extension
        filename = f"{basename}{ext}"
        
        # Rebuild the path, ensuring we don't have double slashes
        clean_path = os.path.join(dirname, filename) if dirname else filename
        clean_path = '/'.join(part for part in clean_path.split('/') if part)
        
        return clean_path.lstrip('/')
        
    def beautify_javascript(self, js_code):
        """
        Beautify JavaScript code using jsbeautifier
        """
        try:
            opts = jsbeautifier.default_options()
            opts.indent_size = 2
            opts.space_in_empty_paren = True
            opts.preserve_newlines = True
            opts.max_preserve_newlines = 2
            return jsbeautifier.beautify(js_code, opts)
        except Exception as e:
            self.log(f"Error beautifying JavaScript: {str(e)}", "ERROR")
            return js_code  # Return original if beautification fails

    def get_content_type(self, url):
        # Guess content type from URL extension
        path = urlparse(url).path
        ext = os.path.splitext(path)[1].lower()
        
        content_types = {
            '.html': 'text/html',
            '.htm': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp',
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.pdf': 'application/pdf',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.txt': 'text/plain'
        }
        
        return content_types.get(ext, 'application/octet-stream')

    # ----------------- Extract Links -----------------
    def extract_links(self, html, base_url, current_url):
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        
        # Get current URL depth
        current_path = urlparse(current_url).path
        current_depth = current_path.count('/') if current_path else 0
        
        # Check if we've reached the depth limit
        depth_limit = self.depth_limit_var.get()
        if current_depth >= depth_limit:
            return links
        
        # Define tags and attributes to extract
        tag_attributes = {
            'a': 'href',
            'link': 'href',
            'script': 'src',
            'img': 'src',
            'source': 'src',
            'iframe': 'src',
            'embed': 'src',
            'video': 'src',
            'audio': 'src',
            'track': 'src',
            'object': 'data',
            'form': 'action'
        }
        
        # Extract links from all specified tags
        for tag_name, attr in tag_attributes.items():
            # Skip certain tags based on settings
            if tag_name == 'img' and not self.include_images_var.get():
                continue
            if tag_name == 'link' and not self.include_css_var.get():
                continue
            if tag_name == 'script' and not self.include_js_var.get():
                continue
            if tag_name in ['video', 'audio', 'source', 'track'] and not self.include_media_var.get():
                continue
                
            for tag in soup.find_all(tag_name):
                link = tag.get(attr)
                if link:
                    full_url = urljoin(base_url, link)
                    if self.is_valid_url(full_url, base_url) and full_url not in self.downloaded_urls:
                        links.add(full_url)
        
        # Extract CSS background images
        if self.include_css_var.get():
            for tag in soup.find_all(style=True):
                style = tag.get('style')
                if style:
                    # Extract background-image URLs
                    bg_images = re.findall(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
                    for bg_url in bg_images:
                        full_url = urljoin(base_url, bg_url)
                        if self.is_valid_url(full_url, base_url) and full_url not in self.downloaded_urls:
                            links.add(full_url)
        
        # Parse JavaScript for URLs if enabled
        if hasattr(self, 'parse_javascript_var') and self.parse_javascript_var.get():
            for script in soup.find_all('script'):
                if script.string:
                    # Extract URLs from JavaScript code
                    js_urls = re.findall(r'[\'"]((http|https)://[^\'"]+)[\'"]', script.string)
                    for js_url in js_urls:
                        full_url = js_url[0]
                        if self.is_valid_url(full_url, base_url) and full_url not in self.downloaded_urls:
                            links.add(full_url)
        
        return links

    def is_valid_url(self, url, base_url):
        if not self.is_same_domain(url, base_url):
            return False
        if url.startswith('#'):
            return False
        if url.startswith(('mailto:', 'tel:', 'javascript:', 'data:')):
            return False
        return True

    # ----------------- Backend/API Discovery -----------------
    def extract_api_endpoints_from_js(self, js_code, base_url):
        """Parse JS source for fetch/axios/XHR calls and extract API endpoints."""
        endpoints = set()

        patterns = [
            r'''fetch\s*\(\s*[`'"](\/[^`'"]*?)[`'"]''',
            r'''fetch\s*\(\s*[`'"](https?:\/\/[^`'"]*?)[`'"]''',
            r'''axios\.\w+\s*\(\s*[`'"](\/[^`'"]*?)[`'"]''',
            r'''axios\.\w+\s*\(\s*[`'"](https?:\/\/[^`'"]*?)[`'"]''',
            r'''axios\s*\(\s*\{[^}]*url\s*:\s*[`'"](\/[^`'"]*?)[`'"]''',
            r'''\.open\s*\(\s*[`'"]\w+[`'"]\s*,\s*[`'"](\/[^`'"]*?)[`'"]''',
            r'''\.open\s*\(\s*[`'"]\w+[`'"]\s*,\s*[`'"](https?:\/\/[^`'"]*?)[`'"]''',
            r'''[`'"](\/api\/[^`'"]*?)[`'"]''',
            r'''[`'"](\/graphql[^`'"]*?)[`'"]''',
            r'''[`'"](\/v[0-9]+\/[^`'"]*?)[`'"]''',
            r'''[`'"](\/rest\/[^`'"]*?)[`'"]''',
            r'''[`'"](\/wp-json\/[^`'"]*?)[`'"]''',
            r'''baseURL\s*[:=]\s*[`'"](https?:\/\/[^`'"]+)[`'"]''',
            r'''apiUrl\s*[:=]\s*[`'"](https?:\/\/[^`'"]+)[`'"]''',
            r'''API_URL\s*[:=]\s*[`'"](https?:\/\/[^`'"]+)[`'"]''',
            r'''endpoint\s*[:=]\s*[`'"](\/[^`'"]+)[`'"]''',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            for match in matches:
                endpoint = match.strip()
                if endpoint.startswith('/'):
                    full_url = urljoin(base_url, endpoint)
                    endpoints.add(full_url)
                elif endpoint.startswith('http'):
                    endpoints.add(endpoint)

        return endpoints

    async def discover_backend_paths(self, base_url, session, proxy):
        """Brute-force common backend/API paths and save responses."""
        self.log("Starting backend/API path discovery...", "INFO")
        discovered = 0

        all_paths = list(COMMON_BACKEND_PATHS)
        if hasattr(self, 'custom_api_paths_text'):
            custom = self.custom_api_paths_text.get("1.0", "end-1c").strip()
            if custom:
                all_paths.extend(line.strip() for line in custom.split('\n') if line.strip())

        tasks = []
        for path in all_paths:
            full_url = urljoin(base_url, path)
            if full_url not in self.downloaded_urls and full_url not in self.failed_urls:
                tasks.append(self.probe_backend_path(full_url, session, proxy))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, int):
                discovered += result

        self.log(f"Backend discovery done. {discovered} endpoints found.", "INFO")
        return discovered

    async def probe_backend_path(self, url, session, proxy, is_api_endpoint=False):
        """Probe a single backend path. Returns 1 if found, 0 if not."""
        if self.is_canceled:
            return 0
        try:
            async with session.get(url, proxy=proxy, allow_redirects=False) as response:
                if response.status in (200, 201, 204, 301, 302):
                    content_type = response.headers.get('Content-Type', '')
                    data = await response.read()

                    if len(data) == 0:
                        self.log(f"Backend empty response: {url} [{response.status}]", "DEBUG")
                        return 0

                    api_folder = os.path.join(self.site_folder, '_backend')
                    os.makedirs(api_folder, exist_ok=True)

                    parsed = urlparse(url)
                    safe_path = parsed.path.lstrip('/').replace('/', os.sep)
                    if not safe_path:
                        safe_path = 'index'

                    if 'json' in content_type:
                        if not safe_path.endswith('.json'):
                            safe_path += '.json'
                        try:
                            parsed_json = json.loads(data)
                            data = json.dumps(parsed_json, indent=2, ensure_ascii=False).encode('utf-8')
                        except (json.JSONDecodeError, ValueError):
                            pass
                    elif 'xml' in content_type:
                        if not safe_path.endswith('.xml'):
                            safe_path += '.xml'
                    elif 'html' in content_type:
                        if not safe_path.endswith('.html'):
                            safe_path += '.html'
                    elif 'text/plain' in content_type:
                        if not safe_path.endswith('.txt'):
                            safe_path += '.txt'
                    else:
                        ext = os.path.splitext(safe_path)[1]
                        if not ext:
                            safe_path += '.bin'

                    filepath = os.path.join(api_folder, safe_path)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)

                    with open(filepath, 'wb') as f:
                        f.write(data)

                    self.downloaded_urls.add(url)
                    self.stats['downloaded_files'] += 1
                    self.stats['bytes_downloaded'] += len(data)

                    self.current_file_list.append({
                        'url': url,
                        'path': f'_backend/{safe_path}',
                        'size': len(data),
                        'status': f'Backend [{response.status}]'
                    })

                    self.stats['backend_hits'] = self.stats.get('backend_hits', 0) + 1
                    self.root.after(0, self.update_stats)
                    self.log(f"Backend found: {url} [{response.status}] ({self.format_bytes(len(data))})", "INFO")
                    return 1
                else:
                    self.log(f"Backend miss: {url} [{response.status}]", "DEBUG")
                    return 0
        except asyncio.TimeoutError:
            self.log(f"Backend timeout: {url}", "DEBUG")
            return 0
        except Exception as e:
            self.log(f"Backend probe error {url}: {str(e)}", "DEBUG")
            return 0

    async def discover_api_from_downloaded_js(self, base_url, session, proxy):
        """Scan all downloaded JS files for API endpoints, then probe them."""
        if not self.extract_api_js_var.get():
            return

        self.log("Scanning downloaded JS files for API endpoints...", "INFO")
        api_endpoints = set()

        js_folder = self.site_folder
        for root_dir, dirs, files in os.walk(js_folder):
            for fname in files:
                if fname.lower().endswith('.js'):
                    fpath = os.path.join(root_dir, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            js_code = f.read()
                        endpoints = self.extract_api_endpoints_from_js(js_code, base_url)
                        api_endpoints.update(endpoints)
                    except Exception as e:
                        self.log(f"Error reading JS {fpath}: {str(e)}", "DEBUG")

        if not api_endpoints:
            self.log("No API endpoints found in JS files.", "INFO")
            return

        self.log(f"Found {len(api_endpoints)} API endpoints in JS. Probing...", "INFO")

        tasks = []
        for endpoint in api_endpoints:
            if endpoint not in self.downloaded_urls and endpoint not in self.failed_urls:
                if self.is_same_domain(endpoint, base_url) or self.save_api_responses_var.get():
                    tasks.append(self.probe_backend_path(endpoint, session, proxy, is_api_endpoint=True))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        found = sum(1 for r in results if isinstance(r, int) and r > 0)
        self.log(f"JS API scan done. {found}/{len(api_endpoints)} endpoints responded.", "INFO")

    # ----------------- Domain Check -----------------
    def is_same_domain(self, url, base_url):
        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc
        
        # Remove 'www.' prefix if present
        if base_domain.startswith('www.'):
            base_domain = base_domain[4:]
        if url_domain.startswith('www.'):
            url_domain = url_domain[4:]
            
        return base_domain == url_domain

    # ----------------- Save Files -----------------
    async def save_file(self, url, data, content_type, session=None):
        """
        Save file to disk with proper handling for different file types.
        For JavaScript files, also download source maps and beautify the code.
        """
        # Get the local path using get_local_path
        path = self.get_local_path(url, content_type)
        
        # Clean filename if enabled (only clean the filename part, not the path)
        if hasattr(self, 'clean_filenames_var') and self.clean_filenames_var.get():
            import unicodedata
            import re
            
            # Split path into directory and filename
            dirname, filename = os.path.split(path)
            
            # Clean the filename only, not the path
            if filename:
                # Normalize unicode characters
                filename = unicodedata.normalize('NFKD', filename)
                # Replace special characters with underscores, but preserve dots and hyphens
                filename = re.sub(r'[^\w\s.-]', '_', filename)
                # Recombine path
                path = os.path.join(dirname, filename) if dirname else filename
        
        # Create the full file path
        filepath = os.path.join(self.site_folder, path)
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        is_js = ('application/javascript' in content_type or 
                'text/javascript' in content_type or
                filepath.lower().endswith('.js'))
        
        # For JavaScript files, try to beautify the code
        if is_js and data:
            try:
                # Try to decode as UTF-8, fallback to latin-1 if that fails
                try:
                    js_code = data.decode('utf-8')
                except UnicodeDecodeError:
                    js_code = data.decode('latin-1')
                
                # Beautify the JavaScript
                beautified_js = self.beautify_javascript(js_code)
                
                # Write the beautified JavaScript
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(beautified_js)
                
                # Look for source map reference in the JavaScript
                source_map_url = self.extract_source_map_url(js_code, url)
                if source_map_url and session:
                    await self.download_source_map(source_map_url, filepath, session)
                
                self.log(f"Saved and beautified JavaScript to: {filepath}", "INFO")
                return
                
            except Exception as e:
                self.log(f"Error processing JavaScript {filepath}: {str(e)}", "ERROR")
                # Fall through to save the original file
        
        # For non-JavaScript files or if beautification failed
        with open(filepath, 'wb') as f:
            f.write(data)
        
        self.log(f"Saved file to: {filepath}", "DEBUG")
    
    def extract_source_map_url(self, js_code, base_url):
        """Extract source map URL from JavaScript code"""
        # Look for sourceMappingURL comment
        source_map_marker = '//# sourceMappingURL='
        source_map_idx = js_code.rfind(source_map_marker)
        
        if source_map_idx != -1:
            # Get everything after the marker
            source_map_line = js_code[source_map_idx + len(source_map_marker):]
            # Take everything up to the next newline or space
            source_map_url = source_map_line.split('\n')[0].split()[0].strip()
            
            # If it's a relative URL, make it absolute
            if source_map_url and not source_map_url.startswith(('http://', 'https://')):
                return urljoin(base_url, source_map_url)
            return source_map_url
        return None
    
    async def download_source_map(self, source_map_url, js_filepath, session):
        """Download and save source map file"""
        try:
            # Determine the expected source map filename
            source_map_path = f"{js_filepath}.map"
            
            # Skip if we've already downloaded this source map
            if os.path.exists(source_map_path):
                return
                
            self.log(f"Downloading source map: {source_map_url}", "INFO")
            
            async with session.get(source_map_url, timeout=30) as response:
                if response.status == 200:
                    source_map_data = await response.read()
                    
                    # Save the source map
                    with open(source_map_path, 'wb') as f:
                        f.write(source_map_data)
                    
                    self.log(f"Saved source map to: {source_map_path}", "INFO")
                    
        except Exception as e:
            self.log(f"Error downloading source map {source_map_url}: {str(e)}", "ERROR")

    # ----------------- Download Control -----------------
    def pause_download(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="Resume")
            self.status_label.config(text="Download paused")
            self.log("Download paused", "INFO")
        else:
            self.pause_button.config(text="Pause")
            self.status_label.config(text="Downloading...")
            self.log("Download resumed", "INFO")

    def cancel_download(self):
        if messagebox.askyesno("Cancel Download", "Are you sure you want to cancel the download?"):
            self.is_canceled = True
            self.status_label.config(text="Download canceled")
            self.log("Download canceled", "INFO")
            self.download_complete()

    def download_complete(self):
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        # Determine status
        if self.is_canceled:
            status = "Canceled"
        elif self.stats['failed_files'] > 0:
            status = "Completed with errors"
        else:
            status = "Completed"
        
        # Add to history
        history_entry = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'url': self.url_entry.get(),
            'files': self.stats['downloaded_files'],
            'size': self.stats['bytes_downloaded'],
            'status': status,
            'file_list': self.current_file_list
        }
        
        self.download_history.append(history_entry)
        
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        self.phase_label.config(text="")

        for i in range(self.notebook.index("end")):
            self.notebook.tab(i, state=tk.NORMAL)

        self.notebook.select(self.current_tab)
        self.refresh_history()

        backend_hits = self.stats.get('backend_hits', 0)
        mins, secs = divmod(int(elapsed_time), 60)

        completion_message = (
            f"Download {status.lower()} in {mins}m {secs}s\n"
            f"Frontend files: {self.stats['downloaded_files']}\n"
            f"Backend endpoints: {backend_hits}\n"
            f"Failed: {self.stats['failed_files']}\n"
            f"Total size: {self.format_bytes(self.stats['bytes_downloaded'])}"
        )

        self.log(completion_message, "PHASE")
        messagebox.showinfo("Download Complete", completion_message)
        self.status_label.config(text="Ready")

# ----------------- Run App -----------------
if __name__ == "__main__":
    # Create themed window
    root = Window(themename="darkly")
    app = WebsiteCopier(root)
    root.mainloop()