0922

좋아 Hojun, 그럼 지금까지 우리가 만든 **DOA Trader**의 전체 구조와 실행 흐름을 한눈에 볼 수 있게 정리해줄게.  
그리고 이걸 어떻게 보관·관리하면 좋은지도 추천해줄게.

---

## 📂 전체 파일 구조 & 실행 흐름

```
DOA-Trader/
│
├── app/
│   ├── main.py                # FastAPI 앱 초기화 & 라우터 등록
│   ├── scheduler.py           # 장전/장중/장후 스케줄링
│   │
│   ├── routes/
│   │   └── dashboard.py       # /ui API (status, price, holdings, logs)
│   │
│   ├── workflows/
│   │   ├── pre_open.py        # 장전 종목 발굴
│   │   ├── intraday_loop.py   # 장중 전략 실행
│   │
│   ├── trade/
│   │   └── executor.py        # KIS API 실거래 주문
│   │
│   ├── data/
│   │   └── watchlist.py       # 당일 매매 종목 리스트 저장
│   │
│   └── log/
│       └── audit.py           # 이벤트 로그 기록/조회
│
├── web/
│   ├── index.html              # 프론트엔드 메인 페이지
│   └── static/
│       ├── css/style.css       # 프리미엄 UI 스타일
│       └── js/app.js           # 실시간 데이터 갱신 & UI 이벤트
│
├── .env                        # 환경변수 (KIS API 키, 계좌번호 등)
└── requirements.txt            # Python 패키지 목록
```

---

## 🔄 실행 순서

1. **08:30 장전 루틴 (`pre_open.py`)**
   - 전 종목 스캔 → 점수화 → 상위 N개 종목 `watchlist` 저장

2. **09:00~15:30 장중 루프 (`intraday_loop.py`)**
   - `watchlist` 종목 실시간 시세 조회
   - 매수/매도 조건 충족 시 `executor.py`로 실거래 주문
   - 모든 이벤트 `audit.py`에 기록

3. **15:40 장후 루틴**
   - 당일 거래 요약
   - 로그 저장 및 분석

4. **프론트엔드 (`index.html` + `style.css` + `app.js`)**
   - `/ui/status` → 시장 상태·계좌 잔고
   - `/ui/price` → 실시간 차트
   - `/ui/holdings` → 보유 종목 테이블
   - `/ui/logs` → 실시간 로그
   - 버튼 클릭 시 `/orders/start|stop|kill` 호출

---

## 📌 보관 & 관리 추천

- **Git 저장소**  
  - GitHub, GitLab, Bitbucket 중 하나에 private repo로 올려두면 버전 관리와 백업이 동시에 가능  
  - `.env` 파일은 `.gitignore`에 반드시 추가 (API 키·계좌번호 유출 방지)

- **환경변수 관리**  
  - 로컬 개발용 `.env`  
  - 서버 배포 시는 OS 환경변수 또는 Docker secrets 사용

- **문서화**  
  - `README.md`에 설치 방법, 실행 방법, 환경변수 설명, 실행 흐름 다 적어두기  
  - 나중에 유지보수나 기능 추가할 때 큰 도움

- **배포 자동화**  
  - Dockerfile 만들어서 컨테이너로 배포하면 환경 차이 없이 실행 가능  
  - 서버 재시작 시 자동 실행되게 `systemd`나 Docker Compose 설정

---

💡 내가 원하면 이 구조를 **README.md 템플릿**으로 바로 만들어줄 수 있어.  
그렇게 하면 GitHub에 올렸을 때 프로젝트 소개, 설치법, 실행법이 한눈에 보이게 돼서  
다른 사람에게 보여주거나 협업할 때도 깔끔해.  

원해? 그러면 바로 README.md 완성본 만들어줄게.
