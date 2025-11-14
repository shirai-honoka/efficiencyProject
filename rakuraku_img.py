from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()

        page.goto('https://tms.kinnosuke.jp/app/login', wait_until="networkidle")

        # 各フィールドが出るまで待つ
        page.wait_for_selector('#customerId', timeout=15000)

        # 入力
        page.fill('#customerId', 'ncdsol')  
        page.fill('#loginId', 'n25010')  
        page.fill('#password', 'Honoka0820#3')  

        # ログインボタンをクリック
        page.click('button:has-text("ログイン")')

        # ページ遷移待機
        page.wait_for_load_state('networkidle')

        # 出勤簿画面リンクが出るまで待つ
        page.wait_for_selector('img[title="出勤簿画面を表示"]', timeout=10000)
        page.click('img[title="出勤簿画面を表示"]')
        
        # チェックボックスが出るまで待つ
        page.wait_for_selector('input.checkbox[value="1"]', timeout=15000, state='attached')

        page.eval_on_selector('input.checkbox[value="1"]', """
        el => {
        el.checked = true;
        el.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """)
        
        page.click('img[title="出勤簿のPDFエクスポート"]')



        # ブラウザを閉じずに待機（10分）
        page.wait_for_timeout(10 * 60 * 1000)

if __name__ == '__main__':
    run()
