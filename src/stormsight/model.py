"""Small retrospective benchmark with disjoint train, calibration, and test storms."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_log_error

FEATURES=['min_distance_km','max_wind_knots','hours_near','log_land_area','water_share','latitude','longitude']
TARGETS=['claim_count','paid_loss']
TRAIN=['AL092011','AL092012','AL182012','AL142016','AL092017','AL112017','AL062018','AL142018']
CALIBRATION=['AL052019','AL132020','AL192020']
TEST=['AL092021','AL092022','AL102023','AL092024','AL142024']
MODEL_PATH=Path(__file__).resolve().parents[2]/'data/processed/model.joblib'


def design(frame):
    f=frame.copy()
    f['log_land_area']=np.log1p(f.land_area_m2)
    f['water_share']=f.water_area_m2/(f.land_area_m2+f.water_area_m2)
    values=f[FEATURES]
    if not np.isfinite(values.to_numpy()).all():
        raise ValueError('Model inputs must be finite.')
    return values


def fit_benchmark(table, directory=MODEL_PATH.parent):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    assert not (set(TRAIN)&set(CALIBRATION) or set(TRAIN)&set(TEST) or set(CALIBRATION)&set(TEST))
    usable=table[table.target_eligible].copy()
    train=usable[usable.storm_id.isin(TRAIN)]; cal=usable[usable.storm_id.isin(CALIBRATION)]; test=usable[usable.storm_id.isin(TEST)]
    if any(x.empty for x in [train,cal,test]): raise ValueError('Missing required dataset split')
    metrics=[]; models={}; intervals={}; choices={}
    predictions=test.copy()
    for target in TARGETS:
        candidates={'mean_baseline':DummyRegressor(strategy='mean'),
                    'gradient_boosting':HistGradientBoostingRegressor(loss='poisson',max_iter=150,max_depth=3,min_samples_leaf=25,l2_regularization=10,random_state=42)}
        scores={}
        for name,model in candidates.items():
            model.fit(design(train),train[target])
            cp=np.maximum(0,model.predict(design(cal)))
            tp=np.maximum(0,model.predict(design(test)))
            scores[name]=mean_absolute_error(cal[target],cp)
            metrics.append({'target':target,'model':name,'calibration_mae':float(scores[name]),
                            'test_mae':float(mean_absolute_error(test[target],tp)),
                            'test_rmsle':float(np.sqrt(mean_squared_log_error(test[target],tp)))})
            predictions[f'{target}_{name}']=tp
        # Selection uses calibration storms, never final test performance.
        chosen=min(scores,key=scores.get); m=candidates[chosen]
        residual=np.abs(cal[target].to_numpy()-m.predict(design(cal)))
        width=float(np.quantile(residual,.9,method='higher'))
        models[target]=m; intervals[target]=width; choices[target]=chosen
        pp=np.maximum(0,m.predict(design(test)))
        predictions[f'{target}_predicted']=pp
        predictions[f'{target}_lower']=np.maximum(0,pp-width)
        predictions[f'{target}_upper']=pp+width
    package={'models':models,'intervals':intervals,'choices':choices,'features':FEATURES,
             'train_storms':TRAIN,'calibration_storms':CALIBRATION,'test_storms':TEST}
    joblib.dump(package,directory/'model.joblib')
    predictions.to_csv(directory/'test_predictions.csv',index=False)
    coverages={target:float(((predictions[target]>=predictions[f'{target}_lower'])&(predictions[target]<=predictions[f'{target}_upper'])).mean()) for target in TARGETS}
    totals=predictions.groupby(['storm_id','name'])[['claim_count','paid_loss','claim_count_predicted','paid_loss_predicted']].sum().reset_index()
    totals.to_csv(directory/'test_storm_totals.csv',index=False)
    summary={'metrics':metrics,'chosen_models':choices,'coverage':coverages,'interval_method':'90th percentile absolute calibration residual, symmetric and clipped at zero; empirical, not guaranteed',
             'train_rows':len(train),'calibration_rows':len(cal),'test_rows':len(test),'train_storms':TRAIN,'calibration_storms':CALIBRATION,'test_storms':TEST,
             'features':FEATURES,'limitations':['Targets are available reported NFIP payment sums, not ultimate or complete losses. Missing components are counted separately, not inferred.', 'Signed payment adjustments are retained. Negative county totals and entirely missing payment targets are excluded.', 'Selected storm cohort, not a representative sample of all storms.','Geographic proximity and dates do not prove storm causation.','County internal points miss large county footprints and remote rainfall flooding.','No historical policy exposure denominator; insurance take up and coverage changes are unmodeled.','Claims include zero payment records; counts are matched records, not unique properties.','Current county geography is used retrospectively. NRI is context only, excluded from predictors.','Intervals are empirical and county errors are correlated within storms.','Full observed tracks are used, so this is a retrospective benchmark, not a forecast validation.']}
    (directory/'validation.json').write_text(json.dumps(summary,indent=2))
    return summary


def predict(frame, package=None):
    if package is None: package=joblib.load(MODEL_PATH)
    result=frame.copy()
    for target in TARGETS:
        p=np.maximum(0,package['models'][target].predict(design(frame)))
        result[f'{target}_predicted']=p
        result[f'{target}_lower']=np.maximum(0,p-package['intervals'][target])
        result[f'{target}_upper']=p+package['intervals'][target]
    return result
