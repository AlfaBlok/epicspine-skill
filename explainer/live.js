/* Plays the live scenes on a page (agent_team E78-S2 round 3). Any element with data-scene="<id>" gets that scene.
 * A scene plays while 35% of it is on screen, restarts each time it comes back, loops every `len` seconds (the
 * final frame held about 3 s) and rests on its final frame off screen, so a screenshot never catches half a frame.
 * ?still, prefers-reduced-motion or no IntersectionObserver: final frame only, nothing moves.
 * ?at=<seconds>: every scene drawn at that moment (to look at one point of the motion).
 */
(function () {
  var q = location.search;
  var still = /[?&]still\b/.test(q) || (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  var at = /[?&]at=([\d.]+)/.exec(q);
  var live = [];
  document.querySelectorAll('[data-scene]').forEach(function (host) {
    var h = LiveScenes.mount(host, host.getAttribute('data-scene'));
    if (at) { h.draw(+at[1]); return; }
    if (still || !('IntersectionObserver' in window)) return;
    var s = { h: h, on: false, t0: 0 };
    live.push(s);
    new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        s.on = e.isIntersecting;
        if (s.on) s.t0 = performance.now(); else h.final();
      });
    }, { threshold: 0.35 }).observe(host);
  });
  if (!live.length) return;
  (function tick(now) {
    live.forEach(function (s) {
      if (!s.on) return;
      var t = (now - s.t0) / 1000;
      s.h.draw(t % s.h.len);
    });
    requestAnimationFrame(tick);
  })(performance.now());
})();
