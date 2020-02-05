import os
import pandas as pd

def concat_csv(input_dir_path, name_prefix, output_path):
    names = [x for x in os.listdir(input_dir_path)
               if x.startswith(name_prefix) and x.endswith(".csv")]
    if len(names) == 0:
        raise Exception("No files to concatenate")

    df_out = pd.DataFrame()
    for name in names:
        df_partial = pd.read_csv(os.path.join(input_dir_path, name),
                                 sep=",",
                                 header=0)
        df_out = pd.concat([df_out, df_partial])
    # save concatenated file on disk
    df_out.to_csv(output_path, index=False, encoding='utf-8')

    # delete the partial files
    for name in names:
        path = os.path.join(input_dir_path, name)
        os.remove(path)
