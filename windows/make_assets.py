from PIL import Image,ImageDraw,ImageFilter
import math,random
from pathlib import Path
ROOT=Path(__file__).parent/'assets';ROOT.mkdir(exist_ok=True)
random.seed(27)
W,H=1550,340
im=Image.new('RGB',(W,H)); pix=im.load()
for y in range(H):
 for x in range(W):
  wave=.05*math.sin(x/150)+.018*math.sin(y/30)
  glow=max(0,1-math.sqrt(((x-1150)/790)**2+((y-130)/400)**2))
  pix[x,y]=(int(9+glow*35+wave*20),int(15+glow*26+wave*14),int(20+glow*14+wave*8))
d=ImageDraw.Draw(im,'RGBA')
# distant sun
cx,cy=1170,127
for r in range(140,10,-5):
 a=int(13*(1-r/150))
 d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(236,176,87,a))
d.ellipse((cx-61,cy-61,cx+61,cy+61),fill=(203,154,84,48))
# hills layers
for layer,col in [(0,(43,44,40,255)),(1,(27,34,35,255)),(2,(18,26,30,255))]:
 pts=[(0,H)]
 for x in range(0,W+40,30):
  y=202+layer*50+35*math.sin(x/120+layer*2)+12*math.sin(x/41)
  pts.append((x,y))
 pts.append((W,H));d.polygon(pts,fill=col)
# fortress silhouette, right
sil=(12,18,23,255)
x0=1110
# walls
for x1,x2,top,bottom in [(1060,1400,210,340),(1115,1168,155,315),(1260,1310,137,310),(1370,1414,179,315)]:
 d.rectangle((x1,top,x2,bottom),fill=sil)
 d.rectangle((x1-7,top-12,x2+7,top+6),fill=sil)
 for x in range(x1-5,x2+1,17):d.rectangle((x,top-21,x+10,top-7),fill=sil)
d.polygon([(1242,142),(1286,103),(1329,142)],fill=sil)
d.polygon([(1100,157),(1144,111),(1182,157)],fill=sil)
for x,y in [(1134,197),(1280,184),(1380,218)]:d.arc((x,y,x+25,y+53),180,360,fill=(207,150,69,135),width=3)
# horizontal filigree lines
for y in [12,328]:d.line([(15,y),(W-15,y)],fill=(184,139,80,90),width=1)
for x in range(12,210,17):
 d.line([(x,321),(x+6,325)],fill=(202,166,106,35),width=1)
im.save(ROOT/'medieval_banner.png',optimize=True)
# shield crest
S=280
crest=Image.new('RGBA',(S,S),(0,0,0,0));e=ImageDraw.Draw(crest)
shield=[(140,10),(252,51),(238,179),(194,240),(140,271),(86,240),(42,179),(28,51)]
e.polygon(shield,fill=(8,17,22,255),outline=(224,176,99,255),width=10)
inside=[(140,27),(233,63),(220,173),(184,225),(140,250),(96,225),(60,173),(47,63)]
e.polygon(inside,fill=(26,39,43,255),outline=(117,86,54,255),width=3)
e.polygon([(140,61),(202,86),(189,170),(140,217),(91,170),(78,86)],fill=(153,113,61,255))
e.polygon([(140,76),(187,94),(174,160),(140,197),(106,160),(93,94)],fill=(23,32,33,255))
e.line([(140,92),(140,185)],fill=(236,204,137,255),width=13)
e.line([(105,127),(175,127)],fill=(236,204,137,255),width=12)
e.polygon([(140,74),(149,96),(132,96)],fill=(236,204,137,255))
e.arc((101,143,178,213),30,150,fill=(236,204,137,200),width=5)
crest.resize((160,160),Image.Resampling.LANCZOS).save(ROOT/'kruchyx_crest.png')
# left ornament
orn=Image.new('RGBA',(400,22),(0,0,0,0));od=ImageDraw.Draw(orn)
od.line((0,11,185,11),fill=(167,122,69,160),width=1)
od.polygon([(200,2),(209,11),(200,20),(191,11)],fill=(185,142,79,235))
od.line((215,11,400,11),fill=(167,122,69,160),width=1)
orn.save(ROOT/'divider_gold.png')
print([p.name for p in ROOT.iterdir()])
