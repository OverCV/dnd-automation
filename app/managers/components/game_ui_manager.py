"""
Manejo de interfaz de usuario para juegos (widgets, layout, highlights)
"""

import tkinter as tk
from typing import Dict, Callable
from ui.components.arduino_colors import ArduinoColors
from .game_registry import GameRegistry


class GameUIManager:
    """Maneja toda la interfaz de usuario relacionada con juegos"""
    
    def __init__(self, game_registry: GameRegistry):
        self.registry = game_registry
        self.colors = ArduinoColors()
        self.game_widgets: Dict[str, Dict] = {}
        
    def create_game_entries(self, parent_frame, start_game_callback: Callable, 
                           start_test_callback: Callable, stop_game_callback: Callable,
                           show_status_callback: Callable):
        """Crear entradas para cada juego disponible en layout de 3 por fila"""
        
        # Crear frame contenedor con grid
        games_grid = tk.Frame(parent_frame, bg=self.colors.BLACK)
        games_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar grid para 3 columnas
        for col in range(3):
            games_grid.columnconfigure(col, weight=1)
        
        # Procesar juegos en grupos de 3
        available_games = self.registry.get_available_games()
        game_list = list(available_games.items())
        
        for i, (game_id, game_class) in enumerate(game_list):
            row = i // 3
            col = i % 3
            
            # Crear frame del juego
            game_frame = self._create_game_frame(games_grid, row, col)
            
            # Crear componentes del juego
            temp_game = self.registry.create_temp_game_instance(game_id, None)
            if temp_game:
                info_frame = self._create_info_section(game_frame, game_id, temp_game)
                controls_frame = self._create_controls_section(
                    game_frame, game_id, start_game_callback, 
                    start_test_callback, stop_game_callback, show_status_callback
                )
                
                # Guardar referencias de widgets
                self._store_widget_references(game_id, game_frame, controls_frame)
    
    def _create_game_frame(self, parent, row: int, col: int) -> tk.Frame:
        """Crear frame principal para un juego"""
        game_frame = tk.Frame(parent, bg=self.colors.LIGHT_GRAY, relief=tk.RAISED, bd=2)
        game_frame.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
        parent.rowconfigure(row, weight=1)
        return game_frame
    
    def _create_info_section(self, parent, game_id: str, temp_game) -> tk.Frame:
        """Crear sección de información del juego"""
        info_frame = tk.Frame(parent, bg=self.colors.LIGHT_GRAY)
        info_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Título con icono
        icon = self.registry.get_game_icon(game_id)
        title_label = tk.Label(
            info_frame,
            text=f"{icon} {temp_game.name}",
            bg=self.colors.LIGHT_GRAY,
            fg=self.colors.BLUE_DARK,
            font=("Arial", 14, "bold"),
        )
        title_label.pack(anchor=tk.W)

        # Descripción
        desc_label = tk.Label(
            info_frame,
            text=temp_game.description,
            bg=self.colors.LIGHT_GRAY,
            fg=self.colors.PURPLE,
            font=("Arial", 9),
            wraplength=280,
            justify=tk.LEFT,
        )
        desc_label.pack(anchor=tk.W, pady=(5, 8))

        # Información técnica
        tech_info = self.registry.get_tech_info(game_id)
        tech_label = tk.Label(
            info_frame,
            text=tech_info,
            bg=self.colors.LIGHT_GRAY,
            fg=self.colors.BLUE_MID,
            font=("Arial", 8),
            wraplength=280,
            justify=tk.LEFT,
        )
        tech_label.pack(anchor=tk.W)
        
        return info_frame
    
    def _create_controls_section(self, parent, game_id: str, start_callback: Callable,
                               test_callback: Callable, stop_callback: Callable, 
                               status_callback: Callable) -> tk.Frame:
        """Crear sección de controles del juego"""
        controls_frame = tk.Frame(parent, bg=self.colors.LIGHT_GRAY)
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=12)

        # Botón iniciar
        start_btn = tk.Button(
            controls_frame,
            text="▶️ Iniciar",
            command=lambda: start_callback(game_id),
            bg=self.colors.SUCCESS,
            fg=self.colors.BLUE_DARK,
            relief=tk.FLAT,
            width=10,
            height=2,
            font=("Arial", 9, "bold"),
        )
        start_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        # Botón probar (solo para juegos que lo soporten)
        test_btn = None
        if game_id in self.registry.get_games_with_test_mode():
            test_btn = tk.Button(
                controls_frame,
                text="🧪 Probar",
                command=lambda: test_callback(game_id),
                bg=self.colors.ERROR,
                fg=self.colors.PURPLE,
                relief=tk.FLAT,
                width=10,
                height=2,
                font=("Arial", 9, "bold"),
            )
            test_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        # Botón detener
        stop_btn = tk.Button(
            controls_frame,
            text="⏹️ Detener",
            command=stop_callback,
            bg=self.colors.WARNING,
            fg=self.colors.BLUE_DARK,
            relief=tk.FLAT,
            width=10,
            height=2,
            font=("Arial", 9, "bold"),
        )
        stop_btn.grid(row=1, column=0, 
                     columnspan=(2 if test_btn else 1), 
                     padx=2, pady=2, sticky="ew")

        # Botón de estado
        status_btn_text = "📈 Análisis" if game_id == "piano_digital" else "📊 Estado"
        status_btn = tk.Button(
            controls_frame,
            text=status_btn_text,
            command=lambda: status_callback(game_id),
            bg=self.colors.INFO,
            fg=self.colors.BLUE_DARK,
            relief=tk.FLAT,
            width=10,
            font=("Arial", 8),
        )
        status_btn.grid(row=2, column=0, 
                       columnspan=(2 if test_btn else 1), 
                       padx=2, pady=2, sticky="ew")

        # Configurar expansión de columnas
        controls_frame.columnconfigure(0, weight=1)
        if test_btn:
            controls_frame.columnconfigure(1, weight=1)
        
        return controls_frame
    
    def _store_widget_references(self, game_id: str, game_frame: tk.Frame, 
                                controls_frame: tk.Frame):
        """Almacenar referencias de widgets para acceso posterior"""
        # Buscar widgets específicos
        start_btn = None
        test_btn = None
        stop_btn = None
        status_btn = None
        
        for child in controls_frame.winfo_children():
            if isinstance(child, tk.Button):
                text = child.cget("text")
                if "Iniciar" in text:
                    start_btn = child
                elif "Probar" in text:
                    test_btn = child
                elif "Detener" in text:
                    stop_btn = child
                elif "Estado" in text:
                    status_btn = child
        
        # Guardar referencias
        widgets_dict = {
            "frame": game_frame,
            "start_btn": start_btn,
            "stop_btn": stop_btn,
            "status_btn": status_btn,
        }
        
        if test_btn:
            widgets_dict["test_btn"] = test_btn
            
        self.game_widgets[game_id] = widgets_dict
    
    def highlight_active_game(self, active_game_id: str):
        """Resaltar juego activo visualmente"""
        for game_id, widgets in self.game_widgets.items():
            if game_id == active_game_id:
                widgets["frame"].config(bg=self.colors.BLUE_LIGHT, bd=3)
                widgets["start_btn"].config(text="🎮 Ejecutándose", state=tk.DISABLED)
                if "test_btn" in widgets:
                    widgets["test_btn"].config(state=tk.DISABLED)
            else:
                widgets["frame"].config(bg=self.colors.LIGHT_GRAY, bd=2)
                widgets["start_btn"].config(text="▶️ Iniciar", state=tk.NORMAL)
                if "test_btn" in widgets:
                    widgets["test_btn"].config(state=tk.NORMAL)

    def highlight_test_mode(self, active_game_id: str):
        """Resaltar juego en modo prueba visualmente"""
        for game_id, widgets in self.game_widgets.items():
            if game_id == active_game_id:
                widgets["frame"].config(bg=self.colors.PURPLE, bd=3)
                widgets["start_btn"].config(state=tk.DISABLED)
                if "test_btn" in widgets:
                    widgets["test_btn"].config(text="🧪 Probando...", state=tk.DISABLED)
            else:
                widgets["frame"].config(bg=self.colors.LIGHT_GRAY, bd=2)
                widgets["start_btn"].config(text="▶️ Iniciar", state=tk.NORMAL)
                if "test_btn" in widgets:
                    widgets["test_btn"].config(text="🧪 Probar", state=tk.NORMAL)

    def restore_game_ui(self):
        """Restaurar UI de juegos al estado normal"""
        for game_id, widgets in self.game_widgets.items():
            widgets["frame"].config(bg=self.colors.LIGHT_GRAY, bd=2)
            widgets["start_btn"].config(text="▶️ Iniciar", state=tk.NORMAL)
            if "test_btn" in widgets:
                widgets["test_btn"].config(text="🧪 Probar", state=tk.NORMAL)
    
    def get_game_widgets(self) -> Dict[str, Dict]:
        """Obtener diccionario de widgets de juegos"""
        return self.game_widgets 