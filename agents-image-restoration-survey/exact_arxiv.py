#!/usr/bin/env python3
import urllib.request, urllib.parse, re, json, ssl, time
from pathlib import Path
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA={'User-Agent':'Hermes Agent research'}
OUT=Path('/Users/dxb/auto/agents-image-restoration-survey')
queries=[
 '"RestoreAgent"', '"An Intelligent Agentic System for Complex Image Restoration Problems"',
 '"LLMRA" "Restoration Assistant"', '"InstructIR" "Human Instructions"',
 '"Hybrid Agents for Image Restoration"', '"Restore-R1" "Image Restoration Agents"',
 '"Self-Evolving Agentic Image Restoration"', '"MoA-VR" "Video Restoration"',
 '"Chain-of-Restoration" "Universal Image Restorers"', '"LM4LV" "Low-level Vision"',
 '"PromptIR" "Image Restoration"', '"AutoDIR" "Image Restoration"',
 '"Diffusion" "image restoration" "language model"', '"all-in-one image restoration" "instruction"',
]

def fetch(q):
    params={'search_query':'all:'+q,'start':'0','max_results':'10','sortBy':'relevance','sortOrder':'descending'}
    url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=30,context=ctx) as r: return r.read().decode('utf-8','ignore')

def parse(txt,q):
    out=[]
    for e in re.findall(r'<entry>(.*?)</entry>',txt,re.S):
        def tag(n):
            m=re.search(fr'<{n}[^>]*>(.*?)</{n}>',e,re.S)
            return re.sub(r'\s+',' ',m.group(1)).strip() if m else ''
        authors=', '.join(re.findall(r'<author>\s*<name>(.*?)</name>\s*</author>',e,re.S)[:8])
        cats=re.findall(r'<category term="([^"]+)"',e)
        out.append({'query':q,'title':tag('title'),'summary':tag('summary'),'published':tag('published'),'updated':tag('updated'),'url':tag('id'),'authors':authors,'categories':cats})
    return out
items=[]
for q in queries:
    try: items+=parse(fetch(q),q)
    except Exception as e: print('ERR',q,e)
    time.sleep(3.3)
# dedupe
d={}
for it in items:
    d[it['url']]=it
items=list(d.values())
(OUT/'exact_arxiv.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'n':len(items),'titles':[x['title'] for x in items[:30]]},ensure_ascii=False,indent=2))
