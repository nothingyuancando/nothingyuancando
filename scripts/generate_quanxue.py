"""Generate the once-only README typewriter. Requires Pillow and a CJK font.
Run: python3 scripts/generate_quanxue.py [--font /path/to/font.ttc]
"""
from pathlib import Path
import argparse, re
from PIL import Image, ImageDraw, ImageFont, ImageChops, GifImagePlugin

paragraphs = ['Agent 曰：Vibe Coding 不可以已。', 'GPT，取之于 Data，而贵于 Data；Bug，生之于 Code，而多于 Code。Prompt 直中需求，润以 Context，其答中规；虽有 Clear Chat，不复记忆者，Session 使之然也。故 Code 受 Lint 则净，Model 就 RAG 则博；君子博问而日三省乎 Prompt，则需求明而少返工矣。', '吾尝终日而 Debug 矣，不如 GPT 须臾之所改也；吾尝踮脚而看 Log 矣，不如 Agent 一搜之博见也。登 Context 而问，脑非加 RAM 也，而知者广；顺 Prompt 而呼，声非加 Token 也，而答者彰。假 Agent 者，非善敲键也，而致千行；假 MCP 者，非能分身也，而接万端。君子生非异也，善假于 GPT 也。', '积 Token 成山，账单兴焉；积 Context 成渊，幻觉生焉；积 Commit 成 Repo，而 README 自得，项目备焉。故不积小 Prompt，无以成大 App；不积小 Commit，无以至 Release。GPT 一跃，不能上线；Agent 十轮，功在重试。Debug 而舍之，红字不灭；Debug 而不舍，余额可竭。', '小 Agent 无旗舰之参数，万卡之集群，上读 README，下改 TODO，用心一也。人有百般 Model、千种 Plugin，而一个 Demo 无所寄托者，切换躁也。故 Vibe Coding 者，非终日点 Accept 也；必先明其意，再验其 Code。能跑而不测，非稳也；全绿而上线，亦未必无 Bug 也。君子曰：Token 有尽，而需求无穷；善用 Agent，亦善按 Undo 也。']

parser=argparse.ArgumentParser()
parser.add_argument('--font', type=Path)
args=parser.parse_args()
candidates=[Path('/System/Library/Fonts/Hiragino Sans GB.ttc'),
            Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]
font_path=args.font or next((p for p in candidates if p.exists()), None)
if not font_path:
    parser.error('Pass --font pointing to a font with Chinese glyphs.')
body=ImageFont.truetype(str(font_path),18)
heading=ImageFont.truetype(str(font_path),28)
credit=ImageFont.truetype(str(font_path),14)
background=(250,249,246)
ink=(55,62,71)
accent=(235,87,104)
rows=[('劝码',heading,accent,24),('作者：GPT',credit,ink,64)]
y=104
for paragraph in paragraphs:
    sentences=re.findall(r'[^；。！？!?;]+[；。！？!?;]?',paragraph)
    i=0
    while i<len(sentences):
        line=sentences[i]
        if i+1<len(sentences) and body.getlength(line+sentences[i+1])<=766:
            line+=sentences[i+1]
            i+=1
        rows.append((line,body,ink,y))
        y+=28
        i+=1
    y+=12
width=max(850,round(max(font.getlength(line) for line,font,_,_ in rows))+84)
height=y+12
canvas=Image.new('RGB',(width,height),background)
# A global palette avoids flashing colors between frames.
palette=Image.new('P',(1,1))
colors=[]
for color in (ink,accent):
    for i in range(128):
        colors.extend(round(background[k]+(color[k]-background[k])*i/127) for k in range(3))
palette.putpalette(colors)
def indexed(image):
    return image.quantize(palette=palette,dither=Image.Dither.NONE)
previous=indexed(canvas)
output=Path('assets/quanma.gif')
frames=1
with output.open('wb') as stream:
    header,_=GifImagePlugin.getheader(previous,info={'version':b'GIF89a'})
    for chunk in header: stream.write(chunk)
    for chunk in GifImagePlugin.getdata(previous,duration=250,disposal=1): stream.write(chunk)
    for line,font,color,y in rows:
        for j in range(1,len(line)+1):
            draw=ImageDraw.Draw(canvas)
            draw.rectangle((0,y,width-1,y+font.size+4),fill=background)
            draw.text((42,y),line[:j],font=font,fill=color,anchor='lt')
            current=indexed(canvas)
            bbox=ImageChops.difference(current,previous).getbbox()
            if bbox:
                duration=300 if j==len(line) else (100 if font==heading else 50)
                for chunk in GifImagePlugin.getdata(current.crop(bbox),offset=bbox[:2],duration=duration,disposal=1):
                    stream.write(chunk)
                frames+=1
            previous=current
    stream.write(b';')
canvas.save('/tmp/quanma-final.png')
Path('README.md').write_text('<div align="center">\n\n<img src="./assets/quanma.gif" width="850" alt="劝码 · 作者：GPT。逐字打出，逐行累积，播放一次后保留全文。" />\n\n</div>\n')
# Decode the actual delivered animation, including all delta frames.
with Image.open(output) as gif:
    assert gif.n_frames==frames
    assert 'loop' not in gif.info
    gif.seek(0)
    assert all(low==high for low,high in gif.convert('RGB').getextrema())
    gif.seek(gif.n_frames-1)
    assert ImageChops.difference(gif.convert('RGB'),previous.convert('RGB')).getbbox() is None
assert ''.join(line for line,_,_,_ in rows[2:])==''.join(paragraphs)
assert all(font.getlength(line) <= width-84 for line,font,_,_ in rows)
print(f'Validated {frames} cumulative GIF frames; {width}×{height}; {output.stat().st_size//1024} KB; plays once.')
