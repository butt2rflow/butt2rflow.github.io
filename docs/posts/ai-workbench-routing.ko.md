---
title: "Claude Code에서 Codex와 로컬 Qwen에 일을 맡기는 MCP 브리지 만들기"
nav_title: "Codex·Qwen MCP 브리지 만들기"
date: 2026-11-17
tags: [local-llm, qwen, ollama, claude-code, codex, muse, mcp]
lang: ko
description: "Claude Code의 요청으로 Codex를 실행하고 재연결 뒤에도 작업을 조회하는 Python stdio 브리지를 만들어요. 이미 로드된 Qwen에 읽기 작업을 맡기는 경로도 추가해요."
---

# Claude Code에서 Codex와 로컬 Qwen에 일을 맡기는 MCP 브리지 만들기

## 1. 위임 흐름 준비하기

Claude Code가 작업을 조율해요. MCP로 범위를 정한 요청을 보내고, 작업 ID를 받아 뒀다가 나중에 결과를 조회해요. 조사·수정·테스트·1차 리뷰는 Codex에 맡겨요. 긴 문서 읽기·목차 만들기·요약은 필요할 때 로컬 Qwen에 맡겨요. 중요한 판단과 최종 검토는 Claude Code가 담당해요.

![Claude Code가 작업을 조율하면서 일부 작업을 도구에 맡겨요](../assets/diagrams/muse-model-or-tool.svg)

Linux 호스트에 Python 3, Git, Claude Code, 로그인된 Codex CLI를 준비해요. 브리지 스크립트 `coop.py`는 `~/ai-cooperation`처럼 신뢰할 수 있고 위임 대상 프로젝트와 분리된 폴더에 둬요. 예제에는 실습용 개인 Git 프로젝트를 써요. 위임은 개인 프로젝트로 한정하고 업무 코드와 문서는 요청에서 제외해요. 이 범위는 호출자가 확인해요.

**확인.** 호스트 셸에서 `python3 --version`, `git --version`, `claude --version`, `codex --version`을 실행해요. 실습 프로젝트와 브리지 폴더가 분리돼 있는지도 확인해요.

[핵심 참고 구현](https://github.com/butt2rflow/butt2rflow.github.io/tree/main/code/claude-codex-bridge)에서 브리지 코드와 테스트를 받을 수 있어요. GPU 레시피 실행기는 공개 코드에서 제외했어요.

## 2. Python stdio 서버 만들기

Python 표준 라이브러리로 `coop.py`를 만들어요. `argparse`로 `serve`와 내부 워커 명령을 나누고, `json`과 `pathlib`로 상태를 기록하고, `subprocess`로 워커를 실행해요. 표준 입력에서 JSON-RPC 메시지를 한 줄씩 읽고, 응답에 요청 ID를 담아 표준 출력으로 한 줄씩 즉시 내보내요. 진단 메시지는 표준 오류로 보내요. `initialize`, `ping`, `tools/list`, `tools/call`을 처리하고, 도구별 입력 스키마를 공개해 호출 전에 인자를 검사해요. [MCP stdio 전송 사양](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)

| 도구 | 구현할 동작 |
|---|---|
| `cooperation_status()` | 최근 작업과 Qwen 사용 가능 여부를 반환해요. |
| `delegate_task(cwd, task, ...)` | 요청을 검사하고 프로젝트 잠금을 얻은 뒤 작업을 저장하고 독립 워커를 시작해요. 모델 응답을 기다리지 않고 ID를 반환해요. |
| `job_result(job_id, detail=false)` | 저장한 상태를 읽고 결과가 나오면 짧은 요약을 반환해요. |

`cwd`와 입력 파일의 실제 경로를 확인해요. 심볼릭 링크를 따라갔을 때도 `cwd` 밖의 파일은 거부해요. Git 작업 트리의 루트를 기준으로 `fcntl.flock`의 비차단 배타 잠금을 걸고, Git 밖에서는 실제 디렉터리를 기준으로 삼아요. 실행 위치는 요청의 `cwd`를 유지해요. 잠금 파일 디스크립터를 워커와 그 자식인 Codex에 넘기면 워커가 죽어도 Codex가 계속 실행되는 동안 잠금이 유지돼요. 직접 연 편집기나 CLI 세션은 별도로 조율해야 해요.

`runs/<id>/`에 `request.json`과 대기 상태인 `state.json`을 먼저 기록해요. 표준 입출력을 별도로 연결하고 `start_new_session=True`로 워커를 띄워요. 상태 파일은 원자적으로 교체하고, 마지막 답변은 `result.md`에 저장해요. 실행 전후 Git 상태와 로그, 인계 기록을 남긴 뒤 최종 상태를 게시해요. 작업 기록은 비공개로 보관하고 요청에 비밀 값을 넣지 않아요.

**확인.** 브리지 폴더에서 초기화와 도구 목록을 요청해요. JSON 응답이 두 줄이고, 두 번째 응답에 도구 세 개가 있어야 해요.

```bash
python3 coop.py serve <<'JSON'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"smoke","version":"1"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
JSON
```

## 3. Claude Code에 브리지 등록하기

사용자 범위로 stdio 서버를 등록해요. `--` 뒤에는 서버를 시작할 명령과 인자를 써요. 브리지 폴더를 다르게 정했다면 스크립트 경로를 바꿔요. [Claude Code MCP 공식 문서](https://code.claude.com/docs/en/mcp)

```bash
claude mcp add --transport stdio --scope user ai-cooperation \
  -- /usr/bin/python3 "$HOME/ai-cooperation/coop.py" serve
```

**확인.** 실습 프로젝트에서 Claude Code를 열고 `/mcp`에 `ai-cooperation`이 연결됐는지 봐요. Claude에게 `cooperation_status`를 호출해 달라고 해요. 브리지가 연결돼도 Qwen을 쓸 수 없는 이유가 표시될 수 있어요.

## 4. 워커에서 Codex 실행하기

명령과 인자는 배열로 만들고, 프롬프트 인자 `-`를 써서 작업 내용을 표준 입력으로 넘겨요. Codex 출력은 `codex.log`에 남기고 마지막 답변은 별도 파일로 받아요. 핵심 읽기 전용 호출을 셸로 옮기면 아래와 같아요. 프로젝트와 결과 파일 경로는 워커에서 정해요.

```bash
codex -a never exec --cd "$project_dir" --sandbox read-only \
  --output-last-message "$result_path" -
```

조사와 리뷰에는 `read-only`를 써요. 수정 권한을 받은 `write=true` 작업만 `workspace-write`로 실행해요. 요청에 적은 허용 파일 목록은 모델에 주는 지침이에요. 샌드박스는 작업 공간 단위로 권한을 제한해요. 샌드박스를 유지하고 권한 우회 플래그는 쓰지 않아요.

Codex는 별도 프로세스 그룹에서 실행해요. 기본 제한은 1,800초이고, 30~7,200초 사이로 지정할 수 있어요. 시간이 지나면 그룹에 SIGTERM을 보내고 Codex 종료를 최대 10초 기다려요. 여전히 종료되지 않으면 그룹에 SIGKILL을 보내요. 상태를 `needs_review`로 남기고 부분 변경을 확인할 수 있게 보존해요.

**확인.** 실습 프로젝트에서 README 읽기를 위임하고 결과와 작업 트리에 변경이 없는지 확인해요. 다음으로 승인한 파일 하나만 고치게 한 뒤 수용 테스트를 직접 실행해요. 가짜 Codex로 시간 초과 시 `needs_review`가 기록되고, 잠금을 잡은 동안 같은 작업 트리의 두 번째 위임이 거부되는지도 확인해요.

## 5. 필요하면 로컬 Qwen 추가하기

![로컬 도구가 경로로 파일을 읽고 짧은 요약을 돌려줘요](../assets/diagrams/muse-read-route.svg)

`target=qwen` 경로의 기본 모델은 `qwen3.8:27b`예요. 서버 환경 변수 `AI_COOP_QWEN_MODEL`로 모델을 바꿀 수 있어요. `urllib.request`로 로컬 Ollama API를 호출해요. 먼저 `nvidia-smi`와 Ollama의 `/api/ps`를 조회해요. Ollama 외의 연산 프로세스가 GPU를 점유하거나, 지정한 모델이 올라와 있지 않거나, CPU 오프로딩이 감지되거나, 조회에 실패하면 거부해요. 크기 정보가 유효하고 `size > 0`, `size_vram >= size`를 만족해야 해요. 작업과 지정한 텍스트를 비스트리밍 `/api/chat`으로 보내기 직전에 다시 검사하고, 초안은 `result.md`에 남겨요. 이 경로에서 PDF는 텍스트를 추출해 넘겨요.

브리지는 모델 로드·해제나 다른 작업 종료 명령을 자동으로 실행하지 않아요. 다만 검사와 호출은 별개라, 그사이에 모델이 내려가면 Ollama 요청이 다시 로드할 수 있고 외부 GPU 작업이 새로 시작될 수도 있어요. GPU를 함께 쓰는 작업을 시작하기 전에 `qwen-disable`로 새 호출을 막고, 실행 중인 Qwen 작업이 끝날 때까지 기다려요. `qwen-enable`은 차단 표시만 해제해요.

기본 경로는 Codex예요. `qwen`을 명시하면 GPU 조건을 충족하지 못할 때 요청이 거부돼요. 읽기 작업에서 `auto`를 선택하면 Qwen을 쓸 수 없을 때 실행 전에 Codex로 배정할 수 있어요. 실행 이후 실패는 기록을 확인해요. 실행 중 모델을 자동으로 바꾸지 않아요.

기존 `local_llm`은 Ollama를 쓰는 별도 MCP 도구예요. 이미 연결돼 있다면 PDF나 오피스 파일을 추출할 때 `task`와 절대 경로인 `file_paths`를 넘겨요. 이 도구에는 별도의 GPU 검사가 있어요. 새 브리지의 가드와 작업 기록은 `delegate_task`를 통한 호출에 적용돼요. [내 GPU 로컬 AI로 Claude 사용량 줄이기](local-llm-reading.md)

**확인.** 테스트용 응답으로 GPU 점유, 모델 미로드, CPU 오프로딩이 각각 거부되는지 확인해요. 호스트에서는 `cooperation_status`로 준비 상태를 봐요. 준비됐다면 `target=qwen`과 `files`에 프로젝트 기준 상대 경로인 작은 텍스트 파일 하나를 지정해 읽기를 맡기고, 요약과 원문을 비교해요. 사전 검사가 막으면 SKIP으로 기록해요.

## 6. 작업 조건을 적고 결과 검증하기

`cwd`에는 실제 프로젝트의 절대 경로를 넣어요. 목표, 수정 허용 범위, 완료 조건, 검증 방법, 워커가 읽을 수 있는 근거 경로를 적어요. 실습 프로젝트라면 다음처럼 작업을 적고 `target=codex`, `write=true`로 `delegate_task`를 호출해요.

- 목표 — 설치 안내에서 잘못된 명령을 고쳐요.
- 수정 범위 — README.md만 수정하고 기존 변경을 보존해요.
- 완료 조건 — 프로젝트 루트에서 안내 명령이 실행돼요.
- 검증 — 안내 명령과 `git diff --check`를 실행하고 결과와 근거 경로를 보고해요.

보고는 짧게 8줄, 800자 이내로 요청해요. 실패를 먼저 적고, 결과와 변경 파일 또는 리뷰 지적, `PASS`·`FAIL`·`NOT RUN`으로 표시한 검증, 남은 결정이나 근거 경로를 받아요. 브리지는 기본 요약을 1,200자로 자르고, 잘렸으면 `summary_truncated`를 표시해요. 더 필요하면 `job_result(job_id, detail=true)`로 최대 12,000자를 조회하거나 디스크의 `result.md` 원문을 열어요.

**확인.** ID를 저장하고 긴 작업은 30~60초 간격으로 `job_result`를 조회해요. 실행 중에는 중간 보고서 없이 상태가 돌아와요. Codex의 `completed`는 프로세스가 성공적으로 끝나 마지막 답변을 남겼다는 뜻이에요. 작업을 받아들이기 전에 보고된 검증 결과와 필요한 파일 또는 테스트 근거를 확인해요.

## 7. 작업 기록으로 문제 해결하기

| 증상 | 확인할 조치 |
|---|---|
| 시작 중 `Read-only file system` | 초기 두 건은 바깥 실행 환경에서 `~/.codex`가 읽기 전용이라 모델 호출 전에 중단됐어요. `codex.log`와 Git 상태 기록을 확인해요. 요청한 프로젝트 샌드박스를 유지하면서 Codex를 초기화할 수 있는 호스트 세션에서 실행해요. |
| 연결 오류 또는 시간 초과 | `/mcp`나 작업 로그에서 어디가 막혔는지 확인해요. Codex가 명시적으로 사용 한도 오류를 보고할 때만 한도 소진으로 판단해요. 실제 소진이 확인되면 Claude가 저장된 기록에서 이어갈 수 있어요. |
| 호출자 연결 종료 | 독립 워커는 계속 실행돼요. 다시 연결해 같은 ID를 조회해요. ID를 잃었다면 다시 요청하기 전에 `cooperation_status`에서 최근 작업을 찾아요. |
| `needs_review` | `state.json`, 로그, `HANDOFF.md`를 열고 전후 Git 상태와 실제 diff를 비교해요. 실패하거나 중단된 작업은 일부 수정이 남을 수 있고, 상태 기록에는 기존 변경도 들어 있어요. 현재 상태에서 마무리할지 재시도할지 판단해요. |

**확인.** 실습 작업에서 ID를 받은 뒤 호출자를 닫아요. 다시 열어 재접수 없이 같은 ID가 최종 상태에 도달하는지 확인해요. MCP 연결을 쓸 수 없으면 브리지 폴더에서 `python3 coop.py result JOB_ID`로 조회해요.

## 8. 어디까지 검증됐는지 확인하기

| 경로 | 기록된 결과 |
|---|---|
| Claude Code 등록과 도구 탐색 | PASS. Claude Code에서 Connected를 확인했고 호스트 검증에서 도구 세 개를 찾았어요. |
| MCP → 실제 Codex | PASS. 읽기와 재연결, 수정과 독립 수용 테스트, 의도적으로 넣은 결함의 읽기 전용 리뷰를 확인했어요. |
| 작업 처리와 GPU 조건 거부 | 자동 테스트 PASS. 호스트에서도 GPU 점유를 감지해 Qwen을 건너뛰었어요. |
| 새 브리지의 MCP → 실제 Qwen | 호스트 검증에서 GPU 점유로 SKIP. 실제 추론은 아직 미검증이에요. |

**확인.** 블로그 저장소의 `code/claude-codex-bridge` 폴더에서 아래 명령을 실행해요. 첫 명령은 모델과 GPU 대신 가짜 응답을 써요. 두 번째는 선택 사항으로, 실습 입력에 실제 Codex를 호출하고 `verification/host-*/REPORT.md`에 결과를 남겨요. 실행하지 않은 검증은 따로 기록해요.

```bash
python3 -m unittest -v test_coop.py
python3 verify_host.py
```

쇼핑 위임은 [Claude Code와 Codex를 MCP로 Muse에 연결하는 법](muse-mcp-shopping.md)에서 볼 수 있어요.
