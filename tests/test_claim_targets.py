import pandas as pd
import pytest
from src.stormsight.data import summarize_claims

def test_missing_components_are_visible_and_adjustments_retained():
    f=pd.DataFrame({'storm_id':['s']*3,'county_fips':['00001','00001','00002'],'id':[1,2,3],
    'amountPaidOnBuildingClaim':[100,-10,None],'amountPaidOnContentsClaim':[None,20,None],
    'amountPaidOnIncreasedCostOfComplianceClaim':[0,0,None]})
    result=summarize_claims(f).set_index('county_fips')
    assert result.loc['00001','paid_loss']==110
    assert result.loc['00001','claim_count']==2
    assert result.loc['00001','missing_payment_count']==1
    assert pd.isna(result.loc['00002','paid_loss'])
    assert result.loc['00002','available_components']==0
