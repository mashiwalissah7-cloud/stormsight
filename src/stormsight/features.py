"""Auditable geographic features. Distances are to interpolated storm centers."""
import numpy as np
import pandas as pd

EARTH_RADIUS_KM = 6371.0088
CORRIDOR_KM = 250.0


def haversine(lat1, lon1, lat2, lon2):
    """Great circle distance in kilometers; supports NumPy arrays."""
    a, b, c, d = map(np.radians, (lat1, lon1, lat2, lon2))
    h = np.sin((c-a)/2)**2 + np.cos(a)*np.cos(c)*np.sin((d-b)/2)**2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(h, 0, 1)))


def hourly_track(track):
    """Interpolate at hourly intervals; retain observations at special times."""
    t = track.sort_values('time_utc').set_index('time_utc')
    index = t.index.union(pd.date_range(t.index.min(), t.index.max(), freq='h'))
    numeric = t[['latitude','longitude','wind_knots']].copy()
    # Unwrap longitude before inserting missing hourly rows.
    numeric['longitude'] = np.degrees(np.unwrap(np.radians(numeric.longitude)))
    numeric = numeric.reindex(index)
    return numeric.interpolate(method='time', limit_area='inside').dropna().reset_index(names='time_utc')


def county_features(track, counties, radius=CORRIDOR_KM):
    """County representative points are a proxy, not flood or wind footprints."""
    t = hourly_track(track)
    if t.empty:
        return pd.DataFrame()
    distance = haversine(counties.latitude.to_numpy()[:,None], counties.longitude.to_numpy()[:,None],
                         t.latitude.to_numpy()[None,:], t.longitude.to_numpy()[None,:])
    rows = []
    times = t.time_utc
    for i, county in enumerate(counties.to_dict('records')):
        near = distance[i] <= radius
        if not near.any():
            continue
        # Trapezoid integration avoids counting special records as extra hours.
        dt = times.diff().dt.total_seconds().to_numpy()[1:] / 3600
        duration = float(np.sum(dt * (near[:-1].astype(float) + near[1:].astype(float))/2))
        row = dict(county)
        row.update(min_distance_km=float(distance[i].min()), max_wind_knots=float(t.loc[near,'wind_knots'].max()),
                   hours_near=duration, first_near=times[near].min(), last_near=times[near].max())
        rows.append(row)
    return pd.DataFrame(rows)


def claim_candidates(claims, windows):
    """Bound intermediate joins by event dates to avoid a large cross-year join."""
    c = claims.copy()
    c['loss_day'] = pd.to_datetime(c.dateOfLoss, utc=True).dt.floor('D')
    parts = []
    for sid, window in windows.groupby('storm_id'):
        w = window[['storm_id','county_fips','first_near','last_near']].copy()
        w['start'] = pd.to_datetime(w.first_near, utc=True).dt.floor('D')
        w['end'] = pd.to_datetime(w.last_near, utc=True).dt.floor('D') + pd.Timedelta(days=3)
        relevant = c[c.loss_day.between(w.start.min(), w.end.max())]
        joined = relevant.merge(w, on='county_fips', how='inner')
        parts.append(joined[joined.loss_day.between(joined.start,joined.end)])
    return pd.concat(parts,ignore_index=True) if parts else pd.DataFrame(columns=list(c.columns)+['storm_id'])


def match_claims(claims, windows):
    """Match county and nearby dates plus three trailing days; exclude ambiguity."""
    candidates = claim_candidates(claims, windows)
    counts = candidates.groupby('id').storm_id.nunique()
    unique = counts[counts == 1].index
    matched = candidates[candidates.id.isin(unique)].drop_duplicates('id')
    return matched, {'unmatched':int(len(claims)-len(counts)), 'ambiguous':int((counts>1).sum()), 'matched':len(matched)}
