import pandas as pd
import pytest
from src.stormsight.portfolio import read_portfolio,portfolio_exposure

def test_leading_zero_and_duplicate_aggregation():
    f=read_portfolio('county_fips,insured_value\n01001,100\n01001,200\n',{'01001'})
    assert f.county_fips.tolist()==['01001']
    assert f.insured_value.sum()==300

@pytest.mark.parametrize('row',['01001,-1','01001,inf','01001,NaN','1001,2','99999,2'])
def test_reject_invalid_portfolio(row):
    with pytest.raises(ValueError): read_portfolio('county_fips,insured_value\n'+row,{'01001'})

def test_corridor_value_is_not_loss():
    p=pd.DataFrame({'county_fips':['01001','01003'],'insured_value':[100,200]})
    c=pd.DataFrame({'county_fips':['01001'],'min_distance_km':[20]})
    result,value=portfolio_exposure(p,c)
    assert value==100
    assert result.in_corridor.tolist()==[True,False]
