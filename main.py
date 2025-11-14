from export.export_kenshu import export_kenshu
from export.export_work import export_work
from export.export_worktime_personal import export_worktime_personal
from import_data import get_kintone_df
from config.settings import KINTONE_CONFIG

# -----------------------------
# Kintoneからスタッフ情報取得
# -----------------------------
df_staff = get_kintone_df(
    app_id=KINTONE_CONFIG["APP_ID"],
    api_token_data=KINTONE_CONFIG["API_TOKEN"],
    domain=KINTONE_CONFIG["DOMAIN"]
)

# -----------------------------
# 出力対象設定
# -----------------------------
pattern_code = "PAT001"          # パターンコード
zexis_keiyaku_no = "A580114"    # 受注番号
tanto_cd = "08009"               # 社員番号（必要なら単数でもOK）

# -----------------------------
# 出力処理
# -----------------------------
export_kenshu(zexis_keiyaku_no, pattern_code)

# staff_list を渡す場合（単数もOK）
export_work(zexis_keiyaku_no, df_staff, staff_list=tanto_cd, pattern_code=pattern_code)

export_worktime_personal(zexis_keiyaku_no,tanto_cd)

print("出力処理が完了しました。")
