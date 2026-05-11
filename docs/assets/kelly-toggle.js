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
  const STORAGE_KELLY = "kelly-fraction";
  const STORAGE_PROFILE = "kelly-discount-profile";

  function recalc(card) {
    const kelly = card.dataset.kelly || "half";
    const profileKey = card.dataset.discountProfile || "standard";
    const profile = DISCOUNT_PROFILES[profileKey] || DISCOUNT_PROFILES.standard;

    const base = parseFloat(card.dataset["base" + kelly[0].toUpperCase() + kelly.slice(1)]);
    if (isNaN(base)) return;

    const sCS = card.dataset.stateCorskew || "ok";
    const sVTS = card.dataset.stateVixts || "ok";
    const sVV = card.dataset.stateVolvol || "ok";

    const dCS = profile[sCS];
    const dVTS = profile[sVTS];
    const dVV = profile[sVV];
    const equity = Math.min(Math.round(base * dCS * dVTS * dVV), 100);
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
  }

  function setActive(card, attr, value) {
    card.querySelectorAll(`[${attr}]`).forEach((btn) => {
      btn.classList.toggle("is-active", btn.getAttribute(attr) === value);
    });
  }

  function initCard(card) {
    const savedKelly = localStorage.getItem(STORAGE_KELLY);
    const savedProfile = localStorage.getItem(STORAGE_PROFILE);
    if (savedKelly) {
      card.dataset.kelly = savedKelly;
      setActive(card, "data-kelly-set", savedKelly);
    } else {
      card.dataset.kelly = "half";
    }
    if (savedProfile) {
      card.dataset.discountProfile = savedProfile;
      setActive(card, "data-discount-set", savedProfile);
    } else {
      card.dataset.discountProfile = "standard";
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

    recalc(card);
  }

  function init() {
    document.querySelectorAll(".kelly-card").forEach(initCard);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
