from io import BytesIO

import pandas as pd

from utils.logger import setup_logger

logger = setup_logger(__name__)

class DataReader:
    """
    A class to read data from a csv file
    """
    def read_csv(self, file: BytesIO) -> pd.DataFrame:
        """
        read data from a csv file
        """
        df = pd.read_csv(file)
        return self.__get_df_as_str(df)
    def read_excel(self, file: BytesIO, sheet_name=0) -> pd.DataFrame:
        """
        Read data from an Excel file object
        """
        try:
            df = pd.read_excel(file, sheet_name=sheet_name, header=0)
            return self.__get_df_as_str(df)
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise FileNotFoundError("Error reading Excel file")

    @staticmethod
    def __get_df_as_str(df):
        for col in df.columns:
            df[col] = df[col].astype(str)
        return df