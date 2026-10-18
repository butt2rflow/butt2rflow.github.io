"""
Monthly review of the morning briefing — compares what the briefings said
with what happened, and proposes playbook edits.

Inputs:  brief_log/*.json (live, scored by score_briefs.py)
         brief_log/backfill.csv (template replayed over history, scored)
         brief_playbook.md (current rules)
Outputs: brief_review/<YYYY-MM>.md (report: tables + Claude's read)
         brief_playbook.md (Claude's proposed revision — lands via PR)

Run from project root (after score_briefs.py):
    python scripts/review_briefs.py            # needs ANTHROPIC_API_KEY
    python scripts/review_briefs.py --no-llm   # tables only
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import morning_brief as mb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DIR = ROOT / "brief_review"
MODEL = "claude-opus-5-5"


# ============================================================
# Tables
# ============================================================
def _agg(g: pd.DataFrame) -> dict:
    return {"n": len(g),
            "P(dd10≤−2%)": (g.h10_maxdd <= -2).mean(),
            "P(dd10≤−5%)": (g.h10_maxdd <= -5).mean(),
            "dd10 중앙": g.h10_maxdd.median(),
            "ret20 중앙": g.h20_ret.median(),
            "VIX−RV20 중앙": (g.vix - g.h20_rv).median(),
            "SKEW 20일 변화 중앙": g.h20_skew_chg.median()}


def _table(rows: dict[str, dict]) -> str:
    df = pd.DataFrame(rows).T
    fmt = {c: (lambda v: f"{v:.0%}") for c in df.columns if c.startswith("P(")}
    out = df.copy()
    for c in out.columns:
        out[c] = [("" if pd.isna(v) else fmt[c](v) if c in fmt
                   else f"{int(v):,}" if c == "n" else f"{v:+.2f}") for v in df[c]]
    return out.to_markdown()


def backfill_tables(bf: pd.DataFrame) -> str:
    bf = bf.dropna(subset=["h10_maxdd", "h20_ret"]).copy()
    bf["vrp_top20"] = bf.vrp >= bf.vrp.rolling(252).quantile(0.8)

    def flags(x: pd.DataFrame) -> dict[str, pd.Series]:
        return {
            "전체": x.vix.notna(),
            "SKEW 5일 ≥ +8": x.skew_5d >= mb.HEDGE_SKEW_5D,
            "SKEW 1년 ≥ 90%": x.skew_pct >= mb.HEDGE_SKEW_PCT,
            "COR90D 5일 ≥ +4": x.cor90d_5d >= mb.HEDGE_COR90D_5D,
            "VIX/VIX3M ≥ 0.95": x.vix_vix3m >= mb.STRESS_VIX_VIX3M,
            "VVIX ≥ 105": x.vvix >= mb.STRESS_VVIX,
            "VIX9D/VIX > 1": x.vix9d_vix > 1,
            "VRP < 0": x.vrp < 0,
            "VRP 1년 상위 20%": x.vrp_top20,
        }

    parts = []
    for label, sub in (("전 기간", bf), ("최근 12개월", bf.iloc[-252:])):
        by_state = {s: _agg(g) for s, g in sub.groupby("state")}
        by_flag = {k: _agg(sub[v]) for k, v in flags(sub).items()}
        parts.append(f"### 백필 — {label} ({sub.index[0]} → {sub.index[-1]})\n\n"
                     f"상태별\n\n{_table(by_state)}\n\n신호별\n\n{_table(by_flag)}")
    return "\n\n".join(parts)


def live_section(month: str | None) -> tuple[str, list[dict]]:
    recs = [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(mb.LOG_DIR.glob("????-??-??.json"))]
    if not recs:
        return "실제 브리핑 기록 없음.", []
    lines = ["| 날짜 | 상태 | 증폭 | h5 최대하락 | h10 최대하락 | h20 수익 | h10 이후 최악 상태 |",
             "|---|---|---|---|---|---|---|"]
    compact = []
    for r in recs:
        o = r.get("outcome") or {}

        def g(h, k):
            v = (o.get(h) or {}).get(k)
            return "" if v is None else (f"{v:+.1f}%" if isinstance(v, float) else str(v))
        lines.append(f"| {r['data_date']} | {r['state']['emoji']} {r['state']['label']} | "
                     f"{'ON' if r.get('amp_on') else 'OFF' if r.get('amp_on') is False else ''} | "
                     f"{g('h5', 'maxdd')} | {g('h10', 'maxdd')} | {g('h20', 'ret')} | "
                     f"{g('h10', 'worst_state')} |")
        if month is None or r["data_date"].startswith(month):
            gex = (r.get("inputs") or {}).get("gex") or {}
            compact.append({"date": r["data_date"], "state": r["state"], "amp_on": r.get("amp_on"),
                            "commentary": r.get("commentary"), "outcome": o,
                            "gex_live": gex.get("net_bn"), "gex_published": gex.get("published_net_bn"),
                            "pre": (r.get("inputs") or {}).get("pre")})
    return "\n".join(lines), compact


# ============================================================
# Claude
# ============================================================
REVIEW_SYSTEM = """당신은 변동성·보험료 관점의 아침 브리핑을 매달 복기하는 분석가입니다.
입력: 현재 playbook, 백필(같은 판정 규칙을 과거에 적용한 결과) 통계표, 실제 브리핑 기록과 그 후 결과.
할 일:
1. report_md: 한국어 복기 보고서. 이번 달 브리핑이 말한 것과 실제 결과를 비교하고, 어떤 신호가
   맞았고 틀렸는지, 해설이 과장하거나 놓친 것이 무엇인지 씁니다. 근거는 표의 숫자와 n을 인용합니다.
   playbook의 '확인할 것' 항목 중 이번 데이터로 답할 수 있는 것은 답합니다
   (예: gex_live와 gex_published가 실제로 다른지, 프리마켓 VIX가 찍혔는지).
2. playbook_md: 수정된 playbook 전체. playbook의 '변경 규칙'을 반드시 지킵니다 —
   n ≥ 30이고 차이가 뚜렷할 때만 임계값·판정 규칙을 바꾸고, 아니면 '발견'이나 '확인할 것'에만 기록합니다.
   범위를 변동성·보험료 밖으로 넓히지 않습니다. 바꿀 근거가 없으면 기존 내용을 그대로 둡니다.
3. changes: playbook에서 바꾼 점을 한 줄씩. 없으면 빈 목록.
백필은 GEX·풋/콜·VX 곡선 이력이 없어 일부 신호만 담고 있다는 한계를 감안합니다."""

SCHEMA = {
    "type": "object",
    "properties": {
        "report_md": {"type": "string"},
        "playbook_md": {"type": "string"},
        "changes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["report_md", "playbook_md", "changes"],
    "additionalProperties": False,
}


def ask_claude(playbook: str, tables: str, live_md: str, live: list[dict]) -> dict | None:
    import anthropic
    client = anthropic.Anthropic()
    content = (f"## 현재 playbook\n\n{playbook}\n\n## 백필 통계\n\n{tables}\n\n"
               f"## 실제 브리핑 결과표\n\n{live_md}\n\n## 이번 달 실제 브리핑 상세\n\n"
               + json.dumps(live, ensure_ascii=False, default=float))
    try:
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=32000,
            output_config={"effort": "high",
                           "format": {"type": "json_schema", "schema": SCHEMA}},
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default"},
            system=REVIEW_SYSTEM,
            messages=[{"role": "user", "content": content}],
        ) as stream:
            resp = stream.get_final_message()
    except anthropic.APIStatusError as e:
        print(f"  [WARN] Claude API {e.status_code}: {e.message}")
        return None
    except anthropic.APIConnectionError as e:
        print(f"  [WARN] Claude API connection failed: {e}")
        return None
    if resp.stop_reason in ("refusal", "max_tokens"):
        print(f"  [WARN] review stopped: {resp.stop_reason}")
        return None
    text = "".join(b.text for b in resp.content if b.type == "text")
    print(f"  usage: in {resp.usage.input_tokens}, out {resp.usage.output_tokens}")
    return json.loads(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--month", help="YYYY-MM under review (default: previous month)")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    month = args.month or (pd.Timestamp(now.date()).replace(day=1)
                           - pd.Timedelta(days=1)).strftime("%Y-%m")
    bf = pd.read_csv(mb.LOG_DIR / "backfill.csv", index_col="date")
    tables = backfill_tables(bf)
    live_md, live = live_section(month)
    playbook = mb.PLAYBOOK.read_text(encoding="utf-8")

    report = [f"# 브리핑 월간 복기 — {month}", "",
              f"_생성 {now:%Y-%m-%d %H:%M} UTC · 백필 {len(bf):,}일 · 실제 기록 "
              f"{len(list(mb.LOG_DIR.glob('????-??-??.json')))}건_", ""]
    changes: list[str] = []
    if not args.no_llm and os.environ.get("ANTHROPIC_API_KEY"):
        out = ask_claude(playbook, tables, live_md, live)
        if out:
            report += ["## 복기", "", out["report_md"], ""]
            changes = out["changes"]
            if changes and out["playbook_md"].strip() != playbook.strip():
                mb.PLAYBOOK.write_text(out["playbook_md"].rstrip() + "\n", encoding="utf-8")
            report += ["## playbook 변경 제안", ""] + ([f"- {c}" for c in changes] or ["- 없음"]) + [""]
    report += ["## 실제 브리핑과 결과", "", live_md, "", "## 백필 통계", "", tables, ""]

    REVIEW_DIR.mkdir(exist_ok=True)
    path = REVIEW_DIR / f"{month}.md"
    path.write_text("\n".join(report), encoding="utf-8")
    print(f"Review: {path} · playbook changes: {len(changes)}")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"month={month}\nchanges={len(changes)}\n")


if __name__ == "__main__":
    main()
