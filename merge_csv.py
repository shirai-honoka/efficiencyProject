import pandas as pd
import glob
import os
from sqlalchemy import create_engine

# CSVフォルダ
csv_folder = r"C:\Users\shirai.honoka\Desktop\project\static"
# まとめCSV
output_csv = r"C:\Users\shirai.honoka\Desktop\project\static\all_data.csv"

csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))

# CSVをまとめる（Shift-JISとUTF-8の両方を自動対応）
all_data_list = []
for f in csv_files:
    try:
        df = pd.read_csv(f, encoding="cp932")
    except UnicodeDecodeError:
        df = pd.read_csv(f, encoding="utf-8-sig")
    all_data_list.append(df)

all_data = pd.concat(all_data_list, ignore_index=True)

# 保存もcp932（Excelで開ける）
all_data.to_csv(output_csv, index=False, encoding="cp932")


