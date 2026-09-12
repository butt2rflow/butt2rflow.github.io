// Open off-site links in a new tab so readers don't lose the article.
document.addEventListener("DOMContentLoaded", function () {
  var host = window.location.hostname;
  var links = document.querySelectorAll('a[href]');
  for (var i = 0; i < links.length; i++) {
    var a = links[i];
    if (a.hostname && a.hostname !== host) {
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    }
  }
});
