import tkinter as tk
from tkinter import ttk
from window import MainWindow


def main():
    """Función principal para iniciar la aplicación"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
