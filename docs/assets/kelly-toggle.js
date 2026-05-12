// kelly-toggle.js
// Lets the user switch Kelly fraction (Quarter/Half/Full) and risk-discount
// profile (Loose/Standard/Tight) on the live dashboard cash-allocation card.
// All math happens in the browser; Python only ships base values + signal
// states via data-* attributes. Selection persists in localStorage.

(function () {
  const DISCOUNT_PROFILES = {
    loose:    { ok: 1.00, caution: 0.95, danger: 0.85 },
    standard: { ok: 1.00, caution: 0.90, danger: 0.75 },
    tight:    { ok: 1.00, caution: 0.85, danger: 0.65 },
  };
  // Main / Tactical capital split — user-selectable from the master bar.
  // Trades crisis-buy power (higher tactical %) against cash drag in normal
  // conditions (lower tactical %). Backing doc: cash-allocation.md#choosing-the-split
  const SPLIT_PROFILES = {
    "80-20": { main: 0.80, tactical: 0.20 },
    "90-10": { main: 0.90, tactical: 0.10 },
    "95-5":  { main: 0.95, tactical: 0.05 },
  };
  // Equity-risk premium (μ−r) used in Kelly base. Python ships pre-computed
  // base values at μ−r = 5% (conservative); recomputing for 7% / 9% multiplies
  // by 1.4 / 1.8 respectively, since f* is linear in (μ−r).
  const PREMIUM_PROFILES = {
    conservative: { value: 0.05, ratio: 1.0 },
    standard:     { value: 0.07, ratio: 7 / 5 },
    aggressive:   { value: 0.09, ratio: 9 / 5 },
  };
  // Kelly fraction key → dataset attribute name (camelCased automatically
  // by the browser, but using single tokens keeps the lookup simple).
  const KELLY_DATASET_KEY = {
    quarter:      "baseQuarter",
    half:         "baseHalf",
    threequarter: "baseThreequarter",
    full:         "baseFull",
  };
  const KELLY_CAP = 100;  // hard cap, mirrors Python's KELLY_CAP = 1.00
  // New-visitor defaults — chosen to give a sensible "calm market, accumulator"
  // baseline rather than the most-conservative-possible combo. Existing visitors'
  // localStorage values take precedence on every key.
  const DEFAULT_KELLY = "threequarter";
  const DEFAULT_DISCOUNT = "standard";
  const DEFAULT_PREMIUM = "standard";
  const DEFAULT_SPLIT = "90-10";
  const STORAGE_KELLY = "kelly-fraction";
  const STORAGE_PROFILE = "kelly-discount-profile";
  const STORAGE_SPLIT = "allocation-split";
  const STORAGE_PREMIUM = "kelly-equity-premium";

  function recalc(card) {
    const kelly = card.dataset.kelly || DEFAULT_KELLY;
    const profileKey = card.dataset.discountProfile || DEFAULT_DISCOUNT;
    const premiumKey = card.dataset.premium || DEFAULT_PREMIUM;
    const profile = DISCOUNT_PROFILES[profileKey] || DISCOUNT_PROFILES[DEFAULT_DISCOUNT];
    const premium = PREMIUM_PROFILES[premiumKey] || PREMIUM_PROFILES[DEFAULT_PREMIUM];

    // Python ships the base at μ−r = 5% (conservative). Scaling by the
    // premium ratio reproduces the value for 7% / 9% without re-fetching:
    // f* = (μ−r)/σ² is linear in (μ−r), so doubling μ−r doubles the base
    // (before the 100% cap).
    const baseRaw = parseFloat(card.dataset[KELLY_DATASET_KEY[kelly] || "baseHalf"]);
    if (isNaN(baseRaw)) return;
    const base = Math.min(Math.round(baseRaw * premium.ratio), KELLY_CAP);

    const sCS = card.dataset.stateCorskew || "ok";
    const sVTS = card.dataset.stateVixts || "ok";
    const sVV = card.dataset.stateVolvol || "ok";

    const dCS = profile[sCS];
    const dVTS = profile[sVTS];
    const dVV = profile[sVV];
    const equity = Math.min(Math.round(base * dCS * dVTS * dVV), KELLY_CAP);
    const cash = 100 - equity;

    const set = (sel, val) => {
      const el = card.querySelector(sel);
      if (el) el.textContent = val;
    };
    set("[data-kelly-base]", Math.round(base));
    set('[data-kelly-d="corskew"]', dCS.toFixed(2));
    set('[data-kelly-d="vixts"]', dVTS.toFixed(2));
    set('[data-kelly-d="volvol"]', dVV.toFixed(2));
    set("[data-kelly-equity]", equity);
    set("[data-kelly-cash]", cash);

    // Composite total — master bar above sits across main + tactical buckets.
    // It owns the split config (main/tactical fractions) and the tactical
    // deploy state; this card only contributes the main-bucket equity %.
    const master = document.querySelector(".allocation-master");
    if (master) {
      const deployPct = parseFloat(master.dataset.deployPct) || 0;
      const mainFrac = parseFloat(master.dataset.mainFrac) || 0.80;
      const tacticalFrac = parseFloat(master.dataset.tacticalFrac) || 0.20;
      const totalEquity = Math.min(
        Math.round(mainFrac * equity + tacticalFrac * deployPct),
        100
      );
      const totalCash = 100 - totalEquity;
      const setMaster = (sel, val) => {
        const el = master.querySelector(sel);
        if (el) el.textContent = val;
      };
      setMaster("[data-total-equity]", totalEquity);
      setMaster("[data-total-cash]", totalCash);
      setMaster("[data-kelly-equity-mini]", equity);
      setMaster("[data-deploy-mini]", deployPct);
      setMaster("[data-total-equity-mini]", totalEquity);
      setMaster("[data-main-pct]", Math.round(mainFrac * 100));
      setMaster("[data-tactical-pct]", Math.round(tacticalFrac * 100));
      const fill = master.querySelector("[data-master-equity-fill]");
      if (fill) fill.style.width = totalEquity + "%";
    }
  }

  function applySplit(master, splitKey) {
    const profile = SPLIT_PROFILES[splitKey] || SPLIT_PROFILES[DEFAULT_SPLIT];
    master.dataset.mainFrac = profile.main;
    master.dataset.tacticalFrac = profile.tactical;
    master.querySelectorAll("[data-split-set]").forEach((btn) => {
      btn.classList.toggle("is-active", btn.getAttribute("data-split-set") === splitKey);
    });
    // Trigger Kelly card recalc so the composite total picks up the new split.
    // The recalc() above reads mainFrac/tacticalFrac off the master bar, so
    // re-running it from each Kelly card propagates the change everywhere.
    document.querySelectorAll(".kelly-card").forEach(recalc);
  }

  function initMaster() {
    const master = document.querySelector(".allocation-master");
    if (!master) return;
    const saved = localStorage.getItem(STORAGE_SPLIT);
    const initial = saved && SPLIT_PROFILES[saved] ? saved : DEFAULT_SPLIT;
    master.querySelectorAll("[data-split-set]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const v = btn.getAttribute("data-split-set");
        localStorage.setItem(STORAGE_SPLIT, v);
        applySplit(master, v);
      });
    });
    applySplit(master, initial);
  }

  function setActive(card, attr, value) {
    card.querySelectorAll(`[${attr}]`).forEach((btn) => {
      btn.classList.toggle("is-active", btn.getAttribute(attr) === value);
    });
  }

  function initCard(card) {
    const savedKelly = localStorage.getItem(STORAGE_KELLY);
    const savedProfile = localStorage.getItem(STORAGE_PROFILE);
    const savedPremium = localStorage.getItem(STORAGE_PREMIUM);
    if (savedKelly && KELLY_DATASET_KEY[savedKelly]) {
      card.dataset.kelly = savedKelly;
      setActive(card, "data-kelly-set", savedKelly);
    } else {
      card.dataset.kelly = DEFAULT_KELLY;
    }
    if (savedProfile && DISCOUNT_PROFILES[savedProfile]) {
      card.dataset.discountProfile = savedProfile;
      setActive(card, "data-discount-set", savedProfile);
    } else {
      card.dataset.discountProfile = DEFAULT_DISCOUNT;
    }
    if (savedPremium && PREMIUM_PROFILES[savedPremium]) {
      card.dataset.premium = savedPremium;
      setActive(card, "data-premium-set", savedPremium);
    } else {
      card.dataset.premium = DEFAULT_PREMIUM;
    }

    card.querySelectorAll("[data-kelly-set]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const v = btn.getAttribute("data-kelly-set");
        card.dataset.kelly = v;
        setActive(card, "data-kelly-set", v);
        localStorage.setItem(STORAGE_KELLY, v);
        recalc(card);
      });
    });
    card.querySelectorAll("[data-discount-set]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const v = btn.getAttribute("data-discount-set");
        card.dataset.discountProfile = v;
        setActive(card, "data-discount-set", v);
        localStorage.setItem(STORAGE_PROFILE, v);
        recalc(card);
      });
    });
    card.querySelectorAll("[data-premium-set]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const v = btn.getAttribute("data-premium-set");
        card.dataset.premium = v;
        setActive(card, "data-premium-set", v);
        localStorage.setItem(STORAGE_PREMIUM, v);
        recalc(card);
      });
    });

    recalc(card);
  }

  function init() {
    initMaster();
    document.querySelectorAll(".kelly-card").forEach(initCard);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
