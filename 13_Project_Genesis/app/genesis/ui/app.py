import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from genesis.core.repository import RepositoryManager


class GenesisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Project Genesis — Certiaura Repository Manager")
        self.root.geometry("720x460")

        self.repo_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Repository not selected")

        self._build_layout()

    def _build_layout(self):
        title = tk.Label(
            self.root,
            text="PROJECT GENESIS",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=(18, 4))

        subtitle = tk.Label(
            self.root,
            text="Certiaura Repository Manager v1.0",
            font=("Segoe UI", 11)
        )
        subtitle.pack(pady=(0, 18))

        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=24)

        tk.Label(frame, text="Repository Path:", anchor="w").pack(fill="x")

        path_row = tk.Frame(frame)
        path_row.pack(fill="x", pady=4)

        entry = tk.Entry(path_row, textvariable=self.repo_path)
        entry.pack(side="left", fill="x", expand=True)

        browse = tk.Button(path_row, text="Browse", command=self.select_repository)
        browse.pack(side="left", padx=(8, 0))

        tk.Label(
            self.root,
            textvariable=self.status_text,
            fg="green",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=14)

        buttons = tk.Frame(self.root)
        buttons.pack(pady=10)

        tk.Button(buttons, text="Validate Repository", width=24, command=self.validate_repository).grid(row=0, column=0, padx=8, pady=6)
        tk.Button(buttons, text="Open Asset Register", width=24, command=self.open_asset_register).grid(row=0, column=1, padx=8, pady=6)
        tk.Button(buttons, text="Import Build Pack", width=24, command=self.import_build_pack_placeholder).grid(row=1, column=0, padx=8, pady=6)
        tk.Button(buttons, text="Commit & Push", width=24, command=self.commit_push_placeholder).grid(row=1, column=1, padx=8, pady=6)

        dashboard = tk.LabelFrame(self.root, text="Repository Dashboard")
        dashboard.pack(fill="both", expand=True, padx=24, pady=16)

        self.dashboard_text = tk.Text(dashboard, height=8)
        self.dashboard_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.dashboard_text.insert("end", "Select the Certiaura repository folder to begin.\\n")
        self.dashboard_text.configure(state="disabled")

    def select_repository(self):
        selected = filedialog.askdirectory(title="Select certiaura-knowledge-engine repository folder")
        if selected:
            self.repo_path.set(selected)
            self.status_text.set("Repository selected")
            self.refresh_dashboard()

    def manager(self):
        path = Path(self.repo_path.get())
        return RepositoryManager(path)

    def validate_repository(self):
        if not self.repo_path.get():
            messagebox.showwarning("No repository", "Please select the repository folder first.")
            return

        manager = self.manager()
        result = manager.validate()

        if result["valid"]:
            messagebox.showinfo("Validation passed", "Repository structure looks valid.")
        else:
            messagebox.showerror("Validation failed", "\\n".join(result["errors"]))

        self.refresh_dashboard()

    def refresh_dashboard(self):
        manager = self.manager()
        summary = manager.summary()

        self.dashboard_text.configure(state="normal")
        self.dashboard_text.delete("1.0", "end")
        self.dashboard_text.insert("end", f"Repository: {summary['repo']}\\n")
        self.dashboard_text.insert("end", f"Markdown assets: {summary['markdown_files']}\\n")
        self.dashboard_text.insert("end", f"JSON assets: {summary['json_files']}\\n")
        self.dashboard_text.insert("end", f"Asset register present: {summary['asset_register_present']}\\n")
        self.dashboard_text.insert("end", f"Change log present: {summary['changelog_present']}\\n")
        self.dashboard_text.insert("end", f"Validation status: {summary['validation_status']}\\n")
        self.dashboard_text.configure(state="disabled")

    def open_asset_register(self):
        manager = self.manager()
        path = manager.asset_register_path()
        if path.exists():
            import os
            os.startfile(path)
        else:
            messagebox.showwarning("Missing", "Master Asset Register not found.")

    def import_build_pack_placeholder(self):
        messagebox.showinfo(
            "Coming next",
            "Build Pack import will be added in Genesis v1.1."
        )

    def commit_push_placeholder(self):
        messagebox.showinfo(
            "Coming next",
            "Commit and push controls will be added in Genesis v1.2."
        )

    def run(self):
        self.root.mainloop()
