// Move the build-time "recent posts + categories" block (hooks/home_sidebar.py)
// from the homepage content into the left sidebar, which is otherwise empty.
(function () {
  function place() {
    var src = document.getElementById("home-sidebar-src");
    if (!src) return;
    var nav = document.querySelector(".md-sidebar--primary .md-sidebar__inner");
    if (!nav) return;
    src.removeAttribute("hidden");
    src.removeAttribute("id");
    nav.appendChild(src);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", place);
  } else {
    place();
  }
})();
