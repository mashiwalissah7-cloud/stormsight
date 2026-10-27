"""Fetch bounded FEMA claim windows and create a reproducible study table.
Run from repository root: .venv/bin/python -m scripts.build_dataset
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
import requests
import pandas as pd
from src.stormsight.data import load_tracks, summarize_claims
from src.stormsight.features import county_features, match_claims, claim_candidates

API = 'https://www.fema.gov/api/open/v3/NfipClaims'
STUDY = ['AL092011','AL092012','AL182012','AL142016','AL092017','AL112017',
         'AL062018','AL142018','AL052019','AL132020','AL192020','AL092021',
         'AL092022','AL102023','AL092024','AL142024']
FIELDS = 'id,countyCode,dateOfLoss,amountPaidOnBuildingClaim,amountPaidOnContentsClaim,amountPaidOnIncreasedCostOfComplianceClaim,floodEvent'
RAW = Path('data/raw')
OUT = Path('data/processed')


def request(params):
    for attempt in range(4):
        try:
            r=requests.get(API,params=params,timeout=60)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException,ValueError):
            if attempt==3: raise
            time.sleep(2**attempt)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    Path('work').mkdir(exist_ok=True)
    tracks=load_tracks()
    counties=pd.read_csv(OUT/'counties.csv',dtype={'county_fips':str})
    # Restrict the study to contiguous states; exclude Alaska, Hawaii and territories.
    counties=counties[~counties.state.isin(['AK','HI','PR','VI','GU','AS','MP'])]
    all_windows=[]
    # Include every nearby storm in these years when checking ambiguous claims.
    for sid,t in tracks[(tracks.year>=2011)&(tracks.year<=2024)].groupby('storm_id'):
        f=county_features(t,counties)
        if not f.empty:
            f['storm_id']=sid; f['name']=t.name.iloc[0]; f['year']=int(t.year.iloc[0]); all_windows.append(f)
    windows=pd.concat(all_windows,ignore_index=True)
    windows.to_csv(OUT/'all_county_windows.csv',index=False)
    selected=windows[windows.storm_id.isin(STUDY)].copy()
    manifests=[]; chunks=[]
    def fetch_storm(sid):
        w=selected[selected.storm_id==sid]
        if w.empty: raise ValueError(f'No counties for study storm {sid}')
        start=pd.to_datetime(w.first_near,utc=True).min().floor('D')
        end=pd.to_datetime(w.last_near,utc=True).max().floor('D')+pd.Timedelta(days=3)
        filt=f"dateOfLoss ge '{start:%Y-%m-%d}T00:00:00.000Z' and dateOfLoss le '{end:%Y-%m-%d}T00:00:00.000Z'"
        path=RAW/f'claims-{sid}.json'
        if path.exists():
            saved=json.loads(path.read_text())
        else:
            progress=Path('work')/f'download-{sid}.json'
            if progress.exists():
                partial=json.loads(progress.read_text()); data=partial['rows']; expected=partial['expected']
            else: data=[]; expected=None
            while expected is None or len(data)<expected:
                cursor=max((r['id'] for r in data),default=None)
                page_filter=filt+(f" and id gt {cursor}" if cursor is not None else '')
                params={'$filter':page_filter,'$select':FIELDS,'$top':2000,'$orderby':'id'}
                if expected is None: params['$inlinecount']='allpages'
                payload=request(params)
                page=payload['NfipClaims']
                if expected is None: expected=payload['metadata']['count']
                if not page and len(data)<expected: raise ValueError('Incomplete FEMA pagination')
                data.extend(page)
                progress.write_text(json.dumps({'rows':data,'expected':expected}))
                print(sid, len(data), '/', expected,flush=True)
            if len(data)!=expected or len({r['id'] for r in data})!=expected:
                raise ValueError('FEMA returned an incomplete or duplicate page set')
            saved={'source':API,'filter':filt,'select':FIELDS,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'expected_count':expected,'rows':data}
            path.write_text(json.dumps(saved))
        if len(saved['rows'])!=saved['expected_count']: raise ValueError('Incomplete cache')
        return pd.DataFrame(saved['rows']), {k:v for k,v in saved.items() if k!='rows'}|{'storm_id':sid,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for frame,manifest in pool.map(fetch_storm,STUDY):
            chunks.append(frame); manifests.append(manifest)
    claims=pd.concat(chunks,ignore_index=True).drop_duplicates('id')
    claims['county_fips']=claims.countyCode.astype('string').str.zfill(5)
    pay=['amountPaidOnBuildingClaim','amountPaidOnContentsClaim','amountPaidOnIncreasedCostOfComplianceClaim']
    claims[pay]=claims[pay].apply(pd.to_numeric,errors='coerce')
    invalid_payment=claims[pay].isna().any(axis=1)|(claims[pay]<0).any(axis=1)
    # Target is the sum of available reported payment components, not full ultimate loss.
    # Missing fields are counted explicitly; signed reported adjustments are retained.
    matched,audit=match_claims(claims,windows)
    sums=summarize_claims(matched)
    result=selected.merge(sums,on=['storm_id','county_fips'],how='left',validate='one_to_one')
    numeric=['claim_count','paid_loss','invalid_payment_count','missing_payment_count','available_components']
    result[numeric]=result[numeric].fillna(0)
    # Exclude every county window containing an ambiguous claim from evaluation targets.
    # Unmatched claims remain outside the spatial/time study definition.
    cand=claim_candidates(claims,windows)
    n=cand.groupby('id').storm_id.nunique(); ambiguous=cand[cand.id.isin(n[n>1].index)][['storm_id','county_fips']].drop_duplicates(); ambiguous['ambiguous_target']=True
    result=result.merge(ambiguous,on=['storm_id','county_fips'],how='left')
    result['ambiguous_target']=result.ambiguous_target.fillna(False).astype(bool)
    result['target_eligible']=~result.ambiguous_target & (result.paid_loss>=0) & ((result.claim_count==0)|(result.available_components>0))
    result['payment_complete']=(result.missing_payment_count==0)
    result.loc[(result.claim_count>0)&(result.available_components==0),'paid_loss']=float('nan')
    result.to_csv(OUT/'study_counties.csv',index=False)
    audit.update(unique_downloaded_claims=len(claims),missing_or_negative_payment_records=int(invalid_payment.sum()),study_county_rows=len(result),eligible_rows=int(result.target_eligible.sum()),study_storms=STUDY)
    (OUT/'claims_audit.json').write_text(json.dumps(audit,indent=2))
    (OUT/'claims_manifest.json').write_text(json.dumps(manifests,indent=2))
    print('DONE',audit,flush=True)

if __name__=='__main__': main()
