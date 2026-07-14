import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from genesis.core.repository import RepositoryManager
from genesis.core.build_importer import BuildPackImporter


class GenesisApp:
    VERSION = "1.1.0"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Project Genesis — Certiaura Repository Manager v{self.VERSION}")
        self.root.geometry("760x520")

        self.repo_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Repository not selected")

        self._build_layout()

    def _build_layout(self):
        title = tk.Label(
            self.root,
            text="PROJECT GENESIS",
            font=("Segoe UI", 22, "bold"),
        )
        title.pack(pady=(18, 4))

        subtitle = tk.Label(
            self.root,
            text=f"Certiaura Repository Manager v{self.VERSION}",
            font=("Segoe UI", 11),
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
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=14)

        buttons = tk.Frame(self.root)
        buttons.pack(pady=10)

        tk.Button(
            buttons,
            text="Validate Repository",
            width=24,
            command=self.validate_repository,
        ).grid(row=0, column=0, padx=8, pady=6)

        tk.Button(
            buttons,
            text="Open Asset Register",
            width=24,
            command=self.open_asset_register,
        ).grid(row=0, column=1, padx=8, pady=6)

        tk.Button(
            buttons,
            text="Import Build Pack",
            width=24,
            command=self.import_build_pack,
        ).grid(row=1, column=0, padx=8, pady=6)

        tk.Button(
            buttons,
            text="Commit & Push",
            width=24,
            command=self.commit_push_placeholder,
        ).grid(row=1, column=1, padx=8, pady=6)

        dashboard = tk.LabelFrame(self.root, text="Repository Dashboard")
        dashboard.pack(fill="both", expand=True, padx=24, pady=16)

        self.dashboard_text = tk.Text(dashboard, height=10)
        self.dashboard_text.pack(fill="both", expand=True, padx=8, pady=8)
        self._set_dashboard_text("Select the Certiaura repository folder to begin.\n")

    def _set_dashboard_text(self, text: str):
        self.dashboard_text.configure(state="normal")
        self.dashboard_text.delete("1.0", "end")
        self.dashboard_text.insert("end", text)
        self.dashboard_text.configure(state="disabled")

    def select_repository(self):
        selected = filedialog.askdirectory(
            title="Select certiaura-knowledge-engine repository folder"
        )
        if selected:
            self.repo_path.set(selected)
            self.status_text.set("Repository selected")
            self.refresh_dashboard()

    def manager(self):
        return RepositoryManager(Path(self.repo_path.get()))

    def validate_repository(self):
        if not self.repo_path.get():
            messagebox.showwarning(
                "No repository",
                "Please select the repository folder first.",
            )
            return

        manager = self.manager()
        result = manager.validate()

        if result["valid"]:
            messagebox.showinfo(
                "Validation passed",
                "Repository structure looks valid.",
            )
        else:
            messagebox.showerror(
                "Validation failed",
                "\n".join(result["errors"]),
            )

        self.refresh_dashboard()

    def refresh_dashboard(self):
        if not self.repo_path.get():
            return

        manager = self.manager()
        summary = manager.summary()

        text = (
            f"Repository: {summary['repo']}\n"
            f"Markdown files: {summary['markdown_files']}\n"
            f"JSON files: {summary['json_files']}\n"
            f"Asset register present: {summary['asset_register_present']}\n"
            f"Change log present: {summary['changelog_present']}\n"
            f"Validation status: {summary['validation_status']}\n"
        )
        self._set_dashboard_text(text)

    def open_asset_register(self):
        if not self.repo_path.get():
            messagebox.showwarning(
                "No repository",
                "Please select the repository folder first.",
            )
            return

        path = self.manager().asset_register_path()
        if path.exists():
            import os
            os.startfile(path)
        else:
            messagebox.showwarning(
                "Missing",
                "Master Asset Register not found.",
            )

    def import_build_pack(self):
        if not self.repo_path.get():
            messagebox.showwarning(
                "No repository",
                "Please select the repository folder first.",
            )
            return

        build_pack = filedialog.askdirectory(
            title="Select extracted Certiaura Build Pack folder"
        )
        if not build_pack:
            return

        importer = BuildPackImporter(
            repo_path=Path(self.repo_path.get()),
            build_pack_path=Path(build_pack),
        )

        preview = importer.preview()

        if not preview["valid"]:
            messagebox.showerror(
                "Build Pack rejected",
                "\n".join(preview["errors"]),
            )
            return

        summary = (
            f"Build Pack: {preview['build_pack']}\n\n"
            f"New files: {preview['new_files']}\n"
            f"Files to replace: {preview['replace_files']}\n"
            f"Directories scanned: {preview['directories_scanned']}\n\n"
            "Proceed with import?"
        )

        if not messagebox.askyesno("Confirm Build Pack Import", summary):
            return

        try:
            result = importer.import_pack()
        except Exception as exc:
            messagebox.showerror(
                "Import failed",
                f"Build Pack import failed:\n\n{exc}",
            )
            return

        self.status_text.set("Build Pack imported successfully")
        self.refresh_dashboard()

        messagebox.showinfo(
            "Import complete",
            (
                f"Imported {result['files_copied']} files.\n"
                f"New files: {result['new_files']}\n"
                f"Replaced files: {result['replaced_files']}\n\n"
                "The changes are now in the local repository and ready for review."
            ),
        )

    def commit_push_placeholder(self):
        messagebox.showinfo(
            "Coming next",
            "Commit and push controls will be added in Project Genesis v1.2.",
        )

    def run(self):
        self.root.mainloop()
