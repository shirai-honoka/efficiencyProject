import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from config.kintone_api import get_kintone_records
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text



# DB接続
user = 'efficiencyProjectStg'
password= 'NaWGKGrYN2dn'
host = '13.208.147.74'
port = '5432'
database = 'work_project'
engine = create_engine(
    f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
)

#キントーンAPI
app_id = 507      # data用アプリID            
domain = 'ncdsol.cybozu.com'      # 例：xxx.cybozu.com
api_token_data ='tJP8uyTTMnnKnfL2NrNJT8b4C4eAiulgFgeXoVHl'        

# dataのデータ取得
def get_kintone_df(app_id, api_token_data, domain):
    # ---- データ取得 ----
    records = get_kintone_records(app_id, api_token_data, domain, query='')

          
    # ---- 要員明細の展開 ----
    staff_list = []
    for _, rec in records.iterrows():  # ← DataFrame対応
        order_no = rec.get('ZEXIS契約No', {}).get('value') if isinstance(rec.get('ZEXIS契約No'), dict) else rec.get('ZEXIS契約No')

        details = rec.get('要員明細', [])
        if isinstance(details, list):
            for member in details:
                val = member.get('value', {})
                staff_list.append({
                    'order_no': order_no,
                    'member_no': val.get('担当者コード', {}).get('value'),
                    'member_name': val.get('担当者名称', {}).get('value')
                })

    df_staff = pd.DataFrame(staff_list)
    return df_staff


# -------------------------
# CSV読み込み例
# -------------------------
rc_df = pd.read_csv('records.csv', encoding='cp932')
pr_df = pd.read_csv(r"C:\Users\shirai.honoka\Desktop\project\static\all_data.csv", encoding="cp932")

# 必要なカラム抽出・リネームは以前のまま
rc_df = rc_df[['社員番号',
               '日付',
               '曜日',
               '計算開始',
               '計算終了',
               '休憩時間',
               '勤務時間',
               '所定内労働',
               '時間外労働',
               '深夜時間',
               '有給休暇時間']]

rc_df = rc_df.rename(columns={
    '社員番号':'member_no',
    '日付':'work_date',
    '曜日':'weekday',
    '計算開始':'start_dtime',
    '計算終了':'end_dtime',
    '休憩時間':'rest_time',
    '勤務時間':'work_time',
    '所定内労働':'standard_time',
    '時間外労働':'over_time',
    '深夜時間':'night_time',
    '有給休暇時間':'paid_leave_time',
})

pr_df = pr_df[['社員番号',
               '日付',
               'プロジェクトコード',
               'タスクコード',
               'タスク名称',
               '工数']]

pr_df = pr_df.rename(columns={
    '社員番号':'member_no',
    '日付':'work_date',
    'プロジェクトコード':'pj_cd',
    'タスクコード':'task_cd',
    'タスク名称':'task_name',
    '工数':'man_hour_time',
})

pr_df['work_date'] = pd.to_datetime(pr_df['work_date'])
now = datetime.now()
for df_tmp in [rc_df, pr_df]:
    df_tmp['entry_date'] = now
    df_tmp['update_date'] = now
    df_tmp['del_flg'] = False

# -------------------------
# DB登録関数例
# -------------------------
def delete_existing_month_data(df, schema_name, table_name):
    target_month = df['work_date'].min().strftime('%Y-%m')
    with engine.begin() as conn:
        sql = text(f"DELETE FROM {schema_name}.{table_name} WHERE TO_CHAR(work_date, 'YYYY-MM') = :target_month")
        conn.execute(sql, {"target_month": target_month})
    print(f"{schema_name}.{table_name} の {target_month} の既存データを削除しました。")

def insert_with_check(df, table_name):
    try:
        df.to_sql(table_name, con=engine, schema='weprj', if_exists='append', index=False)
        print(f"{table_name} にデータ挿入完了！")
    except IntegrityError as e:
        print(f"{table_name} の挿入中に重複エラー発生、処理中断！")
        raise e

# -------------------------
# DB登録処理例
# -------------------------
delete_existing_month_data(pr_df, 'weprj', 'man_hours')
rc_df.to_sql('work_record', con=engine, schema='weprj', if_exists='append', index=False)
insert_with_check(pr_df, 'man_hours')

# -------------------------
# Kintoneデータ取得（カラム確認）
# -------------------------
print("Kintoneデータ取得開始")
df_staff = get_kintone_df(app_id, api_token_data, domain)
print("Kintoneデータ取得終了")


