// VIX TS history player — slider + play/pause/restart + speed + date range
// Reads docs/assets/diagrams[_en]/vix_history/manifest.json and lets the
// reader scrub through past daily snapshots of the VIX futures term
// structure chart. The start/end date pickers constrain the playback
// window to a subset of the available archive.
(function () {
  function isHomepage() {
    var p = location.pathname;
    return p === "/" || p === "/en/" || p === "/index.html" || p === "/en/index.html";
  }

  function archivePath() {
    // mkdocs-static-i18n keeps all assets under the single /assets/ root —
    // both locales' diagrams live there (diagrams/ for ko, diagrams_en/ for
    // en) and the /en/ prefix only applies to HTML pages. Using "/en/assets/"
    // would 404 — the EN locale has no separate asset tree.
    return location.pathname.indexOf("/en/") === 0
      ? "/assets/diagrams_en/vix_history/"
      : "/assets/diagrams/vix_history/";
  }

  function locale() {
    return location.pathname.indexOf("/en/") === 0 ? "en" : "ko";
  }

  function strings() {
    return locale() === "ko"
      ? {
          play: "▶ 재생",
          pause: "⏸ 일시정지",
          restart: "⟲ 처음부터",
          speed: "속도",
          rangeFrom: "기간:",
          rangeTo: "~",
          empty: "기록이 아직 쌓이는 중입니다 (매일 평일 22:00 UTC 갱신)",
          fast: "빠르게",
          medium: "보통",
          slow: "천천히",
        }
      : {
          play: "▶ Play",
          pause: "⏸ Pause",
          restart: "⟲ Restart",
          speed: "Speed",
          rangeFrom: "Range:",
          rangeTo: "to",
          empty: "History is still building up (refreshed daily on weekdays at 22:00 UTC)",
          fast: "Fast",
          medium: "Normal",
          slow: "Slow",
        };
  }

  function init() {
    if (!isHomepage()) return;
    var mount = document.getElementById("vix-history-player");
    if (!mount) return;
    if (mount.dataset.initialized === "1") return;
    mount.dataset.initialized = "1";

    var t = strings();
    var base = archivePath();

    fetch(base + "manifest.json", { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (manifest) {
        var dates = manifest.dates || [];
        if (dates.length === 0) {
          mount.innerHTML = '<div class="vix-history-empty">' + t.empty + "</div>";
          return;
        }
        render(mount, dates, base, t);
      })
      .catch(function () {
        mount.innerHTML = '<div class="vix-history-empty">' + t.empty + "</div>";
      });
  }

  function render(mount, allDates, base, t) {
    // Playback state. `view` is the currently-active subset of allDates,
    // re-derived whenever the date pickers change. The slider and counter
    // index into `view`, not allDates, so a 30-day window shows "1 / 21"
    // even though the archive has 95 entries.
    var view = allDates.slice();
    var speedMs = 1000;  // default 1s/frame
    var playing = false;
    var timer = null;

    mount.innerHTML =
      '<div class="vix-history-player__controls">' +
      '  <button class="vix-history-player__play" type="button" aria-label="play">' + t.play + "</button>" +
      '  <button class="vix-history-player__restart" type="button" aria-label="restart" title="' + t.restart + '">' + t.restart + "</button>" +
      '  <span class="vix-history-player__date" data-role="date">' + view[view.length - 1] + "</span>" +
      '  <input type="range" class="vix-history-player__slider" min="0" max="' + (view.length - 1) + '" value="' + (view.length - 1) + '" />' +
      '  <span class="vix-history-player__counter" data-role="counter">' + view.length + ' / ' + view.length + "</span>" +
      '  <select class="vix-history-player__speed" aria-label="' + t.speed + '">' +
      '    <option value="500">' + t.fast + " (0.5s)</option>" +
      '    <option value="1000" selected>' + t.medium + " (1s)</option>" +
      '    <option value="2000">' + t.slow + " (2s)</option>" +
      "  </select>" +
      "</div>" +
      '<div class="vix-history-player__range">' +
      '  <span class="vix-history-player__range-label">' + t.rangeFrom + "</span>" +
      '  <input type="date" class="vix-history-player__from" min="' + allDates[0] + '" max="' + allDates[allDates.length - 1] + '" value="' + allDates[0] + '" />' +
      '  <span class="vix-history-player__range-sep">' + t.rangeTo + "</span>" +
      '  <input type="date" class="vix-history-player__to" min="' + allDates[0] + '" max="' + allDates[allDates.length - 1] + '" value="' + allDates[allDates.length - 1] + '" />' +
      "</div>" +
      '<div class="vix-history-player__image">' +
      '  <img data-role="img" src="' + base + view[view.length - 1] + '.png" alt="VIX Term Structure ' + view[view.length - 1] + '" />' +
      "</div>";

    var img = mount.querySelector('[data-role="img"]');
    var dateLabel = mount.querySelector('[data-role="date"]');
    var counter = mount.querySelector('[data-role="counter"]');
    var slider = mount.querySelector(".vix-history-player__slider");
    var btnPlay = mount.querySelector(".vix-history-player__play");
    var btnReset = mount.querySelector(".vix-history-player__restart");
    var speedSel = mount.querySelector(".vix-history-player__speed");
    var fromInput = mount.querySelector(".vix-history-player__from");
    var toInput = mount.querySelector(".vix-history-player__to");

    function show(i) {
      if (!view.length) return;
      i = Math.max(0, Math.min(view.length - 1, i));
      slider.value = i;
      img.src = base + view[i] + ".png";
      img.alt = "VIX Term Structure " + view[i];
      dateLabel.textContent = view[i];
      counter.textContent = (i + 1) + " / " + view.length;
    }

    function setPlaying(p) {
      playing = p;
      btnPlay.textContent = playing ? t.pause : t.play;
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
      if (playing) {
        timer = setInterval(function () {
          var i = parseInt(slider.value, 10);
          var next = i + 1;
          if (next >= view.length) {
            next = 0;  // loop
          }
          show(next);
        }, speedMs);
      }
    }

    function applyDateRange() {
      // Recompute the visible subset of allDates from the pickers, snap
      // both endpoints to actual archive entries (the pickers allow any
      // calendar date, but the archive skips weekends/holidays/sparse
      // days), then reset the slider geometry.
      var from = fromInput.value;
      var to = toInput.value;
      if (from > to) {
        // Swap rather than reject — user might pick to first then from.
        var tmp = from; from = to; to = tmp;
        fromInput.value = from;
        toInput.value = to;
      }
      var filtered = allDates.filter(function (d) { return d >= from && d <= to; });
      if (!filtered.length) {
        // Pickers landed entirely outside the archive (e.g. both inside
        // a multi-week gap). Fall back to the full archive rather than
        // leaving the player in a blank state.
        filtered = allDates.slice();
        fromInput.value = allDates[0];
        toInput.value = allDates[allDates.length - 1];
      }
      view = filtered;
      var newMax = view.length - 1;
      slider.max = newMax;
      // Land on the latest date in the new window (matches initial-load
      // behaviour of "show me the most recent snapshot first").
      show(newMax);
    }

    slider.addEventListener("input", function () {
      show(parseInt(slider.value, 10));
    });
    btnPlay.addEventListener("click", function () { setPlaying(!playing); });
    btnReset.addEventListener("click", function () {
      // Jump back to the start of the current view; don't change play
      // state — if the user was playing, keep playing from frame 1.
      show(0);
    });
    speedSel.addEventListener("change", function () {
      speedMs = parseInt(speedSel.value, 10);
      if (playing) setPlaying(true);  // restart with new speed
    });
    fromInput.addEventListener("change", applyDateRange);
    toInput.addEventListener("change", applyDateRange);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
