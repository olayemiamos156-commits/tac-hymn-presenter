import json
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

APP_NAME = "TAC Hymn Presenter"
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(__import__("sys"), "frozen", False):
    APP_DIR = os.path.dirname(__import__("sys").executable)
DATA_FILE = os.path.join(APP_DIR, "hymns.json")

DEFAULT_HYMNS = [
    {
        "number": 1,
        "title": "Sample hymn (replace with your hymn)",
        "lyrics": "Verse 1\nAdd your hymn lyrics here.\n\nVerse 2\nAdd the next verse here."
    }
]

class TACPresenter:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1000x680")
        self.root.minsize(850, 560)
        self.hymns = self.load_hymns()
        self.current_hymn = None
        self.current_verse = 0
        self.verses = []
        self.projector = None
        self.projector_text = None
        self.projector_title = None
        self.projector_canvas = None
        self.projector_fullscreen = False
        self.font_size = tk.IntVar(value=34)
        self.bg_color = tk.StringVar(value="Black")
        self.fg_color = tk.StringVar(value="White")
        self.build_ui()
        self.refresh_list()

    def load_hymns(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return sorted(data, key=lambda h: int(h.get("number", 0)))
            except Exception:
                messagebox.showwarning(APP_NAME, "The hymn data file could not be read. Starting with an empty collection.")
        return DEFAULT_HYMNS.copy()

    def save_hymns(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(sorted(self.hymns, key=lambda h: int(h.get("number", 0))), f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not save hymn collection:\n{e}")

    def build_ui(self):
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="TAC HYMN PRESENTER", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Button(top, text="Open Projector", command=self.open_projector).pack(side="right", padx=(6, 0))
        ttk.Button(top, text="Import Hymns (JSON/CSV/TXT)", command=self.import_hymns).pack(side="right")

        body = ttk.Panedwindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        left = ttk.Frame(body, padding=8)
        right = ttk.Frame(body, padding=8)
        body.add(left, weight=1)
        body.add(right, weight=3)

        ttk.Label(left, text="Hymn Library", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.search_var = tk.StringVar()
        search = ttk.Entry(left, textvariable=self.search_var)
        search.pack(fill="x", pady=(6, 8))
        search.bind("<KeyRelease>", lambda e: self.refresh_list())
        self.hymn_list = tk.Listbox(left, font=("Segoe UI", 10), activestyle="dotbox")
        self.hymn_list.pack(fill="both", expand=True)
        self.hymn_list.bind("<<ListboxSelect>>", self.select_hymn)

        left_buttons = ttk.Frame(left)
        left_buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(left_buttons, text="Add Hymn", command=self.add_hymn).pack(side="left", fill="x", expand=True)
        ttk.Button(left_buttons, text="Edit", command=self.edit_hymn).pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(left_buttons, text="Delete", command=self.delete_hymn).pack(side="left", fill="x", expand=True)

        ttk.Label(right, text="Selected Hymn", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.title_label = ttk.Label(right, text="Choose a hymn from the library", font=("Segoe UI", 16, "bold"))
        self.title_label.pack(anchor="w", pady=(8, 4))
        self.preview = tk.Text(right, height=15, wrap="word", font=("Segoe UI", 12), state="disabled")
        self.preview.pack(fill="both", expand=True)
        nav = ttk.Frame(right)
        nav.pack(fill="x", pady=10)
        ttk.Button(nav, text="◀ Previous Verse", command=self.previous_verse).pack(side="left")
        self.verse_label = ttk.Label(nav, text="Verse — / —")
        self.verse_label.pack(side="left", padx=12)
        ttk.Button(nav, text="Next Verse ▶", command=self.next_verse).pack(side="left")
        ttk.Button(nav, text="Show Current Verse", command=self.update_projector).pack(side="right")

        settings = ttk.LabelFrame(right, text="Projector display settings", padding=8)
        settings.pack(fill="x")
        ttk.Label(settings, text="Text size").pack(side="left")
        ttk.Button(settings, text="−", width=3, command=lambda: self.change_font(-4)).pack(side="left", padx=(6, 2))
        ttk.Label(settings, textvariable=self.font_size, width=3).pack(side="left")
        ttk.Button(settings, text="+", width=3, command=lambda: self.change_font(4)).pack(side="left", padx=2)
        ttk.Label(settings, text="Background").pack(side="left", padx=(18, 4))
        bg = ttk.Combobox(settings, textvariable=self.bg_color, values=["Black", "Navy", "Dark Green", "White"], width=12, state="readonly")
        bg.pack(side="left")
        bg.bind("<<ComboboxSelected>>", lambda e: self.update_projector())
        ttk.Label(settings, text="Text").pack(side="left", padx=(12, 4))
        fg = ttk.Combobox(settings, textvariable=self.fg_color, values=["White", "Yellow", "Cyan", "Black"], width=10, state="readonly")
        fg.pack(side="left")
        fg.bind("<<ComboboxSelected>>", lambda e: self.update_projector())

        self.root.bind("<Right>", lambda e: self.next_verse())
        self.root.bind("<Left>", lambda e: self.previous_verse())
        self.root.bind("<F5>", lambda e: self.open_projector())

    def refresh_list(self):
        query = self.search_var.get().strip().lower()
        self.hymn_list.delete(0, tk.END)
        self.visible_hymns = []
        for hymn in sorted(self.hymns, key=lambda h: int(h.get("number", 0))):
            searchable = f"{hymn.get('number','')} {hymn.get('title','')} {hymn.get('lyrics','')}".lower()
            if query in searchable:
                self.visible_hymns.append(hymn)
                self.hymn_list.insert(tk.END, f"{hymn.get('number', ''):>4}  {hymn.get('title', 'Untitled')}")
        if not self.visible_hymns:
            self.hymn_list.insert(tk.END, "No matching hymns")

    def select_hymn(self, event=None):
        sel = self.hymn_list.curselection()
        if not sel or sel[0] >= len(self.visible_hymns):
            return
        self.current_hymn = self.visible_hymns[sel[0]]
        self.verses = self.split_verses(self.current_hymn.get("lyrics", ""))
        self.current_verse = 0
        self.title_label.config(text=f"{self.current_hymn.get('number', '')}. {self.current_hymn.get('title', '')}")
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert(tk.END, self.current_hymn.get("lyrics", ""))
        self.preview.config(state="disabled")
        self.update_verse_label()
        self.update_projector()

    def split_verses(self, lyrics):
        # Separate verses by blank lines. Labels such as "Verse 1" are retained.
        chunks = [part.strip() for part in re.split(r"\n\s*\n", lyrics.strip()) if part.strip()]
        return chunks or ["Add hymn lyrics using Add Hymn or Edit."]

    def update_verse_label(self):
        total = len(self.verses) if self.verses else 0
        self.verse_label.config(text=f"Verse/section {self.current_verse + 1 if total else 0} / {total}")

    def current_text(self):
        if not self.current_hymn:
            return "Select a hymn from the library"
        if not self.verses:
            return self.current_hymn.get("lyrics", "")
        return self.verses[self.current_verse]

    def next_verse(self):
        if self.verses and self.current_verse < len(self.verses) - 1:
            self.current_verse += 1
            self.update_verse_label()
            self.update_projector()

    def previous_verse(self):
        if self.verses and self.current_verse > 0:
            self.current_verse -= 1
            self.update_verse_label()
            self.update_projector()

    def change_font(self, delta):
        self.font_size.set(max(18, min(72, self.font_size.get() + delta)))
        self.update_projector()

    def open_projector(self):
        if self.projector and self.projector.winfo_exists():
            self.projector.deiconify()
            self.projector.lift()
            self.update_projector()
            return
        self.projector = tk.Toplevel(self.root)
        self.projector.title("TAC Hymn Presenter — Projector")
        self.projector.geometry("1200x700+80+40")
        self.projector.configure(bg=self.bg_value())
        self.projector_canvas = tk.Frame(self.projector, bg=self.bg_value())
        self.projector_canvas.pack(fill="both", expand=True)
        self.projector_title = tk.Label(self.projector_canvas, text="", bg=self.bg_value(), fg=self.fg_value(),
                                        font=("Segoe UI", 18, "bold"), wraplength=1100)
        self.projector_title.pack(fill="x", padx=30, pady=(25, 10))
        self.projector_text = tk.Label(self.projector_canvas, text="", bg=self.bg_value(), fg=self.fg_value(),
                                       font=("Segoe UI", self.font_size.get(), "bold"), justify="center",
                                       anchor="center", wraplength=1100)
        self.projector_text.pack(fill="both", expand=True, padx=40, pady=30)
        controls = tk.Frame(self.projector, bg=self.bg_value())
        controls.pack(fill="x")
        tk.Button(controls, text="◀ Previous", command=self.previous_verse).pack(side="left", padx=8, pady=6)
        tk.Button(controls, text="Next ▶", command=self.next_verse).pack(side="left", padx=8, pady=6)
        tk.Button(controls, text="Full Screen (F11)", command=self.toggle_fullscreen).pack(side="right", padx=8, pady=6)
        tk.Button(controls, text="Exit Full Screen (Esc)", command=self.exit_fullscreen).pack(side="right", padx=8, pady=6)
        self.projector.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.projector.bind("<Escape>", lambda e: self.exit_fullscreen())
        self.projector.bind("<Right>", lambda e: self.next_verse())
        self.projector.bind("<Left>", lambda e: self.previous_verse())
        self.projector.protocol("WM_DELETE_WINDOW", self.close_projector)
        self.update_projector()

    def bg_value(self):
        return {"Black": "#000000", "Navy": "#07152e", "Dark Green": "#063b2b", "White": "#ffffff"}.get(self.bg_color.get(), "#000000")

    def fg_value(self):
        return {"White": "#ffffff", "Yellow": "#fff200", "Cyan": "#00ffff", "Black": "#000000"}.get(self.fg_color.get(), "#ffffff")

    def update_projector(self):
        if not self.projector or not self.projector.winfo_exists():
            return
        bg, fg = self.bg_value(), self.fg_value()
        self.projector.configure(bg=bg)
        for widget in (self.projector_canvas, self.projector_title, self.projector_text):
            if widget and widget.winfo_exists():
                widget.configure(bg=bg, fg=fg)
        if self.projector_title and self.projector_title.winfo_exists():
            title = f"{self.current_hymn.get('number', '')}. {self.current_hymn.get('title', '')}" if self.current_hymn else APP_NAME
            self.projector_title.config(text=title)
        if self.projector_text and self.projector_text.winfo_exists():
            self.projector_text.config(text=self.current_text(), font=("Segoe UI", self.font_size.get(), "bold"))
        if hasattr(self, "projector_canvas") and self.projector_canvas:
            for child in self.projector_canvas.winfo_children():
                try:
                    child.configure(bg=bg, fg=fg)
                except Exception:
                    pass

    def toggle_fullscreen(self):
        if self.projector and self.projector.winfo_exists():
            self.projector_fullscreen = not self.projector_fullscreen
            self.projector.attributes("-fullscreen", self.projector_fullscreen)

    def exit_fullscreen(self):
        if self.projector and self.projector.winfo_exists():
            self.projector_fullscreen = False
            self.projector.attributes("-fullscreen", False)

    def close_projector(self):
        if self.projector and self.projector.winfo_exists():
            self.projector.destroy()
        self.projector = None
        self.projector_text = None
        self.projector_title = None
        self.projector_canvas = None
        self.projector_fullscreen = False

    def add_hymn(self):
        self.hymn_editor(None)

    def edit_hymn(self):
        if not self.current_hymn:
            messagebox.showinfo(APP_NAME, "Select a hymn to edit first.")
            return
        self.hymn_editor(self.current_hymn)

    def hymn_editor(self, hymn):
        win = tk.Toplevel(self.root)
        win.title("Add Hymn" if hymn is None else "Edit Hymn")
        win.geometry("650x540")
        win.transient(self.root)
        form = ttk.Frame(win, padding=12)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text="Hymn number").grid(row=0, column=0, sticky="w", pady=5)
        number_var = tk.StringVar(value=str(hymn.get("number", "") if hymn else (max([int(h.get("number", 0)) for h in self.hymns] + [0]) + 1)))
        ttk.Entry(form, textvariable=number_var, width=15).grid(row=0, column=1, sticky="w", pady=5)
        ttk.Label(form, text="Hymn title / first line").grid(row=1, column=0, sticky="w", pady=5)
        title_var = tk.StringVar(value=hymn.get("title", "") if hymn else "")
        ttk.Entry(form, textvariable=title_var).grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Label(form, text="Lyrics (leave a blank line between verses/sections)").grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 4))
        lyrics_box = tk.Text(form, wrap="word", font=("Segoe UI", 11))
        lyrics_box.grid(row=3, column=0, columnspan=2, sticky="nsew")
        if hymn:
            lyrics_box.insert("1.0", hymn.get("lyrics", ""))
        form.columnconfigure(1, weight=1)
        form.rowconfigure(3, weight=1)

        def save():
            try:
                num = int(number_var.get().strip())
                title = title_var.get().strip()
                lyrics = lyrics_box.get("1.0", "end-1c").strip()
                if not title or not lyrics:
                    messagebox.showwarning(APP_NAME, "Please enter a title and lyrics.", parent=win)
                    return
                existing = next((h for h in self.hymns if int(h.get("number", -1)) == num and h is not hymn), None)
                if existing:
                    messagebox.showwarning(APP_NAME, f"Hymn number {num} already exists.", parent=win)
                    return
                new = {"number": num, "title": title, "lyrics": lyrics}
                if hymn is None:
                    self.hymns.append(new)
                else:
                    hymn.update(new)
                self.save_hymns()
                self.refresh_list()
                self.current_hymn = new if hymn is None else hymn
                self.verses = self.split_verses(self.current_hymn["lyrics"])
                self.current_verse = 0
                self.title_label.config(text=f"{num}. {title}")
                self.preview.config(state="normal")
                self.preview.delete("1.0", tk.END)
                self.preview.insert(tk.END, lyrics)
                self.preview.config(state="disabled")
                self.update_verse_label()
                self.update_projector()
                win.destroy()
            except ValueError:
                messagebox.showwarning(APP_NAME, "Hymn number must be a whole number.", parent=win)
        ttk.Button(form, text="Save Hymn", command=save).grid(row=4, column=1, sticky="e", pady=(10, 0))

    def delete_hymn(self):
        if not self.current_hymn:
            messagebox.showinfo(APP_NAME, "Select a hymn to delete first.")
            return
        if messagebox.askyesno(APP_NAME, f"Delete hymn {self.current_hymn.get('number')} — {self.current_hymn.get('title')}?"):
            self.hymns = [h for h in self.hymns if h is not self.current_hymn]
            self.current_hymn = None
            self.verses = []
            self.save_hymns()
            self.refresh_list()
            self.title_label.config(text="Choose a hymn from the library")
            self.preview.config(state="normal")
            self.preview.delete("1.0", tk.END)
            self.preview.config(state="disabled")
            self.update_verse_label()
            self.update_projector()

    def import_hymns(self):
        path = filedialog.askopenfilename(
            title="Import hymn collection",
            filetypes=[("Hymn data", "*.json *.csv *.txt"), ("JSON", "*.json"), ("CSV", "*.csv"), ("Text", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            imported = []
            ext = os.path.splitext(path)[1].lower()
            if ext == ".json":
                with open(path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data = data.get("hymns", [])
                for h in data:
                    imported.append({"number": int(h["number"]), "title": str(h["title"]), "lyrics": str(h["lyrics"])})
            elif ext == ".csv":
                import csv
                with open(path, "r", encoding="utf-8-sig", newline="") as f:
                    for row in csv.DictReader(f):
                        imported.append({"number": int(row["number"]), "title": row["title"], "lyrics": row["lyrics"]})
            else:
                with open(path, "r", encoding="utf-8-sig") as f:
                    raw = f.read()
                blocks = [b.strip() for b in re.split(r"\n\s*---+\s*\n", raw) if b.strip()]
                for block in blocks:
                    lines = block.splitlines()
                    match = re.match(r"\s*(\d+)\s*[.|:-]\s*(.+)", lines[0])
                    if not match:
                        continue
                    imported.append({"number": int(match.group(1)), "title": match.group(2).strip(), "lyrics": "\n".join(lines[1:]).strip()})
            if not imported:
                raise ValueError("No valid hymns found. See README for the import format.")
            known = {int(h.get("number", 0)): h for h in self.hymns}
            for h in imported:
                known[h["number"]] = h
            self.hymns = sorted(known.values(), key=lambda h: int(h.get("number", 0)))
            self.save_hymns()
            self.refresh_list()
            messagebox.showinfo(APP_NAME, f"Imported {len(imported)} hymn(s).")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not import hymns:\n{e}\n\nSee README.txt for supported formats.")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.1)
    except Exception:
        pass
    app = TACPresenter(root)
    root.mainloop()
