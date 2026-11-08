"""Original, lightweight robot-hand drawing for the notebook homepage."""
from html import escape
from math import hypot
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT.parent


def make_art():
    parts = []

    def path(d, cls='hand-outline'):
        parts.append(f'<path class="{cls}" d="{d}"/>')

    def circle(x,y,r,cls='hand-detail'):
        parts.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}"/>')

    def line(a,b,cls='hand-detail'):
        path(f'M{a[0]:.2f} {a[1]:.2f}L{b[0]:.2f} {b[1]:.2f}',cls)

    def phalanx(a,b,r0,r1,terminal=False):
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=hypot(dx,dy)
        ux,uy=dx/length,dy/length
        nx,ny=-uy,ux
        ex,ey=(b[0]-ux*r1,b[1]-uy*r1) if terminal else b
        q=lambda x,y:f'{x:.2f} {y:.2f}'
        # Tapered, rounded finger armour with a visible hinge at the near end.
        path(f'M{q(a[0]+nx*r0,a[1]+ny*r0)} L{q(ex+nx*r1,ey+ny*r1)} '
             f'A{r1} {r1} 0 0 0 {q(ex-nx*r1,ey-ny*r1)} '
             f'L{q(a[0]-nx*r0,a[1]-ny*r0)} A{r0} {r0} 0 0 0 {q(a[0]+nx*r0,a[1]+ny*r0)}Z')
        # Two restrained seams make the rounded segments read as mechanical fingers.
        start=(a[0]+ux*(r0+7),a[1]+uy*(r0+7))
        end=(ex-ux*(r1+4),ey-uy*(r1+4))
        if length>70:
            line((start[0]-nx*r0*.4,start[1]-ny*r0*.4),
                 (end[0]-nx*r1*.4,end[1]-ny*r1*.4),'hand-seam')
        for distance, width in [(r0*.75,r0*.72)]:
            cx,cy=a[0]+ux*distance,a[1]+uy*distance
            line((cx+nx*width,cy+ny*width),(cx-nx*width,cy-ny*width),'hand-seam')
        circle(a[0],a[1],r0*.34)
        circle(a[0],a[1],r0*.11,'hand-seam')
        if terminal:
            cx,cy=ex-ux*8,ey-uy*8
            line((cx+nx*r1*.57,cy+ny*r1*.57),(cx-nx*r1*.57,cy-ny*r1*.57),'hand-seam')

    def finger(points,radii):
        for i in range(len(points)-1):
            phalanx(points[i],points[i+1],radii[i],radii[i+1],i==len(points)-2)

    parts.append('''<svg class="hands-illustration" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" fill="none" aria-hidden="true">
<style>
.hands-illustration path,.hands-illustration circle,.hands-illustration ellipse{vector-effect:non-scaling-stroke;stroke-linejoin:round;stroke-linecap:round}
.hands-illustration .hand-outline{fill:var(--paper,#f2efe8);stroke:var(--ink,#302b38);stroke-width:1.15}
.hands-illustration .hand-detail{fill:none;stroke:var(--ink,#302b38);stroke-width:.9}
.hands-illustration .hand-seam{fill:none;stroke:var(--ink,#302b38);stroke-width:.65;opacity:.5}
.hands-illustration .hand-accent{fill:none;stroke:var(--accent,#ac6248);stroke-width:.9;opacity:.75}
.hands-illustration .hand,.hands-illustration .index-digit{transform-box:view-box;animation-duration:9.6s;animation-timing-function:cubic-bezier(.45,0,.25,1);animation-iteration-count:infinite}
.hands-illustration .hand--left{transform-origin:220px 410px;animation-name:hands-left-reach}
.hands-illustration .hand--right{transform-origin:1400px 610px;animation-name:hands-right-reach}
.hands-illustration .index--left{transform-origin:500px 380px;animation-name:hands-left-index}
.hands-illustration .index--right{transform-origin:1140px 505px;animation-name:hands-right-index}
.hands-illustration .contact-mark{fill:var(--accent,#ac6248);opacity:0;animation:hands-contact 9.6s ease-in-out infinite}
.hands-hero[data-paused=true] .hand,.hands-hero[data-paused=true] .index-digit,.hands-hero[data-paused=true] .contact-mark{animation-play-state:paused}
@keyframes hands-left-reach{0%,100%{transform:translate(-22px,9px) rotate(-.65deg)}40%,60%{transform:translate(0,0) rotate(0)}}
@keyframes hands-right-reach{0%,100%{transform:translate(22px,5px) rotate(.65deg)}40%,60%{transform:translate(0,0) rotate(0)}}
@keyframes hands-left-index{0%,100%{transform:rotate(-1.2deg)}40%,60%{transform:rotate(0)}}
@keyframes hands-right-index{0%,100%{transform:rotate(1.1deg)}40%,60%{transform:rotate(0)}}
@keyframes hands-contact{0%,34%,69%,100%{opacity:0}43%,57%{opacity:.7}}
@media(prefers-reduced-motion:reduce){.hands-illustration .hand,.hands-illustration .index-digit,.hands-illustration .contact-mark{animation:none;transform:none}}
</style>''')

    parts.append('<g class="hand hand--left">')
    # Forearm, cuff and back plate. No labels or decorative measuring apparatus.
    path('M-100 291L162 331Q194 336 212 361L238 438Q244 462 226 480L-100 510Z')
    path('M-100 313L156 352Q174 356 181 372L207 443Q210 453 202 458L-100 488','hand-seam')
    path('M-100 340L147 374M-100 456L176 429','hand-detail')
    path('M183 341L218 334L265 454L229 482L207 469L170 368Z')
    path('M199 343L242 456M182 352L223 466','hand-seam')
    circle(220,407,24)
    circle(220,407,15,'hand-accent')
    circle(220,407,6)
    path('M235 345Q282 306 341 314L423 336Q463 349 483 390L505 444Q512 482 482 509L401 548Q365 560 328 540L270 510Q241 491 232 457L211 393Q205 365 235 345Z')
    path('M262 362Q300 333 339 340L408 360Q437 371 449 399L464 440Q472 463 449 481L391 511Q364 522 337 507L290 481Q271 469 264 443L248 395Q242 375 262 362Z','hand-detail')
    path('M278 385L315 368Q324 365 333 369L392 389Q404 394 409 405L427 449Q430 458 421 463L384 480Q374 485 363 479L305 451Q294 445 291 435Z','hand-seam')
    path('M278 473Q314 497 343 506M284 356Q313 342 335 348','hand-seam')
    for x,y in [(270,382),(334,335),(445,397),(384,532)]:
        circle(x,y,3.4)
    # Curled fingers form a readable hand silhouette beneath the extended index.
    finger([(458,428),(553,455),(569,515),(510,549)],[23,21,17,14])
    finger([(435,470),(509,508),(496,565),(441,584)],[22,20,17,13])
    finger([(397,509),(453,548),(430,594),(384,604)],[19,17,14,11])
    # Opposable thumb, slightly open rather than a clenched industrial gripper.
    finger([(278,474),(315,550),(378,582),(427,557)],[27,23,19,15])
    parts.append('<g class="index-digit index--left">')
    finger([(483,379),(599,409),(710,454),(800,480)],[25,23,18,13])
    # A zero-size anchor follows the actual fingertip for browser visual checks.
    parts.append('<circle class="left-tip" cx="800" cy="480" r=".1" fill="transparent"/>')
    parts.append('</g></g>')

    parts.append('<g class="hand hand--right">')
    path('M1700 590L1446 534Q1417 527 1399 548L1366 627Q1357 652 1383 676L1700 758Z')
    path('M1700 614L1450 557Q1435 554 1427 571L1403 626Q1397 640 1413 650L1700 731','hand-seam')
    path('M1700 647L1455 590M1700 704L1435 627','hand-detail')
    path('M1432 532L1465 550L1421 676L1383 674L1368 650L1404 548Z')
    path('M1446 546L1406 662M1458 553L1420 667','hand-seam')
    circle(1418,606,24)
    circle(1418,606,15,'hand-accent')
    circle(1418,606,6)
    path('M1400 563Q1385 518 1340 496L1255 475Q1219 468 1185 489L1137 524Q1114 544 1132 576L1205 649Q1241 686 1287 678L1367 650Q1406 631 1400 598Z')
    path('M1365 561Q1355 539 1324 525L1254 506Q1233 501 1211 514L1171 542Q1160 550 1172 568L1231 626Q1251 646 1277 640L1338 621Q1367 610 1365 589Z','hand-detail')
    path('M1328 556L1261 535Q1246 530 1234 540L1207 560L1255 608Q1265 618 1280 612L1336 593Z','hand-seam')
    path('M1234 496Q1264 491 1297 504M1366 615Q1341 635 1312 643','hand-seam')
    for x,y in [(1368,560),(1250,492),(1156,548),(1280,662)]:
        circle(x,y,3.4)
    finger([(1157,553),(1074,571),(1043,627),(1077,673)],[24,21,18,14])
    finger([(1194,597),(1127,639),(1112,697),(1158,726)],[22,20,17,13])
    finger([(1240,632),(1205,678),(1216,728),(1256,742)],[20,17,14,11])
    finger([(1340,534),(1263,481),(1196,476),(1155,513)],[27,23,18,14])
    parts.append('<g class="index-digit index--right">')
    finger([(1157,509),(1035,486),(919,477),(800,480)],[25,22,18,13])
    parts.append('<circle class="right-tip" cx="800" cy="480" r=".1" fill="transparent"/>')
    parts.append('</g></g>')
    parts.append('<circle class="contact-mark" cx="800" cy="480" r="2.4"/>')
    parts.append('</svg>')
    return '\n'.join(parts)


if __name__=='__main__':
    art=make_art()
    (SITE/'_includes/home-hands.html').write_text(art)
    (ROOT/'hands.svg').write_text(art)
    template=(ROOT/'hands.template.html').read_text()
    page=template.replace('<!-- HANDS -->',art)
    (ROOT/'hands.html').write_text(page)
    (ROOT/'hero.html').write_text(page)
    print('Built the original touching-hands illustration and homepage preview.')
