"""Optional public-source news lookup. No portfolio data is sent to this service."""
from urllib.parse import urlparse
from tavily import TavilyClient


def search_storm_news(storm_name, year, api_key):
    if not api_key: raise ValueError('A Tavily API key is required for live source lookup.')
    query=f'{storm_name} {int(year)} hurricane NOAA NHC FEMA storm report'
    response=TavilyClient(api_key=api_key).search(query=query,max_results=5,include_domains=['nhc.noaa.gov','fema.gov','weather.gov'],search_depth='basic')
    rows=[]
    for r in response.get('results',[]):
        u=urlparse(r.get('url','')); host=u.hostname or ''
        if u.scheme=='https' and any(host==d or host.endswith('.'+d) for d in ['nhc.noaa.gov','fema.gov','weather.gov']):
            rows.append({'title':r.get('title','Source'),'url':r['url'],'content':r.get('content','')[:1600]})
    return rows
