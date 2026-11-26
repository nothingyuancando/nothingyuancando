from pathlib import Path
import html, re, xml.etree.ElementTree as ET
paragraphs = [
'Agent 曰：Vibe Coding 不可以已。',
'GPT，取之于 Data，而贵于 Data；Bug，生之于 Code，而多于 Code。Prompt 直中需求，润以 Context，其答中规；虽有 Clear Chat，不复记忆者，Session 使之然也。故 Code 受 Lint 则净，Model 就 RAG 则博；君子博问而日三省乎 Prompt，则需求明而少返工矣。',
'吾尝终日而 Debug 矣，不如 GPT 须臾之所改也；吾尝踮脚而看 Log 矣，不如 Agent 一搜之博见也。登 Context 而问，脑非加 RAM 也，而知者广；顺 Prompt 而呼，声非加 Token 也，而答者彰。假 Agent 者，非善敲键也，而致千行；假 MCP 者，非能分身也，而接万端。君子生非异也，善假于 GPT 也。',
'积 Token 成山，账单兴焉；积 Context 成渊，幻觉生焉；积 Commit 成 Repo，而 README 自得，项目备焉。故不积小 Prompt，无以成大 App；不积小 Commit，无以至 Release。GPT 一跃，不能上线；Agent 十轮，功在重试。Debug 而舍之，红字不灭；Debug 而不舍，余额可竭。',
'小 Agent 无旗舰之参数，万卡之集群，上读 README，下改 TODO，用心一也。人有百般 Model、千种 Plugin，而一个 Demo 无所寄托者，切换躁也。故 Vibe Coding 者，非终日点 Accept 也；必先明其意，再验其 Code。能跑而不测，非稳也；全绿而上线，亦未必无 Bug 也。君子曰：Token 有尽，而需求无穷；善用 Agent，亦善按 Undo 也。'
]
# Keep each sentence intact, including its ending punctuation.
def sentences(paragraph):
    return re.findall(r'[^；。！？!?;]+[；。！？!?;]?', paragraph)

rows=[('劝码', 'heading', 46),('作者：GPT', 'credit', 84)]
y=142
for paragraph in paragraphs:
    for line in sentences(paragraph):
        rows.append((line,'body',y));y+=43
    y+=24
height=y+10
# Reserve a full em for every non-ASCII glyph and generous Latin widths.
# Expand the canvas rather than cutting a sentence or squeezing its letters.
width=max(850, int(max(sum(24 * (.75 if ord(c)<128 else 1.05) for c in line)
                           for line,kind,_ in rows if kind=='body'))+100)
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
'<title id="title">劝码</title>',
'<desc id="desc">作者：GPT。仿《劝学》的技术梗改写。'+html.escape(''.join(paragraphs))+'</desc>',
'''<style>
  text { fill: #ff5f6d; font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; font-size: 24px; letter-spacing: 0; font-kerning: normal; }
  .heading { font-size: 32px; font-weight: 600; }
  .credit { font-size: 16px; }
  @media (prefers-reduced-motion: reduce) { .reveal { width: 100% !important; } }
</style>''']
# Animate one clip per complete line; no per-character opacity or positioning.
# SMIL's frozen final width keeps earlier lines visible throughout the passage.
delay=0
texts=[]
clips=[]
for i,(line,kind,y) in enumerate(rows):
    size={'heading':32,'credit':16,'body':24}[kind]
    duration=max(.7,len(line)*.075)
    advances=[size*(.75 if ord(c)<128 else 1.05) for c in line]
    cumulative=[0]
    for advance in advances:
        cumulative.append(cumulative[-1]+advance)
    values=';'.join(f'{n:.3f}' for n in cumulative)
    times=';'.join(f'{j/len(line):.6f}' for j in range(len(line)+1))
    clips.append(f'<clipPath id="line-{i}" clipPathUnits="userSpaceOnUse"><rect class="reveal" x="40" y="{y-size-16}" width="0" height="{size+36}"><animate attributeName="width" values="{values}" keyTimes="{times}" calcMode="discrete" begin="{delay:.3f}s" dur="{duration:.3f}s" fill="freeze" /></rect></clipPath>')
    texts.append(f'<text class="{kind}" x="40" y="{y}" xml:space="preserve" clip-path="url(#line-{i})">{html.escape(line)}</text>')
    delay+=duration+(.55 if kind!='body' else .24)
parts+=['<defs>']+clips+['</defs>']+texts+['</svg>']
Path('assets/gpt-quanxue.svg').write_text('\n'.join(parts)+'\n')
Path('README.md').write_text('<div align="center">\n\n<img src="./assets/gpt-quanxue.svg" width="850" alt="劝码。作者：GPT。全文逐行打出，保留已显示内容。" />\n\n</div>\n')
root=ET.parse('assets/gpt-quanxue.svg').getroot()
assert len(root.findall('{http://www.w3.org/2000/svg}text'))==len(rows)
assert all(len(t.attrib['x'].split()) == 1 for t in root.findall('{http://www.w3.org/2000/svg}text'))
assert [''.join(t.itertext()) for t in root.findall('{http://www.w3.org/2000/svg}text')] == [line for line,_,_ in rows]
assert ''.join(line for line,kind,_ in rows if kind=='body') == ''.join(paragraphs)
assert all(line.endswith(tuple('；。！？!?;')) for line,kind,_ in rows if kind=='body')
print(f'Validated: {len(rows)} sequential lines; {height}px canvas; completes in {delay:.1f}s; final text remains visible.')
