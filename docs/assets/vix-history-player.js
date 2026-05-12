// VIX TS history player — slider + play/pause + speed control
// Reads docs/assets/diagrams[_en]/vix_history/manifest.json and lets the
// reader scrub through past daily snapshots of the VIX futures term
// structure chart.
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
    var t = locale() === "ko"
      ? {
          play: "▶ 재생",
          pause: "⏸ 일시정지",
          speed: "속도",
          date: "날짜",
          empty: "기록이 아직 쌓이는 중입니다 (매일 평일 22:00 UTC 갱신)",
          fast: "빠르게",
          medium: "보통",
          slow: "천천히",
        }
      : {
          play: "▶ Play",
          pause: "⏸ Pause",
          speed: "Speed",
          date: "Date",
          empty: "History is still building up (refreshed daily on weekdays at 22:00 UTC)",
          fast: "Fast",
          medium: "Normal",
          slow: "Slow",
        };
    return t;
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

  function render(mount, dates, base, t) {
    var lastIdx = dates.length - 1;
    var speedMs = 1000;  // default 1s/frame
    var playing = false;
    var timer = null;

    mount.innerHTML =
      '<div class="vix-history-player__controls">' +
      '  <button class="vix-history-player__play" aria-label="play">' + t.play + "</button>" +
      '  <span class="vix-history-player__date" data-role="date">' + dates[lastIdx] + "</span>" +
      '  <input type="range" class="vix-history-player__slider" min="0" max="' + lastIdx + '" value="' + lastIdx + '" />' +
      '  <span class="vix-history-player__counter" data-role="counter">' + (lastIdx + 1) + ' / ' + dates.length + "</span>" +
      '  <select class="vix-history-player__speed" aria-label="' + t.speed + '">' +
      '    <option value="500">' + t.fast + " (0.5s)</option>" +
      '    <option value="1000" selected>' + t.medium + " (1s)</option>" +
      '    <option value="2000">' + t.slow + " (2s)</option>" +
      "  </select>" +
      "</div>" +
      '<div class="vix-history-player__image">' +
      '  <img data-role="img" src="' + base + dates[lastIdx] + '.png" alt="VIX Term Structure ' + dates[lastIdx] + '" />' +
      "</div>";

    var img = mount.querySelector('[data-role="img"]');
    var dateLabel = mount.querySelector('[data-role="date"]');
    var counter = mount.querySelector('[data-role="counter"]');
    var slider = mount.querySelector(".vix-history-player__slider");
    var btn = mount.querySelector(".vix-history-player__play");
    var speedSel = mount.querySelector(".vix-history-player__speed");

    function show(i) {
      i = Math.max(0, Math.min(dates.length - 1, i));
      slider.value = i;
      img.src = base + dates[i] + ".png";
      img.alt = "VIX Term Structure " + dates[i];
      dateLabel.textContent = dates[i];
      counter.textContent = (i + 1) + " / " + dates.length;
    }

    function setPlaying(p) {
      playing = p;
      btn.textContent = playing ? t.pause : t.play;
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
      if (playing) {
        timer = setInterval(function () {
          var i = parseInt(slider.value, 10);
          var next = i + 1;
          if (next >= dates.length) {
            next = 0;  // loop
          }
          show(next);
        }, speedMs);
      }
    }

    slider.addEventListener("input", function () {
      show(parseInt(slider.value, 10));
    });
    btn.addEventListener("click", function () { setPlaying(!playing); });
    speedSel.addEventListener("change", function () {
      speedMs = parseInt(speedSel.value, 10);
      if (playing) setPlaying(true);  // restart with new speed
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
