---
title: "실습 노트 (0) — 실물 산업용 로봇 없이 배우기: SO-101과 URSim"
nav_title: "0부 · 실물 로봇 없이 배우기"
date: 2026-09-28
tags: [physical-ai, hands-on, ros2, moveit2, isaac-ros, so-101, ursim, jetson]
lang: ko
description: "실물 UR이나 화낙을 붙여 배우기는 어렵다. 가상 컨트롤러(URSim, ROBOGUIDE)와 작은 실물 팔(SO-101)을 연습장으로 쓰면 무엇을 배우고 무엇은 못 배우는지, 무엇이 실물로 옮겨 가는지, 그리고 Jetson Orin NX와 엮는 구성과 앞으로의 실습 계획."
---

# 실습 노트 (0) — 실물 산업용 로봇 없이 배우기: SO-101과 URSim

> **실습 노트 · 0부.** 개념 글([펜던트에서 ROS 2로](ros2-for-robot-programmers.md), [Physical AI를 고르는 법](choosing-physical-ai.md))에서 설명한 것을 직접 해 보며 기록하는 시리즈의 첫 글입니다. 이 글은 연습장을 고르는 계획 글이고, 결과는 해 본 뒤에 씁니다.

ROS 2, MoveIt 2, Isaac ROS를 글로 읽었다면, 다음은 로봇을 직접 움직여 볼 차례입니다. 그런데 배우는 단계에서 실물 UR이나 화낙을 붙이기는 쉽지 않아요.

![배우는 단계에서 실물을 붙이기 어려운 세 가지](../assets/diagrams/hon-why-not-real.svg)

이 글은 쓸 수 있는 연습장을 비교하고, 각각이 무엇을 가르쳐 주는지, 무엇이 실물로 옮겨 가는지를 정리합니다.

---

## 30초 요약

- 연습장은 크게 두 종류입니다. 진짜 컨트롤러 소프트웨어를 가상으로 실행하는 **URSim**(UR)과 **ROBOGUIDE**(화낙), 그리고 작은 실물 교육용 팔인 **SO-101**.
- 둘이 가르쳐 주는 게 거의 겹치지 않습니다. 산업용 드라이버와 안전 설정은 URSim, 카메라와 물리와 시연 학습은 SO-101.
- 작업 순서, 좌표계, MoveIt 사용법, 비전 코드는 실물로 그대로 옮겨 가고, 설계도(URDF)·드라이버·MoveIt 설정만 갈아 끼웁니다. 실제 안전 인증과 하중은 실물에서만 배웁니다.
- Jetson Orin NX가 양쪽의 ROS 2 두뇌 역할을 하고, 앞으로 여섯 편에 걸쳐 실제로 해 본 결과를 씁니다.

---

## 연습장 셋, 그리고 실물

![서로 가르쳐 주는 게 거의 겹치지 않는다](../assets/diagrams/hon-four-grounds.svg)

**URSim**은 UR이 무료로 제공하는 가상 컨트롤러입니다. 펜던트 화면까지 그대로 떠서, 진짜 UR ROS 2 드라이버를 붙이면 실물과 거의 같은 방식으로 명령이 오가요. 속도 조절이나 보호 정지 같은 산업용 동작도 볼 수 있습니다. **화낙** 쪽은 공식 ROS 2 드라이버가 ROBOGUIDE의 가상 로봇을 제어할 수 있지만, ROBOGUIDE는 유료 라이선스이고 가상 컨트롤러에도 스트리밍 옵션(J519·R912)이 필요합니다. 로봇 없이 명령받은 대로 움직였다고만 대답하는 mock 하드웨어([펜던트 2부](ros2-robot-description.md))는 UR·화낙 드라이버가 모두 지원해서, 드라이버와 MoveIt 연결까지는 무료로 연습할 수 있어요.

**SO-101**은 오픈소스 교육용 팔로, 사람이 움직이는 리더 팔과 따라 하는 팔로워 팔이 짝을 이룹니다. 관절 5개와 그리퍼로 실제 물체를 집을 수 있고, 카메라를 붙이면 인식부터 시연 학습까지 한 팔로 다룰 수 있습니다.

## 무엇이 실물로 옮겨 가나

![위층은 그대로, 아래층은 교체, 맨 아래는 실물에서](../assets/diagrams/hon-what-transfers.svg)

[펜던트에서 ROS 2로 4부](isaac-ros-gpu.md)의 "한 스택, 여러 로봇"을 연습 관점에서 다시 본 그림입니다. 맨 아래층은 연습장이 대신할 수 없으니, 실물로 넘어갈 때 느린 속도와 위험성 평가부터 다시 시작합니다.

## URSim 연습장 구성

![가상 UR 컨트롤러에 진짜 ROS 2 드라이버를 붙인다](../assets/diagrams/hon-ursim-setup.svg)

e-Series URSim은 x86용이라 PC에서 실행하고, Jetson은 같은 네트워크로 붙이는 구성이 무난합니다. PolyScope X 시뮬레이터라면 arm64 이미지가 있어 Jetson 한 대로 모두 실행하는 것도 방법입니다(이때는 External Control URCapX를 씁니다).

## SO-101 연습장 구성

![작은 실물 팔 하나로 Track A와 B를 모두](../assets/diagrams/hon-so101-setup.svg)

Track 0·A·B는 [고르는 법](choosing-physical-ai.md)의 세 가지 설계입니다. SO-101은 LeRobot이 기본으로 지원해서 시연 기록과 학습(Track B, 시연 학습)은 바로 시작할 수 있습니다. ROS 2 쪽(Track A, 인식 + 플래너)은 커뮤니티가 만든 패키지를 씁니다. URDF, 서보용 ros2_control 드라이버, MoveIt 2 설정이 들어 있는 저장소가 여럿 있으니, 실습 2부에서 어떤 것을 왜 골랐는지 적겠습니다.

## 연습장과 개념 글의 짝

![개념 글과 실습이 짝을 이룬다](../assets/diagrams/hon-map.svg)

펜던트 1~3부를 읽었다면 URSim부터, 학습 정책 글을 읽었다면 SO-101부터 시작하면 됩니다.

## 연습장의 한계

![연습장이 알려 주지 않는 것](../assets/diagrams/hon-limits.svg)

SO-101에서 집기가 실패하면, 비전이 틀렸는지 팔이 부정확했는지부터 가려야 합니다. 그래서 비교 실험(6부)에서는 같은 팔, 같은 블록, 같은 조건으로 20회씩 반복하고, 팔 자체의 반복 정밀도도 따로 재 둘 계획입니다.

## 앞으로의 실습

![해 본 만큼 쓴다](../assets/diagrams/hon-roadmap.svg)

순서는 이렇게 잡았습니다. 시연을 따라 하는 팔을 먼저 보면 캘리브레이션 같은 지루한 단계를 버틸 힘이 생길 것 같았고, 인식과 제어는 따로 디버깅해야 원인을 찾기 쉽다고 봤어요. 각 편은 실제로 해 본 뒤에 쓰고, 막혔던 곳과 푼 방법을 그대로 적겠습니다.

---

## 정리

| 연습장 | 배우는 것 | 못 배우는 것 |
|---|---|---|
| **URSim** (무료) | UR 드라이버, External Control, 속도 조절, 보호 정지, 펜던트 1~3부 내용 | 카메라, 물리, 집기 |
| **화낙 가상** (ROBOGUIDE 유료) | 화낙 드라이버 연결, MoveIt 설정 | (ROS 2 경로 기준) 카메라, 물리 |
| **mock 하드웨어** (무료, UR·화낙 공통) | 드라이버와 MoveIt 연결 | 실제 컨트롤러 동작 전부 |
| **SO-101** (저렴) | 물리, 카메라, 캘리브레이션, Isaac ROS, 시연 학습 | 산업용 컨트롤러 동작, 정밀도 |
| **실물 산업용** | 전부, 특히 안전 인증과 실제 하중 | (구하기 어려움) |

---

**시리즈** · 다음: 실습 노트 1부, SO-101 조립과 시연 기록 (준비 중)

*관련: [펜던트에서 ROS 2로 1부](ros2-for-robot-programmers.md) · [Physical AI를 고르는 법](choosing-physical-ai.md) · [학습 정책(Track B)](learned-policy-track-b.md) · [로봇의 뇌를 엣지에 올리기 (1)](jetson-ros2-setup.md) · [카메라는 몇 대, 어디에](camera-placement.md)*

### 출처와 표기

URSim의 도커 이미지와 지원 아키텍처는 Universal Robots의 ROS 2 드라이버 문서와 Docker Hub의 공식 이미지(universalrobots/ursim_e-series, ursim_polyscopex)를, 화낙 가상 로봇과 mock 모드는 FANUC Corporation의 FANUC ROS 2 Driver 문서를, SO-101의 하드웨어 설계는 TheRobotStudio의 오픈소스 SO-ARM100 저장소를, ROS 2 지원은 커뮤니티 저장소들과 Hugging Face LeRobot 문서를 참고했습니다. 이 글은 실습 전의 계획이며, 구성과 결과는 실제로 해 보며 바뀔 수 있습니다. Universal Robots·UR·URSim·URCaps·PolyScope는 Universal Robots A/S(Teradyne 계열)의, FANUC·ROBOGUIDE·HandlingPRO는 FANUC Corporation의, NVIDIA·Jetson·Orin·Isaac ROS·cuMotion·FoundationPose는 NVIDIA Corporation의, Feetech는 Shenzhen Feetech RC Model Co., Ltd.의, Hugging Face·LeRobot은 Hugging Face, Inc.의, Docker는 Docker, Inc.의, ROS는 Open Source Robotics Foundation(Open Robotics)의, MoveIt은 PickNik Inc.의 상표이며, 지칭 목적으로만 사용했습니다.

### 용어 설명

- *연습장*: 실물 산업용 로봇 대신 배울 수 있는 환경. 가상 컨트롤러나 작은 실물 팔
- *URSim*: UR의 가상 컨트롤러. 실제 컨트롤러 소프트웨어와 펜던트 화면을 PC에서 실행한다
- *ROBOGUIDE*: 화낙의 오프라인 프로그래밍·시뮬레이션 소프트웨어 (유료)
- *mock 모드*: 로봇 없이 명령받은 대로 움직였다고 대답하는 가짜 하드웨어
- *SO-101*: 리더 팔과 팔로워 팔로 이뤄진 오픈소스 교육용 로봇 팔. 관절 5개 + 그리퍼
- *External Control*: UR 컨트롤러가 외부 컴퓨터의 명령을 받도록 해 주는 확장 기능(URCap, PolyScope X에서는 URCapX)
- *URDF*: 로봇의 링크와 관절, 모양을 적은 설계도 파일
- *ros2_control*: ROS 2가 모터 드라이버와 명령을 주고받는 표준 틀. 실물과 mock을 갈아 끼울 수 있다
- *Track 0·A·B*: 기하학 매칭(0, 신경망 없음), 인식 + 플래너(A), 시연 학습 정책(B)의 세 가지 설계
- *리더 팔 · 팔로워 팔*: 사람이 손으로 움직이는 팔 · 그 움직임을 따라 하는 팔
- *핸드아이 캘리브레이션*: 카메라가 본 위치를 로봇 좌표로 바꾸는 관계를 재는 작업
- *속도 조절 · 보호 정지*: 펜던트에서 속도를 낮추는 기능 · 충돌이나 한계 초과 시 로봇이 스스로 멈추는 상태
- *에뮬레이션*: 다른 종류의 프로세서용 프로그램을 흉내 내서 실행하는 방식. 느려질 수 있다
- *반복 정밀도*: 같은 점으로 몇 번 돌아와도 얼마나 같은 자리에 오는지
