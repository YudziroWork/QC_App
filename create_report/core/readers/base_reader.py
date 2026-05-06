class BaseReader:
    def __init__(self,file_path:str):
        self.file_path = file_path


    def read(self)->list:
        raise NotImplementedError