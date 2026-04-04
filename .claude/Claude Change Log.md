# Claude Change Log — BlogMigration

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
