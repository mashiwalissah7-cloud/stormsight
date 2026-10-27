"""Reproduce the NOAA, Census and official FEMA NRI source snapshots."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,zipfile,io
import pandas as pd
import requests
from src.stormsight.data import SOURCE_URL

CENSUS='https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_counties_national.zip'
NRI='https://services.arcgis.com/XG15cJAlne2vxtgt/arcgis/rest/services/National_Risk_Index_Counties/FeatureServer/0/query'
NRI_ITEM='https://www.arcgis.com/sharing/rest/content/items/39485e8035d446a5bff03259508ae355'

def get(url,**params):
    r=requests.get(url,params=params,timeout=60);r.raise_for_status();return r

def main():
    raw=Path('data/raw');out=Path('data/processed');raw.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    ledger=[]
    for url,name in [(SOURCE_URL,SOURCE_URL.rsplit('/',1)[1]),(CENSUS,'counties-2025.zip')]:
        response=get(url);(raw/name).write_bytes(response.content)
        ledger.append({'url':url,'file':f'data/raw/{name}','retrieved_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(response.content).hexdigest()})
    with zipfile.ZipFile(raw/'counties-2025.zip') as z:
        frame=pd.read_csv(z.open('2025_Gaz_counties_national.txt'),sep='|',dtype={'GEOID':str})
    frame=frame.rename(columns={'GEOID':'county_fips','USPS':'state','NAME':'county','INTPTLAT':'latitude','INTPTLONG':'longitude','ALAND':'land_area_m2','AWATER':'water_area_m2'})
    frame[['county_fips','state','county','latitude','longitude','land_area_m2','water_area_m2']].to_csv(out/'counties.csv',index=False)
    metadata=get(NRI_ITEM,f='json').json();(raw/'nri-metadata.json').write_text(json.dumps(metadata,indent=2))
    assert metadata['owner']=='FEMA_NationalRiskIndex'
    count=get(NRI,f='json',where='1=1',returnCountOnly='true').json()['count'];rows=[]
    while len(rows)<count:
        j=get(NRI,f='json',where='1=1',outFields='STCOFIPS,BUILDVALUE,HRCN_RISKS,HRCN_EALT',returnGeometry='false',resultOffset=len(rows),resultRecordCount=1000,orderByFields='STCOFIPS').json()
        page=[x['attributes'] for x in j.get('features',[])]
        if not page:raise ValueError('Incomplete NRI pagination')
        rows.extend(page)
    frame=pd.DataFrame(rows);frame['STCOFIPS']=frame.STCOFIPS.astype(str).str.zfill(5)
    assert len(frame)==count and not frame.STCOFIPS.duplicated().any()
    frame.to_csv(out/'nri_counties.csv',index=False)
    ledger.append({'url':NRI,'metadata_url':NRI_ITEM,'file':'data/processed/nri_counties.csv','retrieved_utc':datetime.now(timezone.utc).isoformat(),'rows':count,'sha256':hashlib.sha256((out/'nri_counties.csv').read_bytes()).hexdigest()})
    (out/'source_manifest.json').write_text(json.dumps(ledger,indent=2))
    print('Verified all source counts and saved provenance.')
if __name__=='__main__':main()
