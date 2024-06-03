import pandas as pd

from typing import List, Tuple, Dict


def get_languages_from_df_column_names(df: pd.DataFrame) -> List[str]:
    # Assumes that the column name is in the format: {language_code} description
    return [col.replace(' description', '') for col in df.columns if 'description' in col and col != 'description']

def update_df_description(df: pd.DataFrame, results: List[Tuple[str, List[str]]], language_codes: List[str]) -> pd.DataFrame:
    columns = language_codes_to_df_column_names(df, language_codes, 'description')
    df.update(results_to_df(results, columns))
    return df

def update_df_names(df: pd.DataFrame, results: List[Tuple[str, List[str]]], language_codes: List[str]) -> pd.DataFrame:
    columns = language_codes_to_df_column_names(df, language_codes, 'name')
    print(columns)
    df.update(results_to_df(results, columns))
    print(df.head())
    return df

def language_codes_to_df_column_names(df: pd.DataFrame, language_codes: List[str], pattern: str) -> List[str]:
    columns = []
    for language_code in language_codes:
        for col in df.columns:
            # Assumes that the column name is in the format: {language_code} pattern
            if col == f'{language_code} {pattern}':
                columns.append(col)
    return columns

def results_to_df(results: List[Tuple[str, List[str]]], columns: List[str]) -> pd.DataFrame:   
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


def convert_to_df_names(df: pd.DataFrame, results: List[Tuple[int, List[str]]], language_codes: List[str]) -> pd.DataFrame:
    columns = language_codes_to_df_column_names(df, language_codes, 'name')
    return results_to_df(results, columns)

def convert_to_df_description(df: pd.DataFrame, results: List[Tuple[int, List[str]]], language_codes: List[str]) -> pd.DataFrame:
    columns = language_codes_to_df_column_names(df, language_codes, 'description')
    return results_to_df(results, columns)
