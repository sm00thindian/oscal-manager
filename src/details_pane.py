# details_pane.py
import tkinter as tk
from tkinter import ttk
from group_details import GroupDetails
from control_details import ControlDetails
from oscal_pydantic.catalog import ControlGroup, Control

class DetailsPane(ttk.Frame):
    """Manages switching between group and control details with scrolling."""
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager

        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(fill="x", pady=5)
        self.back_button = tk.Button(self.nav_frame, text="Back", command=self.manager.go_back, state=tk.DISABLED)
        self.back_button.pack(side="left", padx=5)
        self.new_control_button = tk.Button(self.nav_frame, text="New Control", command=self.manager.new_control)
        self.new_control_button.pack(side="left", padx=5)
        self.new_group_button = tk.Button(self.nav_frame, text="New Group", command=self.manager.new_group)
        self.new_group_button.pack(side="left", padx=5)
        self.delete_control_button = tk.Button(self.nav_frame, text="Delete Control", command=self.manager.delete_control)
        self.delete_control_button.pack(side="left", padx=5)
        self.delete_group_button = tk.Button(self.nav_frame, text="Delete Group", command=self.manager.delete_group)
        self.delete_group_button.pack(side="left", padx=5)
        self.save_button = tk.Button(self.nav_frame, text="Save Changes", command=self.manager.save_changes)
        self.save_button.pack(side="left", padx=5)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.group_details = GroupDetails(self.scrollable_frame, manager)
        self.control_details = ControlDetails(self.scrollable_frame, manager)
        self.no_selection_label = tk.Label(self.scrollable_frame, text="Select a group or control to edit")
        self.no_selection_label.pack(pady=5)
        self.current_details = None
        self.current_object = None

        self.update_colors()

    def update_colors(self):
        """Update widget colors based on the current theme."""
        theme = self.manager.theme
        self.canvas.configure(bg=theme["bg"])
        self.scrollable_frame.configure(style="TFrame")
        self.no_selection_label.configure(bg=theme["bg"], fg=theme["fg"])
        for button in [self.back_button, self.new_control_button, self.new_group_button, 
                       self.delete_control_button, self.delete_group_button, self.save_button]:
            button.configure(bg=theme["button_bg"], fg=theme["fg"], disabledforeground=theme["disabled_fg"])
        self.group_details.update_colors()
        self.control_details.update_colors()

    def show_group(self, group: ControlGroup):
        self.control_details.pack_forget()
        self.group_details.pack(fill="both", expand=True, padx=5, pady=5)
        self.group_details.load(group)
        self.current_details = self.group_details
        self.current_object = group
        self.no_selection_label.pack_forget()
        self.new_control_button.config(state=tk.NORMAL)
        self.new_group_button.config(state=tk.NORMAL)
        self.delete_control_button.config(state=tk.DISABLED)
        self.delete_group_button.config(state=tk.NORMAL)
        self.update_colors()

    def show_control(self, control: Control):
        self.group_details.pack_forget()
        self.control_details.pack(fill="both", expand=True, padx=5, pady=5)
        self.control_details.load(control)
        self.current_details = self.control_details
        self.current_object = control
        self.no_selection_label.pack_forget()
        self.new_control_button.config(state=tk.DISABLED)
        self.new_group_button.config(state=tk.NORMAL)
        self.delete_control_button.config(state=tk.NORMAL)
        self.delete_group_button.config(state=tk.DISABLED)
        self.update_colors()

    def clear(self):
        self.group_details.pack_forget()
        self.control_details.pack_forget()
        self.no_selection_label.pack()
        self.current_details = None
        self.current_object = None
        self.new_control_button.config(state=tk.DISABLED)
        self.new_group_button.config(state=tk.NORMAL)
        self.delete_control_button.config(state=tk.DISABLED)
        self.delete_group_button.config(state=tk.DISABLED)
        self.update_colors()

    def save_current(self):
        if self.current_details and self.current_object:
            self.current_details.save(self.current_object)
