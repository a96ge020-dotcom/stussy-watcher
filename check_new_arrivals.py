"""
스투시(Stussy) 신상품(New Arrivals) 감지 후 이메일 알림 스크립트
- 대상 페이지: https://www.stussy.com/collections/new-arrivals
- 동작 방식: 상품 링크 목록을 긁어와서 이전 실행 때 저장해둔 목록(seen_products.json)과 비교
             -> 새로 생긴 상품이 있으면 이메일 발송
- 실행 방식: GitHub Actions 등으로 주기적(예: 30분마다) 실행하는 것을 권장
"""

import json
import os
import re
import smtplib
import sys
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

# ----------------------------
# 설정
# ----------------------------
TARGET_URL = "https://www.stussy.com/collections/new-arrivals"
STATE_FILE = "seen_products.json"

# 이메일 설정 (환경변수로 관리 - 코드에 직접 비밀번호를 적지 않습니다)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")        # 보내는 사람 gmail 주소
SENDER_APP_PASSWORD = os.environ.get("SENDER_APP_PASSWORD")  # gmail 앱 비밀번호(16자리)
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")    # 알림 받을 이메일 주소

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_products():
    """새로운 상품 목록 페이지에서 상품명 + 링크를 추출합니다."""
    resp = requests.get(TARGET_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    products = {}
    # 상품 상세 페이지 링크 패턴: /collections/new-arrivals/products/xxxxx
    for a in soup.select("a[href*='/collections/new-arrivals/products/']"):
        href = a.get("href", "")
        if not href:
            continue
        # 절대경로로 변환
        if href.startswith("/"):
            href = "https://www.stussy.com" + href
        # 쿼리스트링 제거해서 중복 방지
        href = href.split("?")[0]

        name = a.get_text(strip=True)
        if not name:
            # 이미지 alt 텍스트에서라도 이름을 가져와 봅니다
            img = a.find("img")
            name = img.get("alt", "").strip() if img else ""

        if href not in products and name:
            products[href] = name

    return products


def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_seen(products):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def send_email(new_items: dict):
    if not (SENDER_EMAIL and SENDER_APP_PASSWORD and RECEIVER_EMAIL):
        print("이메일 환경변수(SENDER_EMAIL / SENDER_APP_PASSWORD / RECEIVER_EMAIL)가 설정되지 않았습니다.")
        return

    lines = [f"- {name}\n  {url}" for url, name in new_items.items()]
    body = "스투시 새 상품이 등록되었습니다!\n\n" + "\n\n".join(lines) + f"\n\n페이지: {TARGET_URL}"

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = f"[Stussy 알림] 신상품 {len(new_items)}건 등록"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())

    print(f"이메일 발송 완료: 신상품 {len(new_items)}건")


def main():
    current = fetch_products()
    if not current:
        print("경고: 상품을 하나도 찾지 못했습니다. 사이트 구조가 바뀌었을 수 있습니다.")
        sys.exit(0)

    seen = load_seen()

    if not seen:
        # 최초 실행: 알림 없이 현재 상태만 저장 (기준점 만들기)
        save_seen(current)
        print(f"최초 실행: 현재 상품 {len(current)}건을 기준으로 저장했습니다. 다음 실행부터 새 상품을 알려드립니다.")
        return

    new_items = {url: name for url, name in current.items() if url not in seen}

    if new_items:
        print(f"새 상품 {len(new_items)}건 발견")
        send_email(new_items)
    else:
        print("새 상품 없음")

    save_seen(current)


if __name__ == "__main__":
    main()
