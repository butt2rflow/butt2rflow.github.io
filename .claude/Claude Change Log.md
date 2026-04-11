# Claude Change Log — BlogMigration

## 2026-04-10 (Session 7)

### Session: Excalidraw Diagrams for Tool Articles + Editorial Review

**PDF Series Diagram Fixes:**
- 실행편 P14 개념 연결도: 박스 x:60→x:200 가운데 정렬 (제목 중심선 맞춤)
- 실행편 P31 신호 결합 흐름: 단계 라벨 y:55→y:35, 액션 y:135→y:150 (시간선 간격 확보)
- 0DTE 시리즈 4편: 4개 신규 다이어그램 (SPX 타임라인, 곱셈 효과, 피드백 루프, Gamma/Charm/Vanna)
- PDF 전체 재생성 완료 (심화편 991→1141KB)

**Blog Tool Articles — 9 New Excalidraw Diagrams:**
- GEX calculator: MM 감마 동작, GEX 공식 분해 (4열 배치), 감마 플립 포인트 (좌우 교정)
- 0DTE patterns: 감마 스케일링 바 차트, 거래 유형 (4열 레이아웃), U자형 패턴
- Volatility dashboard: 내재상관관계 분산/동조화, COR 2축 구조 (COR70D 추가), 세 신호 종합

**Diagram QA — 4 Issues Fixed:**
- `gex_flip_point`: 좌우 반전 (낮은 가격=숏 감마, 높은 가격=롱 감마로 교정)
- `gamma4_three_greeks`: Gamma/Vanna 화살표 MM 박스 안으로 재정렬
- `gex_formula`: 2x2 → 1x4 가로 배치, 점선 정렬
- `0dte_order_flow`: 2행 스택 → 4열 레이아웃 (화살표 겹침 해소)

**Editorial Review (6 articles):**
- 다이어그램 도입 문장 추가 (naked image 방지)
- alt text 구체화 (generic → descriptive)
- intraday_gamma 다이어그램 설명 뒤로 이동
- 연속 다이어그램 사이 구분 문장 (선행 신호와 실전)

**Git Multi-PC Conflict Resolution:**
- docs/ unrelated histories 충돌 (work PC push vs home PC add)
- origin/main 기반 blog-diagrams 브랜치로 clean push
- master reset --soft origin/main으로 동기화

**Memory Updated:**
- project_tool_articles: 다이어그램 9개 추가 반영
- feedback_diagram_review (신규): QA 체크리스트 5항목
- feedback_multi_pc_git (신규): 두 PC + 클라우드 싱크 git pull 규칙

**Notes for Next Session:**
1. 저쪽 PC에서 git pull origin main
2. 크몽 상품 등록 (전문가 등록 완료, 서비스 등록 대기)
3. Pine Script TradingView 실제 테스트

---

## 2026-04-05 (Session 6)

### Session: COR IV Surface Diagram Fix + Color Audit

**COR IV Surface Diagram Fix:**
- diag_cor_iv_surface: 개별 점 라벨 추가 (COR1M, COR6M, COR9M, COR1Y, COR3MD10/30/70/90)
- 기존에는 VIX, COR3M만 라벨 있었음 → 전체 8개 라벨 추가
- create_cor_diagrams.py 소스도 동기화 (라벨 포함하도록 수정)
- PNG 재생성 완료 (1810x884)

**크몽 썸네일 vs MkDocs 테마 컬러 비교:**
- Gold/amber 톤 일치 (#f59e0b ↔ Material amber)
- 크몽 파란 액센트 바(#3b82f6)는 MkDocs에 없음
- 크몽 다크 배경(#1a1a2e) vs MkDocs 라이트 — 의도적 차이
- 결론: 큰 불일치 없음, 플랫폼별 차이는 의도적

**Notes for Next Session:**
1. 크몽 상품 등록 (전문가 등록 완료, 서비스 등록 대기)
2. Pine Script TradingView에서 실제 테스트
3. 크몽/MkDocs 액센트 컬러 통일 여부 (선택사항)

---

## 2026-04-05 (Session 5)

### Session: Kmong + MkDocs Launch + Full Polish Pipeline

**Kmong Package:**
- 크몽 가입 완료, 패키지 불일치 3건 수정 (번들 가격/편수/페이지수)
- 시리즈 4 (심화편) 추가: listing_series4.md, thumb_series4.png
- 번들 업데이트: 3→4시리즈, 16,900→19,900원 (35% 할인)
- 등록 가이드 5개 상품으로 업데이트

**Series 1-4 Editor Review + Fixes:**
- 4-part 원칙편: 조사 오류, 오귀속, 표기 불일치 수정
- 시리즈 2 실행편: Part 2에서 270줄 중복 삭제, 깨진 링크 수정
- 시리즈 3 확장편: 잘못된 시리즈 참조 4곳 수정, TQQQ 수수료 0.86→0.88%
- 모든 시리즈 PDF 재생성 (17개, 블로그 URL 삽입)

**Standalone Posts Polish (7 posts):**
- 저작권 이미지 49개 제거 → 18개 Excalidraw 신규 제작
- COT (4 Excalidraw), Skew (4), FedWatch (2), Hedging Wings (5), 심리변동성 (3)
- 몬테카를로: 파이썬 차트 5개 (matplotlib), 팩트체크 3건 수정
- Almanac: 파이썬 월별 seasonality 차트 4개, 네이버 이미지 12개 추출

**MkDocs GitHub Pages:**
- butt2rflow.github.io 라이브 배포
- 7개 포스트 + 시리즈 1편 무료 + 시리즈 미리보기 4개
- 테마: 앰버 헤더 + 라이트 모드 고정
- butterflow 로고 (Vecteezy, attribution 포함)
- navigation.instant 추가

**Fact-Check Corrections:**
- VIX 설명: "ATM 단일 지점" → "광범위한 OTM, 분산스왑 복제 구조"
- 섀넌 석사 논문 1938→1937, MIT 복귀 1958→1956
- 맥스웰의 도깨비 1871→1867, Vanguard 보고서 2019→2015
- COR 모니터링: 간격 설명 반대로 되어있던 것 수정

**Content Improvements:**
- Hedging Wings: 사전 지식 체크리스트, SPY $540 구체 예시, IV 시나리오 테이블, 실행 난이도 경고, Second Leg Down 출처 추가
- 심리변동성 지수: TradingView BF_COR_TermStructure 차트 추가
- Almanac 네이버 카페 링크 삭제

**GitHub Account:**
- gfunctionfinance → butt2rflow 유저네임 변경
- butt2rflow/butt2rflow.github.io repo 생성
- GitHub Actions 자동 배포 설정

**Additional Work (continued session):**

- 실행편 2편: SPY 변동성 타겟팅 백테스트 (Sharpe 0.56→0.79, MDD -55%→-36%)
- 실행편 3편: 구조 재편 (핵심 3개 집중, 모멘텀 축소, IVTS 사례 추가)
- TradingView Pine Script 3개: BF_VolVol, BF_COR_TermStructure, BF_COR_DeltaSkew
- 0DTE/Skew/심리변동성/Almanac 깊이 보강
- 몬테카를로: 정확한 VaR ($844 5th pct), Hedging Wings: Convexity 설명 + 데드 존 $19.10
- Almanac: IS vs OOS 백테스트 (75% 방향 일치)
- "한국" 불필요 강조 제거, IV Surface 다이어그램 겹침 수정
- 외부 링크 전체 검증, 구글시트 edit→copy, pdfs/ 정리
- 최종 평가: 7.5 → 8.0+ (8.5 목표 개선 적용)

**Notes for Next Session:**
1. 크몽 상품 등록 (전문가 등록 완료, 서비스 등록 대기)
2. Pine Script TradingView에서 실제 테스트
3. CBOE COR 데이터 파이썬 접근 방법 조사

---

## 2026-04-04 (Session 4)

### Session: GEX Diagram Fix + PDF Rename + Standalone Posts Polish

**GEX Profile Diagram Redesign:**
- Strike labels (3800-4200) placed on x-axis with proper spacing
- "SPX 현재가" moved above x-axis with downward arrow
- Flip point, zone labels (풋/콜 OI), 자석/가속기 효과 repositioned
- Multiple rounds of positioning feedback from user

**PDF Filename Convention:**
- `{number}_{name}.pdf` → `s{series}_{seq}_{name}.pdf` (e.g., `s4_03_gex.pdf`)
- generate_pdfs.py SERIES config updated, old files cleaned up

**GEX Article Fix:**
- Limit #5 numbering unified with 1-4 (bold standalone → numbered list)

**Standalone Posts Polished (5 posts):**
1. 변동성 Skew (2023-01-14) — 6 images, Smile vs Smirk, Conditional Correlation
   - Fact-check: NASDAQ 1999 "100% 상승" claim removed (unverified)
2. Hedging the Wings (2023-01-17) — 15 images, 1:2 put ratio spread
   - Fact-check: 10 delta put cost "연 20%" → ATM은 18-30%, 10 delta는 1.5-2%
3. 시장 심리 변동성 지수 (2023-02-12) — 14 images, COR3M, IV Surface
   - Fact-check: COR3MD 누락 추가 (Delta Skew 4→5개)
4. COT — 선물시장에서 현물시장 살펴보기 (2021-07-04) — 5 images, D-COT/TFF
   - Fact-check: "화요일 2시"→"화요일 장마감", Southwest 2019→2008/70%, 13F 5-6개월→1.5-4.5개월, "larger traders"→"Non-Commercial"
5. Fed Fund 선물과 FedWatch Tool (2023-03-26) — 16 images, 2부작 합본
   - Fact-check: EFFR "평균"→"중앙값" (2016 변경), ZQF4→ZQH3, IMM 공식 명확화

**Merged/Deleted Posts:**
- `Fed Fund 선물과 EFFR.md` → FedWatch 글에 합본
- `5월 28일 Smart Money Dumb Money.md` → COT 글에 흡수

**Skipped:**
- 미국 채권 경매 일정 (시사 스냅샷, 교육 가치 낮음)

**Content Strategy Decision:**
- MkDocs: s1 1편(섀넌) 전문 공개 + s2-s4 미리보기 + standalone 전체 공개
- Kmong: s1-s4 합본 PDF 유료 판매
- 퍼널: 검색 유입 → MkDocs → 시리즈 맛보기 → Kmong 구매

**Evaluated for Future:**
- 몬테카를로 시뮬레이션 → 파이썬 버전 추가 예정 (교육 가치 높음)
- Almanac Trader → 구글시트 카테고리 보존, 가벼운 polish

**Notes for Next Session:**
- MkDocs 세팅 + polish된 글 배치
- docs/ 폴더 구조 생성, mkdocs.yml 작성
- 섀넌 1편 전문 + 나머지 시리즈 미리보기 페이지 생성
- standalone 글들 docs/posts/로 배치
- GitHub Pages 배포 설정

## 2026-04-04 (Session 3)

### Session: Gamma Series Rewrite + Full Editorial Review + Kmong Finalization

**Gamma Series (심화편) — 4편 리라이트 from scratch:**
- 1편: 감마 — 델타의 가속도 (속도/가속도 비유, GME 감마 스퀴즈, ATM/만기 관계)
- 2편: 마켓메이커의 동적 헷지 (환전소 비유, 소방관/방화범, 자기강화 루프)
- 3편: GEX — 시장을 움직이는 보이지 않는 손 (GEX 공식, 4가지 가정, 플립 포인트, 개별 종목 GEX 경고)
- 4편: 0DTE — 감마 폭탄의 시대 (거래량 폭증, 장중 감마 증폭, Charm/Vanna 소개)

**3x Review Cycle (팩트체크 + 고급투자자 + 편집자):**
- 감마 300-500x → 100-150x (이론적 근거 1/sqrt(T) 기반)
- SPX ADV +139% → +170% (CBOE 공식)
- 2편 달러 델타 → share equivalent 통일
- GEX 가정 2의 0DTE 시대 구조적 약화 경고 추가
- 개별 종목 GEX 무의미 — 가정 2가 리테일 콜 매수로 깨짐
- "음의 피드백 루프" → "자기강화 루프" (학술 정의 수정)
- MM 관점 명시 강화 (2편 선언 + 3편/4편 주어 추가)
- 마켓메이커 설명 확장 (환전소 비유, 유동성 공급 역할)
- Charm/Vanna 간략 소개 추가 (4편)
- GEX 데이터 소스 표 추가 (SpotGamma, SqueezeMetrics 등)

**7 Excalidraw Diagrams for Gamma Series:**
- diag_gamma1_delta_vs_gamma, diag_gamma1_gamma_atm_curve
- diag_gamma2_market_maker_role, diag_gamma2_hedge_direction, diag_gamma2_feedback_loop
- diag_gamma3_gex_profile
- diag_gamma4_intraday_gamma

**Full 4-Series Editorial Review (8.4/10 overall):**
- 원칙편 9.0, 실행편 7.7, 확장편 8.5, 심화편 8.5
- Best article: 원칙편 4편 "엣지 없는 게임, 엣지 있는 시장"
- Weakest: 실행편 2편 (8개 전략 과밀) → 분리 완료

**실행편 2편→3편 분리:**
- 2편: "비중 조절의 원리 — 후행 신호 전략" (변동성 타겟팅, 역변동성 가중)
- 3편: "선행 신호와 실전" (IVTS, VolVol, Vomma Zone, 모멘텀 결합, 한국 가이드)
- 전체 시리즈 13편 체제로 확장

**PDF Pipeline:**
- generate_pdfs.py: 13개 개별 + 4개 합본으로 업데이트
- PDF 내부 .md 링크 → 텍스트 참조로 자동 변환 (깨진 링크 방지)

**Kmong Package Updated:**
- 실행편 2편→3편, 50p+, 번들 9편 160p+
- 썸네일 2개 재생성

**Notes for Next Session:**
- 크몽 등록 대기 (와이프 회원가입/전문가등록 진행 중)
- 심화편 크몽 판매 전략: 번들 구매자 보너스로 포지셔닝
- GEX 플립 가격 계산기 (Python) — CBOE 데이터 샘플 필요
- 실행편 2편 파일명이 아직 "변동성 타겟 전략"으로 되어 있음 (내용은 후행 신호만)

## 2026-04-03

### Session: PDF Review Pass + New Series Planning

**PDF Diagram Fixes:**
- Fixed text vertical centering in Excalidraw boxes (L080, L101, L356) — manual y positioning required; export tool ignores verticalAlign/containerId
- Changed Excalidraw fontFamily 1 (Virgil) → 3 (monospace) for Korean rendering
- Removed literal tags ([GREEN], [BUST], [YELLOW], [OK], [X]) from diagrams → clean Korean text
- kelly_curve: repositioned Over-betting label + arrow + 파산영역 to correct zone
- L529: fixed arrow connections (smooth diagonal from box centers)
- L356: cleaned up tags, centered text

**Markdown Content Fixes:**
- Removed all emojis from 4 MD files (⚠️❌✅💀⭐ → text; GulimChe renders as □)
- Fixed "두 번째 엣지" → "세 번째 엣지" in Part 4
- Added game rules explanation for 네 가지 게임 비교 (Part 2)
- Fraction display: box-drawing ─── → ASCII ---
- Page breaks before "네 가지 투자 전략 비교" and "섀넌의 도깨비와 켈리의 연결"
- Part 4 beginner improvements: hook, 엣지/기대값 definition, 마틴게일 reminder, $ signs in tables

**New Series Structure (3 series):**
- Series 1: "변동성, 기하 평균, 그리고 켈리" (1-4편, COMPLETED)
- Series 2: "변동성을 다루는 도구들" (옵션 불필요, 한국 투자자 실행 가능)
  - 1편: 변동성, 적인가 친구인가 (HV/IV, VIX, SVXY) — DRAFTED
  - 2편: 변동성 타겟 전략 (IVTS, VolVol, 듀얼 모멘텀, LRS, 볼볼 무한매수법) — DRAFTED, 12 diagrams
- Series 3: "옵션과 변동성" (중급, 미국 증권사 필요)
  - 1편: 옵션의 본질 (moneyness, time decay, 만기일 역설) — DRAFTED

**Key Decisions:**
- Separated series because Korean brokers don't allow option selling or VIX options
- VIX long products (VIXY/UVXY) structurally fail due to contango — explicit warning added
- Option P&L should show time-evolving curves, NOT expiry hockey-stick diagrams
- Expiry = giving up time edge (개인투자자의 가장 큰 엣지를 스스로 포기)

**Notes for Next Session:**
- Series 2 Part 2 needs beginner-friendly simplification pass
- All 3 new articles need Excalidraw diagrams created (use excalidraw skill)
- PDF generation for new articles not yet done
- Memory files updated: series plan, VIX hedge reality, option P&L philosophy, VIX long decay

## 2026-04-04 (Session 2)

### Session: Full Editorial Review + Kmong Prep

**Series 1 Editorial Overhaul:**
- 1편: AI 섹션 삭제, 파론도 역설 70줄→15줄 축소, "=리밸런싱" 등식 제거, L118 중복 제거
- 2편: 변경 없음 (목차만 업데이트)
- 3편: "살아남기" 도입부 회수, 마틴게일 30줄→13줄 축소, f*=0.5 유도 추가, 결론→4편 예고로 교체
- 4편: 제목 변경 "엣지 없는 게임, 엣지 있는 시장"

**Series 2-3 Editorial:**
- "이전 시리즈(변동성, 기하 평균, 그리고 켈리)" 역참조 21회→~10회 축약
- S2-2편: VolVol 신호 규칙 간소화, VIX 경고 49줄→8줄
- S3-1편: "5편" 번호 혼란 수정, S2→S3 전환 문구 수정
- S3-2편: TQQQ 스왑 파이낸싱 비용 추가(~11-13%), "만기일 역설" 중복 제거
- 코드블록 비교표 3개 → 마크다운 테이블로 변환 (GulimChe 정렬 문제)

**Consistency Fixes (beginner+editor review):**
- "캘리/켈리" 혼용 → 전체 "캘리"로 통일 (4편, 5편)
- "WVF" 미정의 용어 삭제 (6편)
- "꼬리 위험" 잘못된 시리즈 참조 수정 (7편)
- "기억하시나요?" 패턴 제거 (8편)
- Stutzer "34% 수익률" → "누적 +34%"로 명시 (1편)

**Series Renaming:**
- "변동성, 기하 평균, 그리고 켈리" → "원칙편: 왜 변동성이 돈이 되는가"
- "변동성을 다루는 도구들" → "실행편: VIX를 읽고 비중을 조절하라"
- "옵션과 변동성" → "확장편: 옵션으로 한 단계 더"
- 8개 파일 전체에서 YAML, TOC, 본문 참조 일괄 변경

**VolVol Google Sheets → Excalidraw:**
- S2-2편 구글 시트 링크 제거, VolVol 로직 플로차트(Excalidraw) 생성
- 화살표 타겟 검증 후 수정 (calc→MA 분기 화살표)

**PDF Pipeline Update:**
- generate_pdfs.py: 시리즈별 합본 3개로 분리 (series1_principles, series2_execution, series3_options)
- 기존 full_series_combined.pdf 대신 시리즈별 독립 합본
- 시리즈별 커버, 목차, 면책조항 자동 생성
- CSS 헤더 하드코딩 시리즈명 제거

**Kmong Listing Prep:**
- 상품 설명 4개 작성 (listing_series1~3.md, listing_bundle.md)
- 썸네일 4개 제작 (Excalidraw, 시리즈별 색상 코드: 파랑/초록/보라/금색)
- 가격: 원칙편 9,900원, 실행편 6,900원, 확장편 6,900원, 번들 16,900원
- 크몽 등록 가이드 + 이메일 드래프트 작성 (kmong/ 폴더)

**Memory Updates:**
- feedback_excalidraw_centering.md → feedback_excalidraw_rendering_rules.md (화살표 타겟 검증 추가)

**Notes for Next Session:**
- 감마 익스포져 시리즈 리라이트 (4편: 감마 스퀴즈, GEX 기초 1/2, 0DTE SPX)
- 크몽 등록 대기 (와이프 계좌 — 회원가입/전문가등록 요청 이메일 발송 완료)
- 시리즈 추가 수정 후 최종 PDF 재생성 필요

## 2026-04-04 (Session 1)

### Session: Excalidraw Diagrams + Series 2-3 Polish + Part 8

**Excalidraw Diagrams (32 new):**
- Series 2 Part 1 (6): 서울vs제주 분포, HV vs IV, VIX 온도계, SVXY 붕괴, 변동성의 두 얼굴, 시리즈 연결도
- Series 2 Part 2 (12): 변동성-기대수익, 변동성 타겟팅, 역변동성 가중, IVTS 세 구역, VolVol, 볼볼 무한매수법, Vomma Zone, 듀얼 모멘텀, LRS, VIX 롱 하락, 신호 결합, ETF 조합
- Series 3 Part 1 (7): 옵션 4요소, Moneyness, OTM/ATM/ITM 전략, IV-프리미엄, 만기vs현재 P&L, 시간감쇠, 옵션 4역할
- Series 3 Part 2 (7): LEAP 비용구조, 델타-레버리지, TQQQ vs LEAP, Protective Put 타이밍, theta 관계, 시장별 전략조합, 시리즈 엣지 연결

**New Article: 8편 옵션 실전 — LEAP, 보험, 그리고 수확**
- LEAP Deep ITM 콜 = 저비용 레버리지 (변동성 드래그 없음, 파산 방지)
- Protective Put = VIX 낮을 때 사는 폭락 보험
- Covered Call = theta 수확 (커버드콜 ETF 대안 포함)
- 세 전략의 IVTS 구역별 조합

**Beginner-Friendliness Fixes (20 edits across 4 files):**
- 6편 VolVol 섹션: 이동평균/볼린저밴드/골든크로스 정의 추가
- 용어 정의: VIX3M, 상대/절대 모멘텀, 무한매수법, Vomma, delta, 내재가치
- Contango/Backwardation 호텔 예약 비유 추가
- 시리즈 참조 모호함 해결 (항상 시리즈 이름 명시)
- 8편 "최대 손실 무제한" 오류 수정 → "투자 원금"

**Duplicate Code Block Removal (12 blocks):**
- 5편 3개, 6편 6개, 7편 3개 — Excalidraw 다이어그램과 중복된 코드블록 삭제

**VIX Strategy Updates:**
- VIX 단독 매수 = 기우제 비유 추가 (시간감쇄 구조적 손실)
- VIX 활용 시 양동 전략(롱+숏) 필수 명시
- "VIX 양동 전략" 예고 삭제 → "LEAP, Protective Put, 커버드콜" 예고로 교체
- ZVOL vs SVOL 비교 리포트 작성 (pdfs/ZVOL_vs_SVOL_Report.md)

**PDF Generation:**
- 8개 개별 PDF + 합본 (5,707 KB) 재생성 완료
- generate_pdfs.py에 8편 추가, COVERS 업데이트

**Notes for Next Session:**
- ZVOL vs SVOL 시뮬레이션 대기 (user 검토 중)
- VIX 양동 전략 상세 (deep ITM $10-11 콜 + ZVOL DRIP) — 시뮬레이션 결과 후 결정
- 동적 헷지 아이디어 (IVTS Warning 시에만 VIX 콜) — user가 생각 중
- 5-7편에 standalone 시각적 코드블록 ~6개 Excalidraw 변환 미완료
