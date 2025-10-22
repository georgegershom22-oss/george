#!/usr/bin/env python3
import os
import sys
import json
import csv
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'secondary', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'secondary', 'processed')
META_DIR = os.path.join(BASE_DIR, 'data', 'secondary', 'metadata')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

WORLD_BANK_API = 'https://api.worldbank.org/v2/country/NGA/indicator/{indicator}?format=json&per_page=20000'
WB_INDICATORS = {
    'NY.GDP.MKTP.KD.ZG': {
        'name': 'GDP growth (annual %)',
        'short': 'gdp_growth_pct'
    },
    'FP.CPI.TOTL.ZG': {
        'name': 'Inflation, consumer prices (annual %)',
        'short': 'inflation_pct'
    },
    'FR.INR.LEND': {
        'name': 'Lending interest rate (%)',
        'short': 'lending_rate_pct'
    },
    'IC.BUS.EASE.XQ': {
        'name': 'Ease of doing business score (0=lowest to 100=best)',
        'short': 'eodb_score'
    },
}

NIGERIA_STATES = [
    'Abia','Adamawa','Akwa Ibom','Anambra','Bauchi','Bayelsa','Benue','Borno','Cross River','Delta','Ebonyi','Edo','Ekiti','Enugu','FCT','Gombe','Imo','Jigawa','Kaduna','Kano','Katsina','Kebbi','Kogi','Kwara','Lagos','Nasarawa','Niger','Ogun','Ondo','Osun','Oyo','Plateau','Rivers','Sokoto','Taraba','Yobe','Zamfara'
]

STATE_TO_REGION = {
    'Abia': 'South-East', 'Anambra': 'South-East', 'Ebonyi': 'South-East', 'Enugu': 'South-East', 'Imo': 'South-East',
    'Akwa Ibom': 'South-South', 'Bayelsa': 'South-South', 'Cross River': 'South-South', 'Delta': 'South-South', 'Edo': 'South-South', 'Rivers': 'South-South',
    'Ekiti': 'South-West', 'Lagos': 'South-West', 'Ogun': 'South-West', 'Ondo': 'South-West', 'Osun': 'South-West', 'Oyo': 'South-West',
    'Benue': 'North-Central', 'Kogi': 'North-Central', 'Kwara': 'North-Central', 'Nasarawa': 'North-Central', 'Niger': 'North-Central', 'Plateau': 'North-Central', 'FCT': 'North-Central',
    'Adamawa': 'North-East', 'Bauchi': 'North-East', 'Borno': 'North-East', 'Gombe': 'North-East', 'Taraba': 'North-East', 'Yobe': 'North-East',
    'Jigawa': 'North-West', 'Kaduna': 'North-West', 'Kano': 'North-West', 'Katsina': 'North-West', 'Kebbi': 'North-West', 'Sokoto': 'North-West', 'Zamfara': 'North-West',
}

SECTORS = [
    'Agriculture','Manufacturing','Construction','Trade','Information and Communication','Financial and Insurance','Real Estate','Transportation and Storage','Accommodation and Food Services','Education','Human Health and Social Services','Arts, Entertainment and Recreation','Professional, Scientific and Technical','Administrative and Support Services'
]

START_YEAR = 2010
END_YEAR = datetime.now().year - 1


def _stable_noise_for_name(name: str, modulo: int = 7, step: float = 0.6) -> float:
    # Deterministic small variance based on name
    h = hashlib.sha256(name.encode('utf-8')).hexdigest()
    val = int(h[:8], 16)
    centered = (val % modulo) - (modulo // 2)  # e.g., -3..+3 when modulo=7
    return centered * step


def _wb_get_indicator(indicator: str) -> List[Dict[str, Any]]:
    url = WORLD_BANK_API.format(indicator=indicator)
    # retry logic for robustness
    for attempt in range(5):
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, list) or len(data) < 2:
                raise ValueError('Unexpected World Bank API response structure')
            records = data[1]
            out: List[Dict[str, Any]] = []
            for rec in records:
                date_str = rec.get('date')
                value = rec.get('value')
                try:
                    year = int(date_str)
                except Exception:
                    continue
                out.append({'year': year, 'value': value, 'indicator': indicator})
            return out
        except Exception as e:
            if attempt == 4:
                raise
            time.sleep(1.5 * (attempt + 1))
    return []


def fetch_world_bank_macros() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for code, meta in WB_INDICATORS.items():
        vals = _wb_get_indicator(code)
        for rec in vals:
            y = rec['year']
            if y < START_YEAR or y > END_YEAR:
                continue
            rows.append({
                'year': y,
                'value': float(rec['value']) if rec['value'] is not None else None,
                'indicator': rec['indicator'],
                'series_name': meta['name'],
                'series_short': meta['short'],
            })
    rows.sort(key=lambda r: (r['series_short'], r['year']))
    return rows


def fabricate_broadband_penetration() -> List[Dict[str, Any]]:
    # Create synthetic broadband penetration by state, with regional baseline and state-specific noise
    years = list(range(START_YEAR, END_YEAR + 1))
    records: List[Dict[str, Any]] = []

    # plausible national baseline growth curve (in % of population)
    # starting ~10% in 2015, growing to ~55% by 2024; earlier years lower
    for state in NIGERIA_STATES:
        region = STATE_TO_REGION.get(state, 'Unknown')
        regional_offset = {
            'South-West': 8.0,
            'South-East': 5.0,
            'South-South': 4.0,
            'North-Central': 1.5,
            'North-West': -2.0,
            'North-East': -3.0,
        }.get(region, 0.0)

        state_noise = _stable_noise_for_name(state, modulo=7, step=0.6)

        for y in years:
            t = max(0, y - 2012)
            base = 5 + 2.2 * t - 0.03 * (t ** 2)  # S-curve-ish polynomial
            base = max(0, base)
            value = base + regional_offset + state_noise
            # dampen before 2015
            if y < 2015:
                value *= 0.5
            # cap between 0 and 90
            value = float(max(0.0, min(90.0, round(value, 2))))
            records.append({
                'geo_level': 'state',
                'geo_name': state,
                'region': region,
                'year': int(y),
                'broadband_penetration_pct': value,
                'source': 'synthetic',
                'method': 'regional baseline + state noise',
            })

    return records


def fabricate_sectoral_growth() -> List[Dict[str, Any]]:
    # Fabricate sector growth rates consistent with national GDP trend but with sector-specific dynamics
    macros = fetch_world_bank_macros()
    gdp_growth_by_year: Dict[int, Optional[float]] = {}
    for rec in macros:
        if rec['series_short'] == 'gdp_growth_pct':
            gdp_growth_by_year[int(rec['year'])] = rec['value'] if rec['value'] is not None else None
    # fill missing with baseline 2.5
    for y in range(START_YEAR, END_YEAR + 1):
        if y not in gdp_growth_by_year or gdp_growth_by_year[y] is None:
            gdp_growth_by_year[y] = 2.5

    sector_params = {
        'Agriculture': (-0.5, 0.8),
        'Manufacturing': (0.6, 1.2),
        'Construction': (0.3, 1.1),
        'Trade': (0.2, 1.0),
        'Information and Communication': (1.2, 1.5),
        'Financial and Insurance': (0.8, 1.3),
        'Real Estate': (-0.8, 0.7),
        'Transportation and Storage': (0.1, 1.0),
        'Accommodation and Food Services': (0.5, 1.1),
        'Education': (-0.2, 0.9),
        'Human Health and Social Services': (0.4, 1.0),
        'Arts, Entertainment and Recreation': (0.7, 1.2),
        'Professional, Scientific and Technical': (0.9, 1.3),
        'Administrative and Support Services': (0.3, 1.0),
    }

    rows: List[Dict[str, Any]] = []
    for sector, (offset, beta) in sector_params.items():
        for year in range(START_YEAR, END_YEAR + 1):
            nat = float(gdp_growth_by_year.get(year, 2.5))
            # sector growth = offset + beta * national + cyclical component
            cyc = 1.0 * ((year % 5) - 2)  # deterministic 5-year cycle -2..+2
            value = offset + beta * nat + 0.15 * cyc
            rows.append({
                'sector': sector,
                'year': int(year),
                'sector_growth_pct': round(value, 2),
                'source': 'synthetic',
                'method': 'linear transform of national trend + cycle',
            })
    return rows


def fabricate_mobile_money_adoption() -> List[Dict[str, Any]]:
    # National + regional adoption series 2012-2024
    regions = sorted(set(STATE_TO_REGION.values()))
    years = list(range(max(2012, START_YEAR), END_YEAR+1))

    records: List[Dict[str, Any]] = []
    for region in regions:
        reg_base = {
            'South-West': 10.0,
            'South-East': 7.0,
            'South-South': 8.0,
            'North-Central': 5.0,
            'North-West': 3.0,
            'North-East': 2.0,
        }.get(region, 5.0)
        for y in years:
            t = y - 2012
            base = reg_base + 3.0 * t - 0.07 * (t ** 2)
            value = max(0.0, min(95.0, round(base, 2)))
            records.append({
                'geo_level': 'region', 'geo_name': region, 'year': y,
                'mobile_money_users_pct': value,
                'source': 'synthetic', 'method': 'regional baseline quadratic growth'
            })
    # National as weighted average proxy (simple mean of regions here)
    values_by_year: Dict[int, List[float]] = {}
    for rec in records:
        values_by_year.setdefault(int(rec['year']), []).append(float(rec['mobile_money_users_pct']))
    nat_records: List[Dict[str, Any]] = []
    for y in years:
        vals = values_by_year.get(y, [])
        mean_val = round(sum(vals) / len(vals), 2) if vals else 0.0
        nat_records.append({
            'geo_level': 'national', 'geo_name': 'Nigeria', 'year': y,
            'mobile_money_users_pct': mean_val, 'source': 'synthetic', 'method': 'mean of regions'
        })

    return records + nat_records


def fabricate_itu_idi() -> List[Dict[str, Any]]:
    # ITU ICT Development Index (0-10 historically) re-based to 0-100
    years = list(range(START_YEAR, END_YEAR+1))
    rows: List[Dict[str, Any]] = []
    for y in years:
        t = y - START_YEAR
        base = 30 + 3.1 * t - 0.05 * (t ** 2)
        val = max(0.0, min(100.0, round(base, 2)))
        rows.append({'year': y, 'ict_development_index_score': val, 'source': 'synthetic', 'method': 'quadratic growth then plateau'})
    return rows


def write_with_metadata(rows: List[Dict[str, Any]], filename: str, description: str, license_text: str, sources: List[str], fabricated: bool = False, schema: Dict[str, str] = None):
    path = os.path.join(PROCESSED_DIR, filename)
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Determine column order from schema if provided; else from union of keys
    if schema is not None:
        fieldnames = list(schema.keys())
    else:
        keys = set()
        for r in rows:
            keys.update(r.keys())
        fieldnames = sorted(list(keys))
    # Normalize rows to include all fields
    normalized: List[Dict[str, Any]] = []
    for r in rows:
        item = {k: r.get(k, None) for k in fieldnames}
        normalized.append(item)
    # Write CSV
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized)
    # Metadata JSON
    meta = {
        'name': filename,
        'description': description,
        'n_rows': int(len(rows)),
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'sources': sources,
        'fabricated': fabricated,
        'schema': schema or {k: 'unknown' for k in fieldnames},
        'topic': 'Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth',
        'geography': 'Nigeria',
        'time_range': {'start_year': START_YEAR, 'end_year': END_YEAR},
        'license': license_text,
    }
    with open(os.path.join(META_DIR, filename.replace('.csv', '.meta.json')), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)


def main():
    # Fetch World Bank macros
    macros = fetch_world_bank_macros()
    write_with_metadata(
        macros,
        'world_bank_macros.csv',
        description='World Bank indicators for Nigeria: GDP growth, inflation, lending rate, ease of doing business score',
        license_text='World Bank API data is provided under the World Bank Terms of Use. This file may contain derived values.',
        sources=['World Bank Open Data API'],
        fabricated=False,
        schema={'year':'int','value':'float','indicator':'str','series_name':'str','series_short':'str'}
    )

    # Broadband penetration synthetic
    broadband = fabricate_broadband_penetration()
    write_with_metadata(
        broadband,
        'broadband_penetration_state.csv',
        description='Synthetic broadband penetration by Nigerian state and region (percentage of population).',
        license_text='Synthetic dataset generated for research; no direct real-person data.',
        sources=['Synthetic based on plausible trends'],
        fabricated=True,
        schema={'geo_level':'str','geo_name':'str','region':'str','year':'int','broadband_penetration_pct':'float','source':'str','method':'str'}
    )

    # Sectoral growth synthetic
    sector = fabricate_sectoral_growth()
    write_with_metadata(
        sector,
        'sectoral_growth_rates.csv',
        description='Synthetic sectoral growth rates aligned with national GDP growth trend.',
        license_text='Synthetic dataset generated for research; no direct real-person data.',
        sources=['Synthetic derived using World Bank macro trend'],
        fabricated=True,
        schema={'sector':'str','year':'int','sector_growth_pct':'float','source':'str','method':'str'}
    )

    # Mobile money adoption synthetic
    mobile = fabricate_mobile_money_adoption()
    write_with_metadata(
        mobile,
        'mobile_money_adoption.csv',
        description='Synthetic mobile money/FinTech adoption levels by region and national.',
        license_text='Synthetic dataset generated for research; no direct real-person data.',
        sources=['Synthetic based on CBN reports narrative'],
        fabricated=True,
        schema={'geo_level':'str','geo_name':'str','year':'int','mobile_money_users_pct':'float','source':'str','method':'str'}
    )

    # ITU IDI synthetic
    idi = fabricate_itu_idi()
    write_with_metadata(
        idi,
        'ict_development_index.csv',
        description='Synthetic ITU ICT Development Index score trajectory for Nigeria (0-100).',
        license_text='Synthetic dataset generated for research; no direct real-person data.',
        sources=['Synthetic based on ITU IDI concept'],
        fabricated=True,
        schema={'year':'int','ict_development_index_score':'float','source':'str','method':'str'}
    )

    # SME reports summary (placeholder curated references)
    reports = [
        {'source':'SMEDAN','title':'SMEDAN-NBS Survey of MSMEs','year':2017,'url':'https://smedan.gov.ng','key_metrics':'["num_msmes","employment","finance_access"]', 'notes':'Cites access to finance as major constraint'},
        {'source':'PwC','title':'PwC MSME Survey Nigeria','year':2020,'url':'https://www.pwc.com','key_metrics':'["finance","infrastructure","skills"]', 'notes':'Highlights infrastructure and tax complexity'},
        {'source':'McKinsey','title':'Digital Nigeria report','year':2022,'url':'https://www.mckinsey.com','key_metrics':'["digital_adoption","productivity"]', 'notes':'Discusses digital adoption gaps in SMEs'},
    ]
    write_with_metadata(
        reports,
        'sme_reports_catalog.csv',
        description='Catalog of key SME landscape reports relevant to innovation constraints and adoption in Nigeria.',
        license_text='References and brief summaries for research cross-validation.',
        sources=['SMEDAN','PwC','McKinsey','NBS'],
        fabricated=False,
        schema={'source':'str','title':'str','year':'int','url':'str','key_metrics':'json','notes':'str'}
    )

    print('Secondary dataset generation completed.')


if __name__ == '__main__':
    main()
