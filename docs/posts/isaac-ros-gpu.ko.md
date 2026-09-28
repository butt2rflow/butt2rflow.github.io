---
title: "티치 펜던트에서 ROS 2로 (4) — Isaac ROS와 cuMotion: 느린 부분을 GPU로"
nav_title: "4부 · Isaac ROS와 cuMotion"
date: 2026-09-28
tags: [physical-ai, ros2, isaac-ros, cumotion, nvidia, jetson, moveit2, robotics]
lang: ko
description: "매 프레임 신경망을 실행하는 인식과 복잡한 경로 계획은 CPU로는 느립니다. 같은 ROS 2 그래프에서 무거운 노드만 GPU로 옮기는 Isaac ROS, 복사를 없애는 NITROS, MoveIt 2의 플래너 자리에 꽂히는 cuMotion, 버전 맞추기, 인식 결과의 관문, 그리고 한 스택으로 여러 로봇을. 4부작 중 4부(완결)."
---

# 티치 펜던트에서 ROS 2로 (4) — Isaac ROS와 cuMotion: 느린 부분을 GPU로

> **티치 펜던트에서 ROS 2로 · 4부작 중 4부(완결).** [1부](ros2-for-robot-programmers.md) ROS 2의 배선, [2부](ros2-robot-description.md) 로봇을 ROS에 설명하기, [3부](moveit2-goals-not-points.md) MoveIt 2에 이어, 마지막으로 느린 부분을 GPU로 옮기는 NVIDIA의 Isaac ROS를 봅니다.

3부의 다섯 단계 중 두 곳이 오래 걸립니다. 1단계 인식은 카메라 사진이 들어올 때마다 신경망(사진을 보고 판단하도록 학습시킨 AI 모델)을 실행해야 하고, 4단계 계획은 셀이 복잡할수록 시험해 볼 경로 후보가 많아지죠. 둘 다 같은 계산을 엄청나게 많이 반복하는 일이라, 그래픽 카드(GPU)가 잘하는 종류입니다.

**Isaac ROS**는 이 무거운 일을 GPU로 하는 ROS 2 패키지 모음입니다. 새 로봇 운영체제가 아니라, 1부에서 본 그래프에 끼워 넣는 노드들이에요.

---

## 30초 요약

- Isaac ROS 노드는 **평범한 ROS 2 노드**입니다. 같은 토픽, 같은 메시지 형식으로 그래프에 들어가고, 무거운 계산만 GPU에서 합니다.
- **NITROS**는 GPU 노드끼리 이미지를 GPU 메모리에 둔 채 넘기는 방식입니다. Isaac ROS 5.0부터는 같은 기능이 ROS 2 자체에 들어갔어요.
- **cuMotion**은 MoveIt 2의 플래너 자리에 꽂히는 GPU 플래너입니다. 코드는 그대로 두고, MoveIt 설정에 cuMotion 파이프라인을 추가해 OMPL 대신 고르면 됩니다. 로봇마다 **XRDF**라는 보조 파일이 필요해요.
- JetPack, ROS 2, Isaac ROS는 **한 세트**로 맞추고 함께 올립니다.
- 인식 결과는 **관문**(신뢰도·누적 공차 범위)을 통과해야 보정에 쓰고, 벗어나면 멈추고 알립니다. 판정에는 넣지 않습니다.
- 로봇을 바꿔도 **위층은 그대로**입니다. 갈아 끼우는 건 설계도, 드라이버, MoveIt 설정 세 가지예요.

---

## 같은 그래프에서 무거운 노드만 GPU로

1부의 집기 셀 그래프를 다시 보면, 무거운 곳은 네 군데입니다.

![Isaac ROS = GPU를 쓰는 ROS 2 노드 모음](../assets/diagrams/r2p4-gpu-nodes.svg)

카메라 두 대로 거리를 재는 깊이 계산(ESS, FoundationStereo), 사진에서 부품만 오려 내는 분할(SAM 2), CAD 모델로 부품의 위치와 방향을 알아내는 자세 추정(FoundationPose), 그리고 경로 계획(cuMotion)이에요(FoundationStereo·SAM 2 패키지는 Isaac ROS 4.0부터). 이 네 곳만 Isaac ROS 노드로 바꾸고, 작업 순서나 로봇 드라이버 같은 나머지는 손대지 않습니다. 각 모델이 무엇을 어떻게 하는지는 [스테레오 비전에서 목표물 잡기까지](stereo-to-grasp.md)와 [세 모델의 안쪽](inside-the-models.md)에 따로 정리해 두었습니다.

Isaac ROS에 전용 화면이 따로 있는 건 아닙니다. 평범한 ROS 2 노드라서 1부의 `rqt_graph`, 2부의 RViz, 또는 Foxglove 같은 웹 기반 ROS 도구로 그대로 봅니다. 블록을 선으로 연결하는 그래픽 편집기는 시뮬레이터인 Isaac Sim 쪽에 있어요. Isaac Sim의 Action Graph(OmniGraph)는 가상 카메라와 로봇을 ROS 2 토픽에 블록과 선으로 연결합니다. 다만 시뮬레이터 안의 이야기이고, 실제 셀의 노드 연결은 여전히 launch 파일에서 합니다.

GPU에서 신경망을 빠르게 실행하는 데는 NVIDIA의 TensorRT가 쓰입니다. 모델을 그 GPU에 맞게 미리 변환해 두는 과정(엔진 빌드)이 한 번 필요한데, 메모리가 작은 엣지 컴퓨터에서는 여기서 처음 막히는 경우가 많아요. [현장 노트](jetson-foundationpose-16gb.md)에 Orin NX 16GB에서 이걸 넘긴 과정을 적어 두었습니다.

## 이미지를 GPU에 둔 채 넘기는 NITROS

GPU 노드를 그냥 연결하기만 하면 기대만큼 빨라지지 않을 때가 있습니다. 이유는 복사예요.

![느린 건 계산보다 복사일 때가 많다](../assets/diagrams/r2p4-nitros.svg)

보통 ROS 2 메시지는 CPU 메모리에 있습니다. 그래서 깊이 노드가 GPU로 계산한 결과를 CPU로 꺼내 보내고, 받는 분할 노드는 그걸 다시 GPU로 올립니다. 카메라 이미지가 초당 수십 장씩 오가면 이 복사만으로 시간이 꽤 들어요.

**NITROS**는 Isaac ROS 노드끼리 이미지를 GPU 메모리에 둔 채 넘기는 방식입니다. 효과가 가장 확실한 건 노드들이 한 프로세스(한 프로그램으로 실행되는 단위) 안에 묶여 있을 때입니다(ROS 2의 구성 가능 노드). 보통 노드가 같은 토픽을 들으면 평범한 메시지로 한 번 바꿔서 넘겨 줘요. 그래서 섞인 그래프도 동작은 합니다. 다만 빨라지는 건 GPU 노드끼리 모여 있는 구간뿐이에요.

이름에 관해 하나 알아 둘 게 있습니다. Isaac ROS 5.0부터는 NITROS 패키지가 빠지고, 같은 "GPU에 둔 채 넘기기"가 ROS 2 Lyrical 자체 기능(`rosidl::Buffer`)으로 들어갔습니다. 그래서 최신 세트에서는 GPU 노드들이 표준 ROS 메시지를 주고받아요. 3.x·4.x에서는 여전히 NITROS라는 이름입니다.

## 버전은 한 세트로

Isaac ROS를 쓰기 시작하면 버전 번호가 많아집니다. 이건 따로따로 바꾸지 말고 한 세트로 다뤄야 합니다.

![따로 올리지 말고 세트로](../assets/diagrams/r2p4-versions.svg)

**JetPack**은 Jetson 보드용 NVIDIA 운영체제 묶음입니다(리눅스, GPU 드라이버, CUDA 등). 그 위에 ROS 2, 그 위에 Isaac ROS가 올라가고, 세 버전이 서로 맞아야 동작합니다. NVIDIA가 이 조합을 미리 넣어 둔 컨테이너(도커 개발 환경)를 주기 때문에, 보통은 그걸 받아 쓰는 게 가장 빠릅니다. 팀원 모두가 똑같은 환경을 쓰게 되는 장점도 있고요.

이 시리즈와 현장 노트는 JetPack 6 + ROS 2 Humble + Isaac ROS 3.2 조합을 썼습니다. 이후 세대는 옮겨 가고 있어요. Isaac ROS 4.x는 ROS 2 Jazzy와 JetPack 7(Thor 세대 추가)로 옮겼고, 2026년 9월에 나온 Isaac ROS 5.0은 ROS 2의 새 장기 지원판인 Lyrical로 옮겼습니다. 개념은 같고, 명령과 패키지 이름만 조금씩 바뀝니다. 새로 시작한다면 그때의 최신 세트를 고르고, 업그레이드할 때는 셋을 함께 바꾸세요.

## MoveIt 2의 플래너 자리에 꽂는 GPU 플래너, cuMotion

3부에서 MoveIt 2 안의 플래너는 골라 끼울 수 있다고 했습니다. **cuMotion**은 그 자리에 들어가는 NVIDIA의 GPU 플래너예요.

![같은 입력, 같은 출력, 플래너만 교체](../assets/diagrams/r2p4-cumotion-slot.svg)

경로를 찾는 방법만 바뀝니다. 쓰려면 MoveIt 설정에 cuMotion 계획 파이프라인을 OMPL 옆에 추가하고, cuMotion 노드를 함께 실행합니다. OMPL이 후보를 하나씩 시험한다면, cuMotion은 GPU로 여러 후보를 동시에 시험하고 다듬습니다. nvblox와 함께 쓰면 카메라 깊이 정보를 계획용 장애물로 바꿔 쓸 수도 있습니다(계획 보조이지 사람 보호 수단은 아닙니다). 제 [현장 노트](jetson-isaac-foundation-models.md)에서는 Orin NX 16GB에서 7축 팔의 경로 하나를 약 210 ms에 계산했습니다. 장면과 설정에 따라 달라지는 값이지만, 엣지 컴퓨터에서도 실전 속도가 난다는 감은 줍니다.

cuMotion을 쓰려면 로봇마다 파일이 하나 더 필요합니다.

![충돌 검사를 공 몇십 개로 단순화](../assets/diagrams/r2p4-xrdf.svg)

**XRDF**는 URDF를 보완하는 파일로, 가장 큰 부분은 로봇의 각 링크를 공 여러 개로 근사한 충돌 모델입니다. 복잡한 3D 모양끼리의 충돌 검사는 느리지만, 공끼리의 거리는 매우 빨리 계산되거든요. 그 덕에 GPU가 수많은 후보를 빨리 걸러 냅니다. 서로 부딪혀도 되는 링크 쌍, 툴 좌표계, 관절의 가속도 한계와 저크(가속도가 얼마나 급하게 바뀌는지) 한계도 같이 적습니다. NVIDIA 문서에 UR10e 예시가 있고, 다른 로봇은 Isaac Sim의 로봇 설명 편집기로 만들 수 있어요. 모양이 비슷해 보여도 링크 치수가 다른 모델이라면 기존 파일을 가져다 쓰지 말고 공을 다시 맞춰야 합니다.

## 인식 결과는 관문을 거쳐서

[1부](ros2-for-robot-programmers.md)에서 판정은 결정론적 하드웨어에 두고, 인식은 움직임을 맞추는 데만 쓴다고 했습니다. 그 둘을 연결하는 지점이 이 관문이에요.

![통과하면 보정, 실패하면 크게 멈춘다](../assets/diagrams/r2p4-gate.svg)

신경망 인식은 조명이나 반사에 따라 결과가 조금씩 흔들립니다. 그래서 결과를 그대로 믿지 않고 두 가지를 확인합니다. 모델이 내는 신뢰도나 맞춤 오차(CAD를 맞췄을 때 남는 거리)가 기준 안인지, 그리고 [3부](moveit2-goals-not-points.md)에서 본 누적 공차 범위 안인지. 범위를 벗어났다면 인식이 틀렸거나 부품이 정말 이상한 자리에 있는 것이니, 조용히 넘어가지 말고 멈추고 알립니다. 조용한 실패가 요란한 실패보다 위험해요.

결과가 흔들리는 곳이 두 군데 더 있습니다. 같은 모델이라도 TensorRT 엔진을 다시 빌드하면 내부 계산 방식이 바뀌어 결과가 아주 조금 달라질 수 있어요. 버전 세트에 엔진 파일까지 포함해 고정하고, 바꿀 때는 [2부](ros2-robot-description.md)의 rosbag2 기록으로 옛 결과와 비교하세요. cuMotion도 무작위 시작점 여러 개에서 최적화하는 방식이라 같은 요청에 경로가 조금씩 다를 수 있습니다. 매번 같은 모양이 필요하면 3부의 Pilz나 저장된 궤적을 쓰세요.

## 한 스택, 여러 로봇

mock 하드웨어나 탁상용 교육 팔(3부에서 말한 관절 다섯 개짜리 같은)로 연습한 게 공장 로봇에서도 통할까요?

![로봇을 바꿔도 위층은 그대로](../assets/diagrams/r2p4-one-stack.svg)

통합니다. 작업 순서, 비전, 좌표계, 목표 자세, 잡는 위치처럼 내가 짠 코드 대부분은 로봇이 바뀌어도 바뀌지 않아요. 갈아 끼우는 건 2부의 설계도(URDF)와 드라이버(ros2_control 하드웨어 인터페이스), 3부의 MoveIt 설정 세 가지입니다. UR은 이 셋을 `ur_description`, `ur_robot_driver`, `ur_moveit_config` 패키지로 제공하고, 컨트롤러 쪽에는 External Control URCap을 설치합니다(PolyScope 5는 URCap, PolyScope X는 URCapX). 화낙도 공식 ROS 2 설명·드라이버·MoveIt 설정 패키지(`fanuc_description`, `fanuc_driver`, `fanuc_moveit_config`)를 내고 있어요. 이 교체를 작게 유지하려면 로봇 이름이나 관절 번호를 내 코드에 박아 두지 마세요.

## 처음 하는 사람이 거의 다 겪는 여섯 가지

마지막으로, 이 시리즈에서 나온 함정에 실물로 넘어갈 때 만나는 것 두 가지를 더해 한곳에 모았습니다.

![흔한 함정 여섯 가지와 확인법](../assets/diagrams/r2p4-traps.svg)

처음 몇 주의 디버깅 시간은 대부분 이 여섯 칸에서 나옵니다. 앞의 네 칸은 [1부](ros2-for-robot-programmers.md)와 [2부](ros2-robot-description.md)에서 다뤘고, 좌표계 착각에는 2부의 시간 함정(사진 찍은 시각의 변환을 쓰지 않는 실수)도 포함됩니다. 포트 충돌은 이런 상황이에요. 카메라 제조사의 설정 프로그램을 켜 둔 채 ROS 카메라 드라이버를 실행하거나, 펜던트 쪽 도구와 ROS 드라이버가 같은 로봇 연결을 동시에 잡으려 하면, 둘 중 하나는 장치를 열지 못하고 알 수 없는 에러를 냅니다. 시뮬레이션은 접촉 힘이 근사치일 뿐이고 실물 로봇에는 시뮬레이터가 모르는 캘리브레이션 오차가 있으니, 실물은 느린 속도로(펜던트의 T1처럼), 비상정지 버튼을 손 닿는 곳에 두고 시작하세요.

---

## 시리즈를 한 장으로

![카메라에서 컨트롤러까지, 어디서 무엇을 봤나](../assets/diagrams/r2p4-series-map.svg)

| 펜던트에서 하던 것 | ROS 2에서 | 어디서 봤나 |
|---|---|---|
| 프로그램 하나 | 여러 노드의 그래프 | 1부 |
| 신호, 레지스터, `CALL` | 토픽, 서비스, 액션 | 1부 |
| 컨트롤러에 내장된 로봇 모델 | URDF | 2부 |
| UFRAME · UTOOL | TF2 / TF 트리 | 2부 |
| 모션 엔진 + 외부 명령 창구 | ros2_control (컨트롤러 + 하드웨어 인터페이스) | 2부 |
| ROBOGUIDE · URSim | mock 하드웨어 | 2부 |
| 펜던트 3D 화면 | RViz | 2부 |
| 경유점 티칭 | move_group에 목표 주기 | 3부 |
| CONFIG | IK 답 고르기 | 3부 |
| J · L · C | Pilz PTP · LIN · CIRC | 3부 |
| 조그 | MoveIt Servo | 3부 |
| 간섭 영역 | 플래닝 씬 (안전 기능은 로봇 컨트롤러에 남음) | 3부 |
| 비전 보정 (VOFFSET) | 티칭 경로 + 오프셋 (그대로 유효, 사다리 2단) | 3부 |
| 합격/불합격 판정 | 그대로 센서·게이지·PLC 인터록 (인식은 관문을 거쳐 움직임에만) | 1·4부 |
| (CPU로는 느린 인식·계획) | Isaac ROS · NITROS · cuMotion | 4부 |

로봇 컨트롤러가 하던 "안전하게 움직이기"는 그대로 두고, 사람이 가르치던 "어디로, 어떻게"만 여러 회사의 프로그램이 대화하며 계산하게 만든다. 네 편에서 본 게 모두 이 이야기였습니다. 펜던트로 로봇을 다뤄 본 경험은 여기서도 쓸모가 있어요. 좌표계와 툴, 이동 방식과 안전을 이미 아는 사람은 ROS를 훨씬 빨리 익힙니다.

### 더 읽을 곳

위에서부터 읽으세요. 앞 문서를 알고 나면 뒤 문서가 훨씬 잘 읽힙니다. 각 문서는 쓰는 버전(예: Humble)에 맞춰 고르세요.

1. **ROS 2 튜토리얼** (docs.ros.org): 노드, 토픽, launch, TF2
2. **MoveIt 2 튜토리얼** (moveit.picknik.ai): 플래닝, 플래닝 씬, Pilz
3. **Universal Robots ROS 2 드라이버 문서** (docs.universal-robots.com): URSim, External Control, 힘 모드
4. **FANUC ROS 2 드라이버** (FANUC-CORPORATION/fanuc_driver): 화낙 쪽 연결
5. **Isaac ROS 문서** (nvidia-isaac-ros.github.io): GPU 패키지, NITROS, cuMotion, XRDF

---

**시리즈** · [← 이전 글: 3부 — MoveIt 2](moveit2-goals-not-points.md)

*관련: [Physical AI를 고르는 법 — Track 0·A·B](choosing-physical-ai.md) · [3부 — MoveIt 2](moveit2-goals-not-points.md) · [로봇의 뇌를 엣지에 올리기 (2) — Isaac ROS와 파운데이션 모델](jetson-isaac-foundation-models.md) · [세 모델의 안쪽](inside-the-models.md) · [직접 해 보기: 실습 노트 (0) — SO-101과 URSim](learn-without-industrial-robot.md)*

### 출처와 표기

Isaac ROS의 구성, NITROS, cuMotion과 MoveIt 2 플러그인, XRDF의 내용, 릴리스별 대상 버전(3.2 Humble·JetPack 6, 4.x Jazzy·JetPack 7, 5.0 ROS 2 Lyrical과 NITROS의 ROS 2 편입)은 NVIDIA Isaac ROS 공식 문서와 릴리스 노트를 근거로 했습니다. 210 ms는 [현장 노트](jetson-isaac-foundation-models.md)에서 직접 측정한 값이며 장면·설정·버전에 따라 달라집니다. UR 패키지와 External Control(URCap/URCapX)은 Universal Robots ROS 2 드라이버 문서를, 화낙 드라이버는 FANUC Corporation의 `fanuc_driver` 저장소를 참고했습니다. ROS는 Open Source Robotics Foundation(Open Robotics)의, MoveIt은 PickNik Inc.의, NVIDIA·Isaac ROS·Isaac Sim·Jetson·Orin·Thor·JetPack·TensorRT·CUDA·cuMotion·nvblox는 NVIDIA Corporation의, Docker는 Docker, Inc.의, Linux는 Linus Torvalds의, Pilz는 Pilz GmbH & Co. KG의, SAM은 Meta의, FANUC·ROBOGUIDE는 FANUC Corporation의, Universal Robots·UR·URSim·URCaps·PolyScope는 Universal Robots A/S(Teradyne 계열)의 상표이며, 지칭 목적으로만 사용했습니다.

### 용어 설명

- *Isaac ROS*: 무거운 계산을 GPU로 하는 NVIDIA의 ROS 2 패키지 모음
- *GPU*: 같은 계산을 대량으로 동시에 처리하는 그래픽 처리 장치
- *TensorRT · 엔진 빌드*: GPU에서 신경망을 빠르게 실행하는 NVIDIA 도구 · 모델을 그 GPU에 맞게 미리 변환하는 과정
- *NITROS*: Isaac ROS 3.x·4.x에서 노드끼리 데이터를 GPU 메모리에 둔 채 넘기는 방식. 5.0부터는 ROS 2 Lyrical의 기본 기능으로 대체
- *구성 가능 노드(composable node)*: 여러 노드를 한 프로세스 안에 묶어 실행하는 ROS 2 방식
- *JetPack*: Jetson 보드용 NVIDIA 운영체제 묶음 (리눅스, GPU 드라이버, CUDA 등)
- *컨테이너*: 소프트웨어 환경을 통째로 묶어 어느 컴퓨터에서나 똑같이 실행하게 하는 방식 (도커)
- *cuMotion*: MoveIt 2의 플래너 자리에 꽂히는 NVIDIA의 GPU 모션 플래너
- *XRDF*: cuMotion용으로 URDF를 보완하는 파일. 충돌용 공, 자기 충돌 규칙, 툴 좌표계, 가속도·저크 한계
- *URCap · URCapX*: UR 펜던트(PolyScope 5 · PolyScope X)에 설치하는 확장 기능
- *관문*: 인식 결과를 움직임에 쓰기 전에 신뢰도와 누적 공차 범위를 검사하는 단계
- *신뢰도 · 맞춤 오차*: 모델이 스스로 내는 확신 점수 · CAD를 맞춘 뒤 남는 거리
- *frame_id*: ROS 메시지에 붙는, 어느 좌표계 기준인지 적은 이름
