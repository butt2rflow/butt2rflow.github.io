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
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import morning_brief as mb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DIR = ROOT / "brief_review"
MODEL = "claude-opus-5-5"


# ============================================================
# Tables
# ============================================================
EP_GAP = 10          # rows more than 10 sessions apart start a new episode
BOOT_BLOCK = 20      # block length for the bootstrap (≥ the 10/20-session horizons)
BOOT_REPS = 400
RNG = np.random.default_rng(7)


def _episodes(mask: pd.Series, pos: pd.Series) -> int:
    p = pos[mask]
    return int((p.diff().fillna(EP_GAP + 1) > EP_GAP).sum())


def _boot_ci(hit: pd.Series, pos: pd.Series) -> tuple[float, float]:
    """Block bootstrap over consecutive-session blocks: daily rows with
    10-session windows overlap, so an iid CI would be far too narrow."""
    if len(hit) < 5:
        return (np.nan, np.nan)
    blocks = (pos // BOOT_BLOCK).values
    keys = np.unique(blocks)
    grouped = {k: hit.values[blocks == k] for k in keys}
    est = []
    for _ in range(BOOT_REPS):
        pick = RNG.choice(keys, size=len(keys), replace=True)
        v = np.concatenate([grouped[k] for k in pick])
        est.append(v.mean())
    return tuple(np.percentile(est, [2.5, 97.5]))


def diff_pvalues(bf: pd.DataFrame, masks: dict[str, pd.Series]) -> dict[str, float]:
    """Two-sided block-bootstrap p-value for P(dd10≤−2%) | signal minus
    P(dd10≤−2%) on all days. The same resampled blocks feed both means, so
    the overlap between signal days and all days is respected."""
    hit = (bf.h10_maxdd <= -2).values.astype(float)
    blocks = (bf.pos // BOOT_BLOCK).values
    keys = np.unique(blocks)
    idx_by = {k: np.flatnonzero(blocks == k) for k in keys}
    m_arr = {name: m.values for name, m in masks.items()}
    diffs = {name: [] for name in masks}
    for _ in range(BOOT_REPS):
        ix = np.concatenate([idx_by[k] for k in RNG.choice(keys, size=len(keys), replace=True)])
        h_all = hit[ix].mean()
        for name, m in m_arr.items():
            sel = m[ix]
            if sel.any():
                diffs[name].append(hit[ix][sel].mean() - h_all)
    out = {}
    for name, ds in diffs.items():
        ds = np.asarray(ds)
        out[name] = 1.0 if ds.size == 0 else min(1.0, 2 * min((ds <= 0).mean(), (ds >= 0).mean()))
    return out


def holm(p: dict[str, float]) -> dict[str, float]:
    """Holm–Bonferroni step-down adjustment across the monthly signal set."""
    items = sorted(p.items(), key=lambda kv: kv[1])
    m, run, adj = len(items), 0.0, {}
    for i, (k, v) in enumerate(items):
        run = max(run, min(1.0, (m - i) * v))
        adj[k] = run
    return adj


def _agg(g: pd.DataFrame) -> dict:
    hit = (g.h10_maxdd <= -2).astype(float)
    lo, hi = _boot_ci(hit, g.pos)
    pre, post = g[g.index < "2020"], g[g.index >= "2020"]
    return {"n": len(g),
            "에피소드": _episodes(g.vix.notna(), g.pos) if len(g) else 0,
            "P(dd10≤−2%)": hit.mean(),
            "95% CI": f"{lo:.0%}–{hi:.0%}" if np.isfinite(lo) else "",
            "~2019": (pre.h10_maxdd <= -2).mean() if len(pre) else np.nan,
            "2020~": (post.h10_maxdd <= -2).mean() if len(post) else np.nan,
            "P(dd10≤−5%)": (g.h10_maxdd <= -5).mean(),
            "ret20 중앙": g.h20_ret.median(),
            "VIX−RV20 중앙": (g.vix - g.h20_rv).median(),
            "SKEW 20일 변화 중앙": g.h20_skew_chg.median()}


def _table(rows: dict[str, dict]) -> str:
    df = pd.DataFrame(rows).T
    pct = {c for c in df.columns if c.startswith("P(") or c in ("~2019", "2020~")}
    out = df.copy()
    for c in out.columns:
        out[c] = [("" if (not isinstance(v, str) and pd.isna(v)) else v if isinstance(v, str)
                   else f"{v:.0%}" if c in pct
                   else f"{int(v):,}" if c in ("n", "에피소드") else f"{v:+.2f}") for v in df[c]]
    return out.to_markdown()


def vix_band_table(bf: pd.DataFrame) -> str:
    """State vs outcome within VIX bands — separates 'stress on top of the
    VIX level' from 'VIX is high' (🔴 is largely a VIX-level proxy)."""
    bands = [(0, 16), (16, 20), (20, 25), (25, 35), (35, 200)]
    rows = {}
    for lo, hi in bands:
        x = bf[(bf.vix >= lo) & (bf.vix < hi)]
        if x.empty:
            continue
        base = (x.h10_maxdd <= -2).mean()
        row = {"n": len(x), "밴드 전체": base}
        for s in ("🟢", "🟡", "🔴"):
            g = x[x.state == s]
            row[f"{s} (n)"] = len(g)
            row[s] = (g.h10_maxdd <= -2).mean() if len(g) else np.nan
        rows[f"VIX {lo}–{hi if hi < 200 else '+'}"] = row
    df = pd.DataFrame(rows).T
    out = df.copy()
    for c in out.columns:
        out[c] = [("" if pd.isna(v) else f"{int(v):,}" if "(n)" in c or c == "n" else f"{v:.0%}")
                  for v in df[c]]
    return out.to_markdown()


def backfill_tables(bf: pd.DataFrame) -> str:
    bf = bf.dropna(subset=["h10_maxdd", "h20_ret"]).copy()
    bf["pos"] = np.arange(len(bf))
    bf["vrp_top20"] = bf.vrp >= bf.vrp.rolling(252).quantile(0.8)

    def flags(x: pd.DataFrame) -> dict[str, pd.Series]:
        return {
            "전체": x.vix.notna(),
            "SKEW 5일 ≥ +8": x.skew_5d >= mb.HEDGE_SKEW_5D,
            "SKEW 1년 ≥ 90%": x.skew_pct >= mb.HEDGE_SKEW_PCT,
            "COR90D 5일 ≥ +4": x.cor90d_5d >= mb.HEDGE_COR90D_5D,
            "VIX/VIX3M ≥ 0.95": x.vix_vix3m >= mb.STRESS_VIX_VIX3M,
            "VVIX 1년 ≥ 90%": x.vvix_pct >= mb.STRESS_VVIX_PCT,
            "(참고) VVIX ≥ 105 — 이전 규칙": x.vvix >= 105,
            "VIX9D/VIX > 1": x.vix9d_vix > 1,
            # Display-only in the brief ("VIX 옵션 보험료"); tracked here in case it earns more.
            "VolVol 데드 (어깨 경고 후보)": ~x.volvol_golden.astype(bool),
            "VVIX 잔차 상위 20% (VIX옵션 비쌈)": x.vvix_resid_pct >= mb.VVIX_RICH,
            "VVIX 잔차 하위 20% (VIX옵션 쌈)": x.vvix_resid_pct <= mb.VVIX_CHEAP,
            "VRP < 0": x.vrp < 0,
            "VRP 1년 상위 20%": x.vrp_top20,
        }

    parts = []
    for label, sub in (("전 기간 — 판단 근거", bf), ("최근 12개월 — 참고용(서술)", bf.iloc[-252:])):
        by_state = {s: _agg(g) for s, g in sub.groupby("state")}
        fl = flags(sub)
        by_flag = {k: _agg(sub[v]) for k, v in fl.items()}
        by_flag["전체"]["에피소드"] = np.nan    # one continuous run; not meaningful
        if label.startswith("전 기간"):
            p_holm = holm(diff_pvalues(sub, {k: v for k, v in fl.items() if k != "전체"}))
            for k, p in p_holm.items():
                floor = 2 / BOOT_REPS          # bootstrap resolution
                by_flag[k]["vs 전체 p(Holm)"] = f"<{floor:.3f}" if p < floor else f"{p:.3f}"
        parts.append(f"### 백필 — {label} ({sub.index[0]} → {sub.index[-1]})\n\n"
                     f"상태별\n\n{_table(by_state)}\n\n신호별\n\n{_table(by_flag)}")
        if label.startswith("전 기간"):
            parts.append(f"VIX 밴드별 상태 (P(dd10≤−2%))\n\n{vix_band_table(sub)}")
    parts.append("_n은 겹치는 일별 행 수, '에피소드'는 10거래일 넘게 떨어진 독립 구간 수입니다. "
                 "판단은 에피소드와 블록 부트스트랩 95% CI로 하고, 신호별 'vs 전체 p(Holm)'은 "
                 "매달 여러 신호를 비교하는 다중비교를 보정한 값입니다(0.05 미만만 의미 있게 봅니다). "
                 "최근 12개월 표의 끝은 "
                 "결과 창(20거래일)이 끝난 날까지라 오늘보다 약 한 달 앞섭니다._")
    return "\n\n".join(parts)


THRESH_HEADER = "## Signals and current thresholds"


def _section(md: str, header: str) -> str | None:
    i = md.find(header)
    if i < 0:
        return None
    j = md.find("\n## ", i + len(header))
    return md[i:] if j < 0 else md[i:j]


def guard_thresholds(old: str, new: str) -> tuple[str, bool]:
    """The thresholds are code constants (morning_brief.HEDGE_*/STRESS_*);
    the review may only *propose* changing them, in the report. Keep the
    playbook's threshold table as it was so it can't drift from the code."""
    o, n = _section(old, THRESH_HEADER), _section(new, THRESH_HEADER)
    if o is None or n is None or o.strip() == n.strip():
        return new, False
    return new.replace(n, o), True


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
   playbook의 'Open questions' 중 이번 데이터로 답할 수 있는 것은 답합니다
   (예: gex_live와 gex_published가 실제로 다른지, 프리마켓 VIX가 찍혔는지).
   임계값·판정 규칙을 바꿔야 한다고 판단하면 '제안'으로 보고서에만 쓰고 근거(에피소드 수, CI,
   2019 이전/2020 이후 각각의 결과)를 붙입니다. 실제 변경은 사람이 코드와 함께 합니다.
2. playbook_md: 수정된 playbook 전체. 'Change rules'를 반드시 지킵니다.
   'Signals and current thresholds' 표는 코드 상수와 같아야 하므로 고치지 않습니다(코드가 되돌립니다).
   'Findings'와 'Open questions'만 근거가 있을 때 갱신합니다. 판단은 '전 기간' 표로만 하고,
   '최근 12개월' 표는 서술용입니다. n(겹치는 일수)이 아니라 에피소드 수와 95% CI를 근거로 쓰고,
   9개 신호를 매달 보는 다중비교라는 점을 감안해 우연한 차이를 발견으로 올리지 않습니다.
   범위를 변동성·보험료 밖으로 넓히지 않습니다. 바꿀 근거가 없으면 기존 내용을 그대로 둡니다.
3. changes: playbook에서 바꾼 점을 한 줄씩. 없으면 빈 목록.
백필은 GEX·풋/콜·VX 곡선 이력이 없어 일부 신호만 담고 있다는 한계를 감안합니다.
🔴 상태는 상당 부분 VIX 수준의 대리변수이므로 'VIX 밴드별 상태' 표로 수준 효과를 걷어내고 읽습니다."""

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
    month = (args.month or os.environ.get("REVIEW_MONTH", "").strip()
             or (pd.Timestamp(now.date()).replace(day=1) - pd.Timedelta(days=1)).strftime("%Y-%m"))
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        sys.exit(f"Invalid month {month!r}; expected YYYY-MM")
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
            new_pb, reverted = guard_thresholds(playbook, out["playbook_md"])
            if reverted:
                changes.append("(코드가 되돌림) 임계값 표 수정 시도 — 임계값은 코드 상수라 보고서의 제안으로만 남김")
            if new_pb.strip() != playbook.strip():
                mb.PLAYBOOK.write_text(new_pb.rstrip() + "\n", encoding="utf-8")
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
