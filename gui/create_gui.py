from tkinter import filedialog, messagebox
from create_report.core import processor
import customtkinter as ctk


class CreateWindow(ctk.CTkToplevel):

    def run_process(self):
        etalon_path = self.etalon_entry.get()
        report_path = self.recognized_entry.get()
        output_path = self.report_entry.get()

        if not etalon_path or not report_path or not output_path:
            messagebox.showwarning("Внимание", "Заполните все пути к файлам")
            return

        try:
            processor.run(
                etalon_path=etalon_path,
                report_path=report_path,
                output_path=output_path,
                report_format="xlsx"
            )
            messagebox.showinfo("Готово", "Отчёт успешно сформирован!")
        except FileNotFoundError as e:
            messagebox.showerror("Файл не найден", str(e))
        except PermissionError as e:
            messagebox.showerror("Нет доступа к файлу", str(e))
        except NotImplementedError as e:
            messagebox.showinfo("В разработке", str(e))
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

    def browse_file(self, entry_widget, save=False):
        if save:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
        else:
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel/PDF files", "*.xlsx *.xls *.pdf")]
            )
        if file_path:
            entry_widget.delete(0, ctk.END)
            entry_widget.insert(0, file_path)

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.title("Создание отчёта")
        self.geometry("600x600")

        # исправлено: начальное значение совпадает со значением радиокнопки
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
            command=lambda: self.browse_file(self.recognized_entry)
        ).grid(row=3, column=1)

        # исправлено: добавлен row=4
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

        self.show_stat_1 = ctk.CTkCheckBox(self.normal_setting_frame, text="Показывать статистику №1")
        self.show_stat_1.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.show_stat_2 = ctk.CTkCheckBox(self.normal_setting_frame, text="Показывать статистику №2")
        self.show_stat_2.grid(row=3, column=0, sticky="w", padx=5)

        self.normal_setting_frame.grid(row=2, column=0, padx=0, pady=10, ipady=2.5)

        # исправлено: кнопка создаётся один раз с command
        self.submit_button = ctk.CTkButton(self, text="Сформировать отчёт", command=self.run_process)
        self.submit_button.grid(row=3, column=0, pady=10)

        # ─────────────────────────────────────────
        # Регрессионный отчёт
        # ─────────────────────────────────────────

        self.regression_path_frame = ctk.CTkFrame(self)
        self.regression_setting_frame = ctk.CTkFrame(self)