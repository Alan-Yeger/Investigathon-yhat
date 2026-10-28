import segno,sys
url='https://github.com/Alan-Yeger/Investigathon-yhat'
def make(eye, B, size, rx, path, px=96, frx=1.4):
    q=segno.make(url, error='m'); m=[[bool(v) for v in r] for r in q.matrix]; n=len(m); S=n+2*B; ink='#143A33'
    fin=lambda r,c:any(r0<=r<r0+7 and c0<=c<c0+7 for r0,c0 in [(0,0),(0,n-7),(n-7,0)])
    o=(1-size)/2
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" viewBox="0 0 {S} {S}">',f'<rect width="{S}" height="{S}" rx="{B*0.8}" fill="#FFFFFF"/>']
    for r in range(n):
        for c in range(n):
            if m[r][c] and not fin(r,c): p.append(f'<rect x="{c+B+o:.2f}" y="{r+B+o:.2f}" width="{size}" height="{size}" rx="{rx}" fill="{ink}"/>')
    for r0,c0 in [(0,0),(0,n-7),(n-7,0)]:
        x,y=c0+B,r0+B
        p.append(f'<rect x="{x+0.5}" y="{y+0.5}" width="6" height="6" rx="{frx}" fill="none" stroke="{ink}" stroke-width="1"/>')
        p.append(f'<rect x="{x+2}" y="{y+2}" width="3" height="3" rx="{frx*0.55}" fill="{eye}"/>')
    p.append('</svg>'); open(path,'w',encoding='utf-8').write("\n".join(p))
v=sys.argv[1]
cfg={'A':('#EB6834',4,0.9,0.25),'B':('#143A33',4,0.9,0.25),'C':('#EB6834',4,1.0,0.3),'D':('#143A33',2,0.88,0.32),'E':('#143A33',4,1.0,0),'F':('#EB6834',4,1.0,0.15),'G':('#EB6834',4,0.92,0.2),'H':('#143A33',4,1.02,0,0),'I':('#143A33',4,1.02,0,1.0),'J':('#143A33',4,0.9,0.25,0),'K':('#EB6834',4,0.9,0.25,1.0)}[v]
make(*cfg[:4], sys.argv[2], px=int(sys.argv[3]), frx=(cfg[4] if len(cfg)>4 else 1.4))
