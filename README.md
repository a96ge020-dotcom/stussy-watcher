# 스투시 신상품 이메일 알림

`https://www.stussy.com/collections/new-arrivals` 페이지를 주기적으로 확인해서
새로운 상품이 등록되면 이메일로 알려주는 스크립트입니다.

## 1. 준비물
- GitHub 계정 (무료)
- Gmail 계정 1개 (알림을 "보내는" 용도. 받는 이메일은 아무 주소나 가능)

## 2. Gmail 앱 비밀번호 발급
Gmail은 일반 로그인 비밀번호로 프로그램 발송을 허용하지 않으므로 "앱 비밀번호"가 필요합니다.
1. 구글 계정 → 보안 → 2단계 인증을 먼저 켭니다.
2. 구글 계정 → 보안 → "앱 비밀번호" 메뉴로 이동해 새 앱 비밀번호를 생성합니다.
3. 생성된 16자리 비밀번호를 복사해둡니다. (이게 `SENDER_APP_PASSWORD` 입니다)

## 3. GitHub 저장소 만들기
1. GitHub에서 새 저장소(Private로 설정 추천)를 만듭니다.
2. 이 폴더(`stussy-watcher`)의 파일들을 그대로 업로드/푸시합니다.
   - `check_new_arrivals.py`
   - `requirements.txt`
   - `.github/workflows/check.yml`

## 4. 비밀 값(Secrets) 등록
저장소 → Settings → Secrets and variables → Actions → "New repository secret" 에서
아래 3개를 등록합니다.

| Name | 값 |
|---|---|
| `SENDER_EMAIL` | 알림을 보낼 Gmail 주소 (예: myalert@gmail.com) |
| `SENDER_APP_PASSWORD` | 2번에서 발급받은 16자리 앱 비밀번호 |
| `RECEIVER_EMAIL` | 알림을 받을 이메일 주소 |

## 5. 실행 확인
- 저장소 → Actions 탭 → "Stussy New Arrivals Watcher" → "Run workflow" 버튼으로 수동 테스트 가능합니다.
- 최초 실행 시에는 알림 없이 현재 상품 목록만 저장합니다. (기준점 생성)
- 그 다음 실행부터 새 상품이 생기면 이메일이 옵니다.
- 기본 설정은 30분마다 자동 실행되며, `.github/workflows/check.yml` 파일의
  `cron: "*/30 * * * *"` 부분 숫자를 바꾸면 주기를 조절할 수 있습니다.
  (너무 짧게 설정하면 사이트에 부담을 줄 수 있어 10분 이상을 권장합니다)

## 참고
- 사이트 구조가 바뀌면(리뉴얼 등) 스크립트 수정이 필요할 수 있습니다.
- 신상품 "등록"만 감지합니다. 특정 상품의 재입고/품절 여부를 감지하려면
  로직을 다르게 짜야 하니 필요하면 말씀해 주세요.
