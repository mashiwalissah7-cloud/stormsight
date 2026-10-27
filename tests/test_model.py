import numpy as np
import pandas as pd
import pytest
from src.stormsight.model import TRAIN,CALIBRATION,TEST,fit_benchmark,predict
import joblib


def synthetic_table():
    rows=[]
    for j,sid in enumerate(TRAIN+CALIBRATION+TEST):
        for i in range(12):
            rows.append({'storm_id':sid,'name':'SYNTHETIC TEST ONLY','county_fips':f'{i:05}',
                         'min_distance_km':i*10,'max_wind_knots':50+j,'hours_near':10+i,
                         'land_area_m2':1000+i,'water_area_m2':20,'latitude':30+i/10,'longitude':-80,
                         'claim_count':i+1,'paid_loss':(i+1)*1000,'target_eligible':True})
    return pd.DataFrame(rows)


def test_final_test_targets_cannot_change_fitted_model(tmp_path):
    a=synthetic_table();b=a.copy();b.loc[b.storm_id.isin(TEST),'paid_loss']*=100
    ra=fit_benchmark(a,tmp_path/'a');rb=fit_benchmark(b,tmp_path/'b')
    ma=joblib.load(tmp_path/'a/model.joblib');mb=joblib.load(tmp_path/'b/model.joblib')
    assert ra['chosen_models']==rb['chosen_models']
    assert ma['intervals']==mb['intervals']
    np.testing.assert_allclose(predict(a,ma).paid_loss_predicted,predict(a,mb).paid_loss_predicted)
    assert not set(TRAIN)&set(TEST)
    assert not set(CALIBRATION)&set(TEST)
