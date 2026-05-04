from tkinter import filedialog

import customtkinter as ctk

class CreateWindow(ctk.CTkToplevel):
    def run_process(self):
        mode=self.report_mode.get()
        if mode=="standart":
            self.etalon_path=self.etalon_entry.get()
            self.recognition_path=self.recognized_entry.get()
            self.report_path=self.report_entry.get()
        self.process(
            etalon_path=self.etalon_path,
            recognized_path=self.recognized_path,
            output_path=self.output_path)

    def switch_mode(self):
        if self.report_mode.get() == "normal":
            self.regression_path_frame.grid_forget()
            self.regression_setting_frame.grid_forget()

            self.normal_path_frame.grid(row=1, column=0, padx=0, pady=0, ipadx=10)
            self.normal_setting_frame.grid(row=2, column=0, padx=0, pady=10, ipady=2.5)

            ctk.CTkButton(self, text="Сформировать отчёт").grid(row=3, column=0)
        else:
            self.regression_path_frame.grid(row=1, column=0, padx=0, pady=0, ipadx=10)
            self.regression_setting_frame.grid(row=2, column=0, padx=0, pady=10, ipady=2.5)

            self.normal_path_frame.grid_forget()
            self.normal_setting_frame.grid_forget()

            ctk.CTkButton(self, text="Сформировать отчёт").grid(row=3, column=0)

    def browse_file(self,entry_widget,save=False):
        if save:
            file_path= filedialog.asksaveasfilename(defaultextension=".xlsx",filetypes=[("Excel files", "*.xlsx")])
        else:
            file_path= filedialog.askopenfilename(filetypes=[("Excel/PDF files", "*.xlsx *.xls *.pdf")])
        if file_path:
            entry_widget.delete(0, ctk.END)
            entry_widget.insert(0, file_path)





    def __init__(self,master, **kwargs):
        super().__init__(master, **kwargs)

        self.title("Создание отчёта")
        self.geometry("600x600")



        self.report_mode=ctk.StringVar(value="standart")

        self.mod_frame =ctk.CTkFrame(self)
        self.mod_frame.grid(row=0, column=0, padx=150, pady=20,ipadx=10)

        self.radio_button_normal = ctk.CTkRadioButton(self.mod_frame,text="Стандартный",variable=self.report_mode,value="normal",command=self.switch_mode)
        self.radio_button_normal.grid(row=0,column=0,padx=20,pady=10)

        self.radio_button_regress = ctk.CTkRadioButton(self.mod_frame,text="Регрессионный",variable=self.report_mode,value="regression",command=self.switch_mode)
        self.radio_button_regress.grid(row=0, column=1)

        #################
        #Стандартный отчёт
        #################

        self.normal_path_frame =ctk.CTkFrame(self)

        #Пути

        ctk.CTkLabel(self.normal_path_frame,text="Файл эталона").grid(row=0,column=0)
        self.etalon_entry=ctk.CTkEntry(self.normal_path_frame)
        self.etalon_entry.grid(row=1,column=0,padx=10,pady=10, ipadx=100)
        ctk.CTkButton(self.normal_path_frame,text="Обзор", command=lambda: self.browse_file(self.etalon_entry)).grid(row=1,column=1)

        ctk.CTkLabel(self.normal_path_frame, text="Файл отчёта SecurOS").grid()
        self.recognized_entry = ctk.CTkEntry(self.normal_path_frame)
        self.recognized_entry.grid(row=3, column=0, padx=10, pady=10, ipadx=100)
        ctk.CTkButton(self.normal_path_frame, text="Обзор", command=lambda: self.browse_file(self.recognized_entry)).grid(row=3, column=1,)

        ctk.CTkLabel(self.normal_path_frame, text="Куда сохранить отчёт").grid()
        self.report_entry = ctk.CTkEntry(self.normal_path_frame)
        self.report_entry.grid(row=5, column=0, padx=10, pady=10, ipadx=100)
        ctk.CTkButton(self.normal_path_frame, text="Обзор", command=lambda: self.browse_file(self.report_entry)).grid(row=5, column=1)

        self.normal_setting_frame = ctk.CTkFrame(self)

        # Настройки
        self.setting_check = ctk.CTkCheckBox(self.normal_setting_frame,text="Выводить настройки")
        self.setting_check.grid(row=0, column=0, sticky="w",padx=5,pady=5)

        self.show_red = ctk.CTkCheckBox(self.normal_setting_frame,text="Показывать не распознанные совпадения")
        self.show_red.grid(row=1, column=0 , sticky="w",padx=5)

        self.show_stat_1= ctk.CTkCheckBox(self.normal_setting_frame,text="Показывать статистику №1")
        self.show_stat_1.grid(row=2, column=0,  sticky="w",padx=5,pady=5)

        self.show_stat_2= ctk.CTkCheckBox(self.normal_setting_frame,text="Показывать статистику №2 ")
        self.show_stat_2.grid(row=3, column=0, sticky="w",padx=5)




        ####
        #Регресс
        ####
        self.regression_path_frame=ctk.CTkFrame(self)
        self.regression_setting_frame=ctk.CTkFrame(self)