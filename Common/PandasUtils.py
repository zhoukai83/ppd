import pandas as pd

from pandas import DataFrame


def save_to_csv(data_file_path, df, item, encoding="utf-8"):
    frame = DataFrame(item)

    if df is None:
        frame.to_csv(data_file_path, encoding=encoding, index=False)
        df = frame
    else:
        df = pd.concat([df, frame], ignore_index=True, sort=False)
        df.to_csv(data_file_path, encoding=encoding, index=False)

    return df