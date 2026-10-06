# SESSION HANDOFF — butterflow 블로그/네이버 발행 워크플로

> **세션 시작 시 이 문서를 먼저 읽으세요.** (또는 `/start-session` 스킬)
> 이 문서는 "지금 어디까지 됐고, 어떻게 발행하며, 무엇을 조심하나"를 담은 **살아있는 핸드오프**입니다.
> 세션 끝에 `/end-session` 스킬이 이 문서의 *현재 상태*와 체인지로그를 갱신합니다.
> **마지막 갱신:** 2026-10-06

---

## 1. 이 프로젝트가 뭔가

- **블로그:** butterflow 노트 — `https://butt2rflow.github.io` (MkDocs Material + GitHub Pages)
- **구조:** 한국어(기본)/영어 병행, `mkdocs-static-i18n` **suffix** 방식 (`name.ko.md` / `name.en.md`)
- **섹션(nav):** Home · **Investing**(투자 노트) · **Physical AI**(2026-10-03 순서: Start Here → Robot Vision → Cobots → Pendant to ROS 2 → Field Notes → Hands-on Notes → Physical AI Investing)
- **이 PC의 clone 경로:** `C:/Users/jae/Downloads/Blog`(문서의 `~/Documents/Blog`는 다른 PC 기준). `tools/r2pgen/lib.py`의 `OUT`이 아직 Documents 경로라 그림 생성기를 그대로 돌리면 실패한다. `lib.OUT`을 덮어쓰고 필요한 그림 함수만 호출할 것.
- **네이버 크로스포스트:** `blog.naver.com/bflownet` — Claude가 접근 못 함. 붙여넣기용 **패키지**만 준비.
- **콘텐츠 준비 프로젝트 루트:** `C:\Users\jae\Documents\Blog` (여기 `naver/`, `drafts/`, `tools/`, `.claude/`). 구 `butterflow-ssf` 작업폴더는 2026-09-27 이곳으로 병합됨 — 잔여물은 `_archive/2026-09-27_butterflow-ssf/`. **이 폴더가 블로그 저장소의 유일한 clone**(branch `main`) — 작업·빌드·배포 모두 여기서.

## 2. 저장소·위치

| 무엇 | 어디 |
|---|---|
| 블로그 저장소(정본) | `github.com/butt2rflow/butt2rflow.github.io`. **유일한 clone = `~/Documents/Blog`** (2026-09-27 통합; 구 `~/Documents/butt2rflow.github.io`는 `.RETIRED-2026-09-27`로 은퇴). **스크래치패드 clone 새로 만들지 말 것** — drift(stale-clone 함정) 원인. 메모리 `butt2rflow-push-auth` #5. |
| 본문 | 저장소 `docs/posts/<slug>.ko.md` / `.en.md` |
| 그림(한/영) | `docs/assets/diagrams/` (KO) · `docs/assets/diagrams_en/` (EN) |
| nav | 저장소 `mkdocs.yml` |
| 네이버 패키지 | `<project>/naver/<slug>/` (txt + PNG + 배너 + UPLOAD.md) |

## 3. 발행 파이프라인 (블로그)

1. 본문/그림/nav 편집 (`~/Documents/Blog` 안에서, `main` 브랜치)
2. **점검:** 볼드 `**` 짝수, 이미지 참조가 실제 파일과 일치, 내부 `.md` 링크 타깃 존재
3. `git add` (해당 파일만) → commit → **push**
   - ⚠️ **인증 함정:** 기본 gh 계정 `416Jae`는 쓰기 권한 없음(403). **active 계정이 `butt2rflow`여야** 하고, push는 자격증명 오버라이드로:
     ```
     git -c credential.helper= -c credential.helper='!gh auth git-credential' \
         -c credential.https://github.com.username=butt2rflow push origin main
     ```
   - 메모리 `butt2rflow-push-auth` 참고.
   - ⚠️ **push 전 clone 최신 확인:** `git fetch origin` → `git rev-list --left-right --count origin/main...HEAD` → 어긋나면 `git rebase origin/main`(자동커밋 워크플로가 main을 움직여 non-fast-forward가 잦음). clone은 하나뿐이어도 CI 자동커밋(VIX 스냅샷 등) 때문에 origin/main이 계속 앞서 나감 → 매번 fetch+rebase.
4. **게이트:** GitHub Actions **"Deploy MkDocs"** 가 `mkdocs build --strict` 수행 → 실패 시 링크/이미지/nav 오류. `gh run watch <id> --exit-status`로 확인.
5. gh-pages 빌드 `built` 대기 → **검증:** `curl` 200 + 라이브 내용 grep (핵심 문구/그림 임베드).

## 4. 네이버 패키지 파이프라인

- **그림 → PNG:** 네이버는 SVG 불가. 래퍼 HTML + headless Chrome `--force-device-scale-factor=2` 로 2× PNG. (라이트 카드 배경 포함, 배너만 다크)
- **본문 → 평문 txt:** 마크다운 0. `##`→`■`, `###`→`▸`, 표→들여쓴 평문, `![]()`→`[이미지 삽입: name.png — 캡션]`, `[text](url)`→평문, `**`·백틱 제거.
- **대표 이미지:** 세로 배너(680×900 SVG → 1360×1800 PNG), 다크 카드 + 훅.
- **canonical:** 네이버 불가 → 하단 "원문은 위 블로그에" + 원문 URL + 고지 유지.
- **UPLOAD.md:** 이미지 배치표 + 절차. 메모리 `naver-publishing` 참고.
- 발행 후 URL은 메모리 `naver-published-urls`에 기록. **URL 확보법:** 네이버 본체·RSS 모두 WebFetch 차단 → 사용자가 브라우저로 `rss.blog.naver.com/bflownet.xml` 열어 내용을 붙여 주면 `<guid>`에서 logNo 추출(한 번에 최근 글 전체).

## 5. 컨벤션·주의

- **그림 SVG:** `viewBox="0 0 680 H"`, 라이트 카드 `fill="#FAF8F2"`. ⚠️ **CSS class `fill`이 inline `fill=` 속성을 덮음** → 색/흰 글씨는 반드시 `style="fill:..."`(inline style)로. KO는 `../assets/diagrams/`, EN은 `../assets/diagrams_en/` 참조.
- **리뷰 게이트(글 품질) — 매 글 5게이트 (2026-09-09 확정):** ① **저작권**/상표·고지 ② **팩트체크**(1차 출처) ③ **사람이 쓴 느낌(de-AI)** — 스타카토 헤지문("미검증. 회의적으로 다루거나…" 류)·과잉 수식어·기계적 3부 병렬·throat-clearing("간단히 말하면") 색출 → 손수 쓴 문장으로 ④ **페르소나**(수학 싫어하는 30대 — 비유 먼저, 전문용어 글로스, **네이티브 한국어(기계번역 금지)**) ⑤ **최종 편집**. 시리즈는 **트릴로지-호(arc) 리뷰**(편 간 일관성·용어·전방링크·중복)도. 게이트는 `git diff`로 변경분만 보게 하면 효율적.
- **용어:** 잇다→**연결하다**, 인컴번트→**기존 강자**, "누르는 쪽"→**"눌리는 쪽"**, FANUC→**화낙(FANUC)**. **돌다(소프트웨어·하드웨어가 "돈다/작동한다" 뜻)→동작하다** (돕니다→동작합니다, 돈다→동작한다, 도는→동작하는, 돌아가다·돌기→동작하다). **타동사 "프로그램·모델을 돌리다"→실행하다** (동작하다는 목적어를 못 받음). ⚠️ **회전(frames "원점을 중심으로 돈다"·감속기가 "돌아가고")·복귀("되돌아가다"·"복리로 돌아가다")·자세("어떻게 돌아가 있나")·후보 렌더링("다 돌려보다")은 그대로 둘 것**. 금융 글은 스코프 밖. (2026-09-18 로봇 글 전체 2패스 적용·발행 완료.)
- **Physical AI 용어·링크 규칙(2026-10-03):** 자세(포즈 아님), 점구름(포인트 클라우드·점군·점 구름 아님), Jetson(젯슨 아님).
- **세 설계 이름(2026-10-03, 사용자):** "Track 0/A/B" 금지(공식 용어 아님, 혼란). **기하 방식 / 신경망 인식 / 학습 정책**(EN geometry / neural perception / learned policy). 허브 글 요약·용어 설명과 코스에는 '공식 용어 아님' 해명 대신 업계 용어(고전적·모델 기반 / 모듈형 파이프라인 / end-to-end 학습)와 한 번 연결(10-04, 블로그 `9d98425`, 코스 `4a8eb71`, 아티팩트 v26). 학습 정책 글 주소 `learned-policy-track-b`는 링크 보존용으로 유지. 블로그 `63f783e`(글 9개, 그림 13종, 네이버 패키지 7개), 코스 `358efd1`(아티팩트 v25). 다른 글을 가리킬 때는 "펜던트에서 ROS 2로 N부", "현장 노트 N부"(정정편·튜닝편·스캔편·모션편·실물편), "Physical AI 투자 N부". 로봇 비전 7편은 이전/다음 줄로 이어져 있고 stereo·frames는 "기본편 1·2부". 새 글을 넣으면 시작하기 글의 지도 표와 `cpa-map` 그림, 홈 한/영 목록(그룹 제목 아래)도 함께 고칠 것. 옛 글 제목의 "A — B" 꼴은 쓰지 않는다.
- **시각·예시 중심(2026-09-18 확정):** 글·코스 모듈은 **개념마다 그림 1 + 워크드 예시 1**을 기본으로 — 텍스트 벽 지양. 메모리 `prefer-visual-heavy`.
- **🔒 기밀:** Physical AI 글은 고객 업무와 얽힌 vault에서 재료를 끌어옴 — **고객사명·고객 응용(라인/제품)·고객 제공 장비 등 특정 식별 정보는 절대 미발행**. 일반적 하드웨어·버전·명령·함정만 사용. 세부 경계는 로컬 메모리 `physical-ai-vault-confidentiality` 참고.

## 6. 현재 상태 (published, live)

- **🖥️ 홈 대시보드 2존 재편 완료(2026-09-09):** "돗데기 시장" → **오늘의 결정 / 시장 신호 한눈에** 2존 + 지표 **8종**(+ **GEX 딜러 감마 레짐** 타일, Yahoo SPY 옵션 라이브 계산) 반응형 그리드 + 차트 접이식(한/영). `update_dashboard.py`(deploy 시 CI 재생성) + `custom.css`. 상세·crumb 함정은 메모리 `home-dashboard-layout`.
- **Investing:** SSF 재출시 · MOVE · CDS · (+ 기존 대시보드/시리즈)
- **Investing › GEX/옵션 시장구조:** `gex-calculator`(보강: 잔물결/파도 섹션) · `gex-0dte-patterns` · **`vanna-charm`(신규 후속편)** · `volatility-dashboard` (Tools 체인 순서: …→gex-0dte→**vanna-charm**→volatility-dashboard)
- **Physical AI › Robot Vision:** 본편 `stereo-to-grasp`, `frames-transforms` + **심화 2부작(2026-09-17):** `inside-the-models`(심화1부·개념) · `model-anatomy`(심화2부·구조) + **`robot-simulation`(2026-09-18 신규 — 시뮬레이션·sim-to-real·도메인 랜덤화, 그림 5종 rvd-sim*, 한/영, 라이브)**. 그림 `rvd*` KO/EN 1:1. (이 글은 Physical-AI 로봇 코스 Unit 2의 dual-use 발행본 — 코스는 `~/Documents/physical-ai-course`로 분리, §8.)
- **Physical AI › Cobots (2부작):** `cobot-basics`(1부) · `cobot-ur-vs-fanuc`(2부). `cobot-investing`은 Physical AI 투자 1편.
- **Physical AI › Field Notes (2부작 + 정정편):** `jetson-ros2-setup`(1 — Jetson·ROS 2) · `jetson-isaac-foundation-models`(2 — Isaac ROS·파운데이션 모델) + **`jetson-foundationpose-16gb`(정정편, 2026-09-20 (2) 신규·라이브)** — 2부의 "16GB 불가·AGX 64GB 필요" 결론을 뒤집음(보드 비우기+워크스페이스 캡+optLevel로 엔진 빌드/구동, 피크 ~6.2GB). 히어로 터미널 캡처(사용자 제공) + recipe 그림. 커밋 `ffc29cb`, CI strict green, 라이브 200. **네이버 스킵.** (1·2부는 2부작 유지 — renumber 안 함.) **2026-09-18 편집(1·2부 라이브):** 용어 돌다→동작/실행 · 드릴→전동드릴 · 보드→엣지 컴퓨터 · 톤 3게이트 · 3패널 깊이 그림 · `hw-tiers` 문구.
- **모션편 3단계 갱신(2026-10-03, `63f783e`):** 「자세를 목표로 바꾸기」가 같은 장면의 카메라 칩 깊이 vs ESS 깊이 비교 사진(`jetson-motion-pose-depth-compare-{ko,en}.jpg`)으로 바뀜. 미니 PC 0.88→0.92, 마우스 0.66→0.87, ESS 목표로 가상 UR20 재실행(0.1 mm 안). 9월 30일 FS 사진은 앞 절로 복귀. 그 전 커밋 `d9668e5`(FS 사진 임시 교체)는 이것으로 대체됨.
- **현장 노트 8부 시뮬레이터편(2026-10-03, `08c8273`, 라이브):** `jetson-ursim-planners` — URSim 두 대(UR12e PS5, UR20 PSX)로 cuMotion·Pilz·OMPL 비교, OMPL 손목 510°, 바닥 함정, 연결 함정. 네이버 패키지 없음(요청 시). **10-04 보강:** Lichtblick 절(캡처 포함)·'보기만'은 브리지에서, 'OMPL 다음이 더 문제였다'(Pilz PTP 홈, UR20 OMPL 기본 제외), 데모 7단계, production 주의(재시작은 R&D용, 장시간 시험 미실시). 실습 노트 0부 'URSim은 x86 리눅스용' 보충. 한국어 전면 다듬기(`8874865`), URSim vs Isaac Sim 단락(`140ef3c`).
- **현장 노트 Isaac Sim편(2026-10-04, `16efb72`, 라이브):** `isaac-sim-pc-and-cloud` — 시뮬레이터편 다음. 집 RTX 3090 vs 클라우드 L4, UR20 바닥 함정, SIL 토픽, 합성 데이터 누수. 그림 `r9-*`(`figs_r9.py`), 사진 `isaac-sdg-quad.jpg`·`isaac-cloud-stream.jpg`. 원자료 `~/Documents/issac-sim`. 네이버 패키지 없음. 다음 글 후보: Jetson 쪽 SIL(실제 보정값, 토픽 연결, cuMotion으로 가상 UR20).
- **현장 노트 메모리편(2026-10-05, `d2de00c`, 라이브):** `jetson-memory-budget` — Isaac Sim편 다음. 인식+모션을 16 GB Orin NX 한 대에: 모션만 7.6시간, 계속 추적 26분·설정 줄여 1시간 10분(메모리를 채운 건 cuMotion이 아니라 인식 쪽), 사이클마다 자세 한 번은 24시간 완료(아래 10-06). 그림 `r10-*`(`figs_r10.py`). 시뮬레이터편 장시간 시험 절도 최종값으로 갱신(`5aee1cc`). **10-05 밤 정정(`f261cfc`):** 'cuMotion이 아낀 1.3 GB를 FoundationPose가 먹었다'는 틀림(인식과 함께면 cuMotion 기본 설정도 2.0~2.55 GB). Docker 컨테이너 숫자는 Jetson에서 부풀려짐(FoundationPose nvmap 4.08 GB 평평, 그래도 Docker +1 GB당 남은 메모리 약 −0.5 GB). 글 상단에 고침 안내. '경로 없음' 최종값: 모션만 8.4%, 설정 줄임 24%. **10-06 24시간 최종(`e735f96`):** 원본 CSV로 재계산 — 자세 2,398/2,399, 남은 메모리 최저 1.18 GB(멈춤 기준까지 0.2 GB 미만 → 실제 셀은 AGX Orin 32 GB 권장), 모션 95.8%(정전·이전 제외 96.2%), '경로 없음' 16%(모션만 8%와 같은 기본 cuMotion 설정 — 설정 탓 아님을 본문에 명시), 드라이버 재시작 4번, C403 0번. 8.5시간째 소등 후 15.5시간 어둠에서도 자세 1,538/1,538 → '조명만으로는 설명 안 됨'(통제 비교는 아님). 그림 `r10-runs`(0~24시간, 밝음/어두움)·`r10-budget`(가장 빠듯한 순간), 시뮬레이터편 표·정리도 갱신. 같은 날 `c41f8ee`: 고침/덧붙임 안내를 없애고 처음부터 쓴 글로 정리, 날짜 2026-10-06.
- **Physical AI 로봇 코스:** 별도 폴더 `~/Documents/physical-ai-course`로 분리(§8). butterflow엔 Unit 2 dual-use 발행본 `robot-simulation`만 남음.
- **Physical AI › Pendant to ROS 2 (4부작 완결, 2026-09-28 라이브):** `ros2-for-robot-programmers`(1 — ROS 2 그래프) · `ros2-robot-description`(2 — URDF·TF2·ros2_control·RViz) · `moveit2-goals-not-points`(3 — MoveIt 2) · `isaac-ros-gpu`(4 — Isaac ROS·cuMotion). TP/URScript 프로그래머 대상, 한/영, 편당 그림 9개. 첫 발행 `07b400f`, 결정론 개정 `cc896aa`. 개정 내용: 움직임은 공차 누적에 맞추고, 판정은 기존 결정론적 하드웨어가 맡는다. 자동화 사다리, 관문, CAD vs 실측도 추가. 5게이트 + 최종편집 통과. 그림 생성기 `Blog/tools/r2pgen/`. 메모리 `pendant-to-ros2-series`. **네이버 미발행.**
- **Physical AI › Start Here (2026-09-28 라이브):** `choosing-physical-ai`(한/영, 그림 10개 `cpa-*`, 생성기 `tools/r2pgen/figs_cpa.py`). 개념 다리 글. Track 0·A·B를 한 축에 놓고 계단, 손익분기, 하이브리드, 조용한 실패, 인수 기준을 다룬다. 끝에 기존 글 지도 표가 있다. 커밋 `217831d`. 시리즈 4편과 stereo-to-grasp에 역링크를 달았다. Track B 전용 글은 '예정'으로 표시. 2026-09-28 `9f8f0fe`: 30초 요약·용어에 Track 0·A·B 이름 뜻 추가(0=인식은 하되 신경망 없는 기준선, A·B=신경망을 쓰는 두 갈래).
- **Start Here 추가 (2026-09-28):** `learned-policy-track-b`(Track B 전용, `6cf7461`).
- **Physical AI 투자 2편 (2026-09-28 라이브, `8d5f1dd`):** `physical-ai-investing-actuators`(관절 하나로 보는 가치 이동·감속기 vs QDD·희토류·ETF 4종, 그림 10개 `inv2-*`, `figs_inv2.py`). nav는 Cobots의 cobot-investing 다음. cobot-investing에 후속편 링크.
- **Physical AI 투자 카테고리 신설 (2026-09-28, `eb5799c`):** nav에 Physical AI › "Physical AI Investing / Physical AI 투자"를 만들어 1편 `cobot-investing`(코봇 3부 겸 투자 1편), 2편 `physical-ai-investing-actuators`, 3편 `physical-ai-investing-power`를 넣음. Cobots 카테고리에는 basics와 ur-vs-fanuc만 남음. 홈 Physical AI 목록도 갱신(시작하기, 펜던트 1~4, 실습 0, 투자 1~3).
- **Physical AI 투자 3편 (2026-09-28 라이브, `f4a9921`):** `physical-ai-investing-power`(휴머노이드 전력 문제: 가동 시간, 무게 악순환, 가동률, 셀 공급, 원자로·원자력 전지가 답이 아닌 이유, 아톰·Nucleon·화성 RTG 에피소드, 직접/간접 테마). 그림 10개 `inv3-*`, `figs_inv3.py`. 5게이트 통과. 배터리 원자재 중국 의존도 섹션 추가(`1861ed4`).
- **Hands-on Notes / 실습 노트 (2026-09-28, 0편 라이브):** `learn-without-industrial-robot`(SO-101 vs URSim/ROBOGUIDE 연습장 계획 글, 그림 8개 `hon-*`, `figs_hon.py`). 1~6편은 실제로 해 본 뒤 작성. 개념 글 5편 관련 줄에 '직접 해 보기' 링크. 메모리 `hands-on-notes-and-investing-2`.
- **왼쪽 메뉴 정리·라이브 시세 제거 (2026-09-28, `90c7f3d`):** `hooks/nav_titles.py`로 메뉴 라벨을 짧게(front matter `nav_title` 우선, 없으면 제목의 " — " 앞부분). 시리즈 글은 "1부 · …" 라벨. 섹션 제목은 강조 띠, 하위 글은 들여쓰기(custom.css). 홈 TradingView 라이브 시세 위젯 삭제. 그 자리에 빌드 때 자동 생성되는 '최근 글 5편(섹션당 1편, 섹션·날짜 표시) + 카테고리' 사이드바(`hooks/home_sidebar.py` + `assets/home-sidebar.js`, `fab9d33`). 새 시리즈 글에는 nav_title을 꼭 넣을 것.
- **새 글 `camera-placement` (2026-09-28 라이브, `5bab7dd`):** "카메라는 몇 대, 어디에" — 설계도/카메라/안전장치 3분류, 손목 하나 기본, 오버헤드 4가지 경우, 유령 장애물, 오버헤드 3역할, Vention GRIIP 공개 웨비나 사례. 그림 7개 `cam-*`(`figs_cam.py`). 메뉴 로봇 비전. 메모리 `camera-placement-post`.
- **0DTE 타일 개편 (2026-09-28, `17fb2cf`·`d4aa8fe`):** 장외엔 마지막 장중 값(ET 시각 표시), 장중 추이 차트, 다음 정규장 예상(전일 OI, 개장 갭 ±2% 시나리오), cron :23, DST 반영. `d4aa8fe`는 이 작업이 낸 배포 장애(로컬 import shutil) 수정.
- **한국어 번역투 일괄 정리 (2026-09-28, `e818962`):** 세션 글 10편+그림 64곳. "크게 멈춘다"→"멈추고 알린다", "조용한 ↔ 드러나는 실패"로 통일. 리뷰 게이트에 번역투 전용 점검 추가(메모리 `review-gates`).
- **Cobots 2부작으로 정리 (2026-09-28, `d7db694`):** `cobot-investing`이 Physical AI 투자 카테고리로 간 뒤 남아 있던 "3부작" 표기 전부 제거. 1·2부에 시리즈 이전/다음 줄 추가, 2부 → 투자 1편으로 이어짐. 다시는 3부작이라 부르지 말 것.
- **현장 노트 실측 캡처 반영 (2026-09-28, `c697ed1`):** 사용자 OAK-D S2 + Orin NX 실측 팩으로 2부의 시뮬레이션 깊이 그림 교체 + 체커보드 정확도 표, 16GB 정정편에 실제 개방어휘 체인(Grounding DINO tiny → SAM2.1 → FoundationStereo → 3D). 책상 장면만 사용(현장 장면엔 좌석 = 고객 부품).
- **Physical AI 전체 편집 리뷰 (2026-09-28, `775dff4`):** 21편, 한국어 약 300곳 번역투 정리(대시 삽입구, 콜론 제목, 무너지다·돌다 오용, 캡션 반복). 코봇 글의 남은 "3부" 표기 제거. 현장 노트 메뉴를 1편·2편 → 1부·2부로 맞춤. 2부 첫머리에 정정편 링크 안내 추가. 사실·숫자·링크·alt는 스크립트로 불변 확인. 메모리 `review-gates`.
- **현장 노트 실측 캡처 추가 (2026-09-28, `8cda26b`):** 2부에 유리 옆판 PC 깊이 비교(내장 블록 매칭은 유리 너머 일부, FoundationStereo는 유리를 평면으로 봄; 벽 "L8" 표시 흐림 처리), 16GB 정정편에 3D 점 구름 3단 그림(XYZ·깊이+마스크·점 구름).
- **16GB 정정편 FoundationPose 실측 (2026-09-28, `9ca10f4`→`68685c5`):** 글자 지시→검출→마스크→깊이→6-DoF 자세 전체 체인. 처음 올린 자세 그림은 180° 뒤집힌 결과(색 없는 CAD)여서 교체. 현재: 첫 자세 1.8초, 추적 ~70ms, IoU 0.92, 반복 0.94mm/0.48°, 방향 교훈 그림, 전체 체인 11.4→4.3초 그림, NanoOWL vs Grounding DINO 비교. "J4012" 표기는 잘라 냄. 30초 요약에도 실측 줄 추가(`894b02c`). 코스도 같은 숫자로 갱신(코스 `5373427`).
- **현장 노트 4·5부 신규 (2026-09-29, 라이브):** 현장 노트는 이제 1·2부 + 정정편 + **튜닝편** + **스캔편**.
  - **`jetson-tuning-licensing`(튜닝편, `d0200e9`·`b11fed6`):**
    - 속도: 11.4→4.0초, 단계별 표, TensorRT 전후 답 비교(SAM2 디코더 TRT 10.3 합치기 버그, 틀린 TAO 체크포인트)
    - 대안: ESS 2.1초, YOLO-World 1.66초(연구용), 고정 상자 1.52초
    - 라이선스: 연구용/상업용 지도(NVLabs 비상업, NGC ESS·FoundationPose 상업 가능, GDINO·SAM2 Apache, YOLO-World GPL/AGPL)
    - 상업용 체인 3.26초·추적 34ms, 가림 시험·손 시험, 크기 검사(난방기 오검출)
    - 반짝이는 부품 거울 컵 시험(`jetson-mirror-cup.jpg`), 후보 줄이기 실패
  - **`jetson-scan-no-cad`(스캔편):**
    - 인쇄용 ChArUco 보드 내려받기(`assets/downloads/charuco-scan-board-letter.svg`), 자동 촬영, 깊이 안에서 보드 평면 재맞춤
    - 높이 지도 메시(4.5초, 100×66 vs 실물 100×62), 스캔 메시로 라이브 추적
    - BundleSDF 비교, 뒤집힘 한계, 1080p K 자르기 함정(5.6%)과 정렬 1.9px
    - **함정 3 자동 초점 추가(`f0f52fb`):** 컬러 초점 거리가 17cm에서 +3.3%, 44cm에서 0.2%. 고정 초점 수동 설정은 가까이서 흐려져 답이 아님. 카메라별 보정표로 1.4→0.24%. 그림 `jetson-af-focal-shift.jpg`·`jetson-af-sharpness.jpg`. 보정표 JSON은 카메라 일련번호가 파일명에 있어 미공개.
  - 마우스 로고는 흐림 처리하고 모델명은 쓰지 않음. 튜닝편→스캔편 다음 글 링크 있음.
  - 정정편 속도 4.1→4.0초로 맞춤.
  - 스캔편 보드 인쇄 메모(`6af3cc8`): 정확히 100%로 인쇄된 앱은 Inkscape뿐이었다(사용자 경험).
  - **최종 편집·교차 참조(`e6aa3bd`):**
    - 현장 노트 5편 전부에 시리즈 이전/다음 줄, "2부작" 표기 제거
    - 홈 목록에 튜닝편·스캔편
    - 튜닝편·스캔편 한국어 편집(돌리다→실행하다 등)
    - 사이트 전체 링크·이미지 점검 통과(CI 생성 PNG 5개 제외)
  - **네이버 미발행.**
- **2026-09-29 (2) 수정 (라이브):**
  - `camera-placement`: "빈 영역 관문"→"빈 공간 확인", "빈 1/2/3"→"부품 통"(`d2e62bc`)
  - 투자 1~3편과 실습 0편의 번호를 "N부"로 통일(`d2e62bc`). 이제 번호 붙은 시리즈는 모두 "N부"다.
  - 투자 2부에 QDD 쪽 종목과 밸류에이션(ALNT·RRX·MP), Unitree·Agility·국내 기업(`063ed8c`)
  - 투자 3부에 수출 통제 연장(2027-01-10, 배터리 소재 미확인), 원자력 밸류에이션(`5178c58`)
  - 투자 1부 P/E 갱신(최근 12개월/향후), Unitree +460%, Agility SPAC(`0ca9ae3`)
  - 1~3부 주가는 모두 2026-09-29 종가 기준
- **2026-10-03 (라이브):**
  - **Physical AI 26편 교차 편집(`5ee26e6`):** 메뉴 순서 변경, 홈 목록 재편(+카메라 글 2편), 시작하기 지도 표 26편, 로봇 비전 이전/다음 줄, 글 사이 모순 정정(실습 0부 PolyScope X URSim은 Orin에서 안 됨, "카메라를 가까이"의 한계, 2부 64GB 안내), 실측 결과를 개념 글에 교차 링크, 용어 통일, 옛 글 대시 제목 약 70곳. 상세는 체인지로그 2026-10-03.
  - **모션편 오버레이(`befc956`→`3982a06`):** 캡션 과장 정정 후 원인 실측. bag의 좌우 영상 20장으로 FS·ESS 깊이 → 같은 nvblox 설정 → 보드 덮음 칩 67% / FS 97% / ESS 96%. 그림 `jetson-motion-map-dense.jpg`. Jetson 쪽 스크립트·결과는 `~/workspaces/fp_buckle/dense/`(dense_extract → dense_depth[fpb-run, 데모 멈춤 필요] → dense_maps.sh[cumotion-nvblox] → overlay는 이 PC 스크래치패드에서). 데모는 `~/start_foundation_demo.sh`로 재시작(사용자 허락받고 멈췄음).
  - `cpa-map` 그림 갱신, 정정편 메모리 7.2→7.7GB(사용자: 최악값 사용), 시뮬레이션 글에 UR 모델도 무료.
  - 네이버 패키지 21개 로컬 재생성(아래 대기 항목 참고).
- **2026-10-02 (라이브):**
  - **현장 노트 6부 모션편 `jetson-pose-to-motion`:** 다른 세션이 아침에 "라이브 지도 첫 시도 실패"로 발행(`7eccee0`) → 같은 날 바로잡음(`5787857`): 실패는 검사 스크립트 문제(삼각형 면을 빼고 꼭짓점만 그림), 라이브 nvblox 중앙값 5 mm. 새 절: ROS bag 녹화, 지도 → cuMotion(`NO_IK_SOLUTION` 함정), 자세가 알려 주는 것(가려진 모서리 CAD 56 mm vs 자 55 mm). 실제 장면 사진 5장(bag 컬러, 지도 겹침, 목표 표시, 자세+CAD, 모서리 거리). 사용자 지적으로 한국어 다듬기(`d9aca08`). 그림 `mot-check`·`mot-planmap` 신규, `mot-carving` 삭제.
  - **현장 노트 7부 실물편 `jetson-real-robot-first-move` (신규, `3d739c0`):** 마침 쉬고 있던 UR20(PolyScope X)에 Orin NX를 연결해 처음 움직인 기록. 읽기만 → 공장 보정 3.95→0.06 mm → 손목 ±5° → cuMotion 계획 움직임(목표에서 0.1 mm). 함정(드라이버만 업그레이드하면 ABI 충돌, 슬라이더 시간 늘어남, cuMotion 기본 바닥), 안전 절차. 그림 `r7-*`(`figs_r7.py`). **UR20 모델명은 사용자 허락으로 표기**(IP·공장 사진·회사 맥락은 계속 제외).
  - **모션편 보강(같은 커밋):** 「자세를 목표로 바꾸기」(잰 카메라 위치, 뒤집힌 마우스), 「UR20용 cuMotion 설정 만들기」(구 71개), 「자세가 먼저 알려 주는 것」(가려진 모서리 56 mm vs 자 55 mm, `d9aca08`). 현장 노트는 이제 7부.
  - **현장 노트 2부:** 옛 데모 사진(브랜드 많은 책상) 2장을 9월 30일 미니 PC 장면으로 교체, 기존 깊이 비교 그림의 마우스 로고 흐림.
  - **코스:** M8 확장 실습이 모션편을 인용(`7405f03`, 아티팩트 v24).
  - **Jetson 접근:** 이 노트북에서 `ssh fos@192.168.1.183`(설정 항목 없이 키로 접속). 데모 서버(`fpb-run`, 카메라 점유)는 사용자 허락 없이 멈추지 말 것.
- **2026-09-30 (라이브):**
  - **새 글 `depth-camera-selection`「어떤 3D 카메라를」(한/영, `0f16645`, 데이터시트 정정 `afad402`, 제목·용어 "깊이 카메라"→"3D 카메라" `31b2eec`):** 로봇 비전, camera-placement 다음. 그림 5개 `dcs-*`(`figs_dcs.py`). Gemini 305 수치는 데이터시트 V1.0 기준(±1.8%, 같은 센서, 최소 거리는 설정별 4~9cm, Box/Bulk). 메모리 `depth-camera-selection-post`.
  - 스캔편: 카메라 함정 수치를 "이 카메라 한 대"로 한정, "공장 보정 거리보다 가까이 가지 않기" 강조, 작업 거리 해결책 추가(`4f5a07a`·`487d4ca`). ROS 2 2부 초점 고정 문장 수정. 메모리 `hardware-findings-unit-specific`.
  - 산업 현장 적합성(`cd1ee97`): D405·D435는 방진 등급 없음, RealSense IP65 모델 D457은 최소 52cm라 오버헤드용, 손목 근거리 + 먼지·물 튐이면 305g, 세척 라인은 IP67.
  - Gemini 305g 데이터시트 V1.0 반영(`20127b2`): 별도 일체형 모델(FAKRA/SMB), 광학·성능은 305와 같음, 깊이 40mm(FAKRA 포함 약 53mm), USB-C는 평가용, 12V GMSL2, 드라이버는 Jetson AGX Orin 계열 개발 키트 기준.
  - 위 발견 사항(305/305g 데이터시트 정정, D457)을 회사 세션 fos-physical-ai-6c에 메시지로 보냄(공개 자료만, 회사 저장소는 손대지 않음).
  - 코스(비공개)도 같은 날 동기화: M5 신뢰 구간 실습, Gemini 305 부록, 데이터시트 정정, 산업 현장 메모, 305g 사실(아티팩트 v21).
  - **계정:** 이 폴더·블로그·코스는 모두 butterflow. gh는 butt2rflow로 둔다(416Jae로 되돌리지 않음). 두 저장소는 저장소 로컬 git 설정으로 butt2rflow 자격 증명에 고정돼 있어 `git push`만 하면 된다.
- **2026-10-01 (라이브):** ROS 2 4부 `isaac-ros-gpu`에 "cuMotion은 무엇을 피하나" 절과 그림 `r2p4-obstacles`(한/영, `3d4ef74`). 장애물 세 경로(nvblox 거리 지도 · 플래닝 씬 · XRDF 구/물체 부착)와 주의 네 가지.
- **작업폴더·clone 통합(2026-09-27):** `~/Documents/Blog` 하나로(구 butterflow-ssf·butt2rflow.github.io 은퇴). 로컬 빌드는 메모리 `blog-local-build`.

## 7. 대기 중 (pending)

- **모션편·3D 카메라 글 한국어 최종 확인:** 리뷰 게이트 서브에이전트는 안 돌렸다. 모션편은 10-02 저녁 사용자 지적 뒤 직접 다듬음. 사용자가 라이브 글을 읽고 확인할 것.
- **모션편 네이버 패키지:** 2026-10-03 생성(`naver/jetson-pose-to-motion/`, 이미지 16장 + 세로 배너, UPLOAD.md). 발행 전 — 발행하면 logNo를 `naver-published-urls` 메모리에 기록.
- **실물편 네이버 패키지:** 2026-10-03 생성(`naver/jetson-real-robot-first-move/`, 그림 4장 + 세로 배너, UPLOAD.md). 발행 전.
- **3D 카메라·투자 2부 네이버 패키지:** 아직 없음(만들려면 사용자 요청 후).
- **네이버 패키지 재생성분(2026-10-03):** 10-03 교차 편집으로 바뀐 20개 + 시뮬레이션 글을 다시 만들었다. 이미 발행한 `cobot-investing`·`jetson-isaac-foundation-models`·`jetson-ros2-setup`은 네이버 글을 고칠지 사용자 결정. 옛 `naver/stereo`·`naver/frames`는 10-03 오후 `naver/stereo-to-grasp`·`naver/frames-transforms`로 이름을 바꾸고 새 형식(정본 링크 꼬리말)으로 다시 만들었다(옛 판 백업은 세션 스크래치패드 `naver-backup/2026-10-03`). 둘 다 이미 발행된 글(09-19)이라 네이버 글을 고칠지는 사용자 결정. 같은 날 Track 개명으로 7개 패키지도 갱신.
- **ROS 2 1부 한/영 `**` 홀수:** 10-03 편집 전부터 있던 것, 라이브는 정상. 원인 찾아 고칠지는 선택.
- **영어판 문체:** 10-03 교차 편집은 영어에 구조·링크·사실만 반영했다. 영어 문체 리뷰는 안 함.
- **모션편 후속(선택):** nvblox `unobserved_esdf_policy`를 막힌 곳으로 둔 지도 비교, ESS 깊이 지도로 cuMotion 거부/통과 다시 재기. (자세 → 목표의 ESS 재실행은 10-03 완료.)
- ~~**메모리편·시뮬레이터편 — 사이클마다 자세 한 번 24시간 시험 최종값 반영**~~ — 10-06 `e735f96`으로 완료(§6).
- **spatial-vision-AI README의 'outran the ~1.3 GB cuMotion saving' 표현(회사 저장소, 이 세션은 안 고침):** 블로그에서 틀린 것으로 정정한 해석. 그쪽 세션/사용자가 고칠지 결정.
- **Lichtblick 카메라 토픽 시험:** 카메라를 로봇에 실제로 단 뒤에(사용자). fos-physical-AI `docs/lichtblick_camera_view_note.md`에 노트(브리지 허용 목록·압축·카메라 점유, 확인 항목, C# 앱 연동 3안, 공존 구성에서의 역할). fos 세션에 메시지 보내지 말 것. 결과가 좋으면 시뮬레이터편/모션편에 한 단락.
- **글감 후보: 펜던트 프로그램을 ROS로 번역하고 시뮬레이터로 검증(10-04 논의):** 노트는 fos-physical-AI `docs/pendant_to_ros_translation_note.md`. 회사에서 실제 프로그램 하나로 시범을 하면, 회사 프로그램을 뺀 일반화 버전을 펜던트에서 ROS 2로 시리즈나 현장 노트 글로.
- **코스 3단계·영업 자료(블로그 밖, 2026-10-04):** physical-ai-course `tiers/`, 브로셔 PDF, 피치 덱 EN/KO(비공개, 공유 완료). 상태와 미결 결정은 코스 저장소 `.claude/SESSION-HANDOFF.md` §7과 코스 메모리 `course-tiers-and-school-channel`.
- **회사 데모 덱(Zero-Shot v33/v34):** fos-physical-ai 세션이 10-03 갱신(work 계정, 10-09 회의용). butterflow 세션에서는 열 수 없음 — 덱 수정은 그 세션에서.
- **Isaac Sim편 리뷰:** 리뷰 게이트 서브에이전트는 안 돌림. 사용자가 라이브 한국어 글을 확인할 것. 네이버 패키지는 요청 시.
- **실물편 리뷰:** 리뷰 게이트 서브에이전트는 안 돌림. 사용자가 라이브 한국어 글을 확인할 것.
- **코스 M8에 실물편 인용(선택):** M8 확장 실습이 모션편만 인용 중. 실물편(실제 로봇 계단·보정·안전 절차)을 인용할지 사용자 결정.
- **실물편 다음 단계(원자료 쪽):** 카메라↔로봇 받침 보정, 파운데이션 모델 자세를 실제 로봇 목표로, 셀 모델, 접촉·힘. 진행되면 8부 후보.
- **모션편 3D 그림(선택):** nvblox 메시 + cuMotion 궤적을 RViz/Foxglove로 찍은 그림은 fos-physical-ai 세션에 "나중에, 원하면"으로 남겨 둠. 더 새 bag `~/bags/blog_2026-10-02`(15초)도 있음(유리 케이스 왼쪽 위 반사 확인 필요).
- **PiPER(AgileX) 도입 검토(코스, 결정 대기):** 지인에게 받을 가능성. 교육용으로는 SO-101 대체가 아니라 공용 6축 스테이션(Track A 심화), URSim은 산업용 다리(무료). 사용자가 코스에 넣을지 결정할 것(코스 핸드오프 참고).

- **리뷰 게이트 완료 (2026-10-01):** `depth-camera-selection`·튜닝편·스캔편·`isaac-ros-gpu` cuMotion 절에 서브에이전트 게이트를 돌려 반영(체인지로그 2026-10-01). **남은 확인 항목도 정리(같은 날 2차):** 54ms/34ms는 캡션으로 설명, 7.9GB 비교 삭제, 1.5°/1.4°는 모순 아님, 카메라 주장 2개 확인·53mm 삭제. 사용자가 라이브 글을 읽고 최종 확인할 것. 3D 카메라 글은 네이버 패키지 없음.
- **스캔편 후속 실험 후보 (2026-10-01 논의, 미착수):** ① 스캔 깊이를 NGC 상용판 FoundationStereo로 다시 재기(Isaac ROS 5.0 `isaac_ros_foundationstereo`는 JetPack 7.2 필요, 현재 Orin NX는 JetPack 6 → 업그레이드하거나 NGC 모델로 TensorRT 엔진 직접 빌드, 320×736이 16GB에 맞는지 확인). ② 높이 지도 대신 nvblox(GPU TSDF, Apache-2.0)로 메시 만들기: ChArUco 카메라 위치 + SAM2 마스크 깊이를 넣고 작은 복셀로. 아랫면·돌출부까지 담을 수 있지만 mm 복셀 품질은 미확인. 스캔편에 "nvblox도 후보" 한 줄 넣을지는 사용자 결정 대기. 메모리 `project_object_scan_followups`, 라이선스 표는 `reference_vision_model_licenses`.
- **네이버 패키지 3개 재생성 완료(2026-10-01):** `jetson-scan-no-cad`·`jetson-tuning-licensing`·`isaac-ros-gpu`를 정정 후 본문으로 다시 만들었다(`tools/naver_refresh.py`, 이제 이 PC에서도 동작). 코스(비공개 저장소)도 같은 정정을 반영했다(`aa3e21d`: 7.9GB 삭제, D405 325, SR PoE 297g, 53mm 삭제, IP69K, 335Lg 문구, 스캔 깊이 라이선스).
- **원자료 개념 문서의 옛 수치:** 새 글의 바탕이 된 업무용 개념 문서에는 Gemini 305 "≤1%"(실제는 공간 정밀도, 정확도는 ±1.8%)와 "최소 4cm"(근거리 설정일 때만)가 남아 있다. 회사 자료라 손대지 않았다. 고칠지는 사용자가 정할 것.
- **305g 호스트 확인 → 결론(2026-09-30):** Orbbec GMSL 드라이버는 NVIDIA 개발 키트만 지원, Seeed 일반 캐리어엔 GMSL2 없음, 로보틱스 캐리어 GMSL 보드는 드라이버 비공개. Seeed Orin NX라면 305g는 확인 불가 → USB 305 또는 OAK-D SR PoE. 블로그(`a6b654d`)·코스(`8126823`) 반영.
- **Gemini 305 구매:** Digi-Key CA Box(CAD 380.24, 케이블 포함)가 맞다. 받으면 스캔편·코스 M5 방식으로 특성 카드를 만들어 볼 것(렌즈 값, 정렬, 설정별 최소 거리).
- **Chrome 확장 미연결:** 2026-09-30 Amazon.ca 확인 때 확장이 연결되지 않았다. Claude 계정을 butterflow로 바꾼 뒤 확장 쪽 로그인 계정이 다를 수 있다.

- **네이버 패키지 18개 준비 완료, 업로드 대기 (2026-09-29).** `naver/<slug>/`에 txt·그림·세로 배너·UPLOAD.md가 있다.
  - 대상은 Physical AI 미발행분 전부다. 코봇 2편, 로봇 비전 심화·시뮬레이션·카메라 4편, 시작하기 2편, 펜던트→ROS 2 4편, 실습 0편, 투자 2·3편, 현장 노트 정정·튜닝·스캔편.
  - 투자 2·3편과 정정편은 오늘 문구로 다시 만들었다. 투자 고지와 기존 태그는 유지했다.
  - 권장 업로드 순서는 시리즈 순서다.
  - 발행 후 logNo를 받아 메모리 `naver-published-urls`에 기록할 것.
  - 빠진 것: 2026 투자 대시보드·도구 글(volatility-dashboard, vix-term-structure, cash-allocation)은 실시간 데이터라 네이버에 맞지 않아 뺐다. options-basics는 사용자에게 물어볼 것.
- ~~홈 KO 대시보드의 "프레임워크 설명" 링크 누락~~ → **문제 없음(2026-10-01 확인).** 라이브 한/영 대시보드의 내부 링크 대상이 같다. 차이는 커밋된 옛 `docs/index.en.md` 스냅샷(2026-05-11)에만 있고 CI가 배포 때 덮어쓴다. 커밋된 홈 파일로 판단하지 말고 라이브 페이지로 비교할 것.
- ~~블로그 체인지로그 커밋 여부~~ → **커밋하기로 결정(2026-09-29, `e233e31`).** 공개 저장소라 커밋 전에 고객명·잡번호·회사 계정명·회사 프로젝트명을 걸러냈다. `.claude/`는 gitignore라 `git commit -- ".claude/Claude Change Log.md"`처럼 경로를 지정해 커밋한다.
- **스캔 원자료:** 캡처 팩 zip 두 개는 사용자가 삭제(2026-09-29). 17:04에 다시 나타나서(동기화 또는 재전송) 자동 초점 자료를 반영한 뒤 **다시 삭제**함. 스캔·자동 초점 자료 사본은 `drafts/scan-no-cad-2026-09-29/`(로컬 전용), 나머지는 `fos-physical-AI/SyncTrash/`의 옛 zip 사본뿐. 또 나타나면 먼저 `drafts/`와 비교할 것.
- **남은 캡처 소재:** 손 시험 영상(`hand_moving_test_clip.mp4`)은 아직 안 씀. GIF로 줄여 튜닝편에 넣을 수 있음.

- **네이버 투자 2·3편:** 775dff4 문구로 패키지 재생성 완료(2026-09-28). [투자 고지] 줄은 스크립트가 안 넣으니 손으로 다시 붙였음. 사용자 업로드 후 URL을 `naver-published-urls`에 기록.
- **동기화 충돌 사본(2026-09-30 정리):** 다른 PC에서 생긴 conflicted copy를 `.git`과 `docs/`에서 치웠다(내용은 커밋본과 같음). 또 생기면 먼저 커밋본과 줄바꿈 무시 비교 후 치울 것.
- **저장소 루트의 미추적 파일 `physical-ai-investment-notes.md`:** 사용자의 Physical AI 투자 리서치 노트다(로컬 전용, 커밋하지 않음). 2026-09-29에 8장(국내 QDD 기업, 네이버 ese4236)과 9장(QDD 쪽 미국 종목·밸류에이션)을 추가했다.
- **루트에 새 미추적 HTML:** 「휴머노이드 QDD 모터 시대, … _ 네이버 블로그.html」. 사용자가 저장한 네이버 글로 보인다. 건드리지 않았다. 필요 없으면 지우거나 `drafts/`로 옮길 것.
- **네이버 패키지 일괄 갱신 완료 (2026-09-30):** 09-29 오후 이후 바뀐 글 11개 패키지를 현재 글로 다시 만들었다(`tools/naver_refresh.py`, 배너·태그·투자 고지 유지).
  - 미발행 9개: camera-placement, choosing-physical-ai, cobot-basics, cobot-ur-vs-fanuc, jetson-scan-no-cad, learn-without-industrial-robot, physical-ai-investing-actuators, physical-ai-investing-power, ros2-robot-description. 그대로 올리면 된다.
  - **이미 네이버에 올린 2개도 갱신:** `cobot-investing`(P/E·Unitree 수치, "코봇 3부작" 문구 → 투자 1부), `jetson-isaac-foundation-models`(09-28 실측 캡처·그림 대거 추가, "3D 카메라", 시리즈 줄). 네이버 글을 고칠지는 사용자 결정. 새 UPLOAD.md는 "수정하기" 절차이고 처음 발행 안내는 `UPLOAD-first-publish.md`로 옮겼다. 옛 이름 PNG는 `_archive/`가 아니라 세션 스크래치패드로 옮겨 둠.
  - 새 글 `depth-camera-selection`은 사용자 요청으로 패키지를 만들지 않았다. camera-placement 네이버 본문의 "다음 글"에는 블로그 주소를 붙였다.
- **사이트 전체 이전/다음 링크(`navigation.footer`) 켤지 결정 대기.** 지금은 시리즈 글에만 직접 링크를 넣음(메모리 `series-prev-next-links`).
- **Pendant to ROS 2 네이버 크로스포스트:** 미실시(4편 × 그림 9개 PNG 변환 필요). Start Here 2편·투자 2·3편·실습 0편도 네이버 미발행.
- **투자 3부 후속 확인:** 미·중 합의는 2027-01-10까지 연장됐다(미국 재무장관, 2026-09-25). 배터리 소재 통제(공고 58호) 유예도 연장되는지 중국 상무부 공고로 확인해야 한다. 본문과 `inv3-controls` 그림에 "미확인"으로 적어 두었다. 늦어도 2026-11-10 전에 다시 볼 것.
- **대시보드 장중 갱신 외부 트리거 설정 대기:** (2026-10-01: 예약 실행이 다시 돌기 시작했다 — 일일 아카이브·백테스트·Deploy 성공. 하지만 장중 9회 중 대부분이 건너뛰어져 외부 트리거는 여전히 필요.) GitHub 예약 실행이 9/26 이후 전혀 안 돌아 cron-job.org → workflow_dispatch로 가기로 함. 사용자가 fine-grained PAT(butt2rflow, 이 저장소 Actions만)와 cron-job.org 작업(ET 평일 :35, 09:35~16:35)을 만든 뒤 실행 기록 확인할 것. 상세는 메모리 `dashboard-indicator-tiles`.
- **사용자 리뷰 대기:** 2026-09-28 발행분(투자 2·3편, 실습 0편, 투자 카테고리 이동, 교차 링크) — 사용자가 라이브 글로 리뷰 예정.

- **GEX Track-1 현행화:** 시트 v1.6 대비 볼륨가중 GEX·멀티인덱스 등을 gex-calculator에 반영(대조 완료, 미반영).
- **네이버 발행 — 완료(2026-09-19):** 대기였던 cds · stereo · frames · cobot-investing · vanna-charm · jetson-ros2-setup · jetson-isaac-foundation-models **전부 발행됨**. logNo 7건 `naver-published-urls` 메모리에 기록 완료. (URL은 `rss.blog.naver.com/bflownet.xml` RSS로 확보 — 네이버는 WebFetch 차단이라 사용자가 RSS 내용을 붙여 줘야 함.) 현재 네이버 미발행 대기 **없음**.
- **Physical-AI 코스:** `~/Documents/physical-ai-course`로 분리 — 잔여·정본은 그쪽(§8). **2026-09-28 정본 = 비공개 GitHub `butt2rflow/physical-ai-course`의 `course/`**(butterflow 소유, 416Jae 협업자). 옛 416 조직 Claude Doc은 읽기 전용.
- (네이버 크로스포스트 URL 전체는 메모리 `naver-published-urls` 참조 — 2026-09-19 기준 9편.)

## 8. 커리큘럼 — 별도 폴더로 분리됨

> **2026-09-28 갱신:** 코스 정본은 이제 Claude Doc이 아니라 비공개 GitHub `butt2rflow/physical-ai-course`의 `course/course.md` + `course/work-status.md`(🔒)다. 그림은 `course/figs/`, 생성기 `tools/figs_course.py`. 블로그와 코스 모두 butterflow 계정 소유(Claude butterflow@gmail.com · GitHub butt2rflow), 416 계정은 협업자 접근만 — 메모리 `user-accounts-split`.

> **Physical-AI 로봇 코스 워크스트림은 2026-09-20 `~/Documents/physical-ai-course`로 완전 분리되었습니다.**
> - 정본 = 살아있는 Claude Doc (`https://claude.ai/code/artifact/9ffcaf89-49f6-4583-a728-314e83126967`, rev 85). 웹페치 금지.
> - 코스 핸드오프·체인지로그·메모리(`physical-ai-robotics-course`)·은퇴 드래프트(`curriculum/`)는 모두 그 폴더로 이동.
> - 이 Blog 작업폴더는 **블로그/네이버 전용**. 커리큘럼 작업은 그 폴더에서 세션을 여세요.
> - 회사 `fos-physical-AI`와도 양방향 분리(코스 폴더 핸드오프 §2).

---

## 친구를 위한 — 자기 세션에 이 워크플로 얹기 (Obsidian vault + Koofr)

이 4종(핸드오프 문서 · 체인지로그 · `/start-session` · `/end-session` 스킬)은 **재사용 가능한 세션 라이프사이클 툴킷**입니다. 친구분은 **Obsidian vault + Koofr 동기화** 환경이니:

1. **핸드오프·체인지로그를 vault 안 마크다운 노트로 둔다.** Obsidian이 마크다운을 네이티브로 렌더하니 `SESSION-HANDOFF.md`·`Claude Change Log.md`를 vault 폴더에 그대로 두면 노트가 됨. 노트 간 연결은 Obsidian **`[[위키링크]]`**로(메모리도 이미 `[[name]]` 사용). 상단 `---` frontmatter는 Obsidian properties로 뜸.
2. **Koofr가 vault를 동기화** → 핸드오프/체인지로그가 기기·세션 간 유지됨. ⚠️ 두 기기 동시 편집 시 **sync 충돌 노트**가 생길 수 있으니: 세션 끝에 `/end-session`으로 정리 → **Koofr 동기화 완료 후** 다른 기기에서 시작.
3. **스킬 위치:** Claude Code 프로젝트 루트를 vault(또는 하위 폴더)로 두면 `<vault>/.claude/skills/`에 넣음. ⚠️ **Koofr가 점(.)으로 시작하는 폴더도 동기화하는지 확인** — 일부 sync는 dotfolder 제외. 제외되면 스킬은 `~/.claude/skills/`(유저 레벨)에 두고 vault엔 **문서만** 둔다.
4. **경로만 바꾸면 됨:** 두 스킬은 상단에 핸드오프/체인지로그 경로를 지정 — 친구 vault 경로로 교체(예: `<vault>/Claude/SESSION-HANDOFF.md`).
5. **내용 교체:** 블로그 URL·GitHub 저장소·gh 계정·네이버·프로젝트 경로(§2, §3 auth username). 자기 프로젝트에 없는 절차(네이버 등)는 삭제. `Claude Change Log.md`는 비우고 자기 세션부터.
6. 세션 시작 때 `/start-session`, 끝에 `/end-session` 습관화 → 핸드오프가 스스로 갱신되는 루프.
