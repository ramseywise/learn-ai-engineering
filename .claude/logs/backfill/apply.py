import json,re,glob,sys,os
R='/Users/ramsey-wise/workspace/learn-ai-engineering/'
os.chdir(R)
src={r['key']:r for r in json.load(open('.claude/logs/references-backfill.json'))}
props=[]
for f in sorted(glob.glob('.claude/logs/backfill/out/batch*.json')):
    props+=json.load(open(f))
dry='--apply' not in sys.argv
def slug(h):
    h=h.strip().lower()
    h=re.sub(r'[^\w\- ]','',h)
    return h.replace(' ','-')
# 1. edits
fails=[]
for p in props:
    for e in p.get('edits',[]):
        t=open(e['file']).read()
        c=t.count(e['old'])
        if c!=1: fails.append((p['key'],e['file'],c,e['old'][:80])); continue
        if not dry: open(e['file'],'w').write(t.replace(e['old'],e['new']))
print('edit failures',fails)
# 2. rows
TARGET={'llm-fundamentals':'generative-ai/01-llm-fundamentals/references.md',
 'prompt':'ai-engineering/01-prompt-engineering/README.md',
 'loop':'ai-engineering/04-loop-engineering/references.md',
 'context':'ai-engineering/02-context-engineering/references.md'}
def key_of(row):
    m=re.search(r'arxiv\.org/abs/(\d{4})\.\d+',row) or re.search(r'\[(\d{4})\.\d{4,5}\]',row)
    if m: return m.group(1)
    m=re.search(r'\((?:[^()]*?)((?:19|20)\d\d)',row)
    return (m.group(1)[2:]+'12') if m else '0000'
for home,path in TARGET.items():
    rows=[p for p in props if src[p['key']]['home']==home and p.get('verdict')!='skip' and p.get('row')]
    if not rows: continue
    lines=open(path).read().split('\n')
    s=next(i for i,l in enumerate(lines) if re.match(r'#+ AI Papers of the Week',l))
    hdr=next(i for i in range(s,len(lines)) if lines[i].startswith('|---'))
    end=hdr+1
    while end<len(lines) and lines[end].startswith('|'): end+=1
    table=lines[hdr+1:end]
    for p in sorted(rows,key=lambda p:key_of(p['row']),reverse=True):
        k=key_of(p['row'])
        idx=next((i for i,l in enumerate(table) if key_of(l)<k),len(table))
        table.insert(idx,p['row'].strip())
    lines[hdr+1:end]=table
    print(path,len(rows),'rows')
    if not dry: open(path,'w').write('\n'.join(lines))
# 3. anchors
for p in props:
    for m in re.finditer(r'\]\(([^)#]+)#([^)]+)\)',p.get('row','')):
        f=os.path.normpath(os.path.join(os.path.dirname(TARGET[src[p['key']]['home']]),m.group(1)))
        if not os.path.exists(f): print('MISSING FILE',p['key'],f);continue
        hs={slug(re.sub(r'^#+\s*','',l)) for l in open(f) if l.startswith('#')}
        if m.group(2) not in hs: print('BAD ANCHOR',p['key'],f,m.group(2))
