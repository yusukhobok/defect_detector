import os

import pandas as pd


class MainLogic:
    def __init__(self):
        self.df_gaps = None
        self.avi_file_name = None
        self.csv_file_name = None
        self.folder = None

    def open_avi(self, file_name):
        self.avi_file_name = file_name
        self.generate_data()

    def open_csv(self, file_name):
        if not os.path.exists(file_name):
            return
        self.csv_file_name = file_name
        self.folder = os.path.dirname(self.csv_file_name)
        self.df_gaps = pd.read_csv(self.csv_file_name, sep=";",
                                   names=["kilometer", "meter", "gap", "file_name", "x1", "x2", "y1", "y2"])
        return True

    def generate_data(self):
        pass
