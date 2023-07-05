
import logging
import os
import subprocess
import yaml
import pandas as pd
import datetime
import gc
import re


def read_config_file(filepath):
    # Reading the YAML configuration file and returning contents it parsed
    with open(filepath, 'r') as stream:
        try:
            config_data = yaml.safe_load(stream)
            return config_data
        except yaml.YAMLError as exc:
            logging.error(f"Error occurred while parsing the YAML file: {exc}")


def replace_consecutive_chars(string, char):
    # Replacing successive instances of a character with a single instance in the string
    pattern = char + '{2,}'
    modified_string = re.sub(pattern, char, string)
    return modified_string


def validate_column_headers(df, table_config):
    '''
    Standardizing and validating column headers
    '''
    # Standardizing column headers
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace('[^\w]', '_', regex=True)
    df.columns = [column.strip('_') for column in df.columns]
    df.columns = [replace_consecutive_chars(column, '_') for column in df.columns]

    # Getting expected column names from the table configuration
    expected_columns = table_config['columns']

    # Sorting and converting expected column names to lowercase for comparison
    expected_columns = sorted([column.lower() for column in expected_columns])

    # Converting DataFrame column names to lowercase
    df.columns = [column.lower() for column in df.columns]

    # Reindexing DataFrame columns in sorted order
    df = df.reindex(sorted(df.columns), axis=1)

    # Validating column names and lengths
    if len(df.columns) == len(expected_columns) and list(df.columns) == expected_columns:
        print("Column name and column length validation passed")
        return 1
    else:
        print("Column name and column length validation failed")

        # Finding mismatched columns between the DataFrame and YAML configuration
        mismatched_columns = list(set(df.columns).difference(expected_columns))
        print("Columns present in the file but not in the YAML configuration:", mismatched_columns)

        missing_columns = list(set(expected_columns).difference(df.columns))
        print("Columns present in the YAML configuration but not in the file:", missing_columns)

        logging.info(f"DataFrame columns: {df.columns}")
        logging.info(f"Expected columns: {expected_columns}")
        return 0
