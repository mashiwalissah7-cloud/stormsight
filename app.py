"""StormSight: transparent retrospective flood insurance research."""
import io
import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
import pydeck as pdk
import streamlit as st
from dotenv import load_dotenv
from src.stormsight.data import DATA_PATH, SOURCE_URL, load_tracks
from src.stormsight.features import county_features,CORRIDOR_KM
from src.stormsight.model import predict,TRAIN,CALIBRATION,TEST,MODEL_PATH
from src.stormsight.portfolio import read_portfolio,portfolio_exposure
from src.stormsight.agent import generate_briefing
from src.stormsight.news import search_storm_news

ROOT=Path(__file__).parent
PROCESSED=ROOT/'data/processed'
load_dotenv(ROOT/'.env')
st.set_page_config(page_title='StormSight | Hurricane flood claims',page_icon=str(ROOT/'assets'/'favicon.png'),layout='wide')
st.markdown('''<style>
.block-container{max-width:1400px;padding-top:4rem;padding-bottom:3rem}
h1{font-size:3rem!important;letter-spacing:-.055em!important;font-weight:750!important}
h2{letter-spacing:-.025em!important} [data-testid="stMetric"]{background:#142236;border:1px solid #26384d;border-radius:14px;padding:18px}
[data-testid="stMetricLabel"]{color:#9eb1c7} [data-testid="stMetricValue"]{font-size:1.8rem}
.stTabs [data-baseweb="tab-list"]{gap:28px;border-bottom:1px solid #26384d}
.stTabs [data-baseweb="tab"]{font-size:15px;padding-bottom:14px}
.eyebrow{color:#38d9c5;font-size:12px;letter-spacing:.2em;font-weight:700;margin-bottom:10px}
.subhead{color:#a7b8cc;font-size:17px;max-width:760px;margin-bottom:24px}
.badge{display:inline-block;border:1px solid #30515b;background:#102d34;color:#71e8d8;padding:5px 12px;border-radius:6px;font-size:12px;margin-bottom:12px}
[data-testid="stSidebar"]{border-right:1px solid #26384d}
@media(max-width:800px){[data-testid="stHorizontalBlock"]{flex-wrap:wrap}[data-testid="stColumn"]{min-width:calc(50% - 1rem)!important;flex:1 1 calc(50% - 1rem)!important}h1{font-size:2.3rem!important}}
</style>''',unsafe_allow_html=True)

@st.cache_data
def tracks_cached(stamp): return load_tracks()

@st.cache_data
def csv_cached(path,stamp): return pd.read_csv(path,dtype={'county_fips':str,'STCOFIPS':str})

def read_csv(name):
    p=PROCESSED/name
    return csv_cached(str(p),p.stat().st_mtime_ns)

@st.cache_data
def features_cached(sid,stamp):
    tracks=tracks_cached(stamp)
    counties=read_csv('counties.csv')
    counties=counties[~counties.state.isin(['AK','HI','PR','VI','GU','AS','MP'])]
    return county_features(tracks[tracks.storm_id==sid],counties)

@st.cache_resource
def model_cached(stamp):
    import joblib
    return joblib.load(MODEL_PATH)

def secret(name):
    value=os.getenv(name,'')
    if not value:
        try: value=st.secrets.get(name,'')
        except Exception: pass
    return str(value)

SESSION_LIMIT=3
LIMIT_NOTE='The AI usage limit for this visit or for today has been reached. All evidence tables remain available.'

@st.cache_resource
def usage_tracker():
    import threading
    return {'lock':threading.Lock(),'day':'','counts':{},'briefings':{}}

def daily_limit():
    try: return max(0,int(secret('DAILY_AI_LIMIT') or 100))
    except ValueError: return 100

def reserve(kind):
    """Allow a paid API call only within the per visit and app wide daily limits."""
    used=st.session_state.get(f'{kind}-used',0)
    usage=usage_tracker(); today=pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%d')
    with usage['lock']:
        if usage['day']!=today: usage.update(day=today,counts={},briefings={})
        if used>=SESSION_LIMIT or usage['counts'].get(kind,0)>=daily_limit(): return False
        usage['counts'][kind]=usage['counts'].get(kind,0)+1
    st.session_state[f'{kind}-used']=used+1
    return True

def money(value): return f'${value:,.0f}'

def safe_records(frame): return json.loads(frame.to_json(orient='records',date_format='iso'))

try:
    stamp=DATA_PATH.stat().st_mtime_ns
    tracks=tracks_cached(stamp)
    counties=read_csv('counties.csv')
except (OSError,ValueError) as error:
    st.error('Source data is missing or invalid. Follow the data setup instructions in README.md.')
    st.stop()

with st.sidebar:
    st.markdown('### StormSight')
    st.caption('HURRICANE EVIDENCE LAB')
    st.divider()
    years=sorted(tracks.year.unique(),reverse=True)
    year=st.selectbox('Historical season',years,index=years.index(2024))
    season=tracks[tracks.year==year]
    storms=season[['storm_id','name']].drop_duplicates().sort_values('storm_id')
    labels=dict(zip(storms.storm_id,storms.name)); ids=storms.storm_id.tolist()
    default=next((i for i,sid in enumerate(ids) if labels[sid]=='HELENE'),0)
    sid=st.selectbox('Storm',ids,index=default,format_func=lambda s:f'{labels[s].title()} · {s}')
    st.caption('Historical replay. No live advisories or forecast tracks are loaded.')
    st.divider()
    st.markdown('**Study corridor**')
    st.write(f'{CORRIDOR_KM:g} km from the observed storm center')
    st.caption('County internal points are a screening proxy. This is not a flood footprint.')
    st.divider()
    config={key:secret(key) for key in ['NEBIUS_API_KEY','NEBIUS_BASE_URL','NEBIUS_MODEL']}
    nebius_ready=all(config.values()); tavily_key=secret('TAVILY_API_KEY')
    st.caption('NEBIUS CONNECTION')
    st.write(f"Model: {config['NEBIUS_MODEL']}" if nebius_ready else 'Not connected')
    st.caption('Tavily lookup available' if tavily_key else 'Tavily not connected')
    st.markdown('[NOAA tracks](https://www.nhc.noaa.gov/data/#hurdat) · [FEMA claims](https://www.fema.gov/openfema-data-page/nfip-redacted-claims-v3)')

track=tracks[tracks.storm_id==sid].sort_values('time_utc')
name=labels[sid].title()
f=features_cached(sid,stamp)
model_ready=MODEL_PATH.exists()
results=predict(f,model_cached(MODEL_PATH.stat().st_mtime_ns)) if model_ready and not f.empty else f.copy()
study=pd.DataFrame()
if (PROCESSED/'study_counties.csv').exists():
    study=read_csv('study_counties.csv'); observed=study[study.storm_id==sid][['county_fips','claim_count','paid_loss','target_eligible','missing_payment_count','payment_complete']]
    if not results.empty: results=results.merge(observed,on='county_fips',how='left',validate='one_to_one')
status='Held out test storm' if sid in TEST else 'Calibration storm' if sid in CALIBRATION else 'Training storm' if sid in TRAIN else 'Outside benchmark cohort'

st.markdown('<div class="eyebrow">STORMSIGHT / HURRICANE EVIDENCE LAB</div>',unsafe_allow_html=True)
st.title('Hurricane flood claims, county by county')
st.markdown('<div class="subhead">Pick a past Atlantic hurricane to see its NOAA track, the counties near it, FEMA flood insurance claims, and model estimates with ranges, including where the model misses.</div>',unsafe_allow_html=True)
st.markdown('<span class="badge">Research prototype · Historical replay</span>',unsafe_allow_html=True)
st.caption('Research and education only. Not a commercial catastrophe model, live forecast, insurance quote, or emergency guidance.')

briefing,portfolio,validation=st.tabs(['Storm briefing','Portfolio','Does it work?'])
with portfolio:
    # Recompute before the agent reads totals; removed or invalid uploads leave no stale evidence.
    st.session_state.pop(f'portfolio-{sid}', None)
    st.subheader('Which portfolio values are near this storm?')
    st.write('Upload county totals or use a fictional sample. This calculation sums insured values inside the study corridor. It does not estimate portfolio losses.')
    sample='county_fips,insured_value\n12071,2500000\n12103,1800000\n12057,1200000\n37119,900000\n'
    st.download_button('Download fictional sample CSV',sample,file_name='fictional-portfolio.csv',mime='text/csv')
    use_sample=st.checkbox('Use fictional sample portfolio',value=True)
    uploaded=st.file_uploader('Your portfolio CSV',type=['csv'],disabled=use_sample)
    st.caption('Required columns: county_fips and insured_value. County codes must contain five digits. Values must be finite and nonnegative. Uploads are processed in this app session. Only aggregate totals are shared with Nebius if you explicitly select that option in Storm briefing.')
    if use_sample or uploaded is not None:
        try:
            text=sample if use_sample else uploaded.getvalue().decode('utf-8-sig')
            p=read_portfolio(text,set(counties.county_fips))
            if f.empty:
                st.info('No counties are in this storm corridor; no uploaded value is classified as near the track.')
            else:
                exposure,total=portfolio_exposure(p,f)
                st.session_state[f'portfolio-{sid}']={'total_value':float(p.insured_value.sum()),'corridor_value':total,'fictional_sample':use_sample,'note':'Insured value near track, not an estimated loss.'}
                x,y,z=st.columns(3);x.metric('Total uploaded value',money(p.insured_value.sum()));y.metric('Value in corridor',money(total));z.metric('Counties in corridor',int(exposure.in_corridor.sum()))
                st.dataframe(exposure[['county_fips','county','state','insured_value','min_distance_km','in_corridor']],hide_index=True,width='stretch')
                st.download_button('Download exposure calculation',exposure.to_csv(index=False),file_name=f'{sid}-portfolio-corridor.csv',mime='text/csv')
                st.warning('Outside the corridor does not mean safe. Flooding can occur far from a track. County aggregate claims cannot be scaled into portfolio losses without a defensible insured exposure denominator.')
        except (ValueError,UnicodeError) as error: st.error(str(error))


with briefing:
    st.subheader(f'{name} · {year}')
    st.caption(f'{sid}  |  {status}  |  {track.time_utc.min():%d %b %Y} to {track.time_utc.max():%d %b %Y} UTC')
    a,b,c,d=st.columns(4)
    wind=track.wind_knots.max(); pressure=track.pressure_mb.min()
    a.metric('Peak observed wind','Unavailable' if pd.isna(wind) else f'{wind:g} kt')
    b.metric('Minimum observed pressure','Unavailable' if pd.isna(pressure) else f'{pressure:g} mb')
    c.metric('Recorded positions',f'{len(track):,}')
    d.metric('Counties in study corridor',f'{len(f):,}')
    points=track[['longitude','latitude']].values.tolist()
    layers=[pdk.Layer('PathLayer',data=[{'path':points}],get_path='path',get_color=[56,217,197],width_min_pixels=3),
            pdk.Layer('ScatterplotLayer',data=track[['longitude','latitude']],get_position='[longitude, latitude]',get_fill_color=[255,190,100],radius_min_pixels=3)]
    if not results.empty:
        mapdata=results.copy(); mapdata['radius']=np.sqrt(mapdata.get('paid_loss_predicted',pd.Series(0,index=mapdata.index)).clip(lower=0))/3+2500
        layers.insert(0,pdk.Layer('ScatterplotLayer',data=mapdata[['longitude','latitude','radius']],get_position='[longitude, latitude]',get_radius='radius',get_fill_color=[85,137,190,90],radius_min_pixels=3,radius_max_pixels=22))
    st.pydeck_chart(pdk.Deck(layers=layers,initial_view_state=pdk.ViewState(latitude=float(track.latitude.mean()),longitude=float(track.longitude.mean()),zoom=3.5),
                 map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'),height=430)
    st.caption('Teal line: observed track. Gold dots: recorded positions. Blue dots: county internal points; size reflects model estimates when available. These are not flood boundaries. Map: CARTO / OpenStreetMap.')
    if results.empty:
        st.info('No contiguous US county internal points fall within this study corridor.')
    elif model_ready:
        st.subheader('County estimates with an audit trail')
        st.warning('Prototype limitation: the held out evaluation substantially underestimates several large storm totals. These estimates are not ready for operational or financial decisions.')
        st.caption('Retrospective estimates of available reported NFIP payments matched by geography and dates. Missing payment fields are not inferred. Not all hurricane losses. Current NRI scores are excluded from model predictors.')
        if sid in TRAIN: st.warning('This storm was used for training. Its fitted estimates are not evidence of accuracy. Open Does it work? for unseen storms.')
        if sid not in TRAIN+CALIBRATION+TEST: st.warning('This storm is outside the evaluation cohort. Treat these estimates as unvalidated extrapolations.')
        ranked=results.sort_values('paid_loss_predicted',ascending=False)
        cols=['county_fips','county','state','min_distance_km','paid_loss_predicted','paid_loss_lower','paid_loss_upper','claim_count_predicted']
        names={'county_fips':'County FIPS','county':'County','state':'State','min_distance_km':'Distance km','paid_loss_predicted':'Estimated NFIP payments USD','paid_loss_lower':'Empirical lower USD','paid_loss_upper':'Empirical upper USD','claim_count_predicted':'Estimated claim records'}
        st.dataframe(ranked[cols].rename(columns=names),hide_index=True,width='stretch',column_config={names[k]:st.column_config.NumberColumn(format='%.0f') for k in cols[3:]})
        st.caption('Ranges use calibration residuals. They are not guaranteed confidence bounds, and do not validate an individual property estimate.')
        st.download_button('Download county evidence',results.to_csv(index=False),file_name=f'{sid}-county-evidence.csv',mime='text/csv')
        if 'target_eligible' in results and results.target_eligible.notna().any():
            with st.expander('Observed claims used for comparison'):
                st.write('These payments are matched by county, distance, and dates. That rule does not prove the storm caused every payment. Missing payment components are omitted from the reported sum and counted separately. The sum may be incomplete. Ambiguous targets, negative totals, and entirely missing payment targets are excluded from evaluation.')
                st.dataframe(results[['county_fips','county','state','claim_count','paid_loss','missing_payment_count','payment_complete','target_eligible']],hide_index=True,width='stretch')
    else:
        st.info('Claims processing and model validation are in progress. No loss estimate is displayed until the benchmark is ready.')
        if not f.empty: st.dataframe(f[['county_fips','county','state','min_distance_km','max_wind_knots','hours_near']].sort_values('min_distance_km'),hide_index=True)
    with st.expander('NOAA observations and provenance'):
        st.dataframe(track,hide_index=True,width='stretch')
        st.markdown(f'[Exact NOAA source file]({SOURCE_URL})')
        st.download_button('Download storm observations',track.to_csv(index=False),file_name=f'{sid}-observations.csv',mime='text/csv')
    if (PROCESSED/'nri_counties.csv').exists() and not f.empty:
        with st.expander('FEMA National Risk Index: context, not a storm forecast'):
            nri=read_csv('nri_counties.csv').rename(columns={'STCOFIPS':'county_fips'})
            context=f[['county_fips','county','state']].merge(nri,on='county_fips',how='left')
            for k in ['BUILDVALUE','HRCN_RISKS','HRCN_EALT']: context[k]=context[k].where(context[k]>=0)
            st.caption('FEMA December 2025 release. BUILDVALUE is county building stock, not NFIP insured exposure. HRCN_EALT is expected annual hurricane loss, not this storm’s loss.')
            st.dataframe(context,hide_index=True,width='stretch')
            st.markdown('[FEMA NRI source and metadata](https://www.arcgis.com/home/item.html?id=39485e8035d446a5bff03259508ae355)')
    st.subheader('Evidence briefing')
    st.caption('The default summary below is produced by Python. It is not an AI response.')
    st.write(f'{name} has {len(track):,} recorded positions. {len(f):,} county internal points fall within the {CORRIDOR_KM:g} km study corridor.')
    if model_ready and not results.empty:
        top=results.sort_values('paid_loss_predicted',ascending=False).head(5)
        st.write('Largest county model estimates in this corridor:')
        st.dataframe(top[['county','state','paid_loss_predicted','paid_loss_lower','paid_loss_upper']],hide_index=True,width='stretch')
    st.write('Key uncertainties: rainfall and surge are not modeled; NFIP participation varies; county points simplify geography; date matching can include unrelated flooding.')
    st.write('What to watch: compare county estimates with the held out results before interpreting any totals. For current hazards, consult official NHC and local emergency guidance.')
    news_key=f'news-{sid}'
    if st.button('Look up official sources with Tavily',disabled=not bool(tavily_key)):
        if not reserve('lookup'): st.warning(LIMIT_NOTE)
        else:
            try:
                with st.spinner('Looking up public official sources…'): st.session_state[news_key]=search_storm_news(name,year,tavily_key)
            except Exception: st.error('Source lookup failed. Check your Tavily key and service availability. No results were invented.')
    for item in st.session_state.get(news_key,[]): st.link_button(item['title'],item['url'])
    st.caption('Optional AI sends selected public storm and county evidence to your configured Nebius endpoint.')
    include_portfolio=st.checkbox('Include portfolio totals in the Nebius briefing',value=False,help='If selected, only aggregate uploaded value and corridor value from the Portfolio tab will be sent to Nebius. Individual rows are not sent.')
    clicked=st.button('Generate Nemotron briefing',type='primary',disabled=not(nebius_ready and model_ready and not results.empty))
    shared=None if include_portfolio else usage_tracker()['briefings'].get(sid)
    if clicked and shared: st.session_state[f'ai-{sid}']={**shared,'shared':True}
    elif clicked and not reserve('briefing'): st.warning(LIMIT_NOTE)
    elif clicked:
        tools={
            'list_storms':lambda:safe_records(storms),
            'get_storm_track':lambda:{'storm':name,'year':int(year),'storm_id':sid,'peak_wind_knots':float(wind),'positions':len(track),'source':SOURCE_URL},
            'predict_county_losses':lambda:{'status':status,'counties':safe_records(results.sort_values('paid_loss_predicted',ascending=False).head(10)[['county_fips','county','state','paid_loss_predicted','paid_loss_lower','paid_loss_upper']]),'warning':'Retrospective sums of available reported NFIP payment components; missing fields are not inferred. Not complete hurricane damage; intervals are empirical.'},
        }
        if include_portfolio and f'portfolio-{sid}' in st.session_state:
            tools['portfolio_exposure']=lambda:st.session_state[f'portfolio-{sid}']
        if tavily_key: tools['search_storm_news']=lambda:search_storm_news(name,year,tavily_key)
        try:
            with st.spinner('Running evidence tools and checking the briefing…'): briefing=generate_briefing(config,tools)
            st.session_state[f'ai-{sid}']=briefing
            # Portfolio free briefings use only public evidence, so one result per storm is reused to limit API use.
            if not include_portfolio: usage_tracker()['briefings'][sid]=briefing
        except ValueError as error: st.error(str(error))
    if f'ai-{sid}' in st.session_state:
        output=st.session_state[f'ai-{sid}']; st.success('Nemotron response received and numerical prose checks passed.')
        if output.get('shared'): st.caption('This briefing was generated earlier for this storm and is reused to limit API use.')
        for field,title in [('summary','Summary'),('uncertainties','Key uncertainties'),('watch_next','What to watch')]:
            st.markdown(f'**{title}**');st.write(output['narrative'][field])
        with st.expander('Agent tool trace'): st.json({'model':output['model'],'tools':output['tools'],'evidence':output['evidence']})


with validation:
    st.subheader('How accurate is the model?')
    st.write('A historical storm map is not proof of prediction accuracy. This benchmark compares a mean baseline with gradient boosting on storms excluded from training.')
    report_path=PROCESSED/'validation.json'
    if report_path.exists():
        report=json.loads(report_path.read_text()); test=read_csv('test_predictions.csv'); totals=read_csv('test_storm_totals.csv')
        a,b,c=st.columns(3);a.metric('Training storms',len(report['train_storms']));b.metric('Calibration storms',len(report['calibration_storms']));c.metric('Held out storms',len(report['test_storms']))
        st.warning('The target is the sum of available reported payment components. Missing fields can make observed sums incomplete. These results do not validate ultimate hurricane losses.')
        st.caption('Model choice uses calibration error. Final test storms are not used to fit models, choose the winner, or set interval widths.')
        st.dataframe(pd.DataFrame(report['metrics']),hide_index=True,width='stretch')
        st.write('MAE means average absolute error in the target’s original units: dollars or claim records. RMSLE measures error after a logarithmic transform. Lower is better.')
        st.write('Selected models:',report['chosen_models'])
        st.write('Measured test interval coverage:',{k:f'{v:.1%}' for k,v in report['coverage'].items()})
        st.caption('Intervals target an empirical calibration residual percentile. Storm clustering and dataset shift prevent a guaranteed coverage claim.')
        target=st.selectbox('Compare observed and estimated',['paid_loss','claim_count'],format_func=lambda t:'NFIP payments' if t=='paid_loss' else 'Matched claim records')
        chart=test[[target,f'{target}_predicted']].rename(columns={target:'Observed',f'{target}_predicted':'Estimated'})
        st.scatter_chart(chart,x='Observed',y='Estimated',height=320)
        st.caption('Each point is an eligible county and held out storm. Agreement would place points on the diagonal.')
        st.markdown('**Storm totals over eligible county targets**');st.dataframe(totals,hide_index=True,width='stretch')
        errors=test.assign(absolute_error=(test[target]-test[f'{target}_predicted']).abs()).sort_values('absolute_error',ascending=False)
        st.markdown('**Largest misses**');st.dataframe(errors[['name','county','state',target,f'{target}_predicted','absolute_error']].head(10),hide_index=True,width='stretch')
        st.download_button('Download held out predictions',test.to_csv(index=False),file_name='held-out-predictions.csv',mime='text/csv')
        with st.expander('Method, split assignments, and limitations'):
            st.json({k:report[k] for k in ['train_storms','calibration_storms','test_storms','features','interval_method']})
            for limitation in report['limitations']: st.write('• '+limitation)
            if (PROCESSED/'claims_audit.json').exists():st.json(json.loads((PROCESSED/'claims_audit.json').read_text()))
    else: st.info('The benchmark is not ready yet. No accuracy metrics are claimed.')
    st.divider()
    st.markdown('**Source ledger**')
    st.markdown('[NOAA HURDAT2](https://www.nhc.noaa.gov/data/#hurdat) · [OpenFEMA NFIP v3](https://www.fema.gov/openfema-data-page/nfip-redacted-claims-v3) · [Census Gazetteer](https://www.census.gov/geographies/reference-files/2025/geo/gazetter-file.html) · [FEMA NRI](https://www.arcgis.com/home/item.html?id=39485e8035d446a5bff03259508ae355)')
    st.caption('NOAA: 1851 through 2025 release. Census: 2025 county internal points. NRI: December 2025. Claims: API retrieval timestamps are recorded in the source manifest. Research snapshot downloaded October 27, 2026.')

st.divider()
legal=st.columns([1,1,4])
legal[0].page_link('pages/privacy.py',label='Privacy policy')
legal[1].page_link('pages/terms.py',label='Terms and conditions')
legal[2].caption('Open source under the MIT license. Data from NOAA, FEMA, and the U.S. Census Bureau.')
