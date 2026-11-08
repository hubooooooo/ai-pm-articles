(() => {
  'use strict';
  const root=document.documentElement;
  const query=new URLSearchParams(location.search);
  let stored;
  try{stored=localStorage.getItem('theme');}catch(_){/* Storage is optional. */}
  const valid=value=>value==='light'||value==='dark';
  const requested=query.get('theme');
  const initial=valid(requested)?requested:valid(stored)?stored:matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
  const themeButton=document.querySelector('.theme-toggle');
  function theme(value){
    root.dataset.theme=value;
    themeButton?.setAttribute('aria-label',value==='dark'?'切换到浅色模式':'切换到深色模式');
    themeButton?.setAttribute('aria-pressed',String(value==='dark'));
  }
  theme(initial);
  themeButton?.addEventListener('click',()=>{
    const next=root.dataset.theme==='dark'?'light':'dark';
    theme(next);
    try{localStorage.setItem('theme',next);}catch(_){/* Storage is optional. */}
  });
  const hero=document.querySelector('.hands-hero');
  if(hero){
    let inView=true;
    const reduced=matchMedia('(prefers-reduced-motion: reduce)');
    function visibility(){
      hero.dataset.paused=String(document.hidden||!inView);
      hero.dataset.motion=reduced.matches?'reduced':document.hidden||!inView?'paused':'running';
    }
    document.addEventListener('visibilitychange',visibility);
    reduced.addEventListener('change',visibility);
    if('IntersectionObserver' in window){
      new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;visibility();}).observe(hero);
    }
    visibility();
  }
  root.dataset.ready='true';
})();
