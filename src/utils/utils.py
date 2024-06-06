"""
A utility module to handle the translation
"""

from typing import List, Tuple
import pandas as pd

from utils.logger import setup_logger

logger = setup_logger(__name__)


def language_codes_to_df_column_names(df: pd.DataFrame, language_codes: List[str], pattern: str) -> List[str]:
    """
    Convert the language codes to the column names in the DataFrame
    Assumes that the column name is in the format: {language_code} {pattern}
    """
    columns = []
    for language_code in language_codes:
        for col in df.columns:
            # Assumes that the column name is in the format: {language_code} pattern
            if col == f'{language_code} {pattern}':
                columns.append(col)
    return columns

def results_to_df(results: List[Tuple[str, List[str]]], columns: List[str]) -> pd.DataFrame:
    """
    Convert the results of LLM to a DataFrame
    """  
    update_data = {'index': []}
    for col in columns:
        update_data[col] = []
    for index, translations in results:
        update_data['index'].append(index)
        if translations:
            for lang_index, translation in enumerate(translations):
                col = columns[lang_index]
                update_data[col].append(translation)
        else:
            for col in columns:
                update_data[col].append(None)

    return pd.DataFrame(update_data).set_index('index')

def convert_to_df(df: pd.DataFrame, results: List[Tuple[int, List[str]]], language_codes: List[str], pattern: str) -> pd.DataFrame:
    """
    Based on the columns of df, it converts the results of LLM to a DataFrame
    """
    columns = language_codes_to_df_column_names(df, language_codes, pattern)
    return results_to_df(results, columns)
