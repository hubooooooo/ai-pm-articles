(() => {
  'use strict';
  const root = document.documentElement;
  const query = new URLSearchParams(location.search);
  const validThemes = new Set(['light', 'dark']);
  let stored;
  try { stored = localStorage.getItem('theme') || localStorage.getItem('ai-pm-prototype-theme'); } catch (_) { /* file URLs may restrict storage. */ }
  const requested = query.get('theme');
  const initial = validThemes.has(requested) ? requested : validThemes.has(stored) ? stored : matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  function applyTheme(theme) {
    root.dataset.theme = theme;
    document.querySelectorAll('.theme-toggle').forEach(button => {
      button.setAttribute('aria-label', theme === 'light' ? '切换到深色模式' : '切换到浅色模式');
      button.setAttribute('aria-pressed', String(theme === 'dark'));
    });
  }
  applyTheme(initial);
  document.querySelectorAll('.theme-toggle').forEach(button => {
    button.addEventListener('click', () => {
      const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      applyTheme(theme);
      try { localStorage.setItem('theme', theme); } catch (_) { /* Storage is optional. */ }
    });
  });

  const assembly = document.querySelector('.assembly');
  if (assembly) {
    createNotebookMotion(assembly);
    const annotations = document.querySelector('.annotation-toggle');
    annotations.addEventListener('click', () => {
      const enabled = assembly.dataset.labels !== 'on';
      assembly.dataset.labels = enabled ? 'on' : 'off';
      annotations.setAttribute('aria-pressed', String(enabled));
      annotations.textContent = enabled ? '标注 开' : '标注 关';
    });
  }

  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = matchMedia('(pointer: fine)');
  const interactive = document.querySelector('.paper-stage');
  if (interactive) {
    interactive.addEventListener('pointermove', event => {
      if (reduced.matches || !finePointer.matches) return;
      const bounds = interactive.getBoundingClientRect();
      const x = (event.clientX - bounds.left) / bounds.width - .5;
      const y = (event.clientY - bounds.top) / bounds.height - .5;
      interactive.style.setProperty('--rx', `${-y*2.4}deg`);
      interactive.style.setProperty('--ry', `${x*3}deg`);
      interactive.style.setProperty('--prx', `${-y*2}deg`);
      interactive.style.setProperty('--pry', `${x*3}deg`);
    });
    interactive.addEventListener('pointerleave', () => {
      ['--rx', '--ry', '--prx', '--pry'].forEach(key => interactive.style.setProperty(key, '0deg'));
    });
  }
  root.dataset.ready = 'true';

  function createNotebookMotion(figure) {
    const expanded = figure.querySelector('[data-engine-state="exploded"]');
    const compact = figure.querySelector('[data-engine-state="assembled"]');
    if (!expanded || !compact) return;
    const expandedPaths = [...expanded.querySelectorAll('path[data-points]')];
    const compactPaths = [...compact.querySelectorAll('path[data-points]')];
    if (expandedPaths.length !== compactPaths.length) return;
    const records = expandedPaths.map((node,index) => ({
      node, a:JSON.parse(node.dataset.points), b:JSON.parse(compactPaths[index].dataset.points),
      closed:node.dataset.closed === '1', rotor:node.dataset.rotor === 'true',
      part:node.closest('.assembly-part')?.dataset.part || 'base'
    }));
    const compactLabels = [...compact.querySelectorAll('[data-anchor]')];
    const labels = [...expanded.querySelectorAll('[data-anchor]')].map((node,index) => ({
      node, a:JSON.parse(node.dataset.anchor), b:JSON.parse(compactLabels[index].dataset.anchor),
      bend:node.dataset.bend.split(',').map(Number), part:node.dataset.part,
      path:node.querySelector('.leader'), dot:node.querySelector('.anchor')
    }));
    const weights = { base:0, eval:0, tools:.2, knowledge:.45, agent:.42, skills:.62, gates:.3, context:1 };
    const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
    const buttons = [...document.querySelectorAll('.diagram-controls [data-view]')];
    const motionButton = document.querySelector('.motion-toggle');
    let playing = !reducedMotion.matches;
    let inView = true;
    let time = 0;
    let clock = 0;
    let raf = 0;
    let drawn = 0;
    let frames = 0;
    let mode = query.get('view') === 'assembled' ? 'assembled' : 'auto';
    let spread = mode === 'assembled' ? 0 : 1;
    let desiredYaw = 0;
    let desiredPitch = 0;
    let yaw = 0;
    let pitch = 0;
    let dragging = false;
    let lastX = 0;
    let lastY = 0;
    const clamp = (value,min,max) => Math.max(min,Math.min(max,value));
    const round = value => Math.round(value*100)/100;

    function controls() {
      figure.dataset.mode = mode;
      figure.dataset.motion = playing ? 'running' : 'paused';
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === mode)));
      if (motionButton) {
        motionButton.textContent = playing ? '暂停动画' : '播放动画';
        motionButton.setAttribute('aria-pressed', String(playing));
        motionButton.setAttribute('aria-label', playing ? '暂停首页装置动画' : '播放首页装置动画');
      }
    }

    function render(delta = 0) {
      const desiredSpread = mode === 'assembled' ? 0 : mode === 'exploded' ? 1 : .76+.22*Math.cos(time*.38);
      const smoothing = playing ? 1-Math.exp(-delta*7) : 1;
      spread += (desiredSpread-spread)*smoothing;
      yaw += (desiredYaw-yaw)*Math.min(1,smoothing*1.7);
      pitch += (desiredPitch-pitch)*Math.min(1,smoothing*1.7);
      const autoYaw = reducedMotion.matches && !playing ? 0 : Math.sin(time*.36)*.085;
      const autoPitch = reducedMotion.matches && !playing ? 0 : Math.sin(time*.29)*.022;
      const sy = Math.sin(yaw+autoYaw), cy = Math.cos(yaw+autoYaw);
      const sx = Math.sin(pitch+autoPitch), cx = Math.cos(pitch+autoPitch);
      const float = Math.sin(time*.95)*10;
      const rotorAngle = time*.4;
      const cr = Math.cos(rotorAngle), sr = Math.sin(rotorAngle);
      function project(a,b,part,rotor=false) {
        let x=a[0],y=a[1];
        const z=b[2]+(a[2]-b[2])*spread+(weights[part]||0)*float;
        if (rotor) { const rx=x*cr-y*sr; y=x*sr+y*cr; x=rx; }
        const xx=x*cy-y*sy;
        const yy=x*sy+y*cy;
        const y3=yy*cx-(z-100)*sx;
        const z3=yy*sx+(z-100)*cx+100;
        return [round(548+.86*xx-.8*y3),round(486+.43*xx+.45*y3-z3)];
      }
      for (const item of records) {
        let path = '';
        for (let i=0;i<item.a.length;i++) {
          const point = project(item.a[i],item.b[i],item.part,item.rotor);
          path += (i ? 'L' : 'M')+point[0]+','+point[1];
        }
        item.node.setAttribute('d',path+(item.closed ? 'Z' : ''));
      }
      for (const item of labels) {
        const [x,y]=project(item.a,item.b,item.part);
        item.path.setAttribute('d',`M${x},${y}L${item.bend[0]},${item.bend[1]}H${item.bend[2]}`);
        item.dot.setAttribute('cx',x);
        item.dot.setAttribute('cy',y);
      }
      figure.dataset.frame=String(++frames);
      figure.dataset.yaw=String(round((yaw+autoYaw)*180/Math.PI));
      figure.dataset.spread=String(round(spread));
    }

    function tick(timestamp) {
      raf = 0;
      if (!playing || !inView || document.hidden) { clock=0; return; }
      const delta=clock ? Math.min((timestamp-clock)/1000,.08) : 0;
      clock=timestamp;
      time+=delta;
      // Cap SVG geometry updates to 24 fps without running a second timer.
      if (!drawn || timestamp-drawn>=1000/24) { render(Math.max(delta,1/24)); drawn=timestamp; }
      raf=requestAnimationFrame(tick);
    }
    function resume() {
      if (playing && inView && !document.hidden && !raf) { clock=0; raf=requestAnimationFrame(tick); }
    }
    function pauseFrameLoop() {
      if (raf) cancelAnimationFrame(raf);
      raf=0;
      clock=0;
    }
    function toggleMotion() {
      playing=!playing;
      controls();
      if (playing) resume(); else pauseFrameLoop();
    }
    buttons.forEach(button => button.addEventListener('click',() => {
      mode=button.dataset.view;
      controls();
      if (!playing) render(); else resume();
    }));
    motionButton?.addEventListener('click',toggleMotion);
    figure.addEventListener('pointerdown',event => {
      if (event.button!==0) return;
      dragging=true;
      lastX=event.clientX;lastY=event.clientY;
      figure.dataset.dragging='true';
      figure.setPointerCapture(event.pointerId);
    });
    figure.addEventListener('pointermove',event => {
      if (!dragging) return;
      desiredYaw=clamp(desiredYaw+(event.clientX-lastX)*.0015,-.22,.22);
      desiredPitch=clamp(desiredPitch+(event.clientY-lastY)*.00065,-.065,.065);
      lastX=event.clientX;lastY=event.clientY;
      if (!playing) render();
    });
    function release() { dragging=false;figure.dataset.dragging='false'; }
    figure.addEventListener('pointerup',release);
    figure.addEventListener('pointercancel',release);
    figure.addEventListener('lostpointercapture',release);
    figure.addEventListener('keydown',event => {
      if (event.key===' '){ event.preventDefault();toggleMotion();return; }
      if (!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Escape'].includes(event.key)) return;
      event.preventDefault();
      if (event.key==='ArrowLeft') desiredYaw=clamp(desiredYaw-.035,-.22,.22);
      if (event.key==='ArrowRight') desiredYaw=clamp(desiredYaw+.035,-.22,.22);
      if (event.key==='ArrowUp') desiredPitch=clamp(desiredPitch-.02,-.065,.065);
      if (event.key==='ArrowDown') desiredPitch=clamp(desiredPitch+.02,-.065,.065);
      if (event.key==='Escape') {desiredYaw=0;desiredPitch=0;mode='auto';controls();}
      if (!playing) render();
    });
    reducedMotion.addEventListener('change',event => {
      if (event.matches) { playing=false;pauseFrameLoop();controls(); }
    });
    document.addEventListener('visibilitychange',() => {
      figure.dataset.suspended=String(document.hidden || !inView);
      if (document.hidden) pauseFrameLoop();else resume();
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {
        inView=entries[0].isIntersecting;
        figure.dataset.suspended=String(!inView || document.hidden);
        if (inView) resume(); else pauseFrameLoop();
      }).observe(figure);
    }
    controls();
    render();
    resume();
  }
})();
