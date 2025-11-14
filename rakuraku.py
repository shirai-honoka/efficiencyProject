from playwright.sync_api import sync_playwright
import os

DOWNLOAD_DIR = r"C:\Users\shirai.honoka\Desktop\project\static"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # --- ログイン ---
        page.goto('https://tms.kinnosuke.jp/app/login', wait_until="networkidle")
        page.fill('#customerId', 'ncdsol') 
        page.fill('#loginId', 'n25010') 
        page.fill('#password', 'Honoka0820#3') 
        page.click('button:has-text("ログイン")')

        # --- プロフィール → モード変更 ---
        page.click('.profile_menu_name_wrapper')
        page.locator('button:has-text("閲覧")').first.click()

        # --- 工数管理 → プロジェクト工数集計 ---
        page.click('button.base_header_tab_base:has-text("工数管理")')
        page.click('li:has-text("プロジェクト工数集計")')
        
        # 過去ページに移動
        page.click('div.change_prev')
        page.click('div.change_prev')

        # --- 最終ページ番号を取得 ---
        page.locator('li:has-text(">>")').click()
        pager_items = page.locator('ul.pager li')
        count = pager_items.count()
        last_page_number = int(pager_items.nth(count - 3).inner_text())
        #--- 1ページ目に戻る ---
        page.locator('li:has-text("1")').click()
        # --- ページごとにCSVダウンロード ---
        for page_number in range(1, last_page_number + 1):
            if page_number != 1:
                # ページ切り替え
                page.locator(f'ul.pager li:has-text("{page_number}")').click()
                page.wait_for_timeout(1500)  

            # チェックボックスON
            page.wait_for_selector('input[name="type"]', state='attached', timeout=15000)
            page.eval_on_selector('input[name="type"]', """
                el => {
                    el.checked = true;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
            """)

            # プレビュー
            page.click('span.export_button.button_positive')

            # CSVエクスポート
            page.click('img[title="プロジェクト工数集計のCSVエクスポート"]')
            page.click('input[name="export_aggregate_unit"][value="2"] >> xpath=..')
            page.click('input[name="export_item_name_content"][value="3"] >> xpath=..')
            page.click('button.label_button.button_positive.narrow')  # 書き出し実行
            page.click('button.label_button.button_positive.narrow')

            page.wait_for_selector('span.close_button', state='attached', timeout=10000)
            page.click('span.close_button')

        # --- お知らせ → お知らせ受信一覧へ ---
        page.click('img[title="お知らせ"]')
        page.click('button:has-text("お知らせ受信一覧へ")')

        # 通知一覧がロードされるまで待つ
        page.wait_for_selector('.notification_row', timeout=10000)
        page.wait_for_timeout(1000)

        # 通知をすべて取得
        notifications = page.locator('.notification_row')
        notif_count = notifications.count()
        download_count = min(last_page_number, notif_count)

        for i in range(download_count):
            notif = notifications.nth(i)

            # 通知が閉じている場合は開く
            content = notif.locator('.notification_content')
            if not content.is_visible():
                notif.click()
                page.wait_for_timeout(1000)

            # ファイルリンクをクリックしてダウンロード
            file_link = notif.locator('a.file_link')
            with page.expect_download() as download_info:
                file_link.first.click()
                download = download_info.value
                filename = download.suggested_filename
                download_path = os.path.join(DOWNLOAD_DIR, filename)
                download.save_as(download_path)

        # --- 待機（10分） ---
        page.wait_for_timeout(10 * 60 * 1000)

if __name__ == '__main__':
    run()
