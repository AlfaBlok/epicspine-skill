/* EpicTeam page, agent_team E43-S11 round 2: plays the whole-loop scenes (scenes.js, a copy of agent_team
 * docs/proposals/e84-s12-whole-loop-video) one after another while the section is on screen: the zoom-out view, then
 * the seven stops Jordi agreed on E84-A2. A step in the list jumps there; Pause holds the frame.
 * prefers-reduced-motion or ?still: each scene rests on its final frame and nothing moves until Play is pressed.
 */
(function () {
  var root = document.querySelector('.loopp');
  if (!root || !window.LiveScenes) return;
  var host = root.querySelector('.loopp-scene');
  var btns = [].slice.call(root.querySelectorAll('.loopp-steps button'));
  var head = root.querySelector('.loopp-cap b'), line = root.querySelector('.loopp-cap span');
  var play = root.querySelector('.loopp-play'), bar = root.querySelector('.loopp-bar i');
  var still = /[?&]still\b/.test(location.search) || (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  var info = {};
  LiveScenes.list.forEach(function (s) { info[s.id] = s; });
  var ids = btns.map(function (b) { return b.getAttribute('data-s'); });
  var idx = 0, h = null, on = false, playing = !still, elapsed = 0, last = 0;

  function show(i) {
    idx = (i + ids.length) % ids.length;
    h = LiveScenes.mount(host, ids[idx]);
    elapsed = 0;
    btns.forEach(function (b, k) { if (k === idx) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current'); });
    head.textContent = info[ids[idx]].headline;
    line.textContent = info[ids[idx]].line;
    if (playing) h.draw(0);
    bar.style.width = playing ? '0' : '100%';
  }
  function setPlaying(p) {
    playing = p;
    play.textContent = p ? 'Pause' : 'Play';
    play.setAttribute('aria-pressed', p ? 'false' : 'true');
    if (!p) { h.final(); bar.style.width = '100%'; } else { elapsed = 0; h.draw(0); }
  }

  btns.forEach(function (b, k) { b.addEventListener('click', function () { show(k); if (!playing) h.final(); }); });
  play.hidden = false;
  play.addEventListener('click', function () { setPlaying(!playing); });
  show(0);
  setPlaying(playing);

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { es.forEach(function (e) { on = e.isIntersecting; }); }, { threshold: 0.35 }).observe(host);
  } else on = true;

  (function tick(now) {
    var dt = last ? Math.min((now - last) / 1000, 0.1) : 0;
    last = now;
    if (playing && on) {
      elapsed += dt;
      if (elapsed >= h.len) show(idx + 1);
      else { h.draw(elapsed); bar.style.width = (100 * elapsed / h.len).toFixed(1) + '%'; }
    }
    requestAnimationFrame(tick);
  })(performance.now());
})();
