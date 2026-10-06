# Claude Change Log — butterflow 블로그/네이버

> `/end-session` 스킬이 세션 끝마다 최상단에 항목을 추가합니다. 최신이 위(역순).
> 형식: `## YYYY-MM-DD — 한 줄 제목` + 변경/커밋/검증.
> 2026-09-27: butterflow-ssf 작업폴더 로그 + 저장소 추적 로그(BlogMigration) 통합.

---

## 2026-10-06 — 세션 마무리: 핸드오프·메모리 정리 (메모리편 세션)

- **What changed:**
  - 핸드오프(`e5fcaa5`): 마지막 갱신 2026-10-06, §6 메모리편 줄을 정정 후 내용으로(메모리를 채운 건 인식 쪽, Docker 숫자 한계, '경로 없음' 8.4%/24%). §7에 대기 두 개: 사이클마다 한 번 24시간 시험 최종값 반영, spatial-vision-AI README의 틀린 '1.3 GB' 표현(회사 저장소라 이 세션은 안 고침).
  - 시험 종료 시각 정정: 현지 시각 약 11:00. 앞서 적은 15:00은 UTC인 soak.log 시각을 현지 시각으로 착각한 것(아래 10-05 항목도 고침).
  - 새 메모리 `verify-cross-repo-claims`(다른 저장소의 원인 해석은 원본 CSV로 확인, Jetson의 Docker 메모리 숫자는 부풀려짐, soak.log는 UTC). `field-notes-tuning-scan`·MEMORY.md 색인 갱신.
- **Commits (10-05~06 이 세션, 모두 push됨):** `5aee1cc` 시뮬레이터편 장시간 시험 최종 · `d2de00c` 메모리편 신규 · `f261cfc` 정정 · 체인지로그 `91625a4`·`4efface`·`69bd912` · 핸드오프 `e5fcaa5` · 이 항목.
- **Verification:** 글 커밋은 모두 CI Deploy green, 한/영 라이브 200, 새 문구 grep(정정 후 옛 문구 0건). 로컬 strict 빌드 깨끗(기존 CI 생성 PNG 5개 제외). 다른 PC 세션과 같은 시각에 핸드오프·체인지로그를 편집해 한때 겹침, 사용자 요청으로 멈췄다가 그쪽 커밋(`190dc73`)을 받은 뒤 이 항목을 넣음. 미추적 `physical-ai-investment-notes.md`·네이버 저장 HTML은 이 세션과 무관해 그대로 둠.

## 2026-10-06 — 기록 정리: 피치 덱 링크 '없음', 핸드오프 장시간 시험 항목 닫음

- 코스 피치 덱 두 개(EN/KO)가 이 계정에서 '아티팩트 없음'으로 감시 종료(10-05). 원본은 코스 저장소 `tiers/deck-source/`에 보관, 복구 절차는 코스 핸드오프·메모리에. 블로그 쪽 변경 없음.
- 시뮬레이터편 장시간 시험은 10-05 다른 세션이 이미 반영(`5aee1cc` 최종 7.6시간, `f261cfc` 바로잡기). 핸드오프 항목은 같은 날 다른 세션(`e5fcaa5`)이 이미 새 대기 항목(사이클마다 자세 한 번 24시간 시험)으로 바꿔 둠. (이 항목의 첫 커밋 `5c9acd6`은 그 사실을 모르고 '대기'라고 적었다가 이 커밋에서 고침.)

## 2026-10-05 (밤) — 메모리편·시뮬레이터편 바로잡기

- 사용자 질문으로 재검토: 'cuMotion에서 아낀 1.3 GB를 FoundationPose가 먹었다'는 틀림. 인식과 함께 실행하면 기본 설정 cuMotion도 2.0~2.55 GB(26분·7.7시간 시험 모두), 멈춘 순간 2.51 vs 2.42 GB로 같았다. 이 해석은 spatial-vision-AI README/체인지로그에서 확인 없이 옮긴 것.
- 같은 날 19:28 spatial-vision-AI `bbcd673`(사이클마다 한 번 시험 8.4시간 중간 결과): FoundationPose GPU 할당(nvmap) 4.08 GB로 평평, Docker 숫자는 통합 메모리에서 믿기 어렵다. 직접 대조해 보니 Docker fp-run과 남은 메모리 상관 −0.86, Docker +1 GB당 남은 메모리 약 −0.5 GB → 압박은 실제지만 부풀려짐. 무엇이 오르내리는지·등록 탓인지는 미확인으로 적음.
- `f261cfc` 한/영: 메모리편 상단에 고침 안내, 30초 요약·표·'멈춘 건 cuMotion 때문이 아니었다' 절 재작성, nvmap 용어, 'Docker 숫자만 믿지 않는다' 교훈. '경로 없음' 최종값으로(모션만 8.4%, 설정 줄임 24%). 사이클마다 한 번 8.4시간 시점 문단(남은 최저 약 1.2 GB, 드라이버 3번째 사망). 시뮬레이터편 같은 주장·6%→8% 정정. 그림 r10-swing·r10-budget 라벨/주석. 홈 한 줄. strict 빌드 깨끗, CI green, 라이브 확인.
- fos-physical-AI: 10-05 17:22 `b0acdec` 이후 새 커밋 없음. 체인지로그 신규분은 소크 장애 2건, URSim을 .170으로 이전, 감시 하한 적응형(800 MB), Jetson headless, 회사 내부 일정(블로그 대상 아님).

## 2026-10-05 — 시뮬레이터편: 장시간 시험 최종 + 인식까지 한 대에 올린 결과

- fos-physical-AI(`isaac_sim_pipeline_plan.md` 10-04~05)와 spatial-vision-AI(`ursim/README.md` 소크 절, Jetson `soak_*` 리포트)의 새 결과를 확인함.
- `5aee1cc` `jetson-ursim-planners` 한/영:
  - 30초 요약: 모션만 7.6시간 98.2%, 3.8 GB에서 멈춤. 인식을 함께 올리면 메모리 부족 불릿 추가.
  - 장시간 시험 표: 중간(3.5시간) → 최종(7.6시간, 3,961단계, 쉬는 동안 캐시가 줄지 않음).
  - 새 절 「인식까지 한 대에 올리면」: 계속 추적 26분, 설정 줄여 1시간 10분(CPU 포화, 경로 없음 26%, 연결 끊김 31/h), 사이클마다 자세 한 번은 7.5시간째 진행 중(자세 757/758, 4.0초, 약 1.5 GB 여유). 원인은 FoundationPose 재탐색 때 약 1.3 GB 출렁임. nvblox 미포함. 결론: Jetson 두 대, AGX Orin 32/64 GB, 또는 가벼운 인식. 조명과 방식이 함께 달라 한 가지 원인으로 가를 수 없다는 점도 적음.
  - 정리 표 2행 갱신.
- CI Deploy green, 한/영 라이브 200·새 문구 확인. 오래된 `.git/index.lock`(12:02, 빈 파일) 제거 후 커밋.
- 반영 안 함: FOSFramework ROS 2 '세 번째 모드'(회사 내부 코드), AF 고정 초점 권고(스캔편·카메라 선택 글에 이미 있음).
- **(같은 날, 사용자 요청) 새 글 `d2de00c` 현장 노트 메모리편 `jetson-memory-budget` 한/영:** Jetson 소크 로그(containers/perception/hostmem/steps.csv)에서 그림 6개 `r10-*`(통합 메모리, 16 GB 나눠 쓰기, 네 시험 지속 시간, FoundationPose 톱니, 계속 추적 vs 한 번씩, 실제 셀 선택지). 외부 근거 arXiv 2603.18284(확인함), NVIDIA 'AGX Orin 등록 3.8초'는 확인 못 해 뺌. nav(Isaac Sim편 다음), 홈 목록 한/영, 시작하기 지도 표, Isaac Sim편 다음 글 줄, 시뮬레이터편에서 연결. 로컬 strict 빌드 깨끗(기존 CI PNG 5개 제외), CI green, 라이브 200.
- **대기:** 사이클마다 자세 한 번 24시간 시험이 10-06 약 11:00(현지 시각, 10-06 정정: 15:00은 UTC인 soak.log 시각)에 끝나면 메모리편(본문·r10-runs·r10-budget)과 시뮬레이터편 표의 '7.7시간째 진행 중'을 최종값으로 바꾸기.


## 2026-10-04 (2) — 현장 노트 Isaac Sim편 신규(집 RTX 3090 vs 클라우드 L4)

- **`16efb72` (KO/EN, 라이브 확인):** 새 글 `isaac-sim-pc-and-cloud`, 시뮬레이터편 다음. 원자료는 `~/Documents/issac-sim`(phase0/RESULTS.md, cloud_validation_2026-10-04/REPORT.md, ISAAC_SIM_SETUP_PLAN.md). 내용: URSim/Isaac Sim 역할 나누기(비추기는 물리 꺼짐이라 기각), 3090 벤치(최소 사양 RTX 4080 아래인데 실제 카메라 해상도 18.9 fps, 5 GB 미만), UR20 '약한 모터'는 관절 0 자세가 팔을 바닥에 누른 시험 잘못, SIL ROS 2 토픽(Jazzy·Zenoh→Humble·Fast DDS, 16 MB 버퍼, mono8 직접 발행, 뿌리 관절), 합성 데이터 500장 0.79 s + 렌더 껐다 켜기 누수(약 130 MB/장, 3090 188장·L4 169장에서 멈춤), 클라우드 L4(595 기준 3090의 49~83%, CPU 병목, 약 1.45달러, 그래픽·인코더 라이브러리와 NVIDIA 런타임 함정, WireGuard 원격 화면).
- 그림 5종 `r9-split/sil/floor/fps/leak`(생성기 `tools/r2pgen/figs_r9.py`, `lib.OUT`을 이 PC 저장소로 덮어씀), 사진 2장 `isaac-sdg-quad.jpg`(컬러·깊이·종류 색칠·2D 상자, 3090 실행 250번째)와 `isaac-cloud-stream.jpg`(작업 표시줄·창 제목 잘라 냄). 사용자 결정: 결과+함정만, GCP 프로젝트·IP·계정 없음.
- 연결: mkdocs nav 현장 노트 끝, 홈 한/영 목록, 시작하기 지도 표, 시뮬레이터편 다음 글 줄과 Isaac Sim 단락 인라인 링크.
- 팩트체크: Isaac Sim 요구 사양 문서(RTX 4080 최소, 16 GB, 32/64 GB, 리눅스 595.58.03, RT 코어 없는 A100/H100 미지원) 재확인. 보고서의 "60~100%"는 드라이버 580 수치가 섞여 있어 글은 595 기준 49~83%로, 누수 수치는 GiB로 2.2→9.9 GB.
- 동기화 충돌 사본 21개(10-04, DESKTOP-GQLCJ7N): 모두 커밋본과 같거나 이전 커밋과 일치 → 세션 스크래치패드로 옮김.
- **검증:** 로컬 strict 빌드는 CI 생성 PNG 5개 외 경고 없음, Deploy MkDocs 성공, 라이브 한/영 200·그림·홈 링크 확인.
- **사용자 피드백 반영(같은 날):** '집 PC' 강조 빼고 '놀고 있던 RTX 3090 PC'(제목·nav·홈·시뮬레이터편 링크·그림, `77082ad`). 한국어 번역투 정리: 약한 모터→관절이 힘을 못 쓰는 줄, 시각 도장→타임스탬프, 종류별 색칠→클래스별 분할, 상자 표시→바운딩 박스, 물리가 가라앉다→상자가 자리를 잡다, 뿌리 관절→루트 관절, 버퍼를 비추는 창→뷰, 평평→더 늘지 않음, 흔들다→움직이다, 가짜 하드웨어→토픽 기반 하드웨어(본문·그림).
- **대기:** 리뷰 게이트 서브에이전트 안 돌림 — 사용자가 라이브 한국어 확인. 네이버 패키지 없음(요청 시).
- **메모리:** 한국어 용어 메모리(`feedback_korean_series_and_terms`)에 이번 번역투 목록과 "기성 외래어(타임스탬프, 바운딩 박스)를 직역 대신" 규칙, '집 PC' 대신 '놀고 있던 RTX 3090 PC' 추가.
- **블로그 밖(코스로 이관):** 같은 세션에서 코스 구상 논의(학생 시연 → 밤새 클라우드 GPU 학습 → 다음 날 학생 PC에서 실행)와 측정(ACT CPU 추론·3090 학습, HF Jobs 가격)을 했고, 사용자 요청으로 메모·스크립트·원자료·메모리를 전부 `physical-ai-course`로 옮김(코스 `9bbe064`, `e4d3fd7`). HF Jobs L4 실측은 크레딧 0(402)으로 사용자가 보류. 측정용 venv 두 개(약 3 GB)는 세션 스크래치패드에만 있음.

## 2026-10-04 — 시뮬레이터편: C403 손목 끼임 원인 확정 + 장시간 시험 중간 결과

- **`3a18264` (KO/EN, 라이브 확인):** 'OMPL 다음이 더 문제였다' 절을 실측 원인으로 교체 — 접힌 자세 보호 정지는 모두 C403 손목 끼임 방지(팔뚝 원기둥–플랜지 구 28 mm, 끌 수 없음, UR12e 115.5 / UR20 130.2 mm), UR ROS 2 설명 이슈 #112(URDF에 없음). 세 겹 대책(계획마다 검사 20/30 mm 여유, cuMotion 끼임 축 충돌 구 + 플랜지 여유, MoveIt 플랜지 여유 구): 위험 계획 58 → 0, 최근접 +40 mm. '원인 미확인' 문장 삭제, 바닥 절에 C403 한 줄.
- 장시간 시험 단락: 1차 RTDE 끊김→제어 노드 사망→감시 추가, 3차 3.5시간 중간값(98.3%, 12 ms 평탄, 메모리 2.4→3.7 GB 정체, 거부 0, 상자 우회 약 6% 경로 없음) 표. 30초 요약·정리 표·측정일(10월 3~4일)·출처(UR 포럼, 컨트롤러 설정, 이슈 #112) 갱신.
- **남은 일 (10-05):** 24시간 최종 결과로 중간값 교체(사용자 "will update again tomorrow").

## 2026-10-03 — Physical AI 26편 교차 편집, 모션편 지도 구멍 원인 실측, UR 모델 무료

- **Physical AI 전체 교차 편집(`5ee26e6`, 52파일):**
  - 메뉴 순서: 시작하기 → 로봇 비전 → 코봇 → 펜던트에서 ROS 2로 → 현장 노트 → 실습 노트 → 투자(현장 노트 6·7부가 ROS 2 3·4부를 전제, 투자는 독자층이 달라 맨 뒤). URL은 그대로.
  - 홈 한/영 Physical AI 목록을 메뉴 순서·그룹 제목으로 재편, 빠져 있던 `camera-placement`·`depth-camera-selection` 추가.
  - 시작하기 지도 표 9편 → 26편 전부. 로봇 비전 7편에 이전/다음 줄, stereo·frames는 "기본편 1·2부".
  - 서로 어긋나던 사실 정정: 실습 0부의 "PolyScope X URSim은 Jetson 한 대로"(모션편 실측: 안쪽 컨테이너가 x86 전용), 세 모델의 안쪽 "카메라를 가까이"에 최소 거리·자동 초점 한계, 현장 노트 2부 "실전은 64GB"에 정정편 안내.
  - 실측 결과를 개념 글에 연결: 실물편 공장 보정 3.95→0.06 mm(UR vs 화낙 절대정확도, ROS 2 2부, 시뮬레이션 글, frames, 실습 0부, ROS 2 4부), 체인 4.0/3.3초, 180° 뒤집힘과 색 CAD, 거울 컵, 186 ms, UR20 구 71개, nvblox 5 mm, cuMotion 기본 바닥, 튜닝편 난방기 오검출(조용한 실패 예), Cognex의 RealSense 인수 발표(투자 1부 융합 논지).
  - 한국어: 포즈→자세, 포인트 클라우드·점군·점 구름→점구름, 젯슨→Jetson. 시리즈 링크 이름 통일(펜던트에서 ROS 2로 N부, 현장 노트 N부, Physical AI 투자 N부), 존재하지 않는 제목 링크 수정. 옛 글 11편의 "A — B" 제목 약 70곳, "우리(cage)"→펜스, 💡⚠️📝 제거, 투자 3부 "1부은"→"1부는".
  - 한/영 모두 같은 구조·링크·사실 수정(영어 문체 다듬기는 하지 않음).
- **모션편 오버레이 캡션 바로잡기(`befc956`, 사용자 지적):** "보드 위에 지도가 그대로 놓였다"는 그림과 달랐다(보드에 구멍, 방열 핀 위 빈 띠). 같은 커밋에서 시작하기 지도 그림 `cpa-map`에 카메라 글·Track B·실습·투자 추가.
- **정정편 메모리 7.2 → 7.7GB(`6325901`, 사용자 결정):** 튜닝편과 맞춰 최악값으로.
- **모션편 지도 구멍 원인 실측(`3982a06`):** bag에 같이 녹화한 좌우 영상 20장으로 FoundationStereo·ESS 깊이를 다시 계산해 같은 nvblox 설정으로 지도를 만듦(카메라 재가동 불필요, 데모 서버는 계산 동안만 멈추고 재시작). 보드를 덮은 비율: 카메라 칩 깊이 67%, FoundationStereo 97%, ESS 96%. 겹치는 픽셀의 깊이 차이는 중앙값 1 mm 안이라 위치가 아니라 빈칸이 원인. 새 그림 `jetson-motion-map-dense.jpg`, 표, 30초 요약, 출처(FS는 NVLabs 연구용 코드). 유리 케이스는 평평한 판으로 들어간다는 단서 유지.
- **로봇 시뮬레이션 글: UR 모델도 무료(같은 커밋, 사용자 질문):** `ur_description`, MuJoCo Menagerie UR5e·UR10e, Isaac Sim UR 모델, Gazebo 패키지, URSim. Franka가 예제마다 나오는 건 연구실 표준 팔이라서.
- **네이버 패키지 21개 재생성(로컬):** 바뀐 글 20개 + 시뮬레이션 글 재생성, 정정편 7.7GB 반영. `jetson-ros2-setup`은 발행된 글이라 UPLOAD.md가 "수정하기" 안내로 바뀜. 옛 `stereo`·`frames` 패키지는 폴더 이름이 글과 달라 도구로 못 고침. 모션편·투자 2부·실물편·3D 카메라 글은 패키지 없음.
- **검증:** 바뀐 52파일 내부 링크·이미지 스크립트 점검(CI 생성 PNG 4개 외 없음), Deploy MkDocs strict 빌드 4회 모두 성공, 라이브 페이지 200·핵심 문구 grep 확인. 로컬 venv는 다른 PC 파이썬을 가리켜 로컬 strict 빌드는 못 함.
- **남은 것:** ROS 2 1부 한/영의 `**` 홀수 개수(이번 편집 전부터, 라이브 정상), 영어 문체 리뷰 안 함, 옛 글 본문 문장 전체 재작성은 안 함.

---

## 2026-10-02 — 모션편 바로잡기: 라이브 장애물 지도는 통과, 지도→경로 계획과 ROS bag 추가

- **모션편 `jetson-pose-to-motion`(한/영):** 아침에 다른 세션이 발행한 첫 판(`7eccee0`)은 라이브 nvblox를 "첫 시도에 실패"로 적었다. 같은 날 원자료 쪽에서 원인이 검사 스크립트(메시 꼭짓점만 1픽셀씩 찍음, 0.4 m에서 2 cm 칸 ≈ 400픽셀)로 밝혀져 고쳤다.
  - 제목·설명·30초 요약·홈 목록·스캔편 다음 글 줄에서 "실패" 표현을 뺐다(새 제목 「모션편: 자세 다음은 움직임, 장애물 지도를 피해 가는 경로까지」).
  - 라이브 절을 "지도가 틀린 줄 알았다"로 다시 썼다: 평평한 장면 중앙값 5 mm·3 cm 안 81%, 유리 케이스 19 mm, 1.5 m 자르기 15 mm·덮는 범위 56%. 교훈은 "도구를 의심하기 전에 검사부터".
  - 새 절: ROS bag 녹화(초점을 공장 보정 위치에 고정, `Image.data`를 `array("B")`로 채워 2.2→10 fps, 카메라 없이 재생 425장), 지도 → cuMotion(지도 끄면 물체 속까지 계획, 켜면 거부, 마우스 위 12 cm는 손목 여유로 거부, `NO_IK_SOLUTION` 함정, 0.3~0.9초).
  - 그림: `mot-carving`(틀린 가설) 삭제, `mot-check`·`mot-planmap` 추가, `mot-status` 갱신. 라이브 비교 그림을 고친 렌더로 교체, 1.5 m 자르기 비교 그림 추가. 컬러 사진은 공장 배경·로고·마우스 모델명이 보여 쓰지 않았다.
- 근거는 사용자 R&D 원자료(10-01~10-02)이며, 로봇 기종 계획 등 회사 쪽 맥락은 넣지 않았다.

- **실제 장면 사진 3장 추가(같은 날 오후):** 10-02 bag의 컬러 영상(오버레이 없음)으로 장면 사진, nvblox 재생 지도를 사진 위에 거리별 색으로 겹친 그림, 지도 켬 결과(거부·통과)를 물체 표면에서 올린 점선과 번호로 사진 위에 표시한 그림. Jetson의 bag·재생 메시·2단계 결과를 SSH로 가져와 이 PC에서 렌더(데모 서버와 카메라는 건드리지 않음). 로고·제품명 없음 확인.

- **9월 30일 사진 반영(저녁):** 사용자가 준 사진 01~07을 글에 나눠 넣었다. 마우스의 로고, 왼쪽 공장 바닥, 오른쪽 사다리는 흐림 처리했다.
  - 현장 노트 2부: 옛 데모 사진(브랜드가 많은 책상 장면) 두 장을 미니 PC 장면의 FoundationStereo 깊이(01+3b)와 SAM2 마스크(02)로 교체. 기존 깊이 비교 그림에 남아 있던 마우스 로고도 흐림 처리.
  - 모션편: 새 절 「자세가 먼저 알려 주는 것: 보이지 않는 모서리까지」(FoundationPose+CAD, 모서리별 보드까지 거리, 가려진 모서리 CAD 56 mm vs 자 55 mm). 05(거리 지도)는 광선 그림과 숫자가 달라 쓰지 않았다. 정정편은 그림이 본문 숫자와 묶여 있어 그대로 뒀다.
- **모션편 한국어 다듬기(사용자 지적):** "면을 채워서"를 "메시는 원래 삼각형 면인데 검사가 꼭짓점만 찍었다"로 풀어 썼다(없는 걸 지어낸 게 아님). 가상 하드웨어 문장, "결과는 … 올라왔습니다" 주술 호응, 반복된 "거예요", 이야기와 맞지 않던 정리 문장, 좌표 변환 번역투, 플래닝 씬·충돌용 구 설명, 상태 그림 alt 정리.

- **새 글 현장 노트 7부 실물편 `jetson-real-robot-first-move`(한/영):** 마침 쉬고 있던 UR20(PolyScope X)에 Orin NX를 연결해 처음 움직인 기록(사용자가 UR20 이름을 직접 제안해 모델명 표기). 읽기만 → 공장 보정(3.95→0.06 mm) → 손목 ±5° → cuMotion 계획 움직임(5 cm, 목표에서 0.1 mm). 함정: 드라이버만 업그레이드하면 ABI 불일치로 죽음, 슬라이더 18%면 5초→28초, cuMotion 기본 바닥(받침면 아래 팔). 안전 절차(인에이블 스위치, 계획→확인→실행, 낡은 계획 거부, 프로그램 업로드는 사람이). 그림 4개 `r7-*`(`figs_r7.py`). IP, 공장 사진, 회사 맥락은 넣지 않음.
- **모션편 자세 그림 설명 바로잡기(사용자 지적):** 파란 CAD가 사진과 잘 맞지 않는데 캡션이 '맞았다'고 해서 고침. 미니 PC는 왼쪽 끝이 비고 오른쪽이 넘침(IoU 0.88), 마우스는 위·오른쪽으로 어긋남(0.66). 원인은 카메라 칩 깊이(방열 핀·검은 마우스에서 깊이가 거의 없음), FoundationStereo 깊이를 쓴 정정편 라이브 데모는 IoU 0.92. 집기 전 접근엔 충분하지만 집기엔 다시 잡아야 한다고 명시.
- **모션편 자세 사진을 FoundationStereo 깊이 결과로 교체(사용자 요청):** 「자세를 목표로 바꾸기」의 칩 깊이 오버레이(`jetson-motion-pose-goal.jpg`, 삭제)를 9월 30일 FoundationStereo 깊이로 잡은 미니 PC 자세(`jetson-motion-pose-cad.jpg`, CAD가 모서리에 그대로 붙음)로 바꿈. 본문은 '이 시험의 목표는 칩 깊이 자세에서 만들어 거칠었다(0.88/0.66), 실제로 집을 땐 FS·ESS 같은 좋은 깊이로'로 정리하고, 헷갈리던 정정편 0.94 mm 문장은 뺌. 같은 사진이 앞 절에도 있던 중복은 앞 절에서 제거(가려진 모서리 그림은 유지). 한/영.
- **모션편 자세 → 목표를 같은 장면의 ESS 깊이 결과로 갱신(10-03, fos-physical-ai 재실행):** 같은 bag 20번 장면의 좌우 영상으로 FoundationStereo·ESS 깊이를 다시 계산(공장 보정값으로 컬러 시점에 맞춤), 자세 코드는 그대로. 미니 PC 0.88→0.92(작업대 맞춤 불필요), 마우스 0.66→0.87(ESS)·0.84(FS), FS vs ESS 1.2°·2.9 mm, ESS 0.05초 vs FS 2초라 목표에는 ESS. 좌우 비교 사진 `jetson-motion-pose-depth-compare-{ko,en}.jpg`(디버그 라벨은 원본 프레임 픽셀로 지움). 교훈 셋째 '좋은 자세는 손대지 않는다'(2 mm 규칙). ESS 목표로 가상 UR20 전체 흐름 재실행(0.1 mm 안, 물체 속 거부). 9월 30일 FS 사진은 앞 절로 복귀. 30초 요약, 4부 표, 측정 날짜(~10월 3일).
- **'Track 0/A/B' 표기 제거(사용자 요청, 공식 용어가 아니라 혼란):** 기하 방식 / 신경망 인식 / 학습 정책(EN geometry / neural perception / learned policy)으로 바꾸고, 허브 글 요약·용어 설명에 '이 블로그의 구분일 뿐 업계 공식 용어 아님'을 명시. 글 9개(한/영)·홈 목록·제목(허브, 학습 정책 글), 그림 13종 한/영(`figs_cpa/hon/cam/tpb` 재생성, 헤드리스 렌더 확인). 학습 정책 글 주소(`learned-policy-track-b`)는 링크 보존을 위해 유지. 네이버 패키지 7개 갱신.
- **코스도 같은 이름으로(사용자 요청):** physical-ai-course `358efd1` — course.md/course.en.md/work-status/curriculum README의 Track 0/A/B를 기하 방식/신경망 인식/학습 정책으로, 일반어 '트랙/track'은 '방식/approach'로. '이름의 뜻' 문단에 '공식 용어 아님' 명시, 블로그 제목 바뀐 링크 글자 맞춤. 코스 아티팩트 v25 재게시. 메모리: 블로그 `feedback-no-track-labels`(신규)·`physical-ai-source-decks`·`field-notes-tuning-scan`(모션편 3단계), 코스 `physical-ai-robotics-course`. 핸드오프 두 곳 갱신.
- **네이버 패키지 정리(사용자 요청):** Track 개명 7개는 이미 갱신됨을 확인(그 뒤 바뀐 글 없음). 옛 이름 폴더 `naver/stereo`·`naver/frames`를 글 slug(`stereo-to-grasp`·`frames-transforms`)로 바꾸고 옛 꼬리말을 정본 링크로 바꿔 `naver_refresh.py`로 다시 만듦(둘 다 10-03 본문 수정을 반영 못 하고 있었음). 배너·태그 유지, 이미지 5장씩 다시 렌더. 모션편·3D 카메라·실물편은 패키지가 없어 만들지 않음.
- **모션편 네이버 패키지 새로 만듦(사용자 요청):** `naver/jetson-pose-to-motion/` — 오늘 판 본문(같은 장면 칩 vs ESS 비교 사진 포함), 이미지 16장, 세로 배너(스캔편 틀: 경로 계획 186 ms · 장애물 지도 5 mm · 가상 UR20 0.1 mm), 태그 24개, UPLOAD.md. 발행 전.
- **실물편 네이버 패키지 새로 만듦(사용자 요청):** `naver/jetson-real-robot-first-move/` — 그림 4장(r7-ladder/calib/gate/table), 세로 배너(공장 보정 3.95→0.06 mm · 첫 계획 움직임 0.1 mm · 계획과 실행 사이에 사람), 태그 22개, UPLOAD.md. IP·회사명 검사 통과. 발행 전.
- **새 글 현장 노트 8부 시뮬레이터편 `jetson-ursim-planners`(한/영, 사용자 요청):** fos-physical-ai 세션의 10-03 저녁 URSim 작업이 바탕. 윈도 PC WSL2·Docker의 URSim 두 대(PolyScope 5 UR12e, PolyScope X UR20)를 Jetson의 같은 스택(UR 드라이버 2.14, cuMotion, MoveIt 2 OMPL+Pilz)으로 구동, 역방향 SSH 터널. 6단계 데모 표, 같은 카메라 RViz 3장(cuMotion·Pilz·OMPL), OMPL 관절 그래프(손목 3 약 510°), UR20 속도 그래프(구간 표시), cuMotion 비결정성(간격 93~199 mm), 바닥 함정(툴 받침면 0.68 m 아래 → 보호 정지), 연결 함정 5개(--ipc host, 프로그램 재전송+3초, 실시간 아님, 브리지 허용 목록·QoS, 강제 종료 참가자), Lichtblick. 그림 `r8-setup/demo/planners/floor`(`figs_r8.py`), 사진 `jetson-ursim-*`(RViz 제목줄 경로·PC 이름·IP 없음). 연결: 메뉴, 홈 목록, 실물편 다음 글, 허브 지도, 펜던트 3부 플래너 표 아래 실측 링크.
- **URSim 'x86' 표현 바로잡기(사용자 질문):** x86은 CPU 종류이고 URSim은 리눅스용이라 윈도 PC에선 WSL2·가상 머신 위에서 실행. 실습 노트 0부(한/영)에 한 줄 보충 + 시뮬레이터편 링크, 시뮬레이터편 구성 절에 'WSL2를 쓴 이유'(리눅스용, PolyScope X는 Docker 이미지뿐, 같은 Ubuntu에 ROS 2·RViz·PlotJuggler).
- **시뮬레이터편: '보기만'의 차이 한 문단(사용자 요청):** RViz·PlotJuggler는 발행도 되는 ROS 2 프로그램이라 Zenoh 브리지 '구독만' 허용 목록으로 막았고, Lichtblick은 foxglove_bridge를 받는 기능 없이 띄워 원천 차단. 실제 로봇 옆에선 브리지에서 막는 쪽이 확실. Lichtblick 캡처는 아직 없음(요청 메시지는 이미 끝난 fos-physical-ai 세션에 감).
- **시뮬레이터편 보강 4가지(10-04, fos-physical-ai 10-03 밤 결과 반영, 사용자 승인):** ① Lichtblick 캡처 `jetson-ursim-lichtblick.jpg`(UR20 cuMotion 장면, 제목줄 잘라 냄)와 함께 Lichtblick 문단을 구성 절의 '보기만 한다면 윈도에서는 Lichtblick'으로 올림(SHA-256 확인, 라디안 주의) ② 새 절 'OMPL 다음이 더 문제였다': 감긴 자세에서 다음 실행 보호 정지, URScript movej 홈도 실패, Pilz PTP 홈(충돌 검사)으로 해결, UR20은 OMPL 기본 제외(원인 미확인) ③ 데모 7단계(그림 `r8-demo`·표·본문), UR20 OMPL 숫자는 기본 제외 전 결과라고 명시 ④ 연결 함정에 '데모 전 드라이버·플래너·MoveIt 컨테이너 재시작'. 30초 요약 2줄, 정리 표 2줄, 용어 Lichtblick.
- **시뮬레이터편 production 주의 한 줄(사용자 질문 '며칠·몇 주 돌면 문제 아닌가'):** 낡음은 R&D식 강제 종료 반복이 원인으로 보이나, 실제 셀은 재시작이 답이 아님: 오래 사는 앱 노드, 시간 제한·재시도, 안전한 시점에만 재시작, 장시간 시험(soak, 미실시)으로 확인. fos-physical-ai에 URSim 장시간 시험 요청 메시지(→ 이미 다른 PC 세션에서 진행 중이라 취소 메시지 보냄).
- **정리(10-04):** 메모리 `field-notes-tuning-scan`(8부 10-04 보강, 장시간 시험 대기), 새 피드백 메모리 `production-implications-of-workarounds`(R&D 임시 처방엔 실제 셀 관점 한 줄), 핸드오프(8부 보강, soak 결과 대기 항목).
- **시뮬레이터편 한국어 다듬기(사용자 지적: 문맥이 어색한 곳이 많음):** 본문 전체를 다시 씀. 구성 절에서 x86 문장 삽입으로 끊긴 'UR12e와 … UR20이에요' 흐름 복구, '툴 끝' 반복 → '도착 오차'·'툴을 목표에 정확히', 데모 소개의 섞인 나열 정리, OMPL 절의 긴 문장(감긴 자세 원인, 접힌 자세 세 번) 풀어 씀, 마지막 연결 함정 항목을 짧게 하고 production 주의는 뒤 문단으로 분리, 정리 표·마무리 문장 자연스럽게. 그림 문구(r8-planners 제목·'어떤 모양이든', r8-setup 제목)와 description도 맞춤. 숫자와 링크는 전후 비교로 동일 확인. 영어판은 그대로.
- **Lichtblick 노트(블로그 밖, 10-04):** 사용자 요청으로 fos-physical-ai 세션에 메시지 대신 `fos-physical-AI/docs/lichtblick_camera_view_note.md`에 노트를 남김(커밋 안 함): 카메라 토픽 보기(카메라를 로봇에 단 뒤 시험), C# 앱 연동 3안(실행 / WebView2 / 프로토콜만, MPL-2.0, C# 앱은 아직 ROS 미지원이라 나중), 공존 구성(Jetson Isaac ROS + 윈도 C# 테스터)에서 디버깅 도구로서의 역할. fos 변경 로그에 안내 한 줄. 메모리 `lichtblick-debug-viewer` 신규, 핸드오프에 대기 항목과 soak 1차 중단·2차 진행 기록.
- **펜던트 → ROS 번역 노트(블로그 밖, 10-04):** `fos-physical-AI/docs/pendant_to_ros_translation_note.md`(커밋 안 함). 펜던트 방식을 유지하는 세 길(오프셋만 / External Control로 섞기 / ROS로 다시 쓰기: 프로그램 하나 + 컨트롤러 설정 체크리스트), Claude 번역 대응표와 기계적이지 않은 부분(블렌딩, CONFIG, 속도 배율, 고유 기능, 안전 검토), URSim·ROBOGUIDE에서 원본 대 번역본 자동 비교, 시범 제안. 일반화하면 블로그 글감(회사 프로그램 제외). 메모리 `pendant-to-ros2-series`에 후속 아이디어, 핸드오프에 글감 후보로 기록.
- **시뮬레이터편: URSim vs Isaac Sim 한 단락(사용자 요청, 한/영):** '왜 실물 다음에 시뮬레이터인가' 절에. URSim = 컨트롤러를 흉내(물리·물체·카메라 없음, 진짜 드라이버·모드·보호 정지), Isaac Sim = 세계를 흉내(중력·접촉·카메라·조명, 일반 관절 컨트롤러, PolyScope·UR 안전 기능 없음, RTX GPU). 이 글의 원격 제어·감긴 자세 보호 정지·바닥 문제는 URSim이라 보였고, 깊이 빠짐·미끄러짐은 Isaac Sim 몫, 보정 차이·접촉 힘은 둘 다 못 보임. 시뮬레이션 글 링크. 메모리(`field-notes-tuning-scan`)와 핸드오프에도 반영.
- **'업계 공식 용어 아님' 문장 교체(사용자 지적: Track을 더 안 쓰니 필요 없음):** 허브 글 요약·용어 설명(한/영), 실습 노트 0부 용어 설명(한/영), 코스 '이름의 뜻'(한/영)에서 해명 문장을 빼고 업계에서 흔히 부르는 말(고전적·모델 기반 방식 / 모듈형 파이프라인 / end-to-end 학습)과 연결. 네이버 패키지 2개 갱신, 코스 아티팩트 v26, 메모리 `feedback-no-track-labels`·`physical-ai-source-decks`·코스 메모리, 블로그·코스 핸드오프, 코스 change log도 갱신.
- **블로그·코스의 핵심 문장(사용자 확인):** 허브 글 도입부에 '이 블로그가 말하려는 것'(한/영, 현장 노트·실습 노트 링크), 코스 과정 개요에 '이 과정이 말하려는 것'(한/영) 인용 상자: 현장 요구에 따라 AI 없는 방식부터 학습 정책까지 가장 낮은 단, 움직임은 적응·판정은 결정론, 그래서 직접 만들어 비교. 허브 네이버 패키지 갱신, 코스 아티팩트 v27, 메모리 `blog-course-core-concept` 신규.
- **코스 3단계 자료(블로그 밖, 10-04):** physical-ai-course `tiers/`에 1·2·3단계 영문 초안, 지역 중립. 계획서, 강사 운영, 강사 안내서 목차, 한 장 소개서(EN/KO + PDF).
  - 3단계는 '펜던트·지그·PLC로 로봇을 쓰던 엔지니어의 Physical AI 전환'에 초점(사용자 본인의 경로).
  - SeeDo Lab 이름은 Seedo 대마 재배기 'Seedo Lab'과 미국 SEEDO 상표 때문에 비추천. 이름과 강사 소개는 미정.
  - 메모리 `user-background-pendant-to-physical-ai` 신규.
- **코스 영업 자료 진행(블로그 밖, 10-04 오후):**
  - 파트너 피치 덱 EN/KO를 만들었다(비공개, 사용자가 Sam·한국 파트너·Diana에게 공유).
  - 개요 + 3과정 결합 브로셔 PDF.
  - 3-에이전트 검토(일관성·사실, 한국어, 마케터·학교·위험)를 반영했다: 책임 강사 소개 과장 수정, 독립 프로그램 명시, 실전 과정 장시간 시험 "시뮬레이터에서", 플래너 비교 정정, 체험 과정 학습 부하 현실화, 온타리오 "engineer" 배지 → Decider(영문), 안전·데이터·운영 문구, 한국어 용어(체험/이해/실전 과정, 시연 vs 시범 운영).
  - 데모 슬라이드는 영상 촬영 전까지 숨김. "와이파이 필요 없음"은 강사 GPU 오프라인 학습으로 유지.
  - 블로그 글 변경은 없음.
- **모션편 6부 보강:** 새 절 「자세를 목표로 바꾸기」(잰 카메라 위치 16.9 cm·16°, 뒤집힌 마우스를 깊이로 잡음, 사진 `jetson-motion-pose-goal.jpg`), 「가상 하드웨어로 끝까지, 그리고 UR20용 cuMotion 설정 만들기」(구 71개 vs UR10e 20개, 자동 맞추기 실패 이유). 다음 글 링크, 메뉴, 홈 목록.

**검증:** 로컬 `mkdocs build --strict` 기존 경고 5개 외 없음, 새 그림 한/영 헤드리스 Chrome 렌더 확인.

---

## 2026-10-01 — ROS 2 4부에 cuMotion 장애물 절 추가, 대기 항목 점검

- **ROS 2 4부 `isaac-ros-gpu`(한/영, `3d4ef74`):** XRDF 절 다음에 "cuMotion은 무엇을 피하나" 절을 넣었다.
  - 장애물이 들어오는 길 세 가지: 깊이 → 로봇 분할기 → nvblox 거리 지도, 플래닝 씬의 상자·메시(FoundationPose로 자세를 잡은 부품 포함), XRDF 충돌 구와 물체 부착
  - FoundationPose가 모르는 물체도 피하는 이유
  - 주의 네 가지: 잡을 부품이 장애물이 되는 문제, 안 보인 공간, 깊이·핸드아이 보정 오차, 사람 보호가 아니라 경로 계획 보조라는 점
  - 그림 `r2p4-obstacles`(한/영), 정리 줄, 용어, 출처 메모
  - 이 커밋은 세션 마무리 없이 푸시돼서 이번 항목으로 기록한다.
- **예약 실행 재개 확인:** 9/26 이후 멈췄던 GitHub 예약 실행이 10/01에 다시 돌았다(VIX 아카이브 09:58, 백테스트 10:32, Deploy 10:01·18:56·23:15 UTC, 모두 성공). 장중 cron(`23 13-21 * * 1-5`) 9회 중 대부분은 건너뛰어서 외부 트리거는 여전히 필요하다.
- **홈 KO 대시보드 "프레임워크 설명" 링크 누락 → 문제 없음:** 라이브 한/영 홈의 대시보드 안 내부 링크 대상이 완전히 같다. "Framework details →" 링크는 저장소에 커밋된 옛 `docs/index.en.md`(2026-05-11 스냅샷)에만 있고, 배포 때 CI가 덮어쓴다. 대기 목록에서 지웠다.
- **리뷰 게이트 실행:** `depth-camera-selection`, `jetson-tuning-licensing`, `jetson-scan-no-cad`, `isaac-ros-gpu` cuMotion 절에 저작권·팩트·기밀·사람 느낌·페르소나·한영 일치 게이트를 서브에이전트로 돌리고, 결과를 한/영 모두에 반영했다.
  - **스캔편:** 🔴 "전부 상업용 부품" 주장 정정. 원자료 확인 결과 스캔 깊이는 FoundationStereo-S v2.0(NVLabs, 연구용 라이선스)이었다. 추적 체인(ESS)만 상업용이고, 상업용이면 스캔 깊이를 ESS로 바꾸라고 적었다(요약·본문·비교표·정리표·고지). 거리 오차 5.6% → 약 5%(5.3%)(초점 거리 오차가 5.6%), 그림 `jetson-scan-k-trap` 포함. BundleSDF는 "FoundationPose와 함께 내놓은" 것이 아니라 이전 연구라고 정정. `calibData.getLensPosition()`으로 보정 거리 찾는 법, depthai #842 링크, OpenCV 4.6 기준 표시. 반복된 "이 카메라 한 대" 문장 2개 삭제, 콜론 제목 2개 정리, "스테레오 카메라" → "3D 카메라", EN에 빠진 문장 2개 추가.
  - **튜닝편:** 🔴 FoundationStereo 라이선스는 "연구 목적만"(FoundationPose는 "연구·평가")으로 구분. 🔴 "ready for commercial use"는 ESS·NGC판 FoundationStereo 카드 문구이고 FoundationPose 카드는 "상업용에 추가 학습 불필요"로 정정, 약관 매핑(EULA / Open Model License)과 EULA 조건(NVIDIA GPU 한정, 재배포 조건) 추가. 본문에 "법률 자문 아님" 한 줄. AGPL 설명 정확히(수정본의 네트워크 서비스), Ultralytics 상업 라이선스 언급. 커버리지 93~95%, 첫 자세 2.4초 통일, 초당 130°, 사진에 맞게 "사무실 책상" → "작업대", 난방기 "천장에 매단". TensorRT 버그는 "~로 보입니다". 그림 `jetson-license-lanes` 설명, `jetson-tuning-stages` 범례 "PyTorch 위주".
  - **cuMotion 절:** FoundationPose가 모르는 물체를 피하는 건 nvblox를 켰을 때만(cuMotion 예제는 ESDF 조회가 꺼져 있음). object attachment가 들고 있는 부품 자리를 거리 지도에서 지운다는 점, `unobserved_esdf_policy`(기본은 못 본 곳을 장애물로 안 침), 분할기 여유 5cm, 간섭 영역 비유. 앞 문단의 중복 문구는 새 절로 넘김. 그림 `r2p4-obstacles` 하단 문구도 같은 조건.
  - **「어떤 3D 카메라를」:** 🔴 D405 가격 272 → 325(공식 스토어, 2026-02 관세 추가분 반영, 직접 확인). 🔴 고압 세척은 IP67이 아니라 IP69K. 🔴 근거리형을 오버헤드에 달면 "깊이가 안 잡힘"이 아니라 "오차가 빠르게 커짐"(305도 1m까지는 깊이가 나옴), 그림 `dcs-order` 포함. OAK-D SR 1m 오차는 cm 단위가 아니라 5mm~1cm, OAK-D SR PoE 무게 297g, GMSL2 설명(휨 내성은 케이블에 달림)과 비유, ZED 0.3m는 ZED X 기준, Box 최소 30대·USB-C–USB-A 케이블. 기밀 게이트 지적으로 큰 팔 예시의 로봇 사양을 범위로 일반화했다. 상표 목록에 Cognex·reComputer·FoundationPose 추가.
  - **반영 안 한 것(사용자 확인 필요):** 튜닝편 실시간 화면의 `pose_track 54ms` vs 본문 34ms, 체인 전체 메모리 7.7GB vs FoundationStereo 단독 7.9GB, 30초 요약의 1.5° vs 본문 1.4°. 측정 원자료 없이는 어느 쪽이 맞는지 알 수 없어 그대로 뒀다. 3D 카메라 글에서 확인 못 한 항목: 305g "FAKRA 포함 약 53mm", "로보틱스 GMSL 보드가 335Lg 기본 지원"(인용한 Seeed 글은 NDA 거절만 뒷받침), ZED X Mini 0.1~8m.
- **남은 항목 확인·정리(2차):**
  - 튜닝편 34ms vs 화면 54ms: 34ms는 코스·업무 노트 모두 "추적 단계 단독" 실측. 화면 값은 같은 루프에서 ESS 깊이(56ms)도 매 프레임 실행되는 라이브 값이라고 캡션과 표에 밝혔다.
  - 메모리: 체인 전체 최고치가 7.7GB인데 "FoundationStereo 7.9GB 대신"은 맞을 수 없어 비교를 빼고 ESS 약 3GB만 남겼다(원자료는 이 PC에 없음).
  - 1.5° vs 1.4°: 요약은 "1.5° 안"(상한), 본문은 기준 체인 1.4°라 모순이 아니어서 그대로 뒀다.
  - 3D 카메라 글: ZED X Mini 0.1~8m(2.2mm 렌즈)는 Stereolabs 스토어로, Seeed 로보틱스 GMSL 보드의 335Lg 지원은 Seeed 위키로 확인하고 출처에 위키를 추가했다. 305g "FAKRA 포함 약 53mm"는 데이터시트(42×42×40mm)에도 다른 곳에도 없어 지우고 "커넥터는 별도"로 고쳤다.
  - 스캔편 상업용 경로(`dc93ded`, 코스 `584a226`): 스캔 깊이의 대체재를 ESS가 아니라 NGC 상용판 FoundationStereo로 바꿨다. 사진 20장 처리라 속도보다 품질이 중요하기 때문이다. Isaac ROS 5.0 `isaac_ros_foundationstereo`(JetPack 7.2 필요, 현재 Orin NX는 JetPack 6)이고 상용판으로는 미실측이라고 적었다. Fast-FoundationStereo는 연구용이라 제외.
  - nvblox 비교(글 수정 없음): 스캔과 nvblox는 둘 다 위치를 아는 여러 깊이 영상을 합치지만, nvblox는 cm 단위 셀 지도(TSDF→ESDF)용이고 스캔은 mm 단위 물체 메시용이다. 스캔편이 처음 시도했다가 실패한 TSDF 융합을 nvblox(Apache-2.0, `isaac_ros_nvblox`도 Apache-2.0)가 GPU로 할 수 있어 후속 실험 후보로 남겼다. 라이선스 표와 실험 후보는 로컬 메모리(`reference_vision_model_licenses`, `project_object_scan_followups`)와 핸드오프에 기록했다.
  - 네이버 패키지 3개(스캔편·튜닝편·ROS 2 4부) 재생성. `tools/naver_refresh.py`의 ROOT를 다른 PC 경로에서 스크립트 기준 상대 경로로 바꿨다(로컬 전용 파일).
- **검증:** 로컬 `mkdocs build --strict`는 기존 CI 생성 PNG 경고 5개 외에 없음. 볼드 짝 확인. 바뀐 그림 3개(`r2p4-obstacles` KO/EN, `dcs-order` KO/EN)는 헤드리스 Chrome으로 렌더링해 글자 넘침 없음 확인.

---

## 2026-09-30 — 새 글 「어떤 3D 카메라를」, 스캔편 카메라 표현 정리, Gemini 305 데이터시트 대조

- **스캔편 `jetson-scan-no-cad`(한/영):**
  - 카메라 함정 절이 "모든 카메라가 그렇다"로 읽혀서, 수치를 "이번에 쓴 카메라 한 대"의 값으로 고쳐 썼다. 같은 모델이라도 한 대씩 다르니, 가져갈 것은 숫자가 아니라 확인 방법이라고 적었다(`4f5a07a`).
  - 해결책에 "작업 거리를 공장 보정 거리 근처로"를 추가했다. 40~50cm는 측정값이 아니라 추정으로 표기했다.
  - 자동 초점 카메라는 "44cm가 최적"이 아니라 **"공장 보정 거리보다 가까이 가지 않기"가 핵심**이라고 요약, 해결책, 정리 세 곳에 넣었다(`487d4ca`).
- **ROS 2 2부 `ros2-robot-description`(한/영, `487d4ca`):** 초점 고정은 "실제 작업 거리에서" 하라고 고치고, 스캔편 실측 링크를 달았다.
- **새 글 `depth-camera-selection`「어떤 3D 카메라를 / Which Depth Camera」(한/영, `0f16645`, 처음 제목은 「어떤 깊이 카메라를」):**
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
- **용어 "깊이 카메라" → "3D 카메라":** 새 글 제목·메뉴(「어떤 3D 카메라를」)와 본문, 다른 글 5곳, 그림 `dcs-order`·`hon-so101-setup`. 처음 나올 때와 용어 설명에 "(깊이 카메라)"를 병기했다. 재는 값을 가리키는 "깊이"(깊이 오차 등)와 "스테레오 카메라"는 그대로, 영어판은 depth camera 유지, 주소도 그대로.
- **산업 현장 적합성(한/영):** 새 글에 "먼지나 물이 튀는 현장" 항목 추가. D405·D435는 방진 등급이 없고, RealSense의 IP65 모델 D457은 베이스라인 95mm·최소 52cm라 오버헤드용이다. 손목 근거리 + 먼지·물 튐이면 305g, 세척 라인이면 IP67. 산업 셀 체크 항목에 등급·잠기는 커넥터·제품 수명 주기를 더했다. 코스에도 같은 내용.
- **Gemini 305g 데이터시트 V1.0 반영(한/영):** 305에 모듈을 붙인 게 아니라 GMSL2 직렬화기를 넣은 별도 일체형 모델(FAKRA/SMB 두 가지), 광학·성능은 305와 같음, 깊이 40mm(FAKRA 포함 약 53mm), USB-C는 평가·설정용, 12V GMSL2 급전, 드라이버는 Jetson AGX Orin 계열 개발 키트 기준. 코스에도 같은 내용.
- **305g 호스트 조건(한/영):** Orbbec GMSL 드라이버 지원 목록은 NVIDIA AGX Orin·Orin NX 개발 키트와 지정 캡처 보드뿐이고 서드파티 캐리어는 없다. Seeed 일반 캐리어엔 GMSL2 입력이 없고, 로보틱스 캐리어용 GMSL 보드는 335Lg만 기본 지원하며 드라이버 소스는 비공개(Seeed 포럼 2026-08). 그런 호스트라면 짧고 휨에 강한 케이블의 USB 305, 20~60cm면 OAK-D SR PoE를 권했다. 다른 세션의 조사 결과를 받아 원문 세 곳(포럼, 드라이버 저장소, Orbbec 가이드)을 직접 확인한 뒤 반영했다. 코스에도 같은 내용.
- **용어 "ToF(비행시간)" → "ToF":** 직역이 어색해서 "ToF (Time of Flight)"로 쓰고 뜻은 문장으로 풀었다(새 글 본문·용어, 그림 `dcs-surfaces`, 코스 부록).
- **네이버 패키지 11개 갱신(로컬 전용):** 최근 수정이 반영되도록 기존 패키지를 현재 글로 다시 만들었다(미발행 9개 + 이미 올린 cobot-investing·jetson-isaac-foundation-models). 배너·태그·투자 고지는 유지, 낡은 시리즈 문구와 남은 `*` 표시를 고쳤다. 새 글은 패키지를 만들지 않았다.
- **정리:** 동기화 프로그램이 `.git` 안과 `docs/`에 만든 충돌 사본(내용은 커밋본과 같고 줄바꿈만 다름)을 스크래치패드로 옮겼다. 두 저장소의 git 자격 증명을 저장소 로컬 설정으로 butterflow 계정에 고정했다.

**커밋:** `4f5a07a` · `487d4ca` · `0f16645` · `afad402` · `31b2eec`(3D 카메라 용어) · `cd1ee97`(산업 현장 적합성) · `20127b2`(305g 데이터시트) · 305g 호스트 조건 + 체인지로그 커밋들 (모두 main에 푸시)

**검증:** 로컬 `mkdocs build --strict`는 기존 CI 생성 PNG 경고 5개 외에 없음. Deploy MkDocs 모두 성공(마지막 `a14538d`까지). 새 글 제목 라이브 확인(「어떤 3D 카메라를」). 새 글 한/영 라이브 `curl` 200. 새 그림은 헤드리스 Chrome으로 한/영 렌더링해 글자 겹침을 확인하고 고쳤다. 새 글은 리뷰 게이트 서브에이전트를 돌리지 않았고, 한국어 번역투 점검만 직접 했다.

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
