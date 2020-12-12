import os

import pandas as pd


class MainLogic:
    def __init__(self):
        self.df_gaps = None
        self.filter_df_gaps = None
        self.avi_file_name = None
        self.csv_file_name = None
        self.folder = None

        self.RAILS = ["обе нити", "левая нить", "правая нить"]
        self.current_rail = "обе нити"
        self.gap_limit = 0

    def open_avi(self, file_name):
        self.avi_file_name = file_name
        self.generate_data()

    def open_csv(self, file_name):
        if not os.path.exists(file_name):
            return
        self.csv_file_name = file_name
        self.folder = os.path.dirname(self.csv_file_name)
        self.df_gaps = pd.read_csv(self.csv_file_name, sep=";",
                                   names=["rail", "kilometer", "meter", "gap", "file_name", "x1", "x2", "y1", "y2"],
                                   dtype={"rail": str, "kilometer": int, "meter": int, "gap": int, "file_name": str, "x1": int, "x2": int, "y1": int, "y2": int})
        return True

    def filter(self):
        if self.current_rail == "обе нити":
            self.filter_df_gaps = self.df_gaps
        elif self.current_rail == "левая нить":
            self.filter_df_gaps = self.df_gaps[self.df_gaps["rail"] == "Л"]
        elif self.current_rail == "правая нить":
            self.filter_df_gaps = self.df_gaps[self.df_gaps["rail"] == "П"]
        self.filter_df_gaps = self.filter_df_gaps[self.filter_df_gaps["gap"] >= self.gap_limit]
        print(self.filter_df_gaps)

    def generate_data(self):
        pass
