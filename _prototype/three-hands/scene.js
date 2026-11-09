import * as THREE from 'three';
import {OutlineEffect} from 'three/addons/effects/OutlineEffect.js';
import description from './hand-description.json';
import packedGeometry from './hand-geometry.json';

/*! Shadow Hand E3M5: Shadow Robot Company / MuJoCo Menagerie, Apache-2.0.
 * Original mesh and kinematic source is retained in vendor/shadow_hand.
 * Meshes quantized, posed and rendered for AI Product Notes. Licenses: assets/licenses/. */
const stage=document.querySelector('.hands-3d-stage');
const hero=document.querySelector('.hands-hero');
const canvas=stage?.querySelector('canvas');
if(stage&&canvas) boot();

function boot(){
 let renderer;
 try{renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'low-power'});}
 catch(error){stage.dataset.ready='fallback';console.warn('3D hands unavailable; retaining the rendered poster.');return;}
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.65));
 renderer.setClearColor(0x000000,0);
 renderer.outputColorSpace=THREE.SRGBColorSpace;
 const scene=new THREE.Scene();
 const camera=new THREE.PerspectiveCamera(32,1,.1,100);
 const effect=new OutlineEffect(renderer,{defaultThickness:.00105,defaultColor:[.025,.02,.035],defaultAlpha:.85,defaultKeepAlive:true});
 const surface=new THREE.MeshBasicMaterial({color:'#f2efe8',polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1});
 const metal=new THREE.MeshBasicMaterial({color:'#f2efe8',polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1});
 const accentSurface=surface.clone(),accentMetal=metal.clone();
 const surfaces=[surface,metal,accentSurface,accentMetal];
 for(const material of surfaces){
  material.onBeforeCompile=shader=>{
   shader.vertexShader='varying vec3 vInkNormal;\n'+shader.vertexShader.replace('#include <begin_vertex>','vInkNormal=normalize(normalMatrix*normal);\n#include <begin_vertex>');
   shader.fragmentShader='varying vec3 vInkNormal;\n'+shader.fragmentShader.replace('#include <opaque_fragment>','float inkVolume=.92+.08*max(0.0,dot(normalize(vInkNormal),normalize(vec3(-.35,.55,1.0))));\noutgoingLight*=inkVolume;\n#include <opaque_fragment>');
  };
  material.customProgramCacheKey=()=> 'notebook-ink-volume-v1';
 }
 const lineMaterial=new THREE.LineBasicMaterial({color:'#3e3549',transparent:true,opacity:.68,depthTest:true});
 const accentLineMaterial=new THREE.LineBasicMaterial({color:'#639a35',transparent:true,opacity:.92,depthTest:true});
 let accentMeshCount=0;
 const geometry={},edges={};
 function bytes(base64){const binary=atob(base64);const array=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)array[i]=binary.charCodeAt(i);return array.buffer;}
 for(const [name,data] of Object.entries(packedGeometry)){
  const quantized=new Uint16Array(bytes(data.p));
  const positions=new Float32Array(quantized.length);
  for(let i=0;i<positions.length;i++)positions[i]=data.min[i%3]+quantized[i]*data.scale[i%3];
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(positions,3));
  g.setAttribute('normal',new THREE.BufferAttribute(new Int8Array(bytes(data.n)),3,true));
  g.setIndex(new THREE.BufferAttribute(data.bits===16?new Uint16Array(bytes(data.i)):new Uint32Array(bytes(data.i)),1));
  geometry[name]=g;
  geometry[name].computeBoundingBox();
  edges[name]=new THREE.EdgesGeometry(geometry[name],23);
 }
 function quat(values){return new THREE.Quaternion(values[1],values[2],values[3],values[0]).normalize();}
 function makeHand(side){
  const spec=description[side],outer=new THREE.Group(),joints=new Map(),bodies=new Map();
  outer.name=side+'-hand';
  outer.scale.setScalar(22);
  function build(item){
   const base=new THREE.Group();base.name=item.name;base.position.fromArray(item.pos);base.quaternion.copy(quat(item.quat));
   let moving=base;
   for(const joint of item.joints){
    const pivot=new THREE.Group();pivot.position.fromArray(joint.pos);moving.add(pivot);
    const contents=new THREE.Group();contents.position.fromArray(joint.pos).negate();pivot.add(contents);
    joints.set(joint.name,{node:pivot,axis:new THREE.Vector3(...joint.axis).normalize(),range:joint.range});moving=contents;
   }
   bodies.set(item.name,moving);
   for(const geom of item.geoms){
    const highlighted=/(?:wrist|ffmiddle|ffdistal)$/.test(item.name);
    const isMetal=geom.material==='metallic';
    const def=spec.meshes[geom.mesh],material=highlighted?(isMetal?accentMetal:accentSurface):(isMetal?metal:surface);
    const mesh=new THREE.Mesh(geometry[geom.mesh],material);mesh.position.fromArray(geom.pos);mesh.quaternion.copy(quat(geom.quat));mesh.scale.fromArray(def.scale);
    const edge=new THREE.LineSegments(edges[geom.mesh],highlighted?accentLineMaterial:lineMaterial);edge.renderOrder=2;mesh.add(edge);moving.add(mesh);
    if(highlighted)accentMeshCount++;
   }
   for(const child of item.children)moving.add(build(child));
   return base;
  }
  outer.add(build(spec.root));scene.add(outer);
  const prefix=side==='left'?'lh_':'rh_';
  const tip=new THREE.Object3D();tip.position.set(-.000025067,.001290492,.032007566);bodies.get(prefix+'ffdistal').add(tip);
  const palmNode=bodies.get(prefix+'palm');
  function set(name,value){const joint=joints.get(prefix+name);if(joint)joint.node.quaternion.setFromAxisAngle(joint.axis,THREE.MathUtils.clamp(value,...joint.range));}
  function pose(time){
   const wave=Math.sin(time*.55)*.045;
   set('WRJ1',-.04);set('WRJ2',.03);
   set('FFJ4',side==='left'?-.08:.06);set('FFJ3',.09+wave*.4);set('FFJ2',.07);set('FFJ1',.07);
   const fingers=side==='left'?[[.62,.82,.55],[.75,.94,.65],[.88,.98,.63]]:[[.5,.8,.55],[.66,.92,.65],[.8,1,.65]];
   for(const [i,name] of ['MF','RF','LF'].entries()){
    set(name+'J4',i===2?-.06:.02);set(name+'J3',fingers[i][0]+wave);set(name+'J2',fingers[i][1]);set(name+'J1',fingers[i][2]);
   }
   set('LFJ5',.1);set('THJ5',side==='left'?.5:.4);set('THJ4',.85);set('THJ3',.04);set('THJ2',side==='left'?-.1:.15);set('THJ1',.65);
  }
  pose(0);outer.updateMatrixWorld(true);
  const relativePalm=palmNode.getWorldQuaternion(new THREE.Quaternion());
  return {side,outer,tip,pose,relativePalm};
 }
 const left=makeHand('left'),right=makeHand('right');
 const settings={leftRoll:-1.05,rightRoll:.8,scale:21,visibleWidth:10.8};
 const tmp=new THREE.Vector3();
 const contactPoint=new THREE.Vector3(0,-.28,0);
 const contactSignal=stage.querySelector('.contact-signal');
 const pointer=new THREE.Vector2();
 let elapsed=5.5,previous=0,raf=0,frames=0,inView=true;
 let width=1,height=1,distance=11;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 function place(hand,time){
  hand.pose(time);
  const isLeft=hand.side==='left',breath=Math.sin(time*.48)*.075;
  const zAxis=new THREE.Vector3(isLeft?1:-1,isLeft?-.25:.17,isLeft?-.18:.16).normalize();
  let xAxis=new THREE.Vector3(0,1,0).addScaledVector(zAxis,-zAxis.y).normalize();
  let yAxis=new THREE.Vector3().crossVectors(zAxis,xAxis).normalize();
  const basis=new THREE.Matrix4().makeBasis(xAxis,yAxis,zAxis);
  const desired=new THREE.Quaternion().setFromRotationMatrix(basis);
  desired.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,0,1),(isLeft?settings.leftRoll:settings.rightRoll)+breath));
  hand.outer.scale.setScalar(settings.scale);
  hand.outer.quaternion.copy(desired).multiply(hand.relativePalm.clone().invert());
  hand.outer.position.set(0,0,0);hand.outer.updateMatrixWorld(true);
  hand.tip.getWorldPosition(tmp);
  const approach=(1-Math.cos(time*2*Math.PI/11))/2;
  const gap=.005+(1-approach)*.16;
  const target=new THREE.Vector3(isLeft?-gap:gap,-.28,0);
  hand.outer.position.copy(target).sub(tmp);hand.outer.updateMatrixWorld(true);
 }
 function updateTheme(){
  const dark=document.documentElement.dataset.theme==='dark';
  surface.color.set(dark?'#232522':'#f2efe8');
  for(const material of [metal,accentSurface,accentMetal])material.color.copy(surface.color);
  lineMaterial.color.set(dark?'#f1eadc':'#302538');lineMaterial.opacity=dark?.8:.9;
  const color=new THREE.Color(dark?'#f1eadc':'#302538');
  const accentColor=new THREE.Color(getComputedStyle(document.documentElement).getPropertyValue('--accent-art').trim()||(dark?'#9fdd63':'#639a35'));
  accentLineMaterial.color.copy(accentColor);accentLineMaterial.opacity=dark?.86:.92;
  for(const material of surfaces){
   const highlighted=material===accentSurface||material===accentMetal;
   material.userData.outlineParameters={color:(highlighted?accentColor:color).toArray(),thickness:highlighted?.0015:.00135,alpha:.95,visible:true,keepAlive:true};
  }
  if(stage.dataset.ready==='true')draw(elapsed);
 }
 function resize(){
  const bounds=stage.getBoundingClientRect();width=Math.max(1,bounds.width);height=Math.max(1,bounds.height);
  renderer.setSize(width,height,false);camera.aspect=width/height;
  const visibleWidth=width<700?8.6:settings.visibleWidth;
  distance=visibleWidth/(2*Math.tan(THREE.MathUtils.degToRad(camera.fov/2))*camera.aspect);
  camera.position.set(0,.28,distance);camera.lookAt(0,0,0);camera.updateProjectionMatrix();
  draw(elapsed);
 }
 function draw(time){
  place(left,time);place(right,time);
  camera.position.set(pointer.x*.8,.28+pointer.y*.55,distance);camera.lookAt(0,0,0);
  effect.render(scene,camera);stage.dataset.frame=String(++frames);stage.dataset.time=time.toFixed(3);
  if(contactSignal){
   const point=contactPoint.clone().project(camera);
   const approach=(1-Math.cos(time*2*Math.PI/11))/2;
   contactSignal.style.setProperty('--contact-x',((point.x*.5+.5)*width).toFixed(2)+'px');
   contactSignal.style.setProperty('--contact-y',((-point.y*.5+.5)*height).toFixed(2)+'px');
   contactSignal.style.setProperty('--contact-alpha',(THREE.MathUtils.smoothstep(approach,.82,.995)*.7).toFixed(3));
  }
 }
 function tick(timestamp){
  raf=0;if(document.hidden||!inView||reduced.matches){previous=0;return;}
  if(!previous)previous=timestamp;
  const delta=Math.min((timestamp-previous)/1000,.08);
  if(delta>=1/30){elapsed+=delta;previous=timestamp;draw(elapsed);}
  raf=requestAnimationFrame(tick);
 }
 function resume(){if(!raf&&!document.hidden&&inView&&!reduced.matches){previous=0;raf=requestAnimationFrame(tick);}}
 function stop(){if(raf)cancelAnimationFrame(raf);raf=0;previous=0;}
 canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();stop();stage.dataset.ready='fallback';});
 canvas.addEventListener('webglcontextrestored',()=>{stage.dataset.ready='true';draw(elapsed);resume();});
 updateTheme();resize();stage.dataset.ready='true';
 new ResizeObserver(resize).observe(stage);
 new MutationObserver(updateTheme).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
 if('IntersectionObserver' in window)new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;if(inView)resume();else stop();}).observe(stage);
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();else resume();});
 reduced.addEventListener('change',()=>{if(reduced.matches){stop();draw(5.5);}else resume();});
 hero.addEventListener('pointermove',event=>{if(event.pointerType==='touch'||reduced.matches)return;const b=hero.getBoundingClientRect();pointer.set((event.clientX-b.left)/b.width-.5,-((event.clientY-b.top)/b.height-.5));},{passive:true});
 hero.addEventListener('pointerleave',()=>pointer.set(0,0));
 window.__hands3D={
  seek(time){stop();elapsed=time;draw(time);},
  play(){resume();},
  view(x,y){pointer.set(x,y);draw(elapsed);},
  configure(values){Object.assign(settings,values);resize();},
  stats(){return {meshes:[...scene.children].reduce((sum,item)=>{item.traverse(n=>{if(n.isMesh)sum++;});return sum;},0),accentMeshes:accentMeshCount,accentColor:'#'+accentLineMaterial.color.getHexString(),triangles:renderer.info.render.triangles,perspective:camera.isPerspectiveCamera,frames,time:elapsed,drawCalls:renderer.info.render.calls};},
  tips(){return [left,right].map(hand=>hand.tip.getWorldPosition(new THREE.Vector3()).project(camera).toArray());}
 };
 if(reduced.matches)draw(5.5);else resume();
}
