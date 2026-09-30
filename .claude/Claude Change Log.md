# Claude Change Log — butterflow 블로그/네이버

> `/end-session` 스킬이 세션 끝마다 최상단에 항목을 추가합니다. 최신이 위(역순).
> 형식: `## YYYY-MM-DD — 한 줄 제목` + 변경/커밋/검증.
> 2026-09-27: butterflow-ssf 작업폴더 로그 + 저장소 추적 로그(BlogMigration) 통합.

---

## 2026-09-30 — 새 글 「어떤 깊이 카메라를」, 스캔편 카메라 표현 정리, Gemini 305 데이터시트 대조

- **스캔편 `jetson-scan-no-cad`(한/영):**
  - 카메라 함정 절이 "모든 카메라가 그렇다"로 읽혀서, 수치를 "이번에 쓴 카메라 한 대"의 값으로 고쳐 썼다. 같은 모델이라도 한 대씩 다르니, 가져갈 것은 숫자가 아니라 확인 방법이라고 적었다(`4f5a07a`).
  - 해결책에 "작업 거리를 공장 보정 거리 근처로"를 추가했다. 40~50cm는 측정값이 아니라 추정으로 표기했다.
  - 자동 초점 카메라는 "44cm가 최적"이 아니라 **"공장 보정 거리보다 가까이 가지 않기"가 핵심**이라고 요약, 해결책, 정리 세 곳에 넣었다(`487d4ca`).
- **ROS 2 2부 `ros2-robot-description`(한/영, `487d4ca`):** 초점 고정은 "실제 작업 거리에서" 하라고 고치고, 스캔편 실측 링크를 달았다.
- **새 글 `depth-camera-selection`「어떤 깊이 카메라를 / Which Depth Camera」(한/영, `0f16645`):**
  - 메뉴는 로봇 비전, `camera-placement` 바로 다음이다. 공개 자료 기반의 업무용 개념 문서를 바탕으로 썼고, 실제 로봇 기종 이름, 잡번호처럼 보이는 모델 코드, 회사 계정 링크는 뺐다.
  - 내용: 장착 위치 → 거리 → 권장 구간이 맞는 카메라 순서, 스테레오 거리 한계 두 가지(수식은 접이식), 컬러·깊이가 같은 센서인지, 무늬 없는 면·반짝이는 면, 근거리 카메라 5종 비교(가격 2026-09-30 정가), 큰 팔 예시, 받은 카메라 확인법
  - 그림 5개 `dcs-*`(생성기 `tools/r2pgen/figs_dcs.py`). 거리별 깊이 오차 차트 포함
  - `camera-placement`에 "다음 글" 줄, 스캔편 관련 줄에 링크를 달았다.
- **Gemini 305 데이터시트 V1.0 대조(한/영, `afad402`):**
  - 두 스테레오 모듈이 모두 컬러이고 깊이 원점이 왼쪽 모듈이다. D405처럼 컬러와 깊이가 같은 센서다("미확인"에서 정정).
  - "50cm에서 1% 이하"는 공간 정밀도였다. 깊이 정확도는 **±1.8%**로 고쳤다(D405 ±2%).
  - 최소 거리는 기본 설정 9cm(1280×800)·6cm(848×530), 시차 탐색 256의 근거리 설정에서만 5·4cm다. 근거리 설정은 전력 1.57→1.88W, 최고 동작 온도 45→40°C.
  - Box는 1m 케이블과 안내서 포함, Bulk는 카메라만이다. 그림 `dcs-ranges`·`dcs-alignment`도 맞춰 고쳤다.
- **코스(비공개 저장소) 동기화:** M5에 "이 카메라의 신뢰 구간 찾기" 실습과 카메라 특성 카드, Track A 자동 초점 노트 강조, W13 틀린 K 찾기 추가. 대체 카메라 부록에 Gemini 305/305g(손목용 1순위)와 근거리 비교표, 캐나다 구매 메모, 데이터시트 정정을 반영했다.
- **정리:** 동기화 프로그램이 `.git` 안과 `docs/`에 만든 충돌 사본(내용은 커밋본과 같고 줄바꿈만 다름)을 스크래치패드로 옮겼다. 두 저장소의 git 자격 증명을 저장소 로컬 설정으로 butterflow 계정에 고정했다.

**커밋:** `4f5a07a` · `487d4ca` · `0f16645` · `afad402` (모두 main에 푸시)

**검증:** 로컬 `mkdocs build --strict`는 기존 CI 생성 PNG 경고 5개 외에 없음. Deploy MkDocs 4회 모두 성공. 새 글 한/영 라이브 `curl` 200. 새 그림은 헤드리스 Chrome으로 한/영 렌더링해 글자 겹침을 확인하고 고쳤다. 새 글은 리뷰 게이트 서브에이전트를 돌리지 않았고, 한국어 번역투 점검만 직접 했다.

---

## 2026-09-29 (2) — 카메라 글 문단 수정, 시리즈 번호 편→부, Physical AI 투자 1~3부 수치 갱신

- **카메라 글 `camera-placement`(한/영, `d2e62bc`):**
  - "빈 영역 관문" 문단을 새로 썼다. 원래 문단은 `choosing-physical-ai`에 없는 "인식 관문"을 참조했다. "관문"은 ROS 2 시리즈 4부의 용어이고 뜻도 달랐다.
  - 용어를 "빈 공간 확인 / clear-space check"로 바꿨다(본문, 표, 용어, 그림 `cam-decision`·`cam-overhead-roles`·`cam-wrist-vs-overhead` 한/영).
  - `cam-wrist-example`: "빈 1/2/3" → "부품 통 1/2/3"(bin이 한국어로 부자연스러움). "빈피킹"이라는 용어는 유지했다.
- **시리즈 번호 통일(`d2e62bc`):** Physical AI 투자 1~3편과 실습 노트 0편을 "N부"로 바꿨다. 코봇 1·2부의 교차 링크 문구도 함께 바꿨다. 이름 붙은 글(스캔편·튜닝편·정정편)과 상품 편수(원칙편 4편 등)는 그대로 뒀다.
- **투자 2부 `physical-ai-investing-actuators`(한/영, `063ed8c`):**
  - "누가 무엇을 만드나"에 QDD 쪽 문단을 추가했다. ALNT(향후 PER 36.6배, 고점 근처, 1년 +156%), RRX(13.3배, 고점 대비 -37%), MP(107.7배·적자, 고점 대비 -55%)
  - Unitree 상장(688836, 외국 개인은 매수 어려움), Agility SPAC(CCXI→AGLT), 국내 로보티즈·하이젠알앤엠도 다뤘다.
  - 정리 표, 출처, 용어(프레임리스 모터·SPAC), `inv2-supply`에 Allient를 넣었다.
- **투자 3부 `physical-ai-investing-power`(한/영, `5178c58`):**
  - 수출 통제 유예: 미국 재무장관이 2026-09-25에 미·중 합의를 2027-01-10까지 연장한다고 밝혔다. 보도된 대상은 희토류다. 배터리 소재(공고 58호) 유예가 포함되는지는 **미확인**으로 적었다(본문, 표, `inv3-controls` 한/영).
  - 원자력 수치: OKLO(시총 69억 달러, 매출 약 120만 달러, 주식 수 +30%, 1년 -66%), CEG(향후 21배, -20%), VST(14배, -32%)
- **투자 1부 `cobot-investing`(한/영, `0ca9ae3`):**
  - TER P/E를 ~47배에서 ~55배로 고쳤다. 비교표를 최근 12개월 / 향후 P/E로 나눴다(NVDA 29/19, TER 55/41, 화낙 31/27).
  - Unitree 상장 첫날 +487%를 종가 기준 +460%로 바로잡았다. Agility SPAC 상장 소식을 한 줄 넣었다.
- **로컬 노트 `physical-ai-investment-notes.md`(미추적, 커밋 안 함):**
  - 8장: 네이버 ese4236 「휴머노이드 QDD 모터 시대…」 요약과 검토 메모(QDD "6~10:1"인데 사례 QC050은 25:1, 감속기 기업의 QDD 위험을 언급하지 않음)
  - 9장: QDD 쪽 미국 투자 수단과 밸류에이션 표
- 주가 수치는 전부 StockAnalysis 2026-09-29 종가 기준이다.

**커밋:** `d2e62bc` · `063ed8c` · `5178c58` · `0ca9ae3` (모두 main에 푸시)

**검증:** Deploy MkDocs 4회 모두 성공. 라이브 `curl` 200과 새 내용 확인(camera-placement "빈 공간 확인", actuators "Allient", power "2027년 1월 10일", cobot-investing "+460%", EN power "January 10, 2027"). 로컬 `mkdocs build` 에러 없음. 새 SVG 글자가 상자에 맞는지는 눈으로 확인하지 않았다.

---

## 2026-09-29 — 현장 노트 튜닝편·스캔편 발행, 코스 갱신(라이선스·클라우드 GPU·반사·스캔)

- **캡처 팩 점검:** `FoundationModels_live_capture_handoff_2026-09-28.zip`(09-29 후속 + session 2 추가), `FoundationStereo_live_demo_keyboard_*.zip`(같은 팩에 책상 장면 루트 배치). 이미 쓴 이미지는 변경 없음, README만 추가. 사용자 요청으로 두 zip 삭제.
- **튜닝편 `jetson-tuning-licensing`(한/영, 라이브):**
  - 속도: 11.4→4.0초, 단계별 시간, TensorRT 전후 결과 비교
  - 대안: ESS 2.1초, YOLO-World(연구용), 고정 상자
  - 라이선스 지도, 상업용 체인 3.26초·34ms, 가림 시험·손 시험, 크기 검사
  - 이후 추가: 반짝이는 부품 거울 컵 시험, 후보 줄이기 결과
  - 그림: SVG 3종(한/영), 사진 4장. 마우스 로고는 흐림 처리.
  - 커밋 `d0200e9`, `b11fed6`
- **스캔편 `jetson-scan-no-cad`(한/영, `3baa2ce`, 라이브):**
  - 인쇄용 ChArUco 보드 내려받기, 자동 촬영 조건, 보드 평면 재맞춤, 높이 지도 메시(4.5초, 100×66mm)
  - BundleSDF 비교, 뒤집힘 한계, 카메라 보정 함정 2개(1080p K 5.6%, 정렬 1.9px)
  - 그림: SVG 3종(한/영), 사진 3장
  - 근거는 회사 저장소 R&D 문서 §9c·9r·9s와 스캐너 코드. 일반적인 방법만 옮기고 고객 관련 내용은 뺐다.
- **스캔편 함정 3 자동 초점(`f0f52fb`):** 17:04에 다시 온 캡처 팩의 `autofocus_vs_calibration/`에서 반영했다.
  - 공장 K는 한 초점 위치(약 44cm)에서만 맞았다. 17cm에서는 +3.3%, 24cm에서는 +2.3% 틀어졌다.
  - 가까이서 초점을 고정하면 흐려진다. 카메라별 보정표로 오차가 1.4%에서 0.24%로 줄었다.
  - 그림 2장을 넣었다. 보정표 JSON은 파일명에 카메라 일련번호가 있어 뺐다.
  - 이 반영 뒤 두 zip을 다시 삭제했다.
- **스캔편 인쇄 메모(`6af3cc8`, 코스 `6334cd9`·아티팩트 v15):** 사용자 경험을 넣었다. 보드 SVG를 정확히 100%로 인쇄한 앱은 Inkscape뿐이었고, 다른 앱은 "실제 크기"로 설정해도 크기가 조금씩 달라졌다.
- **최종 편집·교차 참조(`e6aa3bd`):**
  - 사이트 전체 100개 md 파일을 스크립트로 점검했다(링크·이미지 대상, 한/영 쌍).
  - 누락은 CI가 만드는 PNG 5개뿐이었다. 홈 한/영 링크 수 차이도 CI가 다시 만드는 대시보드 블록 안에 있어 스코프 밖이다.
  - 현장 노트 5편 전부에 시리즈 이전/다음 줄을 달았다. 1·2부에는 없었고, 정정편에는 이전 글이 빠져 있었다.
  - 1·2부와 정정편의 "2부작" 표기를 없앴다.
  - 홈 현장 노트 목록에 튜닝편·스캔편을 추가했다.
  - 튜닝편·스캔편 한국어를 한 줄씩 편집했다. 돌리다→실행하다, "반사를 죽이다"→없애다/줄이다, "확신 있게 따라간다"→"더 쉽게 속는다", 긴 문장 분리.
  - 09-28 전체 편집 이후 바뀐 글만 줄 단위로 봤고, 나머지는 스크립트 점검만 했다.
- **스캔편 자동 초점 보충(`12a8b1f`):** 렌즈가 크게 움직인 뒤 자리 잡는 시간(2.5초 뒤에도 약 1%), 끝 위치 오차 +6%.
- **네이버 패키지 18개(로컬 `naver/`, 커밋 없음):**
  - 대상: Physical AI 미발행 글 전부. 세로 배너는 시리즈별 색 템플릿으로 만들었다.
  - 후처리: 코드 울타리, 줄바꿈 굵은 글씨, 인용 조각을 정리했다. 보드 내려받기에는 URL을 적었다.
  - 기존 3개(투자 2·3편, 정정편)는 오늘 문구로 다시 만들었다. 태그와 투자 고지는 유지했다.
  - 사용자 업로드 대기.
- **정정편:** 속도 4.1→4.0초, 다음 글 링크.
- **코스(`physical-ai-course`, 별도 저장소):**
  - 튜닝·라이선스 표, Isaac Sim 클라우드 GPU 운영안(Brev/AWS/RunPod, 20명 기준 비용 예시)
  - 반사 부품의 조용한 실패, CAD 없는 물체 스캔 대안, 보드 SVG, K·정렬 점검 체크리스트
  - 읽기용 아티팩트 재게시("링크 있는 누구나" 공유 상태)
- **검증:** 로컬 `mkdocs build --strict` 기존 경고 5개 외 없음. Deploy MkDocs 성공 후 라이브 200 확인(글 한/영, 보드 SVG).

---

## 2026-09-27 — 작업폴더·clone 통합: butterflow-ssf + butt2rflow.github.io → ~/Documents/Blog 하나로

### Session 1 (started 21:19)

- **작업폴더 병합:** `~/Documents/butterflow-ssf` → `~/Documents/Blog`. `naver/`(패키지 10종)·`drafts/`·`tools/`는 Blog 루트로(로컬 전용, `.git/info/exclude`에 등록 — 추적 `.gitignore`는 안 건드림). `SESSION-HANDOFF.md`·`skills/`는 `Blog/.claude/`로. zip·COMMIT_MSG·jetson PNG·nav 스니펫·발행 완료된 SSF 번들(`docs/`+CLAUDE.md)은 `_archive/2026-09-27_butterflow-ssf/`. `naver/` 이동은 파일 잠금으로 rename 실패 → 복사 후 `diff -rq` 동일 확인하고 원본 삭제.
- **메모리 병합:** `projects/C--Users-jae-Documents-butterflow-ssf/memory`의 12개 파일을 Blog 메모리로 이동(이름 충돌 없음), MEMORY.md 인덱스 합침. 구 메모리 디렉터리 삭제.
- **clone 하나로 통합:** Blog는 stale `master`(origin/main보다 101커밋 뒤, 미추적/변경 131개)였음. 비교 결과 전부 `main`과 동일하거나 stale/CI 생성물(VIX 스냅샷·kelly/volvol PNG·동기화 충돌 사본) → `_archive/2026-09-27_clone-consolidation/`에 경로 보존 백업 후 `main`으로 ff(`7d2e745`). ⚠️ 함정: `*.py`가 로컬에서 ignore라 `scripts/update_dashboard.py`(구버전)가 checkout 시 경고 없이 덮일 뻔 → 먼저 백업. 로컬 브랜치 `master`/`fix-index-tools`/`i18n-en-translations`는 `git branch -d`(병합 확인)로 삭제. 구 지속 clone `~/Documents/butt2rflow.github.io`(클린, 5커밋 뒤)는 은퇴 후 삭제.
- **체인지로그 통합 + 푸시 `446db38`:** 작업폴더 로그(09-07~20) + 저장소 추적 로그(BlogMigration, 09-17 Session 8 포함)를 날짜순 한 파일로. **공개 저장소라 발행 전 편집:** 고객 식별자·잡번호 제거, 회사 프로젝트명→"회사 업무"(사용자 선택), 비공개 Claude Doc ID·"개인 사업" 문구 삭제. 원본 비편집본은 로컬 archive에만. Deploy MkDocs 성공. push는 `gh auth switch -u butt2rflow` → 오버라이드 push → 회사 계정으로 복귀.
- **문서 갱신:** 핸드오프 §1·§2·§3, Blog `CLAUDE.md`(폴더 트리·브랜치), 메모리 `butt2rflow-push-auth` #5(“clone 하나 = ~/Documents/Blog, 스크래치패드 clone 금지”)·`project_repo_layout`(master 폐기)·`robot-vision-deep-dive-series`(경로).
- **⚠️ 모순 — 사용자 결정 필요:** `/end-session` 규칙은 체인지로그·time-log를 "로컬 전용, 절대 커밋 금지, 추적 중이면 untrack"이라 하는데, 이번 세션에 사용자가 **명시적으로 커밋·푸시 요청**함. end-session에서 untrack 안 함 — 공개 저장소에 계속 둘지(원래 추적되던 파일) 아니면 `git rm --cached` 할지 결정.

**다음 세션:**
- 세션은 `~/Documents/Blog`에서 시작. 빈 `~/Documents/butterflow-ssf` 폴더 삭제(이 세션 cwd라 잠겨 있었음).
- VSCode 등 다른 세션이 구 `butt2rflow.github.io` 경로를 쓰면 `~/Documents/Blog`로 변경.
- 동기화 클라이언트에서 `Blog\.git`·`venv`(662MB) 제외 검토 — "conflicted copy" 원인.
- `_archive/2026-09-27_*`는 확인 후 정리 가능.

---

## 2026-09-20 (2) — Field Notes 팔로업 발행: FoundationPose가 Orin NX 16GB에서 빌드+구동

- **신규 발행(라이브):** `jetson-foundationpose-16gb`(한/영) — Field Notes **2부작의 독립 정정편**(1·2부는 2부작 유지, renumber 안 함). 2부의 "16GB 증명·실전은 AGX 64GB" 결론을 뒤집음: 보드 비우기(유휴 컨테이너 stop + drop_caches: free 663MB→14GB, lfb 3×4MB→303×4MB) + `--memPoolSize=workspace:10240` + `optLevel=5`로 **엔진 빌드 성공**, 노드 라이브 6-DoF, 검출기까지 co-resident 피크 **~6.2GB/16GB**. 진짜 범인=유휴 컨테이너의 **연속 메모리 조각남**(용량 아님).
- **그림 2종:** 히어로 `demos/jetson-freeboard-proof.png`(실제 터미널 FAILED→비우기→PASSED, 사용자 제공·기밀 클린) + `jetson-freeboard-recipe.svg`(한/영, 라이트카드). 메모리 diagram은 히어로와 중복이라 제거.
- **기밀:** 공개 포럼 성공 사례(361112)의 **재현기**로 프레이밍. 클라이언트 식별자 0 — `physical-ai-vault-confidentiality` 선 준수. 회사 세션의 실측 수치는 캡처(사용자 제공)로만 반영, 세션 내용 직접 인용 안 함.
- **5게이트:** 저작권·상표 고지, 팩트(수치를 히어로 캡처에 정합: 1290442752·6.2GB·196MB 제거), de-AI(자기정정 훅), 페르소나(비유·글로스·네이티브), 용어(돌다→동작/타동사 돌리다→실행) 적용.
- **네이버:** 스킵(수작업 부담 — 이 글은 블로그만).

**커밋:** `ffc29cb`(6 files, +399). butt2rflow 계정 + 자격증명 오버라이드로 push.
**검증:** clone을 `origin/main`(dd81d38, VIX 스냅샷)과 동기화 후 발행 → GitHub Actions `mkdocs build --strict` **green**(Node20 경고만) → gh-pages 배포 success → `curl` ko/en/히어로 **200** + 라이브 grep(정정편·메모리 도둑·1290442752·6.2GB·히어로·레시피·nav 3항목) 확인.

---

## 2026-09-20 — 커리큘럼 워크스트림 분리 (→ ~/Documents/physical-ai-course)

- Physical-AI 로봇 코스를 butterflow-ssf(블로그 워크디렉토리)에서 **완전 분리**: `curriculum/`(은퇴 드래프트)·메모리 `physical-ai-robotics-course.md`·코스 핸드오프(§8)·start/end 스킬을 새 폴더 `~/Documents/physical-ai-course`로 이동(`prefer-visual-heavy`는 공유라 복사). butterflow는 **블로그/네이버 전용**, 핸드오프 §8은 포인터 한 줄만.
- 정본 Claude Doc는 폴더 무관(그대로). 회사 업무와 양방향 분리 규칙 유지.
- 아래 `2026-09-19~20` 코스 이력은 butterflow 세션에서 수행된 것 — **이후 코스 이력은 physical-ai-course 체인지로그**로 간다.

---

## 2026-09-19~20 — 코스 Claude Doc 대규모 보강 (작업상태 이관 + 비전 하드웨어/추론/엣지 Q&A 심화)

정본 Claude Doc 단일 문서에 집중 편집(세션이 09-19→09-20 연속, rev 80까지). **butterflow 블로그·git 미변경(이번 세션 배포 없음 — 코스 문서 전용). 회사 업무 세션과 양방향 분리 유지(그 세션의 실측·수치·파일 코스 미반입).**

- **작업 상태 탭 이관·zip 폐기:** rev5 `physical-ai-course-handoff.zip`의 00(맥락)·02(미결 질문)·03(다음 액션)을 Doc **"작업 상태(납품 시 제거)" 탭**에 세 섹션으로 이관. 01·04는 본문 탭에 이미 반영 → **zip 폐기, 문서 하나로 통합.** 🔒 작업상태 탭엔 실명·사업·유통 채널·장비 주문 등 사적 정보 → 공개물 반입 금지.
- **미결 질문 8 신설·정리:** Isaac Sim 모듈 편입 여부. 게이트=GPU만(라이선스는 확인 후 **비이슈로 제거** — 소스 Apache 2.0, AI Enterprise는 외부 서비스형 제공에만; 강의실 공유 서버=내부 사용).
- **본문 부록 — Isaac Sim 선택 모듈:** 필수 트랙 아님. 값=디지털 트윈(실물 전 예행)·Track A 합성데이터(Track B엔 안 씀, sim2real 갭). 운영=**강의실 내 공유 서버**(비용·라이선스 최선). Isaac Sim 5.1.0 최소 **RTX 4080/16GB**·RT코어 필수(3090은 개발기로 충분).
- **하드웨어 구성 — "카메라 선택" 소절:** 동작거리=장착위치(손목 근접 D405 vs 오버헤드 중거리+FOV), RealSense range 표, **min-Z(뎁스 하드리밋) vs K 유효밴드(렌즈 DoF·캘리브 표본)** 구분, 작업거리에서 캘리브.
- **Track A — 고정초점 교육 포인트:** AF는 focus로 K(fx·fy) 흔듦(Luxonis OAK AF 경험담); RealSense 전 계열 고정초점이라 원천 회피.
- **강사 노트 FAQ 3연(추론·엣지):** ① VPU vs GPU(온-VPU=nano 천장·CPU+내장가속기가 VPU-nano 이긴 실사례·RVC4≈32배·구글 TurboQuant/PolarQuant는 **LLM KV용이라 비전 무관**) ② Track A on Jetson Orin(NX16GB 경계선·AGX64GB 실전, **현시점 가성비=AGX Orin 64GB**) ③ **모델(ONNX)은 이식·TensorRT 엔진은 타깃 재빌드·CAD 교체는 재빌드 불필요**(엔진=네트워크별·캐시 재사용).
- **포럼 검증(사용자 요청):** NX 16GB에서 RT-DETR+FoundationPose 튜토리얼 완주 사례(포럼 361112) 확인 → 표현을 **"엔진 빌드 불가"→"빡빡·OOM 잦으나 우회로(`--memPoolSize`·헤드리스·컨테이너 밖·메시 성기게)로 가능"** 으로 정정. 빌드 OOM은 AGX 64GB에서도 발생 사례(359545).

- **15주 잔여 5주 채움(본문 모듈 구성):** 주차별 표 — W11 Isaac Sim 디지털 트윈(선택) · W12 심화 랩1(자기 물체로 트랙 판정) · W13 심화 랩2(실패 진단·강건성) · W14~15 팀 캡스톤. 평가축=트랙 선택 근거+동작+실패 분석; 선택 기준 계단·부록 Isaac Sim과 교차연결.
- **부록 '산업용 팔로의 확장' 기종 확충:** 적합도 표에 **KUKA(iisy·iiwa·KR)·Franka·ABB·야스카와·두산** 행 추가(제어 인터페이스·주기·내장 F/T·평가) + 브랜드 한 줄 설명(KUKA=RSI/EKI/FRI/EAC 옵션이 Track B 전제 / Franka=FCI 연구표준·산업 대형 아님 / ABB=EGM / 야스카와=MotoROS2 / 두산=dsr_ros2). 핵심=**실시간 외부제어 경로 유무가 Track B 가부.**
- **회사 업무 분리 원칙 기록:** 커리큘럼은 회사 업무와 코드·IP·자료 미혼합(양방향) — 작업상태 탭 제약·메모리·핸드오프에 명시.

- **강사 노트 FAQ — Cognex 비교 추가:** 현장 머신비전 매핑 — Cognex 고전(비딥러닝) 비전=결정론 기하 세계(PatMax 2D=계단 ② 2D 비전 · 3D 정합=Track 0 ICP 계열), **"모델 train"은 ML 학습이 아니라 기하 템플릿 1회 캡처**(Track B 학습과 다름), Cognex Deep Learning(ViDi)=학습형. ICP=Iterative Closest Point 명시.

- **본문 Track 0 — ICP 비유 박스 추가:** "직관 — 투명 모형 겹치기"(H3) — 포인트클라우드↔CAD 정합을 투명 모형 겹치기로 설명(①최근접 대응 ②회전·이동 ③반복→6-DoF), 신경망 없음·결정론·잔차, 지역최소/대칭 약점. ICP 정식 명칭(Iterative Closest Point) 포함.

- **NX 16GB 톤 공개-소스 정정(2026-09-20):** Track A 엣지 FAQ·현시점 결론을 "경계선/AGX 필수" → **"메모리 확보가 관건 — 유휴 컨테이너·백그라운드 GPU 정리 + `--memPoolSize` 워크스페이스 캡 + 빌더 최적화로 NX 16GB에서도 엔진 빌드·구동 가능"**으로 완화. 블로그의 '걷는 속도(~0.1 FPS)'는 엔진 미빌드(범용 경로) 상태였음을 명확화, 포럼 361112 링크 추가. **근거=공개 소스(포럼 361112/359545 + butterflow 블로그)만** — 회사 업무 세션 내용·수치는 미사용(양방향 분리 유지). 오해 소지의 "사내" 표현도 "공개/블로그"로 정리.

- **강사 노트 FAQ — RT-DETR vs YOLO 한 줄 추가:** 둘 다 2D 검출 앞단(계단 ② 2D 비전, 트랙 아님); YOLO=CNN·RT-DETR=트랜스포머(DETR) 계보로 하는 일 동일; Track A에서 박스→SAM2→FoundationPose; Isaac ROS 기본 SyntheticaDETR은 정확-인스턴스라 새 물체 재학습 필요.

- **본문 Track A — "위치(마스크) 주는 3가지" 표 추가:** FoundationPose는 **zero-shot이 포즈지 검출이 아님**(물체가 어디 있는지=마스크를 받아야 6-DoF) → 위치 공급 방법 표 ① 고정 ROI(지그) ② 검출기(RT-DETR/YOLO) ③ 수동 태깅. **팔렛/픽스처 공차** 대응 명시: 고정 ROI는 픽셀 완벽 불필요 — 공차 봉투를 덮는 넉넉한 ROI면 되고 정밀 6-DoF는 FoundationPose/ICP가 계산(대략 위치=지그, 정밀 자세=비전). 수동 태깅은 "검출기도 없고 위치도 안 정해진" 경우에만 필요.

- **본문 Track A — "보인다 전제 5조건" 표 + ROI·지그 용어 글로스 추가:** 고정 ROI(검출기 없음)가 성립할 "대상이 보인다"의 5조건(① ROI 안 ② 가림 적음 ③ 유효 깊이 ④ 단일·식별 인스턴스 ⑤ 배경 분리); 하나라도 깨지면 검출기 필요. ROI=Region of Interest, 지그=부품을 같은 위치·자세로 붙잡는 기계적 고정구.

- **강사 노트 FAQ — Grounded-SAM + VLA 스펙트럼 추가:** Grounded-SAM = Grounding DINO(텍스트→박스) + SAM2(박스→마스크) = 텍스트→마스크(Track A 앞단에 끼우면 검출까지 zero-shot=언어 조건 지각). VLA 스펙트럼 표 = 모듈 파이프라인(Track 0/A) → +open-vocab(Grounded-SAM) → VLA end-to-end(RT-2/OpenVLA/π0, Track B 언어 확장); 구조화 산업엔 모듈이 대개 우위.
- **Q&A로 확정(메모리 기록, 일부 Doc 반영):** SAM2 프롬프트=점·박스·마스크(**텍스트 아님**; 실사진 SA-1B/SA-V 사전학습 zero-shot 분할). 검출기 YOLO=RT-DETR **학습 부담 동일**(라벨 필요) — 던 건 합성(SyntheticaDETR)·open-vocab·SAM 자동라벨. **Orin NX 16GB 검출 실현성**: SyntheticaDETR 됨(가벼움·닫힌집합·forum 361112), **Grounding DINO 1.5 Edge(open-vocab) ~10.7 FPS TRT**(원조 1.1); Track A는 검출 init-only라 유리. **Track B는 검출기·SAM2·포즈·CAD 전부 없음**(픽셀→행동). (모두 공개 소스/일반 개념 — 회사 업무 세션 미인용.)

- **부록(산업용 확장) — 무질서 빈피킹 대목 추가:** 지그 없는 랜덤 빈피킹 = Track A(CAD 6-DoF, 산업 표준)의 가장 어려운 끝(가림·엉킴·대칭·반사·인스턴스 검출·그랩이 병목); Track 0 보조·Track B 부적합; 확장 = 학습형 그랩 검출(GraspNet/Contact-GraspNet/Dex-Net). 상황별 접근 표 포함.

**검증:** Claude Doc **rev 85**까지 반영·저장(Docs 커넥터). 근거 링크 문서 내 인용 — NVIDIA Isaac ROS 릴리스노트·포럼 361112/359545, Isaac Sim 5.1.0 요구사양, Luxonis RVC/OAK 문서, RealSense D405/D455 사양, 구글 TurboQuant. **git 배포 없음**(블로그 미변경).

---

## 2026-09-19 — 네이버 크로스포스트 7편 발행 + URL 기록, physical-ai-course-handoff.zip

- **네이버 발행(사용자 수동):** 대기였던 7편 전부 네이버 발행 완료 — cds · stereo-to-grasp · frames-transforms · cobot-investing · vanna-charm · jetson-ros2-setup · jetson-isaac-foundation-models. jetson 2편은 전날 편집(전동드릴·엣지 컴퓨터·톤·3패널·hw-tiers)까지 반영된 패키지로 게시.
- **URL 확보 방법(신규 gotcha):** 네이버 본체·RSS 모두 WebFetch **차단** → 사용자가 `rss.blog.naver.com/bflownet.xml` 내용을 붙여 주면 `<guid>`에서 logNo 추출. 7건 확보.
- **기록:** logNo 7건 `naver-published-urls` 메모리에 추가(총 9편), 8개 `naver/*/UPLOAD.md`의 "발행 완료" 줄에 URL 스탬프, 핸드오프 §7 "네이버 발행 대기 없음"으로 갱신.
- **핸드오프 zip:** `physical-ai-course-handoff.zip`(프로젝트 루트) — 커리큘럼 Unit 1~5(28 md)·다이어그램 32 SVG·README, 이미지 상대경로 resolve 검증, forward-slash 크로스플랫폼. Python `zipfile`로 재패키징.
- **⚠️ 커리큘럼 divergence 발견(2026-09-19):** 코스 설계가 별도 대화에서 진화 — 본편 팔 myCobot→**SO-101**, **Track 0/A/B** 구조, **LeRobot/LeLab**, 산업용 확장(UR/FANUC/KUKA + GELLO), 2채널. 정본은 별도 Claude Doc(rev 26+)+그쪽 핸드오프. butterflow `curriculum/`·zip은 myCobot 기반 **이전 드래프트→stale**. 핸드오프 §8 배너·메모리 `physical-ai-robotics-course` SUPERSEDED 배너로 표시.
- **정본 3-트랙 모델 확보·기록(2026-09-19):** 사용자가 정본 스크린샷/텍스트 제공 → **Track 0(ICP)·A(FoundationPose)·B(ACT)** 정의+비교축+선택 계단+정정("Track B=모방학습 자체, 실시간 외부제어는 산업용 팔의 전제일 뿐")을 handoff §8·메모리에 반영. 플랜을 **REV 2로 재-스파인**(SO-101 주팔·3트랙·LeRobot/LeLab·산업용 확장+GELLO·ROS2/MoveIt=sim Franka), 하단 REV 1(myCobot)은 참고용. **모듈 본체 28개 재정렬(특히 Unit 5→3트랙)은 사용자 확인 후 진행 예정.** 정본은 여전히 별도 Claude Doc rev 26+.
- **커리큘럼 홈 결정·정리(2026-09-19):** 사용자가 정본 패키지 zip(00~04, rev 4)을 프로젝트 루트로 교체 다운로드 → 제가 `01-decisions`·`04-technical-reference`·`00-context`·README를 **읽어** 정본 실체 확인(본문은 **Claude Doc rev 26**, 구조는 **M0~M9 3트랙**·SO-101·RealSense D405·ChArUco·LeRobot/ACT, butterflow Unit1~5와 완전 다름). 결정: **Claude Doc = 단일 정본 유지, butterflow=블로그.** butterflow의 myCobot Unit1~5 드래프트 28 md는 `curriculum/_superseded-mycobot-draft-2026-09-18/`로 **은퇴**, `curriculum/README.md` 포인터 신설. **재구축 안 함**(패키지가 "사본 두지 말 것" 명시 — 드리프트 방지). 핸드오프 §8·메모리 `physical-ai-robotics-course` 정본 기준으로 갱신. 🔒 `00-context` 사적 정보는 공개물 반입 금지.

---

## 2026-09-18 (2) — Physical-AI 로봇 커리큘럼 구축 + robot-simulation 발행 + jetson 글 대규모 용어·편집 정리

복구 이후 하루치 작업. 세 갈래.

### A. Physical-AI / 로봇 커리큘럼 (로컬 `curriculum/`, git 아님 — 발행분만 배포)
- **계획**: `physical-ai-robotics-course-plan.md`. 결정: 이중언어 KO/EN · 독립 코스 문서 · 저가팔 **myCobot 280** · 하드웨어 사다리(sim 무료 Franka → myCobot → 보유 UR/FANUC 캡스톤) · Unit 2 **이중용도**(블로그+코스).
- **신규 저술(이중언어)**: Unit 3(ROS 2 기초 3.1 / MoveIt 2 vs cuMotion 3.2), Unit 2(시뮬·sim-to-real), Unit 5(myCobot 집기 5.1 / UR·FANUC 캡스톤 5.2 / 경제성 5.3), + 재사용 Unit 1·4 **연습문제 래퍼 16종**.
- **다이어그램 16종/32 SVG**(rvd 자기테마, 각 워크드 예시). 사용자 피드백 "그림·예시 더" 반영([[prefer-visual-heavy]]).
- **tech-verify**: myCobot `mycobot_ros2`/`mycobot_280`·`mycobot_280_moveit2 demo.launch.py`, cuMotion 플러그인 **`isaac_ros_cumotion_moveit/CumotionPlanner`**(오기 수정), OMPL·`moveit_py` 확인.

### B. robot-simulation 발행 + 용어 통일(돌다→동작/실행)
- **신규 블로그 글** `robot-simulation`(KO+EN, 그림 5종) — Unit 2 이중용도 발행. Physical AI › Robot Vision, model-anatomy 뒤. 커밋 `c194de5`, CI green, 라이브 200.
- **용어 규칙 확정**: 소프트웨어가 "돈다"=**동작하다**(돕니다→동작합니다/돈다→동작한다/도는→동작하는/돌아가다·돌기), 타동사 "돌리다"=**실행하다**. 회전·복귀·자세·후보렌더링·금융글은 제외. 2패스로 로봇 글 전체 적용 — 커밋 `6016fe8`, `8e78a9a`. 핸드오프 §5 규칙화.

### C. "엉뚱한 세션" 복구 + jetson 글 대규모 편집 (persistent clone `~/Documents/butt2rflow.github.io`)
- **3패널 깊이 비교 그림**(다른 세션에서 커밋된 `e44b742`가 stale base) → origin/main 위로 리베이스 발행 `d91ea1d`. 캡션 문구 `f0a09b2`.
- **톤 3게이트 재검토**(persona/de-AI/final, Field Notes 2편 KO+EN) — 셈/거고요 등 잔여 AI톤 정리 `0bee78b`.
- **일괄 표현 정리** `badd861`: 드릴→전동드릴, 보드→**엣지 컴퓨터**(키보드·캐리어보드·제품명 Jetson보드·GPU보드 제외), 팔→로봇 팔, 오프너 "사무실에서 굴러 다니던", 새 부품이 와도→새로운 부품을 가져와도; **3패널 그림을 'ESS냐 FoundationStereo냐'→'why FoundationStereo' 섹션으로 이동+리프레이밍**(학습형 vs 순진한 블록 매칭, "가운데는 ESS 아님" 명시 — 블록매칭/ESS 혼동 해소).
- **"한 엣지 컴퓨터"(수 세기) → "한 대"/생략** `cceba8b` (손바닥만 한/증명한 은 보존).
- **hw-tiers 그림 SVG** '한 보드'→'한 대'·'실전은 64GB' `8a03203` (블로그는 SVG 직접 임베드 → 라이브; 네이버 `hw-tiers.png` 1360×600 재렌더).
- **네이버 패키지 전 구간 동기화**(jetson-isaac/jetson-ros2 txt·UPLOAD·배너PNG·hw-tiers PNG) — 아직 미발행(수동 붙여넣기 대기)이라 배포 없음.

**커밋(블로그, 전부 push·CI green·라이브 검증):** `c194de5` `6016fe8` `8e78a9a` `d91ea1d` `f0a09b2` `0bee78b` `badd861` `cceba8b` `8a03203`.
**검증:** 매 배포 `mkdocs build --strict`(기존 대시보드 PNG 5경고만) + GitHub Actions success + `curl` 200 + 핵심 문구 라이브 grep.

---

## 2026-09-18 — 세션 크래시 복구 + jetson-isaac 네이버 패키지 완성

세션이 크래시로 유실 → `/start-session` 복구. **콘텐츠 손실 없음** 확인(전부 디스크에 있고 라이브 발행됨).

- **복구 진단:** 크래시 세션(오늘 10:02, id `1789740155_1427`)은 **`jetson-isaac-foundation-models` 네이버 크로스포스트 패키지** 제작 중이었음(스크래치패드에 gifframes 추출·SVG→PNG 래퍼·site 빌드 흔적). 결과물은 `naver/jetson-isaac-foundation-models/`에 온전.
- **네이버 패키지(완성):** `jetson-isaac-naver.txt`(전문 평문) + 대표 세로배너(1360×1800) + 이미지 6종 + **움짤 GIF 2종**(FoundationPose 포즈추적) + scorecard/hw-tiers + `UPLOAD.md`(8곳 이미지 마커 배치표·절차). "로봇의 뇌를 엣지에 (2) — Isaac ROS·파운데이션 모델", 현장 노트 2부작 중 2부.
- **검증:** 블로그 원문 `posts/jetson-isaac-foundation-models/` 한/영 **라이브 200**. 네이버 발행은 사용자 수동 붙여넣기 대기(발행 후 URL → `naver-published-urls`).
- **주의:** 크래시로 `/end-session` 미실행 → 핸드오프·체인지로그가 09-09에 멈춰 있던 것을 이번에 현행화.

---

## 2026-09-17 (Session 8)

### Session: Robot-vision 심화 2부작 + GEX/0DTE dashboard fixes

**Robot Vision 심화 2부작 (new, bilingual — company team training + public):**
- `inside-the-models.{ko,en}.md` (심화 1부 — 세 모델의 안쪽: FoundationStereo·SAM 2·FoundationPose 개념 + 실패 모드)
- `model-anatomy.{ko,en}.md` (심화 2부 — 모델 해부: 아키텍처/텐서/손실, 수식 전부 `<details>` 접이식)
- 38 self-theming SVG (`rvd*.svg`, light/dark `@media`) + 38 English-label (`diagrams_en/`), geometry byte-identical
- nav: Physical AI › Robot Vision, after `frames-transforms`
- 약배경 독자 기준 재작성, 5-gate 리뷰 통과 (copyright·fact·de-AI·persona·editorial), 논문 대조 팩트체크
- Fact fixes: STA = Depth Anything V2, FoundationPose ~60만 장면/120만 이미지, Vention "…with GRIIP"

**GEX tile degenerate-read fix (commit 6e74a50):**
- 증상: `+0.0B / flip — / Max Pain 5675` (spot 7552)가 스냅샷으로 재노출
- 원인: present-but-degenerate Yahoo chain (net~0, no flip, MP far strike)이 `usable<20`/`==0` guard 통과 → 표시 + 캐시 오염 → 매 empty window 재노출
- `_gex_plausible()` 추가 → `fetch_gex` + `_load_gex_cache` 양쪽 게이트 (degenerate는 표시·캐시 안 함, 오염 캐시는 타일 생략 후 self-heal). 라이브 확인: net −0.8B / flip 7643 / MP 7655

**0DTE gamma tile (new, commits e0f6a0d + a03403e):**
- `fetch_gex_0dte()`: 최근접 만기만, sub-day T (1/√T 감마 포착), live-only · omit-on-doubt (>1DTE·<10분·빈체인이면 생략)
- OI(전일 종가) → 국면 + 감마 플립 (만기로 넘어온 포지션); 오늘 per-strike 거래량 → 라이브 "오늘 핀"(±5% ATM 최다거래 = 위치, 부호 아님)
- `gex-0dte-patterns` 포스트로 링크. 무료 데이터 한계 명시 (signed live gamma는 유료 signed-flow 피드 필요; OI는 하루 1회 = 전일 종가)

**레짐 → 국면 (commit 193694f):** KO 대시보드 카드 + `gex-calculator`/`vanna-charm` 본문 9곳 (VIX 카드의 안도/긴장 국면과 통일). EN "regime" 유지.

**Ops:** 깨진 repo 클론 복구 (crashed-git `index.lock` → `reset --hard`, 유실 없음). `mkdocs build --strict` 검증 (내 콘텐츠 경고 0; 남은 5경고는 기존 dashboard PNG). 배포 green + 라이브 URL 200 확인.

**Notes for Next Session:**
- 0DTE "오늘 핀" 라이브 렌더는 장중 배포(주중 <20:00 UTC)에서만 — **2026-09-18 18:30 UTC 검증 routine 예약됨** (`trig_01KaGaMQJmxKnuaTcpjQgvCW`)
- signed live 0DTE gamma 원하면 유료 signed-flow 피드 결정 필요
- 로봇비전 심화 2부작 Naver 크로스포스트 미실시


## 2026-09-17 — 로봇 비전 심화 2부작 발행 (inside-the-models · model-anatomy, 한/영)

Physical AI › 로봇 비전 **심화 2부작** 신규 발행. 본편(stereo-to-grasp → frames-transforms) 뒤에 붙는 개념·구조 심화.

- **글:** `inside-the-models`(심화 1부 · 개념) + `model-anatomy`(심화 2부 · 구조), 각 한/영. 본문 30KB+ 규모.
- **그림:** `rvd*` SVG **한국어 38종 + 영문 38종**(1:1 완전 매칭, 누락 없음) — `docs/assets/diagrams/`(KO) · `docs/assets/diagrams_en/`(EN). 자기테마 rvd 템플릿 사용(메모리 `robot-vision-deep-dive-series`).
- **nav:** `mkdocs-nav-snippet-robotvision.yml` 배치대로 로봇 비전 섹션 frames-transforms 뒤에 두 글 추가.
- **검증:** 한/영 라이브 200(`posts/inside-the-models/`·`posts/model-anatomy/`, sitemap lastmod 2026-09-18). 시리즈: 본편 2부작 → 심화 2부작.
- **비고:** 이 세션도 `/end-session` 미실행이라 당시 체인지로그 미기록 → 09-18 복구 시 소급 기록.

---

## 2026-09-09 (4) — GEX 타일 추가 (딜러 감마 레짐, 라이브 계산)

대시보드 지표 그리드에 **8번째 카드 = GEX(딜러 감마 노출)** 추가(한/영, 라이브).

- **데이터·계산:** 기존 파이프라인에 GEX 소스가 없어 **Yahoo SPY 옵션 체인**에서 라이브 계산(SPX 대리). 근월 ~6개 만기 집계 → **BSM 감마**로 넷 GEX·감마플립·Max Pain. 표시: 레짐(넷 GEX 부호, 🟢롱/🔴숏)·플립 vs 현재가·Max Pain(참고). `fetch_gex()`/`render_gex_card_{ko,en}`/`render_gex_chart()`(→ `gex_regime.png`, 글의 정적 `gex_profile.png`와 별개). 실패 시 타일 생략(graceful).
- **프레이밍:** 부호 취약성 때문에 방향 신호가 아니라 **레짐(잔물결/증폭·억제) 참고용** + Max Pain "맹신 금물" 면책 — 글(`gex-calculator`)의 "감마는 잔물결, 파도는 델타" 논지와 정합.
- **⚠️ Yahoo v7 옵션 함정(해결):** `v7/finance/options`가 이제 **401**(v8 chart는 무인증 OK) → **쿠키+crumb 핸드셰이크**(`fc.yahoo.com` 쿠키 → `getcrumb` → `&crumb=`)로 우회. GitHub Actions IP에서도 동작 확인.
- **검증:** stdlib만으로 로직 복제 로컬 테스트(numpy 없이) → SPY 762 / 넷 −5.5B(숏) / 플립 770 / maxpain 768 (일관·sane). 배포 후 CI 로그 동일 값 + KO/EN 스크린샷·이미지 200 확인. 커밋 `72c0a5c`.
- 메모리 `home-dashboard-layout`에 GEX·crumb 함정 추가, 핸드오프 §6/§7 반영.

---

## 2026-09-09 (3) — 홈 대시보드 2존 재편 (구현·배포, 한/영)

사용자 "돗데기 시장" 지적 → 진단(메모리)만 있던 것을 **실제 구현·배포**.

- **레이아웃(before → after):** 긴 단일 컬럼(지표 8종 풀폭 + 각 풀폭 차트, ~4200px) → **① 오늘의 결정**(비중·Kelly·공격) / **② 시장 신호 한눈에**(지표 7종) **2존** + 지표를 **반응형 그리드 카드**(데스크톱 2열/모바일 1열) + 각 카드 **무거운 차트를 `<details>` 접이식**(기본은 표+상태만).
- **구현:** `scripts/update_dashboard.py`에 `_dash_card()` 헬퍼(카드 래핑+`---` 제거+차트 접기) 추가, KO/EN 조립부 각각 존 헤더·그리드·카드 래핑. `custom.css`에 `.dash-zone`/`.dash-grid`/`.dash-card`/`.dash-chart`(+slate 다크 오버라이드).
- **검증:** py_compile OK → `deploy.yml`이 CI에서 `update_dashboard.py` 재생성 후 gh-deploy → KO(`08fe598`)·EN(`263c8b1`) 라이브 **전체 스크린샷으로 시각 확인**. EN `/en/` 차트 이미지가 접이식 깊은 중첩에도 `../assets/diagrams_en/…`로 정상 재작성됨(200) 확인.
- 미적용(의도): Kelly×VIX 곡선은 결정존 Kelly 카드에 노출 유지(유용, 잡음 아님); 지표는 스파크라인 대신 상태표+접이식 풀차트.
- 메모리 `home-dashboard-layout` DONE으로 갱신, 핸드오프 §6/§7 반영.

---

## 2026-09-09 (2) — 전체 글 리뷰 배포: 그림 버그·HIGH 용어·상호링크·vanna-charm 개선 + 5게이트 표준화

**긴급 버그 수정 (published):**
- **"감마 너머"(vanna-charm) honesty-layer SVG가 안 뜨던 문제** — `<desc>`의 `Barbon&Buraschi` 등 **이스케이프 안 된 `&`**로 `<img>` 로드 시 XML 파싱 실패(three-flows는 정상이라 "그림 하나만" 증상). 한/영 수정(`&`→`&amp;`), 전체 diagram SVG XML 재검증(나머지 정상). 커밋 `054b19f`.

**전체 글 리뷰 (published, strict 통과·라이브 검증, 커밋 `d875511`·`e0f1387`):**
- **HIGH 용어 설명(한/영, 14개 투자글)**: 감마·IV·EFFR·vol drag·0DTE·M1/M2·COR1M/COR1Y/COR90D·OTM·순 숏 변동성 — 첫 등장에 비유 우선 글로스. (용어 감사 에이전트 결과 중 HIGH만 채택 — 사용자 선택.)
- **상호링크 22건 + 오래된 앵커 수정**: 링크 감사 결과 깨진 내부링크 0건. 옵션기초·deriv→SSF 앵커를 신제목으로, gex-calculator "Vanna·Charm" 앵커 4곳 통일. 신설 상호링크: skew↔implied-corr, impl↔move/vix-ts, credit↔fedwatch, jetson↔cobot-investing, stereo/frames→cobot-investing.
- **nav 재분류**: MOVE·Implied Correlation을 Options 101 → **Market Data**.
- **vanna-charm 개선**: 제목 → **"감마 너머 — 바나 랠리, 핀닝, 딜러의 진짜 손놀림"**(inbound 앵커 6곳 동기화), 오프너 문구("금융권 트위터"→"업계 헤드라인 이벤트 사실관계"), 핀닝(자석 비유+유동성 이유+**감마 효과임 명시**), 0DTE 중립화, vanna rally에 **변동성 타깃 재레버리징 교란요인** 추가.

**리뷰 게이트 — 5게이트로 표준화 (사용자 지시):**
- **③ '사람이 쓴 느낌(de-AI)' 게이트 신설.** 표준: ① 저작권 ② 팩트체크 ③ 사람이 쓴 느낌 ④ 페르소나 ⑤ 최종편집. 각 게이트를 `git diff` 대상 병렬 서브에이전트로 실행.
- 반영: 팩트(핀닝=감마 명시·감마 gloss "불어나는지→바뀌는지"·0DTE 중립), 페르소나("갉이는"→"갉아먹히는" 등 비표준어·군더더기), 저작권(pass), 최종편집(OTM "행사가에서 멀어"→"현재가에서 멀어"·gex-calc 앵커), **사람이 쓴 느낌**(반복 3분할 완화·경고박스 중복+"→슬로건" 제거·중첩괄호/화살표 사슬 풀기).
- 메모리 `review-gates` 신설, 핸드오프 §5 갱신.

**대기(사용자 확인 필요):** 홈 대시보드 2존 재편(메모리 `home-dashboard-layout`).

---

## 2026-09-09 — GEX 후속편(Vanna·Charm) 신설 + gex-calculator 보강 + 홈 대시보드 진단

**블로그 (published, strict 빌드 통과·라이브 검증):**
- **후속편 신설** `vanna-charm.{ko,en}` — "감마 너머 — Vanna·Charm와 딜러의 진짜 손놀림" / "Beyond Gamma". 팩트체크 먼저(GPP'09·NPP'05·Barbon&Buraschi'21·Cboe 0DTE·Chilingarian) → **정직 레이어**(✅견고/🟡휴리스틱/⛔과장)로 차별화. 결론: 영향은 있으나 **규모는 과장**, 실제론 크지 않다. 그림 2장(vanna-three-flows·vanna-honesty-layer). Tools 체인에 gex-0dte-patterns 뒤로 삽입, 이전/다음 링크 갱신(gex-0dte→vanna→volatility-dashboard).
- **gex-calculator 보강**(제목 유지): 오프너 + 신규 섹션 "감마는 잔물결, 파도는 델타 — 직접 트레이딩하며 배운 것"(gex-ripple-wave 그림·레짐·방아쇠≠연료·균형 결론) + "Max Pain, 얼마나 믿나" + Cboe 0DTE 각주. 사용자 실전 통찰("감마=잔물결, 파도=대량 델타; 나비효과 인정하되 맹신 금물").
- 문구 확정: "세션 안에서 금세 **실제와 어긋나기 시작**"(사용자 승인). 게이트(팩트·저작권·페르소나·최종편집) 통과.

**홈 대시보드 진단(제안만, 미시행):** 사용자 "돗데기 시장" 지적 → 전체 캡처(1280×4200) 감사. 진단: ~8개 동일폭 스택·차트 과다·상단 카드 vs 하단 raw PNG **두 시각 체계 혼재**·그룹 없음. 제안: **① 결정존**(비중/Kelly/공격) + **② 지표 그리드**(소형 타일·상태점·스파크라인, 차트는 상세페이지로) 2존 재편. 상세는 메모리 `home-dashboard-layout`. **사용자 사인오프 대기.**

**메모리:** `home-dashboard-layout` 신규. `butt2rflow-push-auth`에 **VIX 스냅샷 자동커밋 → push 전 fetch+rebase --autostash** 함정 추가(이번 세션 4회).

**참고 커밋:** `5f5d471`(최종 문구) 외 vanna-charm 신설·gex-calculator 보강·체인/그림 커밋들.

---

## 2026-09-07~08 — 코봇 3부작 완결 + Jetson 현장노트 1부 + 네이버 패키지들

**블로그 (published, strict 빌드 통과·라이브 검증):**
- **코봇 3부작** 완성·정합화 (한/영, Physical AI › Cobots):
  - 1부 `cobot-basics`, 2부 `cobot-ur-vs-fanuc`, 3부 `cobot-investing`(투자편)
  - 그림 대폭 보강(1부 4·2부 3·3부 4장), 트릴로지-arc 리뷰 반영(화낙 표기·전방링크·중복 완화·용어)
  - 2부 정확성 정정: 화낙 외부제어 ~10Hz→Stream Motion 유료 125~250Hz·위치만, 힘 제어 프레이밍, CRX ±0.04mm, NVIDIA 파트너십
  - 3부: 세 갈래 희석·P/E 반전·순수플레이 부재(ABB→소프트뱅크)·가치이동·융합 스파인. 팩트 리서치 3회.
- **Field Notes 신설** + 1부 `jetson-ros2-setup` (Jetson Orin NX·JetPack 6·ROS 2 Humble, 실제 함정, SSH-에이전트 오프너, 그림 3장). nav "현장 노트" 추가.
- 용어 통일: 잇다→연결하다, 누르는→눌리는 쪽, 인컴번트→기존 강자.

**네이버 패키지 (준비 완료, 붙여넣기 대기):**
- `naver/cobot-investing/` · `naver/jetson-ros2-setup/` 신규 (txt + 배너 + 그림 PNG + UPLOAD.md)
- (기존: ssf·move=발행됨, cds·stereo·frames=대기)

**메모리:** `physical-ai-vault-confidentiality` 추가(고객 기밀 경계). `naver-published-urls` 유지.

**주요 커밋:** `c201a57`(2부) → `1a92e67`(2부 정정) → `33da02e`(3부) → `6756ce4`(그림·arc) → `f643c8a`(융합씨앗) → `fc6b2ca`(jetson 1부) → `4d106ee`/`be650f0`(3부 용어) 외.

---

## 그 이전 (이 로그 시작 전)

SSF 재출시, MOVE 지수, 크레딧 스프레드(CDS), 로봇 비전 2부작(stereo/frames), 홈 대시보드 타일 등은 이 로그 이전에 작업됨. 세부는 메모리(`naver-publishing`, `naver-published-urls`, `dashboard-indicator-tiles`, `butt2rflow-push-auth`)와 git 히스토리 참고.


---
# Earlier log (BlogMigration, 2026-04)

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

---

## 2026-09-28

### Session (account split + nav cleanup + investing 2–3 + hands-on 0)

- **Posts published:**
  - `physical-ai-investing-actuators` (investing 2), `f4a9921`/`8d5f1dd`
  - `physical-ai-investing-power` (investing 3: humanoid power problem, Astro Boy / Nucleon / Mars RTG, battery materials section `1861ed4`)
  - `learn-without-industrial-robot` (Hands-on Notes 0)
- **New nav section:** "Physical AI Investing / Physical AI 투자" holds parts 1–3 (`eb5799c`).
- **Track 0/A/B naming** explained in choosing-physical-ai (`9f8f0fe`).
- **Left nav cleanup** (`90c7f3d`):
  - `hooks/nav_titles.py` gives short labels (front matter `nav_title`, else the text before " — ").
  - Section headings get the highlighted-band CSS.
  - The home TradingView ticker is removed.
  - Gotcha: `.gitignore` has `*.py`, so the hook needed a `!hooks/...` exception.
- **Home sidebar** (`fab9d33`): `hooks/home_sidebar.py` + `assets/home-sidebar.js` add recent posts (one per section) and a category list.
- **Accounts:**
  - The user switched Claude accounts mid-session (work ↔ personal). Blog and course now belong to butterflow; see memory `user-accounts-split`.
  - The first push after the switch failed until gh was explicitly switched to butt2rflow.
- **Fixed:** SESSION-HANDOFF.md had a stray leading backtick on every line from an earlier escape bug; stripped.
- **Next:**
  - Recheck China's battery-material export-control suspension after 2026-11-10 (investing 3).
  - Naver crossposts of the new posts are still undone.

### Session (later, 2026-09-28): camera post, 0DTE rework, translationese sweep

- **New post `camera-placement` (KO/EN, 7 diagrams).** Grew out of the user's URDF/overhead/multi-camera questions. The position it takes lives in memory `camera-placement-post`. The fact gate corrected: GRIIP = pipeline, Rapid Operator AI = product; camera details are webinar-only; FoundationStereo computes depth rather than cleaning it; some SO-101 kits ship with cameras; the segmenter package name.
- **0DTE tile rework (`17fb2cf`).**
  - Root cause of the missing tile: GitHub dropped top-of-hour schedules, leaving ~3 runs/day.
  - Now: cron at :23; DST-aware session; last-read fallback (gex0dte_last.json on gh-pages); intraday series + trend chart; next-session preview with open-gap scenarios.
  - Follow-up: redundant local `import shutil` → UnboundLocalError once the trend reached 2 points → all deploys failed until `d4aa8fe`.
- **Translationese.** The user caught "시연이 덮은 범위 밖에서는 무너지는데". A native-Korean sweep then fixed 64 calques across posts and diagram strings (`e818962`), and 6 old alt/title mismatches were realigned. The 번역투 pass is now mandatory in review-gates memory.
- **Also:** Orbbec Gemini 335/336 price check (see course memory). Course got the wrist-camera commercial-example section (`47933ea`, private repo).
- **Next:**
  - Watch that the :23 schedules actually fire (first ones pending).
  - After 2026-11-10, recheck the China export-control suspension (investing 3).
  - Naver crossposts are still undone.

### Session (evening, 2026-09-28): cobot series, scheduling, live captures

- **Cobots is 2 parts (`d7db694`):** the user caught leftover "코봇 3부작" framing after cobot-investing moved to Physical AI Investing. Fixed intros, descriptions and closing lines in KO/EN, added series prev/next lines, and rewrote the calque-y "두 진영 — … — 을 맞대고" intro.
- **Dashboard scheduling:** GitHub `schedule` events have been absent since 9/26 (all 3 workflows active). The user chose cron-job.org → workflow_dispatch. The API dispatch was tested OK and showed the off-session last-read + next-session preview live. Pending: the user creates the PAT and the cron job.
- **Live captures (`c697ed1`):** from the user's OAK-D S2 + Orin NX pack. It replaced Field Notes 2's simulated block-matching panel with a real same-frame comparison, added a checkerboard accuracy table, and added the live open-vocab chain to the 16 GB correction post. The Grounding DINO note now says the tiny checkpoint works. Shop-floor frames were excluded (car seats = client).
- Two background watches were stopped by the system: the 0DTE watch (memory pressure) and the course artifact watch (the account switched to the work account; the artifact lives in the personal account).

### Session (night, 2026-09-28): Physical AI editorial pass

- **Whole-section editorial review (`775dff4`).** The user asked for one pass over every Physical AI post, fixing literal-translation phrasing and cross-refs.
  - Six parallel agents, one per series group, made about 300 KO edits across 21 posts. EN was touched only where needed.
  - Main patterns fixed: dash asides, colon headings, 무너지다/돌다 misuse, captions restated in the body, particle errors.
- **Cross-refs.**
  - Cobot posts: the leftover "3부/Part 3" is gone; they now point to 투자 1편.
  - Field Notes: the menu 1편/2편 became 1부/2부 to match the body.
  - Field Notes 2: added a correction notice linking the 16 GB correction post.
- **Verification.**
  - A script checked alt text = SVG y=26 title and that all links resolve: 0 issues.
  - A numeric-token diff showed no fact changes.
  - Build clean, deploy green, live pages checked.
- **Next:**
  - Regenerate the investing 2·3 Naver packages if they're not uploaded yet.
  - Ask the user about the untracked `physical-ai-investment-notes.md` in the repo root.

### Session (night, 2026-09-28): Naver repack, account check

- Rebuilt the Naver packages for investing 2·3 with the 775dff4 wording. The `[투자 고지]` line was re-appended by hand, since naver_pack.py doesn't emit it.
- Found the Claude login had fallen back to the work account without the user noticing. The user switched to butterflow, and the course artifact was republished. Memory `user-accounts-split` now has the `Artifact list` check.
- `8cda26b`: from the live capture pack, added a glass-panel depth caveat (Field Notes 2, "L8" wall marker blurred) and the 3D point-cloud triptych (16GB correction). The re-sent pack was byte-identical to the earlier one.
- `9ca10f4`: added a FoundationPose 6-DoF chain from capture pack scene08.
- `68685c5`: the pack's next update revealed that pose was 180° flipped (plain mesh). Replaced it with the painted-CAD result (1.8 s, IoU 0.92, 0.94 mm / 0.48°) and added:
  - the orientation lesson figure
  - the whole-chain speed chart (11.4 → 4.3 s)
  - the NanoOWL vs Grounding DINO comparison
  - an in-caption note that the image was replaced
- The product code on the image footer was cropped out, and the wrong-CAD figure was skipped.
- Pending: the user decides whether to update the course's "~0.1 FPS" FoundationPose text.
- `894b02c`: added the live-camera chain bullet to the 16GB correction post's 30-second summary. The course was updated to match (course repo `5373427`). Field Notes 2 keeps its original "walking speed" claim under the correction notice.
- `29883b5`: whole-chain speed updated to 4.05 s (TensorRT scorer); chart replaced. Course `ab088f8`, artifact v9.
