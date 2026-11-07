// dashboard-wizard.js
// Investor-profile wizard for the daily dashboard. Seven questions feed a
// score table; the result drives the four dashboard axes (Kelly fraction,
// risk-discount profile, equity premium, main/tactical split) by clicking
// the existing toggle buttons from kelly-toggle.js. That way the wizard
// adds zero new state — it just chooses defaults on the user's behalf.
//
// Loaded AFTER kelly-toggle.js so the toggle click handlers are already
// wired when applyResult() dispatches synthetic clicks.

(function () {
  // ---------------------------------------------------------------------
  // Score-table data. Each choice contributes (kelly, discount, premium,
  // split) deltas; bucket ranges below convert sums to dashboard values.
  // ---------------------------------------------------------------------

  const QUESTIONS_KO = [
    {
      id: "age",
      label: "나이대가 어떻게 되시나요?",
      sub: "주식 위험을 회복할 시간 → 분할(Split) · 베팅 크기에 영향",
      choices: [
        { label: "20~30대",   scores: { k: +2, d:  0, p:  0, s: -2 } },
        { label: "40~50대",   scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "60대 이상", scores: { k: -2, d:  0, p:  0, s: +2 } },
      ],
    },
    {
      id: "loss_capacity",
      label: "이 자금의 손실 감당 능력은?",
      sub: "투자 자금의 성격 → Kelly 분율 · Split에 영향",
      choices: [
        { label: "생활자금 — 잃으면 안 됨",  scores: { k: -3, d:  0, p:  0, s: +2 } },
        { label: "일부 손실은 감수 가능",      scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "여유자금 — 회복 가능",      scores: { k: +2, d:  0, p:  0, s: -1 } },
      ],
    },
    {
      id: "risk_tolerance",
      label: "변동성을 어떻게 받아들이시나요?",
      sub: "감내도 → Kelly · 위험 민감도(Discount)에 영향",
      choices: [
        { label: "안정 최우선 — 잘 못 견딘다",        scores: { k: -3, d: -2, p:  0, s:  0 } },
        { label: "약간의 변동은 OK",                   scores: { k: -1, d: -1, p:  0, s:  0 } },
        { label: "큰 변동도 견딜 수 있다",             scores: { k: +1, d:  0, p:  0, s:  0 } },
        { label: "매우 공격적 — 변동성을 즐긴다",      scores: { k: +3, d: +1, p:  0, s:  0 } },
      ],
    },
    {
      id: "target_return",
      label: "목표 수익률은?",
      sub: "기대 프리미엄(μ−r)에 직접 영향",
      choices: [
        { label: "자본 보존 위주 (연 3~5%)",     scores: { k:  0, d:  0, p: -2, s:  0 } },
        { label: "시장 평균 수준 (연 7~10%)",    scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "시장 초과 추구 (연 10%+)",     scores: { k:  0, d:  0, p: +2, s:  0 } },
      ],
    },
    {
      id: "experience",
      label: "주식·옵션 투자 경험은?",
      sub: "신호 해석 경험 → Kelly · Discount에 영향",
      choices: [
        { label: "1년 미만",  scores: { k: -1, d: -2, p:  0, s:  0 } },
        { label: "1~3년",     scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "3~7년",     scores: { k:  0, d: +1, p:  0, s:  0 } },
        { label: "7년 이상",  scores: { k: +1, d: +2, p:  0, s:  0 } },
      ],
    },
    {
      id: "crash_response",
      label: "내일 시장이 30% 폭락한다면?",
      sub: "행동 패턴 → Kelly · Discount에 영향",
      choices: [
        { label: "다 팔겠다 — 더 빠지기 전에",        scores: { k: -2, d: -2, p:  0, s:  0 } },
        { label: "그냥 둔다 — 회복을 기다린다",        scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "더 산다 — 세일이다",                 scores: { k: +2, d: +1, p:  0, s:  0 } },
      ],
    },
    {
      id: "income_need",
      label: "이 포트폴리오에서 월별 현금흐름이 필요한가요?",
      sub: "수익화 요구 → 프리미엄 · Split에 영향",
      choices: [
        { label: "필수 — 생활비로 쓴다",            scores: { k:  0, d:  0, p: +2, s: +2 } },
        { label: "있으면 좋지만 필수는 아님",         scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "무관 — 장기 적립 중심",            scores: { k:  0, d:  0, p: -1, s: -1 } },
      ],
    },
  ];

  const QUESTIONS_EN = [
    {
      id: "age",
      label: "What's your age bracket?",
      sub: "Time to recover from equity drawdowns → affects Split · bet size",
      choices: [
        { label: "20s–30s",          scores: { k: +2, d:  0, p:  0, s: -2 } },
        { label: "40s–50s",          scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "60s and older",    scores: { k: -2, d:  0, p:  0, s: +2 } },
      ],
    },
    {
      id: "loss_capacity",
      label: "How much loss can this money absorb?",
      sub: "Nature of capital → affects Kelly fraction · Split",
      choices: [
        { label: "Living expenses — can't lose",      scores: { k: -3, d:  0, p:  0, s: +2 } },
        { label: "Some loss is acceptable",            scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "Discretionary — recoverable",        scores: { k: +2, d:  0, p:  0, s: -1 } },
      ],
    },
    {
      id: "risk_tolerance",
      label: "How do you feel about volatility?",
      sub: "Tolerance → affects Kelly · risk-discount profile",
      choices: [
        { label: "Stability first — can't stand it",         scores: { k: -3, d: -2, p:  0, s:  0 } },
        { label: "Some swings are OK",                        scores: { k: -1, d: -1, p:  0, s:  0 } },
        { label: "Can handle big swings",                     scores: { k: +1, d:  0, p:  0, s:  0 } },
        { label: "Aggressive — I welcome volatility",         scores: { k: +3, d: +1, p:  0, s:  0 } },
      ],
    },
    {
      id: "target_return",
      label: "What's your target return?",
      sub: "Directly drives the equity-premium (μ−r) lever",
      choices: [
        { label: "Capital preservation (3–5% / yr)",          scores: { k:  0, d:  0, p: -2, s:  0 } },
        { label: "Market average (7–10% / yr)",                scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "Beat the market (10%+ / yr)",                scores: { k:  0, d:  0, p: +2, s:  0 } },
      ],
    },
    {
      id: "experience",
      label: "How long have you been investing in equities / options?",
      sub: "Signal-reading experience → affects Kelly · Discount",
      choices: [
        { label: "Under 1 year",   scores: { k: -1, d: -2, p:  0, s:  0 } },
        { label: "1–3 years",       scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "3–7 years",       scores: { k:  0, d: +1, p:  0, s:  0 } },
        { label: "7+ years",        scores: { k: +1, d: +2, p:  0, s:  0 } },
      ],
    },
    {
      id: "crash_response",
      label: "Market drops 30% tomorrow — what do you do?",
      sub: "Behavioral pattern → affects Kelly · Discount",
      choices: [
        { label: "Sell everything — before it gets worse",    scores: { k: -2, d: -2, p:  0, s:  0 } },
        { label: "Hold — wait for recovery",                   scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "Buy more — it's a sale",                     scores: { k: +2, d: +1, p:  0, s:  0 } },
      ],
    },
    {
      id: "income_need",
      label: "Does this portfolio need to generate monthly cash?",
      sub: "Yield need → affects premium target · Split",
      choices: [
        { label: "Yes — I rely on it for living expenses",    scores: { k:  0, d:  0, p: +2, s: +2 } },
        { label: "Nice to have, not required",                 scores: { k:  0, d:  0, p:  0, s:  0 } },
        { label: "No — long-term accumulation only",           scores: { k:  0, d:  0, p: -1, s: -1 } },
      ],
    },
  ];

  // Canonical ordering for each axis. Drives both the result-screen pill
  // rows (so the user can nudge a single axis after seeing the wizard's
  // recommendation) and any future lookups that need a stable list.
  const AXIS_ORDER = {
    kelly:    ["quarter", "half", "threequarter", "full"],
    discount: ["loose", "standard", "tight"],
    premium:  ["conservative", "standard", "aggressive"],
    split:    ["80-20", "90-10", "95-5"],
  };

  // Bucket boundaries — clamp score sums to the closest dashboard value.
  function bucketKelly(score) {
    if (score <= -5) return "quarter";
    if (score <= -1) return "half";
    if (score <=  3) return "threequarter";
    return "full";
  }
  function bucketDiscount(score) {
    if (score <= -3) return "tight";
    if (score <=  1) return "standard";
    return "loose";
  }
  function bucketPremium(score) {
    if (score <= -1) return "conservative";
    if (score <=  1) return "standard";
    return "aggressive";
  }
  function bucketSplit(score) {
    if (score <= -2) return "80-20";
    if (score <=  1) return "90-10";
    return "95-5";
  }

  // Kelly × premium → human-readable profile name.
  const PROFILE_LABELS_KO = {
    "quarter|conservative":      "보수형 인컴",
    "quarter|standard":          "보수형",
    "quarter|aggressive":        "보수형 (현금 인출)",
    "half|conservative":         "안정 적립",
    "half|standard":             "안정형 균형",
    "half|aggressive":           "균형형 인컴",
    "threequarter|conservative": "균형형 보존",
    "threequarter|standard":     "균형형 적립가",
    "threequarter|aggressive":   "성장 지향",
    "full|conservative":         "공격적 보존",
    "full|standard":             "공격적 성장",
    "full|aggressive":           "공격적 성장 (고수익 추구)",
  };
  const PROFILE_LABELS_EN = {
    "quarter|conservative":      "Conservative income",
    "quarter|standard":          "Conservative",
    "quarter|aggressive":        "Conservative (income-focused)",
    "half|conservative":         "Steady accumulator",
    "half|standard":             "Balanced steady",
    "half|aggressive":           "Balanced income",
    "threequarter|conservative": "Balanced preservation",
    "threequarter|standard":     "Balanced accumulator",
    "threequarter|aggressive":   "Growth-oriented",
    "full|conservative":         "Aggressive preservation",
    "full|standard":             "Aggressive growth",
    "full|aggressive":           "Aggressive growth (high yield)",
  };

  // Localized UI strings.
  const I18N_KO = {
    triggerLabel: "🧭 내 프로필 찾기",
    title: "투자 프로필 위자드",
    subtitle: "7개의 질문에 답하면 오늘의 비중 추천을 받습니다",
    progress: (i, n) => `${i} / ${n}`,
    prev: "이전",
    next: "다음",
    finish: "결과 보기",
    resultTitle: "당신의 추천",
    resultIntro: "당신의 답변에 가장 적합한 조합입니다.",
    apply: "대시보드에 적용",
    retake: "다시 풀기",
    close: "닫기",
    bannerLabel: "당신의 프로필",
    bannerWhy: "왜 이 조합? 위자드 답변에 따라 자동 추천",
    share: "🔗 공유 링크 복사",
    shareShort: "🔗",
    shareCopied: "복사됨!",
    backtestTitle: "과거 시뮬레이션",
    backtestCum: "누적",
    backtestCagr: "연 수익",
    backtestMdd: "최대 낙폭",
    backtestVol: "변동성",
    backtestVsSpx: "SPX 100% 비교",
    backtestChartLegendProfile: "내 프로필",
    backtestChartLegendSpx: "SPX 100%",
    backtestDisclaimer: "단순화된 예시 — 가격 수익률만, 배당·세금·슬리피지·옵션 프리미엄 미반영, Discount/Split 토글 미적용. 실제 운용 결과 아님.",
    backtestPeriodMap: { full: "전체", since_2010: "2010~", covid_2020: "코로나 2020", bear_2022: "베어 2022" },
    backtestLoading: "백테스트 불러오는 중…",
    backtestFailed: "백테스트 데이터를 불러올 수 없습니다.",
    axisKelly: "Kelly 분율",
    axisDiscount: "위험 민감도",
    axisPremium: "기대 프리미엄",
    axisSplit: "분할",
    kellyValueLabel: { quarter: "¼", half: "½", threequarter: "¾", full: "Full" },
    discountValueLabel: { loose: "느슨", standard: "기본", tight: "빡빡" },
    premiumValueLabel: { conservative: "5%", standard: "7%", aggressive: "9%" },
    splitValueLabel: { "80-20": "80 / 20", "90-10": "90 / 10", "95-5": "95 / 5" },
  };
  const I18N_EN = {
    triggerLabel: "🧭 Find my profile",
    title: "Investor Profile Wizard",
    subtitle: "Answer 7 questions to get today's allocation recommendation",
    progress: (i, n) => `${i} / ${n}`,
    prev: "Back",
    next: "Next",
    finish: "See result",
    resultTitle: "Your recommendation",
    resultIntro: "The combination that best matches your answers.",
    apply: "Apply to dashboard",
    retake: "Retake",
    close: "Close",
    bannerLabel: "Your profile",
    bannerWhy: "Why this combo? Auto-selected from your wizard answers",
    share: "🔗 Copy share link",
    shareShort: "🔗",
    shareCopied: "Copied!",
    backtestTitle: "Historical simulation",
    backtestCum: "Cumulative",
    backtestCagr: "CAGR",
    backtestMdd: "Max drawdown",
    backtestVol: "Volatility",
    backtestVsSpx: "vs SPX 100%",
    backtestChartLegendProfile: "My profile",
    backtestChartLegendSpx: "SPX 100%",
    backtestDisclaimer: "Illustrative only — price returns only; dividends, taxes, slippage, options premiums excluded; Discount/Split toggles not applied. NOT actual performance.",
    backtestPeriodMap: { full: "Full", since_2010: "Since 2010", covid_2020: "Covid 2020", bear_2022: "Bear 2022" },
    backtestLoading: "Loading backtest…",
    backtestFailed: "Could not load backtest data.",
    axisKelly: "Kelly fraction",
    axisDiscount: "Risk sensitivity",
    axisPremium: "Equity premium",
    axisSplit: "Split",
    kellyValueLabel: { quarter: "¼", half: "½", threequarter: "¾", full: "Full" },
    discountValueLabel: { loose: "Loose", standard: "Std", tight: "Tight" },
    premiumValueLabel: { conservative: "5%", standard: "7%", aggressive: "9%" },
    splitValueLabel: { "80-20": "80 / 20", "90-10": "90 / 10", "95-5": "95 / 5" },
  };

  const STORAGE_PROFILE = "wizard-profile";

  // ---------------------------------------------------------------------
  // Backtest data — fetched once on first use, cached in module scope.
  // Path is relative; the bundle is at /assets/dashboard-wizard.js so
  // ../assets/data/... resolves correctly from the EN page (/en/) too.
  // ---------------------------------------------------------------------
  const BACKTEST_URL = "/assets/data/backtest_results.json";
  let backtestPromise = null;
  function loadBacktest() {
    if (backtestPromise) return backtestPromise;
    backtestPromise = fetch(BACKTEST_URL, { cache: "force-cache" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error("HTTP " + r.status))))
      .catch((err) => {
        // Don't poison the cache on transient failures so a later call can retry.
        backtestPromise = null;
        throw err;
      });
    return backtestPromise;
  }

  function pickLang() {
    // Prefer document lang; fall back to URL prefix (`/en/`).
    const docLang = (document.documentElement.lang || "").toLowerCase();
    if (docLang.startsWith("en")) return "en";
    if (docLang.startsWith("ko")) return "ko";
    return window.location.pathname.startsWith("/en/") ? "en" : "ko";
  }

  function getStrings(lang) {
    return lang === "en" ? I18N_EN : I18N_KO;
  }
  function getQuestions(lang) {
    return lang === "en" ? QUESTIONS_EN : QUESTIONS_KO;
  }
  function getProfileLabels(lang) {
    return lang === "en" ? PROFILE_LABELS_EN : PROFILE_LABELS_KO;
  }

  function computeResult(answers, lang) {
    let k = 0, d = 0, p = 0, s = 0;
    for (const a of answers) {
      if (!a) continue;
      k += a.k; d += a.d; p += a.p; s += a.s;
    }
    const kelly = bucketKelly(k);
    const discount = bucketDiscount(d);
    const premium = bucketPremium(p);
    const split = bucketSplit(s);
    return buildResult(kelly, discount, premium, split, lang, { k, d, p, s });
  }

  function buildResult(kelly, discount, premium, split, lang, scores) {
    const labels = getProfileLabels(lang);
    const profileName = labels[`${kelly}|${premium}`] || (lang === "en" ? "Custom" : "맞춤형");
    return { kelly, discount, premium, split, profileName, scores: scores || null };
  }

  // ---------------------------------------------------------------------
  // Profile ↔ URL query encoding (?profile=kelly-discount-premium-split)
  // Used for share-link generation and to apply a profile on cold visit.
  // ---------------------------------------------------------------------

  const VALID_KELLY    = new Set(["quarter", "half", "threequarter", "full"]);
  const VALID_DISCOUNT = new Set(["loose", "standard", "tight"]);
  const VALID_PREMIUM  = new Set(["conservative", "standard", "aggressive"]);
  const VALID_SPLIT    = new Set(["80-20", "90-10", "95-5"]);

  function encodeProfileQuery(result) {
    return `${result.kelly}-${result.discount}-${result.premium}-${result.split}`;
  }
  function parseProfileQuery(raw, lang) {
    if (!raw) return null;
    // Split into 4 tokens, but split is "95-5" / "90-10" / "80-20" — has a
    // hyphen inside. So split into a max of 4 pieces from the LEFT to keep
    // the split token whole at the end.
    const parts = raw.split("-");
    if (parts.length < 5) return null;
    const kelly    = parts[0];
    const discount = parts[1];
    const premium  = parts[2];
    const split    = parts.slice(3).join("-");
    if (!VALID_KELLY.has(kelly)) return null;
    if (!VALID_DISCOUNT.has(discount)) return null;
    if (!VALID_PREMIUM.has(premium)) return null;
    if (!VALID_SPLIT.has(split)) return null;
    return buildResult(kelly, discount, premium, split, lang, null);
  }

  function buildShareUrl(result) {
    const url = new URL(window.location.href);
    url.searchParams.set("profile", encodeProfileQuery(result));
    url.hash = "";
    return url.toString();
  }

  function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    // Fallback for http / older browsers.
    return new Promise((resolve, reject) => {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try {
        const ok = document.execCommand("copy");
        document.body.removeChild(ta);
        ok ? resolve() : reject(new Error("copy failed"));
      } catch (e) {
        document.body.removeChild(ta);
        reject(e);
      }
    });
  }

  function flashCopiedFeedback(btn, originalLabel, copiedLabel) {
    btn.disabled = true;
    btn.textContent = copiedLabel;
    btn.classList.add("is-copied");
    if (btn._copyResetTimer) clearTimeout(btn._copyResetTimer);
    btn._copyResetTimer = setTimeout(() => {
      btn.textContent = originalLabel;
      btn.classList.remove("is-copied");
      btn.disabled = false;
    }, 1500);
  }

  // Light haptic on choice tap — Android Chrome supports navigator.vibrate;
  // iOS Safari ignores it (no error). Skipped when reduced-motion is on so
  // motion-sensitive users don't get unexpected feedback either.
  function maybeVibrate() {
    if (prefersReducedMotion()) return;
    if (typeof navigator !== "undefined" && navigator.vibrate) {
      try { navigator.vibrate(10); } catch (e) { /* */ }
    }
  }

  function prefersReducedMotion() {
    return typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function fmtPct(v) {
    if (v == null || isNaN(v)) return "—";
    const sign = v > 0 ? "+" : "";
    return `${sign}${v.toFixed(1)}%`;
  }

  // ---------------------------------------------------------------------
  // SVG sparkline: profile NAV vs SPX baseline, both rebased to 1.0 at
  // period start. Linear scale, no axes/grid — the surrounding numbers
  // give the precise readouts; the chart's job is just "which line ended
  // higher and which had a deeper trough."
  // ---------------------------------------------------------------------
  const CHART_WIDTH = 280;
  const CHART_HEIGHT = 72;
  const CHART_PAD_X = 4;
  const CHART_PAD_Y = 6;

  function buildChartSvg(profileSeries, spxSeries) {
    if (!profileSeries || profileSeries.length < 2 ||
        !spxSeries || spxSeries.length < 2) {
      return null;
    }
    const n = Math.min(profileSeries.length, spxSeries.length);
    const yMin = Math.min(
      Math.min(...profileSeries.slice(0, n)),
      Math.min(...spxSeries.slice(0, n))
    );
    const yMax = Math.max(
      Math.max(...profileSeries.slice(0, n)),
      Math.max(...spxSeries.slice(0, n))
    );
    const yRange = yMax - yMin || 1;
    const innerW = CHART_WIDTH - 2 * CHART_PAD_X;
    const innerH = CHART_HEIGHT - 2 * CHART_PAD_Y;

    function pointsFor(series) {
      return series.slice(0, n).map((v, i) => {
        const x = CHART_PAD_X + (innerW * i) / (n - 1);
        const y = CHART_PAD_Y + innerH - (innerH * (v - yMin)) / yRange;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      }).join(" ");
    }

    // Use SVG namespace via createElementNS so the polyline renders.
    // Build via DOM rather than innerHTML to keep CSP-friendly.
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    // Explicit width/height (not just viewBox) so iOS Safari and older
    // Chrome — which don't compute SVG intrinsic size from viewBox alone
    // inside flex/grid containers — actually render with non-zero height.
    // CSS overrides for responsive scaling: `max-width: 100%; height: auto`.
    svg.setAttribute("width", CHART_WIDTH);
    svg.setAttribute("height", CHART_HEIGHT);
    svg.setAttribute("viewBox", `0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`);
    svg.setAttribute("class", "wizard-backtest-chart");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-hidden", "true");

    // SPX baseline first (background, dashed gray).
    const spxLine = document.createElementNS(svgNS, "polyline");
    spxLine.setAttribute("points", pointsFor(spxSeries));
    spxLine.setAttribute("class", "wizard-chart-spx");
    spxLine.setAttribute("fill", "none");
    svg.appendChild(spxLine);

    // Profile in front, solid amber.
    const profLine = document.createElementNS(svgNS, "polyline");
    profLine.setAttribute("points", pointsFor(profileSeries));
    profLine.setAttribute("class", "wizard-chart-profile");
    profLine.setAttribute("fill", "none");
    svg.appendChild(profLine);

    // 1.0 baseline (start value) — light reference hairline.
    if (yMin <= 1.0 && yMax >= 1.0) {
      const baselineY = CHART_PAD_Y + innerH - (innerH * (1.0 - yMin)) / yRange;
      const baseline = document.createElementNS(svgNS, "line");
      baseline.setAttribute("x1", CHART_PAD_X);
      baseline.setAttribute("x2", CHART_WIDTH - CHART_PAD_X);
      baseline.setAttribute("y1", baselineY);
      baseline.setAttribute("y2", baselineY);
      baseline.setAttribute("class", "wizard-chart-baseline");
      svg.insertBefore(baseline, spxLine);
    }
    return svg;
  }

  // fillBacktest renders the entire backtest section (header + period
  // pills + chart + metrics + SPX line + disclaimer) into `box`. The
  // active period is owned by the caller (openWizard closure) so that
  // switching Kelly/Premium pills above doesn't reset the user's chosen
  // period. `onPeriodChange` is fired so the caller can persist it.
  function fillBacktest(box, data, result, t, activePeriod, onPeriodChange) {
    const profileKey = `${result.kelly}|${result.premium}`;
    const profMetrics = data.profiles && data.profiles[profileKey];
    if (!profMetrics) {
      box.innerHTML = "";
      box.appendChild(el("div", { className: "wizard-backtest-error", text: t.backtestFailed }));
      return;
    }
    box.innerHTML = "";
    box.removeAttribute("data-loading");

    const header = el("div", { className: "wizard-backtest-head" }, [
      el("strong", { text: t.backtestTitle }),
      renderPeriodPills(),
    ]);
    const chartWrap = el("div", { className: "wizard-backtest-chart-wrap" });
    const legend = el("div", { className: "wizard-backtest-legend" }, [
      el("span", { className: "wizard-backtest-legend-item" }, [
        el("span", { className: "wizard-backtest-legend-swatch wizard-backtest-legend-swatch--profile" }),
        el("span", { text: " " + t.backtestChartLegendProfile }),
      ]),
      el("span", { className: "wizard-backtest-legend-item" }, [
        el("span", { className: "wizard-backtest-legend-swatch wizard-backtest-legend-swatch--spx" }),
        el("span", { text: " " + t.backtestChartLegendSpx }),
      ]),
    ]);
    const metricsRow = el("div", { className: "wizard-backtest-metrics" });
    const spxLine = el("div", { className: "wizard-backtest-spx" });
    const disclaimer = el("div", { className: "wizard-backtest-disclaimer", text: t.backtestDisclaimer });

    function renderPeriodPills() {
      const wrap = el("div", { className: "wizard-backtest-periods" });
      const keys = ["since_2010", "full", "covid_2020", "bear_2022"];
      keys.forEach((key) => {
        if (!profMetrics[key]) return;
        const pill = el("button", {
          className: "wizard-backtest-pill" + (key === activePeriod ? " is-active" : ""),
          attrs: { type: "button", "data-period": key },
          text: t.backtestPeriodMap[key] || key,
          onClick: () => {
            activePeriod = key;
            if (onPeriodChange) onPeriodChange(key);
            wrap.querySelectorAll(".wizard-backtest-pill").forEach((p) => {
              p.classList.toggle("is-active", p.getAttribute("data-period") === key);
            });
            redrawAll();
          },
        });
        wrap.appendChild(pill);
      });
      return wrap;
    }

    function redrawChart() {
      chartWrap.innerHTML = "";
      const profileSeries = data.series && data.series.profiles
        && data.series.profiles[profileKey] && data.series.profiles[profileKey][activePeriod];
      const spxSeries = data.series && data.series.spx && data.series.spx[activePeriod];
      const svg = buildChartSvg(profileSeries, spxSeries);
      if (svg) chartWrap.appendChild(svg);
    }

    function redrawMetrics() {
      const m = profMetrics[activePeriod];
      const baseline = data.spx_baseline && data.spx_baseline[activePeriod];
      metricsRow.innerHTML = "";
      [
        [t.backtestCum,  fmtPct(m.cum_pct)],
        [t.backtestCagr, fmtPct(m.cagr_pct)],
        [t.backtestMdd,  fmtPct(m.mdd_pct)],
        [t.backtestVol,  fmtPct(m.vol_pct)],
      ].forEach(([name, value]) => {
        metricsRow.appendChild(el("div", { className: "wizard-backtest-metric" }, [
          el("div", { className: "wizard-backtest-metric-name", text: name }),
          el("div", { className: "wizard-backtest-metric-value", text: value }),
        ]));
      });
      spxLine.innerHTML = "";
      if (baseline) {
        spxLine.appendChild(el("span", { className: "wizard-backtest-spx-label", text: t.backtestVsSpx + ":" }));
        spxLine.appendChild(el("span", {
          className: "wizard-backtest-spx-value",
          text: ` ${t.backtestCum} ${fmtPct(baseline.cum_pct)} · ${t.backtestMdd} ${fmtPct(baseline.mdd_pct)}`,
        }));
      }
    }

    function redrawAll() {
      redrawChart();
      redrawMetrics();
    }

    box.appendChild(header);
    box.appendChild(chartWrap);
    box.appendChild(legend);
    box.appendChild(metricsRow);
    box.appendChild(spxLine);
    box.appendChild(disclaimer);
    redrawAll();
  }

  // ---------------------------------------------------------------------
  // DOM helpers
  // ---------------------------------------------------------------------

  function el(tag, props, children) {
    const node = document.createElement(tag);
    if (props) {
      for (const key of Object.keys(props)) {
        const val = props[key];
        if (key === "className") node.className = val;
        else if (key === "dataset") {
          for (const dk of Object.keys(val)) node.dataset[dk] = val[dk];
        }
        else if (key === "html") node.innerHTML = val;
        else if (key === "text") node.textContent = val;
        else if (key.startsWith("on") && typeof val === "function") {
          node.addEventListener(key.slice(2).toLowerCase(), val);
        }
        else if (key === "attrs") {
          // Skip null/undefined so `disabled: null` means "no attribute"
          // rather than setAttribute("disabled", "null") which is truthy.
          for (const ak of Object.keys(val)) {
            if (val[ak] == null) continue;
            node.setAttribute(ak, val[ak]);
          }
        }
        else node[key] = val;
      }
    }
    if (children) {
      for (const c of children) {
        if (c == null) continue;
        node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
      }
    }
    return node;
  }

  // ---------------------------------------------------------------------
  // Wizard modal
  // ---------------------------------------------------------------------

  function openWizard() {
    const lang = pickLang();
    const t = getStrings(lang);
    const questions = getQuestions(lang);

    let idx = 0;
    const answers = new Array(questions.length).fill(null);
    let result = null;
    let phase = "questions"; // or "result"
    // Direction of the last transition between questions — drives the
    // slide-in animation class on .wizard-body. "next" / "prev" / null.
    let lastDirection = null;
    // Active backtest period — owned at the openWizard scope (not inside
    // fillBacktest) so that editing an axis pill above the chart doesn't
    // reset the user's chosen period when the result re-renders.
    let backtestPeriod = "since_2010";

    const overlay = el("div", { className: "wizard-overlay", attrs: { role: "dialog", "aria-modal": "true", "aria-label": t.title } });
    const modal = el("div", { className: "wizard-modal" });
    overlay.appendChild(modal);

    // Close on overlay backdrop click + Esc.
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeWizard(overlay);
    });
    const escHandler = (e) => {
      if (e.key === "Escape") closeWizard(overlay);
    };
    document.addEventListener("keydown", escHandler);
    overlay.dataset.escHandlerAttached = "1";
    overlay._escHandler = escHandler;

    function render() {
      modal.innerHTML = "";
      if (phase === "questions") {
        renderQuestion();
      } else {
        renderResult();
      }
    }

    function renderQuestion() {
      const q = questions[idx];
      const header = el("div", { className: "wizard-header" }, [
        el("div", { className: "wizard-title" }, [
          el("strong", { text: t.title }),
          el("button", {
            className: "wizard-close",
            attrs: { "aria-label": t.close, type: "button" },
            text: "✕",
            onClick: () => closeWizard(overlay),
          }),
        ]),
        el("div", { className: "wizard-subtitle", text: t.subtitle }),
        renderProgress(idx + 1, questions.length),
      ]);

      const slideClass = lastDirection === "prev"
        ? " wizard-slide-from-left"
        : (lastDirection === "next" ? " wizard-slide-from-right" : "");
      const body = el("div", { className: "wizard-body" + slideClass }, [
        el("div", { className: "wizard-question-label", text: q.label }),
        q.sub ? el("div", { className: "wizard-question-sub", text: q.sub }) : null,
        el("div", { className: "wizard-choices" }, q.choices.map((c, ci) => {
          const isPicked = answers[idx] && answers[idx]._choiceIdx === ci;
          const btn = el("button", {
            className: "wizard-choice" + (isPicked ? " is-picked" : ""),
            attrs: { type: "button" },
            text: c.label,
            onClick: () => {
              answers[idx] = { ...c.scores, _choiceIdx: ci };
              maybeVibrate();
              // Auto-advance for snappier UX; user can still go back.
              if (idx < questions.length - 1) {
                idx += 1;
                lastDirection = "next";
                render();
              } else {
                result = computeResult(answers, lang);
                phase = "result";
                lastDirection = "next";
                render();
              }
            },
          });
          return btn;
        })),
      ]);

      const nav = el("div", { className: "wizard-nav" }, [
        el("button", {
          className: "wizard-nav-btn wizard-nav-prev",
          attrs: { type: "button", disabled: idx === 0 ? "disabled" : null },
          text: t.prev,
          onClick: () => {
            if (idx > 0) { idx -= 1; lastDirection = "prev"; render(); }
          },
        }),
        el("button", {
          className: "wizard-nav-btn wizard-nav-next",
          attrs: { type: "button", disabled: answers[idx] ? null : "disabled" },
          text: idx === questions.length - 1 ? t.finish : t.next,
          onClick: () => {
            if (!answers[idx]) return;
            if (idx < questions.length - 1) {
              idx += 1; lastDirection = "next"; render();
            } else {
              result = computeResult(answers, lang);
              phase = "result";
              lastDirection = "next";
              render();
            }
          },
        }),
      ]);

      modal.appendChild(header);
      modal.appendChild(body);
      modal.appendChild(nav);
    }

    function renderResult() {
      const header = el("div", { className: "wizard-header" }, [
        el("div", { className: "wizard-title" }, [
          el("strong", { text: t.resultTitle }),
          el("button", {
            className: "wizard-close",
            attrs: { "aria-label": t.close, type: "button" },
            text: "✕",
            onClick: () => closeWizard(overlay),
          }),
        ]),
        el("div", { className: "wizard-subtitle", text: t.resultIntro }),
      ]);

      const profileBox = el("div", { className: "wizard-profile-name" }, [
        el("span", { className: "wizard-profile-label", text: t.bannerLabel + ":" }),
        el("strong", { text: " " + result.profileName }),
      ]);

      const axes = el("div", { className: "wizard-result" }, [
        renderEditableAxisCard("kelly",    t.axisKelly,    t.kellyValueLabel),
        renderEditableAxisCard("discount", t.axisDiscount, t.discountValueLabel),
        renderEditableAxisCard("premium",  t.axisPremium,  t.premiumValueLabel),
        renderEditableAxisCard("split",    t.axisSplit,    t.splitValueLabel),
      ]);

      // Backtest section — placeholder injected synchronously, populated
      // asynchronously once the JSON fetch resolves. Failures fall back
      // to a short error line; the recommendation flow itself is not
      // blocked on this data.
      const backtestBox = el("div", { className: "wizard-backtest", attrs: { "data-loading": "1" } }, [
        el("div", { className: "wizard-backtest-loading", text: t.backtestLoading }),
      ]);
      loadBacktest()
        .then((data) => fillBacktest(backtestBox, data, result, t, backtestPeriod,
                                     (newPeriod) => { backtestPeriod = newPeriod; }))
        .catch(() => {
          backtestBox.innerHTML = "";
          backtestBox.appendChild(el("div", { className: "wizard-backtest-error", text: t.backtestFailed }));
        });

      const shareBtn = el("button", {
        className: "wizard-nav-btn wizard-nav-share",
        attrs: { type: "button" },
        text: t.share,
        onClick: () => {
          copyToClipboard(buildShareUrl(result))
            .then(() => flashCopiedFeedback(shareBtn, t.share, t.shareCopied))
            .catch(() => { /* */ });
        },
      });

      const nav = el("div", { className: "wizard-nav" }, [
        el("button", {
          className: "wizard-nav-btn wizard-nav-prev",
          attrs: { type: "button" },
          text: t.retake,
          onClick: () => {
            for (let i = 0; i < answers.length; i++) answers[i] = null;
            idx = 0;
            phase = "questions";
            lastDirection = "prev";
            render();
          },
        }),
        shareBtn,
        el("button", {
          className: "wizard-nav-btn wizard-nav-apply",
          attrs: { type: "button" },
          text: t.apply,
          onClick: () => {
            applyResult(result, lang);
            renderBanner(result, lang);
            closeWizard(overlay);
          },
        }),
      ]);

      modal.appendChild(header);
      modal.appendChild(profileBox);
      modal.appendChild(axes);
      modal.appendChild(backtestBox);
      modal.appendChild(nav);
    }

    // Editable axis card — the wizard's recommendation populates each
    // axis, but the user can override any one (or all four) with the
    // pill row before clicking Apply / Share. Kelly+Premium changes
    // ripple into the profile name and the backtest section.
    function renderEditableAxisCard(axisKey, axisName, axisLabels) {
      return el("div", { className: "wizard-axis wizard-axis--editable" }, [
        el("div", { className: "wizard-axis-name", text: axisName }),
        el("div", { className: "wizard-axis-pills" },
          AXIS_ORDER[axisKey].map((val) =>
            el("button", {
              className: "wizard-axis-pill" + (result[axisKey] === val ? " is-active" : ""),
              attrs: { type: "button", "data-axis-value": val },
              text: axisLabels[val],
              onClick: () => setAxis(axisKey, val),
            })
          )
        ),
      ]);
    }

    function setAxis(axisKey, value) {
      if (result[axisKey] === value) return;
      result[axisKey] = value;
      // Profile name depends on Kelly + Premium — recompute when either
      // changes. Discount and Split don't affect the label.
      if (axisKey === "kelly" || axisKey === "premium") {
        const labels = getProfileLabels(lang);
        result.profileName = labels[`${result.kelly}|${result.premium}`]
          || (lang === "en" ? "Custom" : "맞춤형");
      }
      // Re-render the whole result screen. Cheap (DOM rebuild, the
      // backtest fetch is cached). Backtest period persists because
      // backtestPeriod lives in the openWizard closure, not inside
      // fillBacktest.
      render();
    }

    function renderProgress(curr, total) {
      const pct = Math.round((curr / total) * 100);
      const bar = el("div", { className: "wizard-progress" }, [
        el("div", { className: "wizard-progress-fill", attrs: { style: `width: ${pct}%` } }),
      ]);
      return el("div", { className: "wizard-progress-row" }, [
        bar,
        el("div", { className: "wizard-progress-text", text: t.progress(curr, total) }),
      ]);
    }

    document.body.appendChild(overlay);
    document.body.classList.add("wizard-open");
    render();
  }

  function closeWizard(overlay) {
    if (overlay._escHandler) {
      document.removeEventListener("keydown", overlay._escHandler);
    }
    if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    document.body.classList.remove("wizard-open");
  }

  // ---------------------------------------------------------------------
  // Apply / banner / restore
  // ---------------------------------------------------------------------

  function applyResult(result, lang) {
    // Dispatch synthetic clicks on the existing toggle buttons so that
    // kelly-toggle.js handles the .is-active swap, localStorage save,
    // and recalc — single source of truth for state mutation.
    dispatchClick(`[data-kelly-set="${result.kelly}"]`);
    dispatchClick(`[data-discount-set="${result.discount}"]`);
    dispatchClick(`[data-premium-set="${result.premium}"]`);
    dispatchClick(`[data-split-set="${result.split}"]`);

    // Persist the banner state so it survives reload.
    const payload = {
      kelly: result.kelly,
      discount: result.discount,
      premium: result.premium,
      split: result.split,
      profileName: result.profileName,
      lang,
      savedAt: new Date().toISOString(),
    };
    try {
      localStorage.setItem(STORAGE_PROFILE, JSON.stringify(payload));
    } catch (e) { /* private mode etc. */ }
  }

  function dispatchClick(selector) {
    const btn = document.querySelector(selector);
    if (btn) btn.click();
  }

  function renderBanner(result, lang) {
    const placeholder = document.querySelector("[data-wizard-banner]");
    if (!placeholder) return;
    const t = getStrings(lang);

    placeholder.innerHTML = "";
    placeholder.hidden = false;

    const summary = `${t.kellyValueLabel[result.kelly]}K · ${t.discountValueLabel[result.discount]} · ${t.premiumValueLabel[result.premium]} · ${t.splitValueLabel[result.split]}`;

    const shareBtn = el("button", {
      className: "wizard-banner-share",
      attrs: { type: "button", title: t.share, "aria-label": t.share },
      text: t.shareShort,
      onClick: () => {
        copyToClipboard(buildShareUrl(result))
          .then(() => flashCopiedFeedback(shareBtn, t.shareShort, t.shareCopied))
          .catch(() => { /* */ });
      },
    });

    const banner = el("div", { className: "wizard-banner-inner" }, [
      el("span", { className: "wizard-banner-icon", text: "💡" }),
      el("span", { className: "wizard-banner-text" }, [
        el("strong", { text: t.bannerLabel + ": " }),
        el("span", { className: "wizard-banner-profile", text: result.profileName }),
        el("span", { className: "wizard-banner-sep", text: " — " }),
        el("span", { className: "wizard-banner-summary", text: summary }),
      ]),
      shareBtn,
      el("button", {
        className: "wizard-banner-btn",
        attrs: { type: "button" },
        text: t.retake,
        onClick: () => openWizard(),
      }),
      el("button", {
        className: "wizard-banner-close",
        attrs: { type: "button", "aria-label": t.close },
        text: "✕",
        onClick: () => {
          placeholder.hidden = true;
          placeholder.innerHTML = "";
          try { localStorage.removeItem(STORAGE_PROFILE); } catch (e) { /* */ }
        },
      }),
    ]);
    placeholder.appendChild(banner);
  }

  function restoreBanner() {
    const placeholder = document.querySelector("[data-wizard-banner]");
    if (!placeholder) return;
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(STORAGE_PROFILE) || "null"); } catch (e) { saved = null; }
    if (!saved) return;
    // Don't trust the saved lang — use the current page's lang so the
    // banner UI text always matches what the visitor is reading now.
    renderBanner(saved, pickLang());
  }

  // ---------------------------------------------------------------------
  // Init — only runs when the dashboard master bar is on the page.
  // ---------------------------------------------------------------------

  function init() {
    const master = document.querySelector(".allocation-master");
    if (!master) return;
    const lang = pickLang();
    const t = getStrings(lang);

    // Label the trigger button (Python renders an empty <button data-wizard-open>
    // so labels stay in JS — single place to localize).
    document.querySelectorAll("[data-wizard-open]").forEach((btn) => {
      if (!btn.textContent.trim()) btn.textContent = t.triggerLabel;
      btn.addEventListener("click", openWizard);
    });

    // Warm the backtest cache so the result screen has it ready when the
    // user reaches Q7. Silently swallow failures — the result UI handles
    // the missing-data case itself.
    loadBacktest().catch(() => { /* */ });

    // If we arrived from a share link (?profile=...), apply it and rewrite
    // the URL so a manual refresh doesn't re-apply on top of a user's later
    // tweaks. Falls through to restoreBanner() if no query is present.
    const urlResult = parseProfileQuery(
      new URLSearchParams(window.location.search).get("profile"),
      lang
    );
    if (urlResult) {
      // Defer the click dispatch one tick so kelly-toggle.js has finished
      // its own init() — without this, the synthetic clicks fire before
      // its click handlers are attached and nothing happens.
      setTimeout(() => {
        applyResult(urlResult, lang);
        renderBanner(urlResult, lang);
      }, 0);
      try {
        const cleaned = new URL(window.location.href);
        cleaned.searchParams.delete("profile");
        history.replaceState(null, "", cleaned.pathname + cleaned.hash);
      } catch (e) { /* */ }
      return;
    }

    restoreBanner();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
