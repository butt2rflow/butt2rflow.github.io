// Inject the TradingView ticker tape into the left sidebar on the home page.
// Activated on '/' (KO home) and '/en/' (EN home) — not anywhere else.
(function () {
  function isHomepage() {
    var p = location.pathname;
    return p === "/" || p === "/en/" || p === "/index.html" || p === "/en/index.html";
  }

  function ensureWidget() {
    if (!isHomepage()) return;
    var sidebar = document.querySelector(".md-sidebar--primary .md-sidebar__scrollwrap");
    if (!sidebar) return;
    if (sidebar.querySelector(".sidebar-tv-widget")) return;

    var locale = location.pathname.indexOf("/en/") === 0 ? "en" : "kr";

    var wrap = document.createElement("div");
    wrap.className = "sidebar-tv-widget";
    wrap.innerHTML = '<div class="sidebar-tv-widget__title">📈 라이브 시세</div>' +
      '<div class="tradingview-widget-container">' +
      '<div class="tradingview-widget-container__widget"></div>' +
      '</div>';
    sidebar.appendChild(wrap);

    var script = document.createElement("script");
    script.type = "text/javascript";
    script.async = true;
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js";
    script.text = JSON.stringify({
      symbols: [
        { description: "S&P 500", proName: "SP:SPX" },
        { description: "VIX", proName: "CBOE:VIX" },
        { description: "SKEW", proName: "CBOE:SKEW" },
        { description: "COR3M", proName: "CBOE:COR3M" },
        { description: "COR90D", proName: "CBOE:COR90D" },
        { description: "VVIX", proName: "CBOE:VVIX" },
      ],
      showSymbolLogo: true,
      isTransparent: true,
      displayMode: "regular",
      colorTheme: "light",
      locale: locale,
    });
    wrap.querySelector(".tradingview-widget-container").appendChild(script);

    if (locale === "en") {
      wrap.querySelector(".sidebar-tv-widget__title").textContent = "📈 Live Markets";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureWidget);
  } else {
    ensureWidget();
  }
})();
