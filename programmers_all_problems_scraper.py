from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import time

# ✅ 크롬 옵션 설정
options = Options()
options.add_argument('--headless')  # 브라우저 없이 실행
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# ✅ 드라이버 실행
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# ✅ 시작 URL
url = "https://school.programmers.co.kr/learn/challenges?order=acceptance_desc"
driver.get(url)

results = []

while True:
    try:
        # ✅ 테이블 로딩 대기 + 추가 시간 확보
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))
        time.sleep(2)  # 페이지 로딩 충분히 기다림

        # 🔁 문제 목록 새로 가져오기
        row_elements = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

        for i in range(len(row_elements)):
            try:
                row = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")[i]

                title_elem = row.find_element(By.CSS_SELECTOR, "td.title a")
                title = title_elem.text.strip()
                link = title_elem.get_attribute("href")

                level = row.find_element(By.CSS_SELECTOR, "td.level").text.strip()
                solved = row.find_element(By.CSS_SELECTOR, "td.finished-count").text.strip()
                rate = row.find_element(By.CSS_SELECTOR, "td.acceptance-rate").text.strip()

                # ✅ 전처리
                level = level.replace("Lv.", "").strip()
                solved = int(solved.replace(",", "").replace("명", ""))
                rate = float(rate.replace("%", "").strip())

                results.append({
                    "제목": title,
                    "레벨": level,
                    "정답률": rate,
                    "완료한 사람": solved,
                    "링크": link
                })

            except StaleElementReferenceException:
                print("♻️ StaleElement 무시하고 넘어감")
                continue
            except Exception as e:
                print("❌ 파싱 오류:", e)
                continue

        # ✅ 다음 페이지 클릭
        try:
            next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='다음 페이지']")))

            if next_btn.get_attribute("disabled") or next_btn.get_attribute("aria-disabled") == "true":
                print("✅ 마지막 페이지 도달")
                break

            # 페이지 전환되기 전 요소가 사라질 때까지 기다림
            next_btn.click()
            wait.until(EC.staleness_of(row_elements[0]))

            

        except Exception as e:
            print("✅ 다음 페이지 없음 또는 버튼 오류:", e)
            break

    except Exception as e:
        print("✅ 전체 루프 종료:", e)
        break

# ✅ 드라이버 종료
driver.quit()

# ✅ CSV로 저장
df = pd.DataFrame(results)
df.to_csv("programmers_all_problems.csv", index=False, encoding="utf-8-sig")

print(f"🎉 크롤링 완료! 총 {len(results)}개 문제 수집됨 → programmers_all_problems.csv 저장됨.")
