import pandas as pd
from sqlalchemy import create_engine
import requests
from config import settings


def get_engine():
    cfg = settings.DB_CONFIG
    url = f"postgresql+psycopg2://{cfg['USER']}:{cfg['PASSWORD']}@{cfg['HOST']}:{cfg['PORT']}/{cfg['NAME']}"
    return create_engine(url)


def get_kintone_df(app_id=None, api_token=None, domain=None) -> pd.DataFrame:
    app_id = app_id or settings.KINTONE_CONFIG["APP_ID"]
    api_token = api_token or settings.KINTONE_CONFIG["API_TOKEN"]
    domain = domain or settings.KINTONE_CONFIG["DOMAIN"]

    url = f"https://{domain}/k/v1/records.json"
    headers = {
        "X-Cybozu-API-Token": api_token,
    }

    all_records = []
    limit = 100
    offset = 0

    while True:
        # ✅ queryはURLパラメータ用の文字列として定義
        query = f"limit {limit} offset {offset}"

        params = {
            "app": app_id,
            "query": query
        }

        response = requests.get(url, headers=headers, params=params)
        print(f"Request → {response.status_code} offset={offset}")
        if response.status_code != 200:
            print("Error detail:", response.text)
            response.raise_for_status()

        records = response.json().get("records", [])
        if not records:
            break

        all_records.extend(records)
        offset += limit

    df = pd.json_normalize(all_records)
    return df
