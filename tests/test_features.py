import pandas as pd
import pytest
from src.stormsight.features import haversine,county_features,hourly_track,match_claims

def test_haversine_known_distances():
    assert haversine(0,0,0,0)==0
    assert haversine(0,0,0,1)==pytest.approx(111.195,abs=.01)
    assert haversine(0,179,0,-179)==pytest.approx(222.39,abs=.02)

def test_duration_does_not_count_special_records_twice():
    t=pd.DataFrame({'time_utc':pd.to_datetime(['2020-01-01T00:00Z','2020-01-01T01:30Z','2020-01-01T06:00Z']), 'latitude':[0,0,0], 'longitude':[0,0,0], 'wind_knots':[20,20,20]})
    c=pd.DataFrame({'county_fips':['00001'],'latitude':[0], 'longitude':[0]})
    assert county_features(t,c).hours_near.iloc[0]==pytest.approx(6)

def test_dateline_interpolation():
    t=pd.DataFrame({'time_utc':pd.to_datetime(['2020-01-01T00:00Z','2020-01-01T02:00Z']), 'latitude':[0,0], 'longitude':[179,-179], 'wind_knots':[20,20]})
    assert hourly_track(t).longitude.iloc[1]==pytest.approx(180)

def test_matching_excludes_ambiguous_and_far_dates():
    claims=pd.DataFrame({'id':[1,2,3], 'county_fips':['00001']*3, 'dateOfLoss':['2020-01-01','2020-01-04','2020-02-01']})
    w=pd.DataFrame({'storm_id':['a','b'],'county_fips':['00001']*2,'first_near':['2020-01-01','2020-01-04'],'last_near':['2020-01-01','2020-01-04']})
    matched,audit=match_claims(claims,w)
    assert matched.id.tolist()==[1]
    assert audit=={'matched':1,'unmatched':1,'ambiguous':1}
