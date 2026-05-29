from tkinter import filedialog, messagebox
from create_report.core import processor
import customtkinter as ctk
import os
import re

class ScenarioGroup(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)
        self.title = title

        self.enabled= ctk.BooleanVar(value=True)

        self.checkbox= ctk.CTkCheckBox(self, text=title, variable=self.enabled, command=self._toggle)
        self.checkbox.grid(row=0,column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        self.etalon_label=ctk.CTkLabel(self, text="Эталон")
        self.etalon_label.grid(row=1, column=0, padx=10, sticky="w")
        self.etalon_entry=ctk.CTkEntry(self, width=200)
        self.etalon_entry.grid(row=2, column=0,padx=(10,5), pady=5)
        self.etalon_btn=ctk.CTkButton(self, text="...",width=30, command=lambda: self._browse(self.etalon_entry))
        self.etalon_btn.grid(row=2,column=1,padx=(0, 10))

        self.report_label=ctk.CTkLabel(self, text='Распознавание')
        self.report_label.grid(row=3, column=0,padx=10,sticky="w")
        self.report_entry=ctk.CTkEntry(self, width=200)
        self.report_entry.grid(row=4, column=0, padx=(10,5),pady=5)
        self.report_btn=ctk.CTkButton(self, text="...",width=30, command=lambda:self._browse(self.report_entry))
        self.report_btn.grid(row=4, column=1, padx=(0,10), pady=(0,10))

    def _browse(self, entry):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)

    def _toggle(self):
        active = self.enabled.get()
        entry_state = "normal" if active else "readonly"
        btn_state = "normal" if active else "disabled"
        text_color = ("black", "white") if active else ("gray50", "gray50")

        self.etalon_entry.configure(state=entry_state)
        self.etalon_btn.configure(state=btn_state)
        self.report_entry.configure(state=entry_state)
        self.report_btn.configure(state=btn_state)
        self.etalon_label.configure(text_color=text_color)
        self.report_label.configure(text_color=text_color)
        self.checkbox.configure(text_color=text_color)

    def is_active(self):
        return self.enabled.get()

    def get_paths(self):
        return self.etalon_entry.get(), self.report_entry.get()


class CreateWindow(ctk.CTkToplevel):

    def _validate_version(self, value: str) -> bool:
        return value.strip().lower() == "тест" or bool(re.fullmatch(r'\d{4}\.\d{2}', value.strip()))

    def run_process(self):
        if self.report_mode.get() == "normal":
            etalon_path = self.etalon_entry.get()
            report_path = self.recognized_entry.get()
            output_path = self.report_entry.get()

            if not etalon_path or not report_path or not output_path:
                messagebox.showwarning("Внимание", "Заполните все пути к файлам")
                return

            try:
                input_format = self.save_format_mode.get()
                processor.run(
                    etalon_path=etalon_path,
                    report_path=report_path,
                    output_path=output_path,
                    report_format=input_format,
                    show_settings=bool(self.setting_check.get())
                )
                messagebox.showinfo("Готово", "Отчёт успешно сформирован!")
            except FileNotFoundError as e:
                messagebox.showerror("Файл не найден", str(e))
            except PermissionError as e:
                messagebox.showerror("Нет доступа к файлу", str(e))
            except NotImplementedError:
                messagebox.showinfo("В разработке", "Этот функционал ещё в разработке")
            except RuntimeError as e:
                messagebox.showerror("Ошибка", str(e))

        else:
            if not self._validate_version(self.version_entry.get()):
                messagebox.showwarning("Внимание", "Версия должна быть в формате DDDD.DD или 'тест'")
                return

            active_groups = [g for g in [self.group_high, self.group_low, self.group_stop] if g.is_active()]
            if not active_groups:
                messagebox.showwarning("Внимание", "Активируйте хотя бы одну группу")
                return

            for g in active_groups:
                etalon, report = g.get_paths()
                if not etalon or not report:
                    messagebox.showwarning("Внимание", "Заполните пути для всех активных групп")
                    return

            if not self.regression_output_entry.get():
                messagebox.showwarning("Внимание", "Укажите файл отчёта")
                return

            groups = [
                {
                    "name": g.title,
                    "etalon_path": g.get_paths()[0],
                    "report_path": g.get_paths()[1]
                }
                for g in active_groups
            ]

            try:
                processor.run_regression(
                    groups=groups,
                    output_path=self.regression_output_entry.get(),
                    country=self.country_var.get(),
                    version=self.version_entry.get().strip()
                )
                messagebox.showinfo("Готово", "Отчёт успешно сформирован!")
            except FileNotFoundError as e:
                messagebox.showerror("Файл не найден", str(e))
            except PermissionError as e:
                messagebox.showerror("Нет доступа к файлу", str(e))
            except RuntimeError as e:
                messagebox.showerror("Ошибка", str(e))



    def switch_mode(self):
        if self.report_mode.get() == "normal":
            self.regression_path_frame.grid_forget()
            self.regression_setting_frame.grid_forget()

            self.normal_path_frame.grid(row=1, column=0, padx=0, pady=0, ipadx=10)
            self.normal_setting_frame.grid(row=2, column=0, padx=0, pady=10, ipady=2.5)
        else:
            self.regression_path_frame.grid(row=1, column=0, padx=0, pady=0, ipadx=10)
            self.regression_setting_frame.grid(row=2, column=0, padx=0, pady=10, ipady=2.5)

            self.normal_path_frame.grid_forget()
            self.normal_setting_frame.grid_forget()

        self.submit_button.grid(row=3, column=0, pady=10)

    def browse_file(self, entry_widget, save=False,file_type=None):
        if save:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
        elif file_type == "pdf":
            file_path = filedialog.askopenfilename(
                filetypes=[("PDF files", "*.pdf")]
            )
        elif file_type == "xlsx":
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
        else:
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel/PDF files", "*.xlsx *.xls *.pdf")]
            )
        if file_path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

    def _load_countries(self)->list:
        try:
            path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"...","countries.txt")
            with open(path, encoding="utf-8") as f:
                countries = [line.strip()for line in f if line.strip()]
            return countries if countries else["-"]
        except FileNotFoundError:
            return["-"]

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.title("Создание отчёта")
        self.geometry("900x700")


        self.report_mode = ctk.StringVar(value="normal")

        self.mod_frame = ctk.CTkFrame(self)
        self.mod_frame.grid(row=0, column=0, padx=150, pady=20, ipadx=10)

        self.radio_button_normal = ctk.CTkRadioButton(
            self.mod_frame, text="Стандартный",
            variable=self.report_mode, value="normal",
            command=self.switch_mode
        )
        self.radio_button_normal.grid(row=0, column=0, padx=20, pady=10)

        self.radio_button_regress = ctk.CTkRadioButton(
            self.mod_frame, text="Регрессионный",
            variable=self.report_mode, value="regression",
            command=self.switch_mode
        )
        self.radio_button_regress.grid(row=0, column=1)

        # ─────────────────────────────────────────
        # Стандартный отчёт
        # ─────────────────────────────────────────

        self.normal_path_frame = ctk.CTkFrame(self)

        ctk.CTkLabel(self.normal_path_frame, text="Файл эталона").grid(row=0, column=0)
        self.etalon_entry = ctk.CTkEntry(self.normal_path_frame)
        self.etalon_entry.grid(row=1, column=0, padx=10, pady=10, ipadx=100)
        ctk.CTkButton(
            self.normal_path_frame, text="Обзор",
            command=lambda: self.browse_file(self.etalon_entry)
        ).grid(row=1, column=1)

        # исправлено: добавлен row=2
        ctk.CTkLabel(self.normal_path_frame, text="Файл отчёта SecurOS").grid(row=2, column=0)
        self.recognized_entry = ctk.CTkEntry(self.normal_path_frame)
        self.recognized_entry.grid(row=3, column=0, padx=10, pady=10, ipadx=100)
        ctk.CTkButton(
            self.normal_path_frame, text="Обзор",
            command=lambda: self.browse_file(
                self.recognized_entry,
                file_type=self.save_format_mode.get()
            )
        ).grid(row=3, column=1)


        ctk.CTkLabel(self.normal_path_frame, text="Куда сохранить отчёт").grid(row=4, column=0)
        self.report_entry = ctk.CTkEntry(self.normal_path_frame)
        self.report_entry.grid(row=5, column=0, padx=10, pady=10, ipadx=100)
        ctk.CTkButton(
            self.normal_path_frame, text="Обзор",
            command=lambda: self.browse_file(self.report_entry, save=True)
        ).grid(row=5, column=1)

        self.normal_path_frame.grid(row=1, column=0, padx=0, pady=0, ipadx=10)

        self.normal_setting_frame = ctk.CTkFrame(self)

        self.setting_check = ctk.CTkCheckBox(self.normal_setting_frame, text="Выводить настройки")
        self.setting_check.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.show_red = ctk.CTkCheckBox(self.normal_setting_frame, text="Показывать не распознанные совпадения")
        self.show_red.grid(row=1, column=0, sticky="w", padx=5)

        if self.report_mode.get() == "normal":
            ctk.CTkLabel(self.mod_frame, text="Формат файла отчёта SecurOS").grid(row=1, column=0, columnspan=2, pady=(10, 0))

            self.save_format_mode = ctk.StringVar(value="xlsx")

            self.radio_button_xlsx = ctk.CTkRadioButton(
                self.mod_frame, text="XLSX",
                variable=self.save_format_mode, value="xlsx",

            )
            self.radio_button_xlsx.grid(row=2, column=0, padx=20, pady=10)

            self.radio_button_pdf = ctk.CTkRadioButton(
                self.mod_frame, text="PDF",
                variable=self.save_format_mode, value="pdf",

            )
            self.radio_button_pdf.grid(row=2, column=1)

        self.normal_setting_frame.grid(row=2, column=0, padx=0, pady=10, ipady=2.5)

        # исправлено: кнопка создаётся один раз с command
        self.submit_button = ctk.CTkButton(self, text="Сформировать отчёт", command=self.run_process)
        self.submit_button.grid(row=3, column=0, pady=10)

        # ─────────────────────────────────────────
        # Регрессионный отчёт
        # ─────────────────────────────────────────

        self.regression_path_frame = ctk.CTkFrame(self)

        self.group_high=ScenarioGroup(self.regression_path_frame,  "Высокая скорость")
        self.group_high.grid(row=0, column=0, padx=10,pady=10)

        self.group_low=ScenarioGroup(self.regression_path_frame, "Низкая скорость")
        self.group_low.grid(row=0,column=1,padx=10,pady=10)

        self.group_stop=ScenarioGroup(self.regression_path_frame,  "Stop & Go")
        self.group_stop.grid(row=0,column=2, padx=10,pady=10)

        ctk.CTkLabel(self.regression_path_frame, text="Файл отчёта:").grid(row=1, column=0,padx=10, sticky="e")
        self.regression_output_entry = ctk.CTkEntry(self.regression_path_frame, width=300)
        self.regression_output_entry.grid(row=1,column=1,pady=10)
        ctk.CTkButton(self.regression_path_frame, text="Обзор", command=lambda:self.browse_file(self.regression_output_entry, save=True)).grid(row=1, column=2,padx=10)

        self.regression_setting_frame = ctk.CTkFrame(self)

        ctk.CTkLabel(self.regression_setting_frame, text="Страна:").grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.country_var=ctk.StringVar()
        self.country_menu = ctk.CTkOptionMenu(self.regression_setting_frame, variable=self.country_var, values=self._load_countries())
        self.country_menu.grid(row=1,column=0,padx=10,pady=(0,10))

        ctk.CTkLabel(self.regression_setting_frame, text="Версия (DDDD.DD или тест):").grid(row=2, column=0,padx=10,sticky="w")
        self.version_entry = ctk.CTkEntry(self.regression_setting_frame, width=150)
        self.version_entry.grid(row=3,column=0,padx=10,pady=(0,10))

        ctk.CTkCheckBox(self.regression_setting_frame, text="Отчёт производительности (WIP)",state="disabled").grid(row=4, column=0, padx=10,pady=5, sticky="w")
        ctk.CTkCheckBox(self.regression_setting_frame, text="Отчёт предыдущего регресса (WIP)", state='disabled').grid(row=4, column=1, padx=10,pady=(0,10), sticky="w")