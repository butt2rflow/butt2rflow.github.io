"""
V-shape study (one-off, 2026-10-18): do markets that were heavily hedged
before a drawdown (SKEW 20d avg, 1y percentile at the peak) fall less or
rebound faster? Episodes = SPX closes >=3% / >=5% below its running high,
until a new high. Small samples, recovery times censored, definition not
pre-registered -- see brief_playbook.md (hypothesis, not a finding).

Run from project root:  PYTHONUTF8=1 python scripts/study_vshape.py
"""
import sys; sys.path.insert(0,'scripts')
import update_dashboard as ud, pandas as pd, numpy as np
spx=ud._fetch_cboe_index('SPX'); sk=ud._fetch_cboe_index('SKEW'); vix=ud._fetch_cboe_index('VIX')
d=pd.DataFrame({'spx':spx,'sk':sk,'vix':vix}).dropna().loc['1991':]
d['skpct']=d.sk.rolling(252).rank(pct=True)
d['sk20']=d.sk.rolling(20).mean()
d['skpct20']=d.sk20.rolling(252).rank(pct=True)
px=d.spx.values; idx=d.index
def episodes(th):
    eps=[]; i=0; n=len(d); hi=px[0]; hi_i=0
    while i<n:
        if px[i]>=hi: hi, hi_i = px[i], i
        elif px[i]/hi-1<=-th:
            cross=i; j=i; low=px[i]; low_i=i
            while j<n and px[j]<hi:
                if px[j]<low: low, low_i = px[j], j
                j+=1
            rec = j if j<n else None
            # hedging measured BEFORE the decline: 20d avg SKEW pct at the peak
            eps.append(dict(peak=idx[hi_i], cross=idx[cross], skp=d.skpct20.iloc[hi_i], vix_pk=d.vix.iloc[hi_i],
                depth=(low/hi-1)*100, more=(low/px[cross]-1)*100,
                rec_days=(rec-cross) if rec else np.nan,
                fwd20=(px[min(cross+20,n-1)]/px[cross]-1)*100,
                v=bool(rec is not None and rec-cross<=40)))
            hi=px[j] if j<n else hi; hi_i=j if j<n else hi_i; i=j; continue
        i+=1
    return pd.DataFrame(eps).dropna(subset=['skp'])
for th in (0.03,0.05):
    e=episodes(th)
    e['grp']=pd.cut(e.skp,[0,0.5,0.8,1.0],labels=['보험 적음(<50%)','중간','보험 많음(≥80%)'],include_lowest=True)
    print(f'\n=== SPX −{th:.0%} 하락 구간 (1991~), 보험=고점 직전 SKEW 20일평균의 1년 백분위 ===')
    g=e.groupby('grp',observed=True).agg(n=('depth','size'),최종깊이_중앙=('depth','median'),
        추가하락_중앙=('more','median'),깊은침체_10pct=('depth',lambda x:(x<=-10).mean()),
        회복일수_중앙=('rec_days','median'),V자_40일내회복=('v','mean'),진입후20일수익_중앙=('fwd20','median'))
    print(g.round(2).to_string())
    if th==0.05:
        print(e.sort_values('cross').tail(12)[['peak','cross','skp','depth','rec_days','fwd20']].round(2).to_string())
