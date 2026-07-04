#!/usr/bin/env python3
import urllib.request, urllib.parse, json, ssl, time, re, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

OUT = Path('/Users/dxb/auto/agents-image-restoration-survey')
OUT.mkdir(parents=True, exist_ok=True)
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
EMAIL='clawtoken@163.com'
UA={'User-Agent': f'Hermes Agent research (mailto:{EMAIL})'}

queries = [
    'agent image restoration',
    'multimodal large language model image restoration agent',
    'large language model image restoration',
    'LLM agent image restoration',
    'vision language model image restoration',
    'autonomous image restoration',
    'tool learning image restoration',
    'all-in-one image restoration language model',
    'image restoration foundation model agent',
    'diffusion restoration agent',
    'degradation-aware image restoration language',
    'prompt image restoration MLLM',
    'Restoration agent image',
]

def get(url, timeout=35):
    req=urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()

def reconstruct(inv):
    if not inv: return ''
    words={}
    for w, poss in inv.items():
        for p in poss: words[p]=w
    return ' '.join(words.get(i,'') for i in range(max(words.keys())+1)) if words else ''

def search_openalex(q):
    params={
        'search': q,
        'filter':'publication_year:2023-2026,type:article|conference|preprint',
        'per_page':'50',
        'select':'id,doi,title,publication_year,cited_by_count,authorships,primary_location,open_access,abstract_inverted_index,concepts,keywords,publication_date',
        'mailto': EMAIL,
    }
    url='https://api.openalex.org/works?'+urllib.parse.urlencode(params)
    for a in range(3):
        try:
            return json.loads(get(url).decode())
        except Exception as e:
            time.sleep(4*(a+1))
    return {'results':[]}

def search_arxiv(q):
    params={'search_query':'all:'+q,'start':'0','max_results':'20','sortBy':'submittedDate','sortOrder':'descending'}
    url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode(params)
    try:
        txt=get(url, timeout=35).decode('utf-8', errors='ignore')
    except Exception:
        return []
    entries=re.findall(r'<entry>(.*?)</entry>', txt, flags=re.S)
    out=[]
    for e in entries:
        def tag(name):
            m=re.search(fr'<{name}[^>]*>(.*?)</{name}>', e, flags=re.S)
            return re.sub(r'\s+',' ', m.group(1)).strip() if m else ''
        title=tag('title')
        abstract=tag('summary')
        published=tag('published')[:10]
        arxiv_id=tag('id')
        authors=', '.join(re.findall(r'<author>\s*<name>(.*?)</name>\s*</author>', e, flags=re.S)[:6])
        cats=re.findall(r'<category term="([^"]+)"', e)
        out.append({'source':'arxiv','query':q,'title':title,'year':int(published[:4] or 0),'date':published,'authors':authors,'venue':'arXiv','url':arxiv_id,'doi':'','cited_by':0,'abstract':abstract,'categories':cats})
    return out

def search_dblp(q):
    params={'q':q,'h':'50','format':'xml'}
    url='https://dblp.org/search/publ/api?'+urllib.parse.urlencode(params)
    try:
        xml=get(url, timeout=20).decode('utf-8', errors='ignore')
        root=ET.fromstring(xml)
    except Exception:
        return []
    out=[]
    for hit in root.findall('.//hit'):
        info=hit.find('info')
        if info is None: continue
        title=info.findtext('title') or ''
        year=int(info.findtext('year') or 0)
        if year < 2023: continue
        authors_el=info.find('authors')
        authors=', '.join([(a.text or '') for a in authors_el.findall('author')[:6]]) if authors_el is not None else ''
        out.append({'source':'dblp','query':q,'title':title,'year':year,'date':str(year),'authors':authors,'venue':info.findtext('venue') or '', 'url':info.findtext('ee') or info.findtext('url') or '', 'doi':info.findtext('doi') or '', 'cited_by':0,'abstract':''})
    return out

all_items=[]
for i,q in enumerate(queries):
    print('OpenAlex', i+1, q)
    data=search_openalex(q)
    for r in data.get('results',[]):
        src=(r.get('primary_location') or {}).get('source') or {}
        authors=', '.join([a.get('author',{}).get('display_name','') for a in r.get('authorships',[])[:6]])
        all_items.append({'source':'openalex','query':q,'title':r.get('title') or '', 'year':r.get('publication_year'), 'date':r.get('publication_date') or str(r.get('publication_year')), 'authors':authors, 'venue':src.get('display_name') or '', 'url':r.get('id'), 'doi':r.get('doi') or '', 'cited_by':r.get('cited_by_count') or 0, 'abstract':reconstruct(r.get('abstract_inverted_index')), 'oa_url':(r.get('open_access') or {}).get('oa_url') or ''})
    time.sleep(2.1)

for i,q in enumerate(queries):
    print('arXiv', i+1, q)
    all_items.extend(search_arxiv(q))
    time.sleep(3.4)

for i,q in enumerate(queries[:10]):
    print('DBLP', i+1, q)
    all_items.extend(search_dblp(q))
    time.sleep(2.0)

# dedupe and relevance score
relevant_terms = ['restoration','restore','denois','deblur','derain','dehaze','super-resolution','super resolution','low-light','inpaint','degradation','image enhancement','image repair']
agent_terms = ['agent','llm','large language','language model','multimodal','vision-language','vision language','mllm','tool','autonomous','planner','planning','gpt','chatgpt','foundation model','prompt']
exclude_terms = ['medical image registration','speech','audio','point cloud','remote sensing change detection']
seen={}; dedup=[]
for it in all_items:
    title=re.sub(r'\s+',' ', it.get('title','')).strip().rstrip('.')
    if not title: continue
    key=(it.get('doi') or title.lower())
    if key in seen:
        # keep higher citation / richer abstract
        j=seen[key]
        if it.get('cited_by',0)>dedup[j].get('cited_by',0): dedup[j].update(it)
        elif len(it.get('abstract',''))>len(dedup[j].get('abstract','')): dedup[j]['abstract']=it.get('abstract','')
        continue
    it['title']=title
    seen[key]=len(dedup); dedup.append(it)

filtered=[]
for it in dedup:
    text=(it['title']+' '+it.get('abstract','')+' '+it.get('query','')).lower()
    if any(x in text for x in exclude_terms): continue
    r=sum(1 for x in relevant_terms if x in text)
    a=sum(1 for x in agent_terms if x in text)
    if r>=1 and a>=1:
        it['score']=r*3+a*4+min(it.get('cited_by',0),50)/10 + (2 if it.get('year',0)>=2024 else 0)
        filtered.append(it)

filtered.sort(key=lambda x:(x.get('score',0), x.get('year',0), x.get('cited_by',0)), reverse=True)
(OUT/'raw_items.json').write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT/'filtered_papers.json').write_text(json.dumps(filtered, ensure_ascii=False, indent=2), encoding='utf-8')

# markdown summary table top 80
lines=[f'# Agents for Image Restoration survey data\n', f'Generated: {datetime.now().isoformat()}\n', f'Raw items: {len(all_items)}; dedup: {len(dedup)}; filtered: {len(filtered)}\n', '', '| # | Year | Title | Venue | Cites | Source | URL |', '|---|---:|---|---|---:|---|---|']
for k,it in enumerate(filtered[:80],1):
    title=it['title'].replace('|','/')
    venue=(it.get('venue') or '').replace('|','/')
    url=it.get('doi') or it.get('url') or it.get('oa_url') or ''
    lines.append(f'| {k} | {it.get("year","")} | {title} | {venue} | {it.get("cited_by",0)} | {it.get("source","")} | {url} |')
(OUT/'data_summary.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'raw':len(all_items),'dedup':len(dedup),'filtered':len(filtered),'top':[x['title'] for x in filtered[:10]]}, ensure_ascii=False, indent=2))
