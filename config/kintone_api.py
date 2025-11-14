import requests
import pandas as pd

def get_kintone_records(app_id, api_token, domain, query=''):
    """キントーンAPIから全レコードを取得してDataFrameで返す（シンプル版）"""
    url = f"https://{domain}/k/v1/records.json"
    headers = {"X-Cybozu-API-Token": api_token}
    limit = 500
    offset = 0
    all_records = []

    while True:
        q = f"{query} limit {limit} offset {offset}" if query else f"limit {limit} offset {offset}"
        params = {"app": app_id, "query": q}

        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            print(f"❌ Error {res.status_code}: {res.text}")
            break

        data = res.json().get("records", [])
        if not data:
            break

        all_records.extend(data)
        offset += limit

    # キントーンのrecordsをpandas.DataFrameに変換
    def simplify(record):
        return {k: v["value"] for k, v in record.items()}

    if not all_records:
        print("⚠️ データが取得できませんでした。")
        return pd.DataFrame()

    df = pd.DataFrame([simplify(r) for r in all_records])
    print(f"✅ {len(df)} 件のレコードを取得しました。")
    return df
