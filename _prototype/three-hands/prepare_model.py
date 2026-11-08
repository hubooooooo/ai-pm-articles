"""Preserve the MJCF kinematic hierarchy as compact, browser-ready scene data."""
from pathlib import Path
from copy import deepcopy
import json
import xml.etree.ElementTree as ET
import base64
import numpy as np

ROOT=Path(__file__).parent
SOURCE=ROOT/'vendor/shadow_hand'

def numbers(value, default):
    return list(map(float,value.split())) if value else default

def convert(filename):
    xml=ET.parse(SOURCE/filename).getroot()
    classes={}
    def inherit(element,parent):
        current=deepcopy(parent)
        for child in element:
            if child.tag!='default':
                current[child.tag]={**current.get(child.tag,{}),**child.attrib}
        if element.get('class'):classes[element.get('class')]=current
        for child in element.findall('default'):inherit(child,current)
    inherit(xml.find('default'),{})
    def attrs(element,tag,defaultclass):
        return {**classes.get(element.get('class',defaultclass),{}).get(tag,{}),**element.attrib}
    meshdefs={}
    for element in xml.find('asset').findall('mesh'):
        a=attrs(element,'mesh','')
        meshdefs[Path(a['file']).stem]={'file':a['file'],'scale':numbers(a.get('scale'),[1,1,1])}
    def body(element,defaultclass):
        defaultclass=element.get('childclass',defaultclass)
        result={'name':element.get('name'),'pos':numbers(element.get('pos'),[0,0,0]),'quat':numbers(element.get('quat'),[1,0,0,0]),'joints':[],'geoms':[],'children':[]}
        for joint in element.findall('joint'):
            a=attrs(joint,'joint',defaultclass)
            result['joints'].append({'name':a['name'],'axis':numbers(a.get('axis'),[0,0,1]),'pos':numbers(a.get('pos'),[0,0,0]),'range':numbers(a.get('range'),[-3.14,3.14])})
        for geom in element.findall('geom'):
            a=attrs(geom,'geom',defaultclass)
            if a.get('group')!='2' or 'mesh' not in a:continue
            result['geoms'].append({'mesh':a['mesh'],'pos':numbers(a.get('pos'),[0,0,0]),'quat':numbers(a.get('quat'),[1,0,0,0]),'material':a.get('material','black')})
        for child in element.findall('body'):result['children'].append(body(child,defaultclass))
        return result
    return {'meshes':meshdefs,'root':body(xml.find('worldbody').find('body'),'')}

data={'right':convert('right_hand.xml'),'left':convert('left_hand.xml')}
(ROOT/'hand-description.json').write_text(json.dumps(data,separators=(',',':')))

def pack_obj(path):
    vertices=[];normals=[];lookup={};positions=[];directions=[];indices=[]
    for line in path.read_text().splitlines():
        words=line.split()
        if not words:continue
        if words[0]=='v':vertices.append(list(map(float,words[1:4])))
        elif words[0]=='vn':normals.append(list(map(float,words[1:4])))
        elif words[0]=='f':
            polygon=[]
            for token in words[1:]:
                pieces=token.split('/')
                vi=int(pieces[0]);ni=int(pieces[2])
                vi=vi-1 if vi>0 else len(vertices)+vi
                ni=ni-1 if ni>0 else len(normals)+ni
                key=(vi,ni)
                if key not in lookup:
                    lookup[key]=len(positions);positions.append(vertices[vi]);directions.append(normals[ni])
                polygon.append(lookup[key])
            for i in range(1,len(polygon)-1):indices.extend([polygon[0],polygon[i],polygon[i+1]])
    xyz=np.asarray(positions,dtype=np.float64)
    low=xyz.min(axis=0);span=xyz.max(axis=0)-low;span[span==0]=1
    packed=np.rint((xyz-low)/span*65535).astype('<u2')
    normal=np.rint(np.asarray(directions)*127).clip(-127,127).astype('i1')
    index_type=16 if len(positions)<65536 else 32
    index=np.asarray(indices,dtype='<u2' if index_type==16 else '<u4')
    encode=lambda array:base64.b64encode(array.tobytes()).decode()
    return {'p':encode(packed),'n':encode(normal),'i':encode(index),'bits':index_type,'min':low.tolist(),'scale':(span/65535).tolist(),'vertices':len(positions),'triangles':len(indices)//3}

packed={path.stem:pack_obj(path) for path in SOURCE.glob('*.obj')}
(ROOT/'hand-geometry.json').write_text(json.dumps(packed,separators=(',',':')))
print('Prepared articulated hands and quantized geometry:',sum(g['triangles'] for g in packed.values()),'unique triangles.')
