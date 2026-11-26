from pathlib import Path
import pymupdf,json
from PIL import Image,ImageOps,ImageDraw
r=Path(__file__).resolve().parents[3];pdf=r.parent/'output/pdf/Project_24i-3068_24i-3132_24i-3050_C.pdf';dest=r.parent/'tmp/pdfs';dest.mkdir(parents=True,exist_ok=True)
doc=pymupdf.open(pdf);issues=[];thumbs=[]
for i,page in enumerate(doc):
 pix=page.get_pixmap(matrix=pymupdf.Matrix(1.2,1.2));path=dest/f'page-{i+1:02}.png';pix.save(path)
 for block in page.get_text('blocks'):
  x0,y0,x1,y1=block[:4]
  if x0<0 or y0<0 or x1>page.rect.width+1 or y1>page.rect.height+1:issues.append({'page':i+1,'box':[x0,y0,x1,y1]})
 im=Image.open(path).convert('RGB');im.thumbnail((238,337));canvas=Image.new('RGB',(258,365),'#dce4eb');canvas.paste(im,((258-im.width)//2,10));ImageDraw.Draw(canvas).text((12,347),f'Page {i+1}',fill='black');thumbs.append(canvas)
for start in range(0,len(thumbs),12):
 sheet=Image.new('RGB',(258*4,365*3),'white')
 for j,im in enumerate(thumbs[start:start+12]):sheet.paste(im,((j%4)*258,(j//4)*365))
 sheet.save(dest/f'contact-{start//12+1}.png')
(r/'tests/team/evidence/pdf-layout-check.json').write_text(json.dumps({'pages':len(doc),'out_of_page_text_blocks':issues,'rendered':True},indent=2))
print('Rendered',len(doc),'pages; out-of-page blocks:',len(issues))
