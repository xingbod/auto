#!/usr/bin/env python3
import urllib.request, urllib.parse, urllib.error, json, ssl, time, re, xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter

OUT=Path('/Users/dxb/auto/ai-aging-research-survey')
OUT.mkdir(parents=True, exist_ok=True)
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
EMAIL='research@example.com'
UA=f'Hermes Agent (mailto:{EMAIL})'

OPENALEX='https://api.openalex.org/works'
DBLP='https://dblp.org/search/publ/api'
ARXIV='https://export.arxiv.org/api/query'

QUERIES=[
 'artificial intelligence aging research', 'machine learning aging biomarker', 'deep learning aging clock',
 'epigenetic clock machine learning', 'proteomic aging clock', 'transcriptomic aging clock', 'single-cell aging atlas machine learning',
 'AI longevity drug discovery', 'machine learning senolytic drug discovery', 'deep learning cellular senescence',
 'foundation model aging biology', 'generative AI aging biology', 'AI geroscience', 'aging biomarker prediction',
 'biological age prediction machine learning', 'clinical aging AI frailty', 'longevity intervention machine learning'
]

TOPICS={
 'Aging clocks / biological age': ['aging clock','age clock','biological age','epigenetic clock','proteomic clock','transcriptomic clock','methylation age','age prediction','ageing clock'],
 'Multi-omics / biomarkers': ['multi-omics','omics','proteomic','metabolomic','transcriptomic','methylation','biomarker','blood','plasma','microbiome'],
 'Single-cell / spatial aging': ['single-cell','single cell','spatial','cell atlas','cellular atlas','tabula','senescence atlas'],
 'Drug discovery / senolytics': ['drug','senolytic','compound','screening','repurposing','small molecule','target discovery','intervention'],
 'Imaging / histology / morphology': ['image','imaging','histology','pathology','retina','brain age','MRI','morphology','radiomics'],
 'Clinical longevity / frailty': ['clinical','frailty','mortality','healthspan','disease','risk','cohort','ehr','electronic health'],
 'Mechanism modeling / causal': ['causal','mechanism','network','pathway','gene regulatory','systems biology','foundation model','generative'],
 'Review / perspective': ['review','survey','perspective','framework','roadmap']
}

def req_json(url, timeout=30, retries=3, sleep=2):
    for a in range(retries):
        try:
            request=urllib.request.Request(url, headers={'User-Agent':UA})
            with urllib.request.urlopen(request, timeout=timeout, context=ctx) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code==429:
                time.sleep(5*(a+1)); continue
            return {'error':f'HTTP {e.code}'}
        except Exception as e:
            if a==retries-1: return {'error':str(e)}
            time.sleep(sleep*(a+1))

def reconstruct(inv):
    if not inv: return ''
    words={}
    for w, poss in inv.items():
        for p in poss: words[p]=w
    if not words: return ''
    return ' '.join(words.get(i,'') for i in range(max(words)+1))

def norm(s): return re.sub(r'\s+',' ',(s or '').strip())

def topic_assign(title, abstract):
    text=(title+' '+abstract).lower()
    hits=[]
    for t,kws in TOPICS.items():
        if any(kw.lower() in text for kw in kws): hits.append(t)
    return hits or ['Other']

# OpenAlex
papers={}
for q in QUERIES:
    params={
        'search':q,
        'filter':'publication_year:2020-2026,type:article|conference',
        'per_page':'40',
        'select':'id,doi,title,publication_year,cited_by_count,authorships,primary_location,open_access,abstract_inverted_index,concepts,keywords',
        'mailto':EMAIL
    }
    url=OPENALEX+'?'+urllib.parse.urlencode(params)
    data=req_json(url)
    if 'results' not in data:
        print('OpenAlex error', q, data); continue
    for w in data['results']:
        title=norm(w.get('title'))
        if not title: continue
        abstract=reconstruct(w.get('abstract_inverted_index'))
        text=(title+' '+abstract).lower()
        # relevance filter
        if not any(x in text for x in ['aging','ageing','longevity','senescence','biological age','healthspan','frailty','geroscience']):
            continue
        if not any(x in text for x in ['artificial intelligence','machine learning','deep learning','neural','model','algorithm','foundation','generative','prediction','computational']):
            continue
        oid=w.get('doi') or w.get('id') or title.lower()
        src=(w.get('primary_location') or {}).get('source') or {}
        authors=', '.join([(a.get('author') or {}).get('display_name','') for a in w.get('authorships',[])[:5]])
        papers[oid]={
            'source':'OpenAlex','title':title,'year':w.get('publication_year'),'citations':w.get('cited_by_count') or 0,
            'doi':w.get('doi') or '', 'venue':src.get('display_name') or '', 'authors':authors,
            'abstract':abstract[:1200], 'url':((w.get('open_access') or {}).get('oa_url') or w.get('doi') or w.get('id') or ''),
            'topics':topic_assign(title, abstract)
        }
    time.sleep(1.5)

# DBLP XML
dblp_queries=['machine learning aging','deep learning aging','artificial intelligence longevity','aging clock','biological age prediction','senescence machine learning','frailty prediction machine learning','brain age deep learning']
for q in dblp_queries:
    url=DBLP+'?'+urllib.parse.urlencode({'q':q,'h':50,'format':'xml'})
    try:
        request=urllib.request.Request(url, headers={'User-Agent':UA})
        with urllib.request.urlopen(request, timeout=20, context=ctx) as r:
            xml=r.read().decode('utf-8','ignore')
        root=ET.fromstring(xml)
        for hit in root.findall('.//hit'):
            info=hit.find('info')
            if info is None: continue
            title=norm(info.findtext('title') or '')
            year=int(info.findtext('year') or 0)
            if year<2020 or not title: continue
            t=title.lower()
            if not any(x in t for x in ['aging','ageing','longevity','senescence','frailty','biological age','brain age']): continue
            venue=info.findtext('venue') or ''
            doi=info.findtext('doi') or ''
            ee=info.findtext('ee') or ''
            authors_el=info.find('authors')
            authors=', '.join([a.text or '' for a in (authors_el.findall('author') if authors_el is not None else [])[:5]])
            key=doi or ee or title.lower()
            if key not in papers:
                papers[key]={'source':'DBLP','title':title,'year':year,'citations':0,'doi':doi,'venue':venue,'authors':authors,'abstract':'','url':ee,'topics':topic_assign(title,'')}
        time.sleep(2)
    except Exception as e:
        print('DBLP error', q, e)

# arXiv API
arxiv_queries=['all:"aging clock" AND all:"machine learning"','all:"biological age" AND all:"deep learning"','all:"longevity" AND all:"artificial intelligence"','all:"senescence" AND all:"machine learning"','all:"aging" AND all:"foundation model"']
for q in arxiv_queries:
    url=ARXIV+'?'+urllib.parse.urlencode({'search_query':q,'start':'0','max_results':'20','sortBy':'submittedDate','sortOrder':'descending'})
    try:
        request=urllib.request.Request(url, headers={'User-Agent':UA})
        with urllib.request.urlopen(request, timeout=30) as r:
            xml=r.read().decode('utf-8','ignore')
        for entry in re.findall(r'<entry>(.*?)</entry>', xml, re.S):
            title=norm(re.sub('<.*?>',' ', re.search(r'<title>(.*?)</title>', entry, re.S).group(1))) if re.search(r'<title>(.*?)</title>', entry, re.S) else ''
            summary=norm(re.sub('<.*?>',' ', re.search(r'<summary>(.*?)</summary>', entry, re.S).group(1))) if re.search(r'<summary>(.*?)</summary>', entry, re.S) else ''
            year=int((re.search(r'<published>(\d{4})-', entry) or [None,0])[1])
            aid=(re.search(r'<id>(.*?)</id>', entry) or [None,''])[1]
            if year<2020 or not title: continue
            text=(title+' '+summary).lower()
            if not any(x in text for x in ['aging','ageing','longevity','senescence','biological age','frailty']): continue
            authors=', '.join(re.findall(r'<name>(.*?)</name>', entry)[:5])
            if aid not in papers:
                papers[aid]={'source':'arXiv','title':title,'year':year,'citations':0,'doi':'','venue':'arXiv','authors':authors,'abstract':summary[:1200],'url':aid,'topics':topic_assign(title, summary)}
        time.sleep(3.5)
    except Exception as e:
        print('arXiv error', q, e)

plist=list(papers.values())
plist.sort(key=lambda x:(x.get('citations',0), x.get('year') or 0), reverse=True)
# stats
stats={
 'total':len(plist),
 'by_year':Counter(str(p.get('year')) for p in plist),
 'by_source':Counter(p.get('source') for p in plist),
 'by_topic':Counter(t for p in plist for t in p.get('topics',[])),
 'top_venues':Counter(p.get('venue') or 'Unknown' for p in plist).most_common(20)
}
(OUT/'papers.json').write_text(json.dumps(plist, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT/'stats.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
# markdown summary
lines=[]
lines.append('# AI × 衰老研究调研数据摘要\n')
lines.append(f'- Total papers: {stats["total"]}\n')
lines.append(f'- Sources: {dict(stats["by_source"])}\n')
lines.append(f'- Years: {dict(stats["by_year"])}\n')
lines.append('## Topics\n')
for k,v in stats['by_topic'].most_common(): lines.append(f'- {k}: {v}')
lines.append('\n## Top papers by OpenAlex citations\n')
for i,p in enumerate(plist[:35],1):
    lines.append(f'{i}. **{p["title"]}** ({p["year"]}, {p["venue"]}, {p["citations"]}引) — {p["authors"]}')
    if p.get('abstract'): lines.append(f'   - {p["abstract"][:300]}...')
(OUT/'survey-data-summary.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps(stats, ensure_ascii=False, indent=2))
print('saved', OUT)
