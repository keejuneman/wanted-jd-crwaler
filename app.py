import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 크롤링 함수 정의
def crawl_wanted(years_min, years_max, selected_jobs):
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")

    # ChromeDriver 설정
    driver = webdriver.Chrome(options=chrome_options)

    # URL 생성
    base_url = "https://www.wanted.co.kr/wdlist/518?country=kr&job_sort=job.recommend_order"
    url = f"{base_url}&years={years_min}&years={years_max}"

    # 선택한 직무 추가
    for job in selected_jobs:
        url += f"&selected={options[job]}"

    # 원티드 페이지로 이동
    driver.get(url)

    # 페이지 끝까지 스크롤하는 함수
    def scroll_to_end():
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    # 페이지 끝까지 스크롤
    scroll_to_end()

    data = []
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)

    try:
        N = 1
        while True:
            try:
                job_selector = f'//*[@id="__next"]/div[3]/div[2]/ul/li[{N}]/div/a'
                job_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, job_selector)))
                job_url = job_link.get_attribute('href')
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(job_url)
                time.sleep(3)

                try:
                    more_button = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/button/span[2]')
                    more_button.click()
                    time.sleep(1)
                except:
                    pass

                company_name = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div/section/header/div/div[1]/a').text
                job_title = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div/section/header/h1').text
                preferred_qualifications = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/div[3]/p/span').text

                data.append({
                    '회사 명': company_name,
                    '직무': job_title,
                    '우대 사항': preferred_qualifications
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(2)
                N += 1
            except Exception as e:
                print(f"Failed to process job listing {N}: {e}")
                break
    finally:
        driver.quit()

    return pd.DataFrame(data)

# Streamlit 인터페이스
st.title("Wanted Job Scraper")

# 경력 범위 선택
years_min, years_max = st.sidebar.slider('경력 (년)', 0, 10, (0, 10))

# 선택 항목
options = {
    '소프트웨어 엔지니어': 10110,
    '웹 개발자': 873,
    '서버 개발자': 872,
    '프론트엔드 개발자': 669,
    'JAVA 개발자': 660,
    'C, C++ 개발자': 900,
    'Python 개발자': 899,
    '머신러닝 엔지니어': 1634,
    'DevOps / 시스템 관리자': 674,
    '데이터 엔지니어': 655,
    'Node.js 개발자': 895,
    '시스템, 네트워크 관리자': 665,
    '안드로이드 개발자': 677,
    'IOS 개발자': 678,
    '임베디드 개발자': 658,
    '기술지원': 1026,
    'QA,테스트 엔지니어': 676,
    '개발 매니저': 877,
    '데이터 사이언티스트': 1024,
    '보안 엔지니어': 671,
    '빅테이터 엔지니어': 1025,
    '하드웨어 엔지니어': 672,
    '프로덕트 매니저': 876,
    '블록체인 플랫폼 엔지니어': 1027,
    '크로스플랫폼 앱 개발자': 10111,
    'DBA': 10231,
    'PHP 개발자': 893,
    '.NET 개발자': 661,
    '영상, 음성 엔지니어': 896,
    '웹 퍼블리셔': 939,
    'ERP 전문가': 10230,
    '그래픽스 엔지니어': 898,
    'VR 엔지니어': 10112,
    'CTO': 795,
    'BI 엔지니어': 1022,
    '루비온레일즈 개발자': 894,
    'CIO': 793,
    '데이터 엔지니어': 655,
    'BI 엔지니어': 1022,
    '데이터 분석가': 656,
    '퍼포먼스 마케터': 10138,
    '그로스 해커': 717
}

# 선택 박스
selected_jobs = st.sidebar.multiselect('직무 선택 (최대 5개)', options.keys(), max_selections=5)

# 크롤링 버튼
if st.button('크롤링 시작'):
    with st.spinner('크롤링 중...'):
        # 크롤링 함수 호출
        df = crawl_wanted(years_min, years_max, selected_jobs)
        st.success('크롤링 완료!')

        # 데이터프레임 표시
        st.dataframe(df)

        # CSV 다운로드 버튼
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("CSV 다운로드", csv, "wanted_jobs.csv", "text/csv", key='download-csv')
