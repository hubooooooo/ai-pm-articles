"""Build the original vector assembly used by the engineering direction."""
from html import escape
from math import cos, sin, pi
from pathlib import Path
import json
import sys

ROOT = Path(__file__).parent


def draw(exploded=True):
    out = []
    lift = 1 if exploded else .13

    def p(x, y, z=0):
        return (548 + .86*x - .80*y, 486 + .43*x + .45*y - z)

    def points(coords):
        return ' '.join(f'{x:.2f},{y:.2f}' for x, y in coords)

    def path3(coords, cls='detail', close=False, extra=''):
        xy = [p(*q) for q in coords]
        d = 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in xy)
        if close:
            d += ' Z'
        geometry = json.dumps([[round(v, 3) for v in q] for q in coords], separators=(',', ':'))
        out.append(f'<path class="{cls}" d="{d}" data-points="{geometry}" data-closed="{int(close)}" {extra}/>')
        if cls == 'trace' and not close:
            out.append(f'<path class="signal" d="{d}" data-points="{geometry}" data-closed="0"/>')

    def line(a, b, cls='detail'):
        path3([a, b], cls)

    def rect(x, y, w, h, z, cls='detail', cut=0):
        if cut:
            q = [(x+cut,y,z),(x+w-cut,y,z),(x+w,y+cut,z),(x+w,y+h-cut,z),
                 (x+w-cut,y+h,z),(x+cut,y+h,z),(x,y+h-cut,z),(x,y+cut,z)]
        else:
            q = [(x,y,z),(x+w,y,z),(x+w,y+h,z),(x,y+h,z)]
        path3(q, cls, True)

    def circle(x, y, z, r, cls='detail', n=40):
        path3([(x+r*cos(i*2*pi/n),y+r*sin(i*2*pi/n),z) for i in range(n)],cls,True)

    def box(x, y, w, h, z, depth=12, top='surface', side='side'):
        # Visible near faces first, then the top face.
        path3([(x,y+h,z-depth),(x+w,y+h,z-depth),(x+w,y+h,z),(x,y+h,z)],side,True)
        path3([(x+w,y,z-depth),(x+w,y+h,z-depth),(x+w,y+h,z),(x+w,y,z)],'side-light',True)
        rect(x,y,w,h,z,top)

    def screw(x,y,z,r=5):
        circle(x,y,z,r,'detail')
        circle(x,y,z,r*.42,'fine')
        line((x-r*.42,y,z),(x+r*.42,y,z),'detail')

    def cylinder(x,y,z,r,h,cls='surface'):
        # A rounded standoff with both a projected cap and longitudinal edges.
        for a in [0, pi/2]:
            line((x+r*cos(a),y+r*sin(a),z-h),(x+r*cos(a),y+r*sin(a),z),'detail')
        circle(x,y,z-h,r,'fine')
        circle(x,y,z,r,cls)
        circle(x,y,z,r*.55,'detail')

    def label(anchor, mid, end, number, title, sub, align='start', part='context'):
        x,y = p(*anchor)
        mx,my = mid
        ex,ey = end
        geometry = json.dumps(anchor, separators=(',', ':'))
        out.append(f'<g class="annotation" data-anchor="{geometry}" data-bend="{mx},{my},{ex}" data-part="{part}"><path class="leader" d="M{x:.1f},{y:.1f} L{mx},{my} H{ex}"/>'
                   f'<circle class="anchor" cx="{x:.1f}" cy="{y:.1f}" r="2.2"/>'
                   f'<text x="{ex}" y="{ey-15}" text-anchor="{align}" class="annotation-title">'
                   f'<tspan class="accent-text">{number}</tspan>  {escape(title)}</text>'
                   f'<text x="{ex}" y="{ey-5}" text-anchor="{align}" class="annotation-sub">{escape(sub)}</text></g>')

    out.append('<svg xmlns="http://www.w3.org/2000/svg" class="engine-svg" viewBox="0 0 1100 850" fill="none" role="img" aria-labelledby="engine-title engine-desc">')
    out.append('<title id="engine-title">持续运转的产品思考工作台</title><desc id="engine-desc">原创动态轴测装置。技术观察、场景理解、动手实践、复盘记录、产品判断与写作输出共同构成这本手记。</desc>')
    out.append('''<defs>
      <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><path d="M0 0V7" class="hatch-line"/></pattern>
      <pattern id="microdot" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".45" class="dot-fill"/></pattern>
    </defs>''')
    out.append('<g class="registration"><path d="M95 130h14m-7-7v14M1015 130h14m-7-7v14M95 754h14m-7-7v14M1015 754h14m-7-7v14"/></g>')
    # Ground construction guides.
    for d in [-3,-2,-1,0,1,2,3]:
        line((-340,d*62,-42),(340,d*62,-42),'construction')
        line((d*85,-235,-42),(d*85,235,-42),'construction')
    path3([(-270,-170,-39),(270,-170,-39),(270,170,-39),(-270,170,-39)],'ground',True)

    # Four machined feet and the main test/verification plate.
    for x,y in [(-233,-135),(233,-135),(-233,135),(233,135)]:
        cylinder(x,y,-12,11,23)
    out.append('<g class="assembly-part" data-part="eval">')
    box(-270,-170,540,340,0,17)
    rect(-257,-157,514,314,1,'fine',7)
    rect(-249,-149,498,298,1,'fine',5)
    for x,y in [(-234,-134),(234,-134),(-234,134),(234,134)]:
        screw(x,y,1,7)
    for y in range(-108,105,18):
        rect(238,y,8,10,1,'fine')
    for x in range(-190,180,18):
        rect(x,146,8,4,1,'fine')
    # Etched verification marks, readable as drawing detail rather than fake metrics.
    for x in [-188,-118,-48]:
        rect(x,109,53,22,1,'detail')
        line((x+8,120,1),(x+16,126,1),'accent-line')
        line((x+16,126,1),(x+30,114,1),'accent-line')
    for y in [112,119,126]:
        line((41,y,1),(163,y,1),'fine')
    out.append('</g>')

    z1=30+48*lift
    zcore=z1+31+22*lift
    zframe=zcore+40+114*lift
    # Exploded assembly axes and stand-off rods.
    for x,y in [(-226,-125),(226,-125),(-226,125),(226,125)]:
        line((x,y,1),(x,y,zframe+13),'axis')
        cylinder(x,y,z1-12,6,14)
        cylinder(x,y,zframe+9,5,10)

    # Circuit board with a deliberately drawn routing network.
    out.append('<g class="assembly-part" data-part="tools">')
    box(-244,-142,488,284,z1,9,'board')
    rect(-230,-128,460,256,z1+.2,'fine',8)
    # Connector pads on both edges, all with consistent pitch.
    for x in range(-174,181,15):
        rect(x,131,7,9,z1+1,'contact')
    for y in range(-93,91,14):
        rect(234,y,9,6,z1+1,'contact')
    # Wiring is recessed under the central package and terminated in small vias.
    for i in range(11):
        x=-157+i*29
        yy=87+(i%3)*9
        path3([(x,129,z1+1),(x,yy,z1+1),(x+12,yy-14,z1+1),(x+12,66,z1+1)],'trace')
        circle(x+12,66,z1+1,2.1,'trace')
    for i in range(9):
        y=-102+i*24
        xx=153+(i%3)*13
        path3([(232,y,z1+1),(xx,y,z1+1),(xx-17,y+12,z1+1),(99,y+12,z1+1)],'trace')
        circle(99,y+12,z1+1,2.1,'trace')
    # Four interfaces with ports, conductor slots and fasteners.
    for i in range(3):
        x=-183+i*110
        box(x,-139,82,35,z1+19,17,'surface')
        rect(x+8,-133,66,21,z1+19.5,'recess')
        for xx in range(int(x+15),int(x+67),7):
            line((xx,-129,z1+20),(xx,-116,z1+20),'fine')
        screw(x+5,-121,z1+20,2)
        screw(x+77,-121,z1+20,2)
    out.append('</g>')

    # Small reference-memory modules: stepped housings with vent detail.
    out.append('<g class="assembly-part" data-part="knowledge">')
    for j in range(2):
        x=-217+j*53
        box(x,-86,39,137,z1+28,22,'surface')
        rect(x+5,-80,29,124,z1+29,'fine',3)
        for y in range(-72,37,11):
            line((x+9,y,z1+29),(x+30,y,z1+29),'detail')
        for y in [-74,34]:
            screw(x+19,y,z1+29,2)
        for y in range(-70,40,14):
            rect(x-5,y,5,5,z1+2,'contact')
            rect(x+39,y,5,5,z1+2,'contact')
    out.append('</g>')

    # Security gate to the right: a nested, keyed frame.
    out.append('<g class="assembly-part" data-part="gates">')
    box(150,-70,60,140,z1+23,18,'surface')
    rect(159,-60,42,117,z1+24,'fine',6)
    for yy in [-44,-11,22]:
        rect(169,yy,22,18,z1+24,'recess',3)
        circle(180,yy+9,z1+24,3,'accent-line')
    out.append('</g>')

    # The central reasoning package, pins and socket gasket.
    out.append('<g class="assembly-part" data-part="agent">')
    box(-111,-94,222,188,zcore-14,8,'recess')
    rect(-104,-87,208,174,zcore-13,'fine',7)
    for i in range(17):
        q=-81+i*10
        for sign in [-1,1]:
            line((q,sign*76,zcore),(q,sign*100,zcore-13),'detail')
    for i in range(13):
        q=-60+i*10
        for sign in [-1,1]:
            line((sign*89,q,zcore),(sign*115,q,zcore-13),'detail')
    box(-91,-76,182,152,zcore+5,17,'core')
    rect(-82,-67,164,134,zcore+6,'accent-line',5)
    rect(-73,-58,146,116,zcore+6,'fine',5)
    # Finely engraved centre with a loop symbol.
    circle(0,0,zcore+7,39,'detail',72)
    circle(0,0,zcore+7,33,'fine',72)
    circle(0,0,zcore+7,24,'accent-line',64)
    for a in range(0,360,30):
        r=a*pi/180
        line((43*cos(r),43*sin(r),zcore+7),(48*cos(r),48*sin(r),zcore+7),'fine')
    path3([(-7,0,zcore+7),(0,-25,zcore+7),(7,0,zcore+7),(0,16,zcore+7)],'accent-line',True,'data-rotor="true"')
    for x,y in [(-72,-57),(72,-57),(-72,57),(72,57)]:
        screw(x,y,zcore+7,4)
    # Heat spreader ribs at the far side of the package.
    for x in range(-69,70,13):
        box(x,-63,5,32,zcore+17,9,'surface')
    out.append('</g>')

    # A floating procedures cartridge, lifted free of its socket.
    zs=z1+43+48*lift
    out.append('<g class="assembly-part" data-part="skills">')
    box(-53,100,140,38,zs,9,'surface')
    rect(-47,105,128,28,zs+1,'fine',3)
    for i in range(4):
        line((-37,111+i*5,zs+1),(15+(i%2)*35,111+i*5,zs+1),'detail')
    for x in range(-37,73,13):
        rect(x,135,6,6,zs-8,'contact')
    line((-38,119,z1+1),(-38,119,zs-9),'axis')
    line((72,119,z1+1),(72,119,zs-9),'axis')
    out.append('</g>')

    # Four separate rails leave an actual opening onto the central components.
    out.append('<g class="assembly-part" data-part="context">')
    for x,y,w,h in [(-247,-146,494,22),(-247,124,494,22),(-247,-124,22,248),(225,-124,22,248)]:
        box(x,y,w,h,zframe,11,'surface')
    for x,y in [(-226,-125),(226,-125),(-226,125),(226,125)]:
        screw(x,y,zframe+1,7)
        circle(x,y,zframe+1,11,'fine')
    for x in range(-180,190,18):
        line((x,-144,zframe+1),(x,-135,zframe+1),'fine')
    for y in range(-98,110,18):
        line((237,y,zframe+1),(245,y,zframe+1),'fine')
    # Engraved inventory plate on the floating frame.
    box(-95,-146,190,22,zframe+2,2,'recess')
    for i in range(14):
        line((-77+i*10,-141,zframe+3),(-77+i*10,-130,zframe+3),'fine')
    out.append('</g>')

    # Dimension lines remain reference marks, with no invented performance claims.
    line((-270,196,-17),(270,196,-17),'dimension')
    line((-270,182,-17),(-270,210,-17),'dimension')
    line((270,182,-17),(270,210,-17),'dimension')
    line((-300,-170,0),(-300,-170,zframe),'dimension')
    line((-312,-170,0),(-288,-170,0),'dimension')
    line((-312,-170,zframe),(-288,-170,zframe),'dimension')

    label((111,23,zcore+6),(843,349),(987,349),'01','技术观察','TECHNOLOGY · CURIOSITY','end','agent')
    label((-198,-32,z1+28),(290,313),(108,313),'02','理解场景','CONTEXT · PEOPLE','start','knowledge')
    label((194,-121,z1+20),(875,520),(1002,520),'03','动手实践','BUILD · TRY · LEARN','end','tools')
    label((28,119,zs+1),(378,535),(141,535),'04','复盘记录','REFLECT · ITERATE','start','skills')
    label((181,35,z1+24),(825,632),(1002,632),'05','产品判断','DESIGN · DECISIONS','end','gates')
    label((-65,121,1),(303,695),(122,695),'06','写作输出','WRITE · SHARE','start','eval')
    label((73,-135,zframe+1),(738,123),(932,123),'00','持续探索','A NOTEBOOK IN MOTION','end','context')
    out.append('<text x="330" y="780" class="drawing-note">AI PRODUCT NOTES — ALWAYS IN PROGRESS</text>')
    out.append('<text x="330" y="799" class="drawing-note muted-text">观察 / 实践 / 独立判断</text>')
    out.append('</svg>')
    return '\n'.join(out)


if __name__ == '__main__':
    states = []
    for mode in ['exploded','assembled']:
        svg = draw(mode=='exploded')
        for identifier in ['engine-title','engine-desc','hatch','microdot']:
            svg = svg.replace(f'id="{identifier}"', f'id="{mode}-{identifier}"')
            svg = svg.replace(f'#{identifier}', f'#{mode}-{identifier}')
        svg = svg.replace('aria-labelledby="engine-title engine-desc"',
                          f'aria-labelledby="{mode}-engine-title {mode}-engine-desc"')
        (ROOT / f'engine-{mode}.svg').write_text(svg)
        hidden = ' hidden' if mode=='assembled' else ''
        states.append(f'<div data-engine-state="{mode}"{hidden}>{svg}</div>')
    template = (ROOT/'engineering.template.html').read_text()
    template = template.replace('<!-- ENGINE-START -->\n      <!-- ENGINE-END -->',
                                '<!-- ENGINE-START -->\n'+ '\n'.join(states)+'\n<!-- ENGINE-END -->')
    (ROOT/'hero.html').write_text(template)
    if '--site' in sys.argv:
        site = ROOT.parent
        (site/'_includes').mkdir(exist_ok=True)
        (site/'assets/js').mkdir(parents=True, exist_ok=True)
        (site/'_includes/home-art.html').write_text('\n'.join(states))
        (site/'assets/css/home.css').write_text((ROOT/'prototype.css').read_text())
        (site/'assets/js/home.js').write_text((ROOT/'prototype.js').read_text())
    print('Built the animated notebook illustration, prototype' + (' and site assets.' if '--site' in sys.argv else '.'))
