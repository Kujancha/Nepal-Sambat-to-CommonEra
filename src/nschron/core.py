"""Exploratory astronomical Nepal Sambat reconstructor with selected late-Malla documentary matches.

Uses modern Swiss Ephemeris Moshier positions, Lahiri sidereal zodiac,
modern Kathmandu sunrise and a simplified ingress-based amanta model.
All Gregorian dates are PROLEPTIC GREGORIAN.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from functools import lru_cache
import math
import re
import unicodedata
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)
FLAGS = swe.FLG_MOSEPH
SID_FLAGS = FLAGS | swe.FLG_SIDEREAL
KTM = (85.3240, 27.7172, 1400.0)
# Civil-day convention: fixed UTC+05:45, deliberately anachronistic before 1986.
UTC_OFFSET_HOURS = 5.75
NAMES = ("Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna", "Chaitra",
         "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina")
NEWAR = ("Kachhala", "Thinla", "Pwanhela", "Sila", "Chilla", "Chaula",
         "Bachhala", "Tachhala", "Dilla", "Gunla", "Yanla", "Kaula")
MONTH_ALIASES = {
    0: ('kartika','kartik','kattik','kachhala','kachala'),
    1: ('margashirsha','margasirsa','mangsir','margashira','thinla'),
    2: ('pausha','pausa','poush','pousha','pwanhela','pohela'),
    3: ('magha','magh','sila','silla'),
    4: ('phalguna','phalguna','phalgun','falgun','chilla','chila'),
    5: ('chaitra','caitra','chait','chaula','chaulaa'),
    6: ('vaishakha','vaisakha','baisakh','baishakh','bachhala'),
    7: ('jyeshtha','jyestha','jestha','jeth','tachhala'),
    8: ('ashadha','asada','asadha','asar','ashadh','dilla'),
    9: ('shravana','sravana','shrawan','sawan','gunla'),
    10: ('bhadrapada','bhadra','bhadau','yanla','yenla'),
    11: ('ashvina','ashwin','asvina','aswin','kaula'),
}
PAKSHA = {'shukla':'shukla', 'sukla':'shukla', 'suddha':'shukla', 'bright':'shukla',
          'krishna':'krishna','krsna':'krishna','dark':'krishna','bahula':'krishna'}
WEEKDAYS = {'monday':0,'sombar':0,'somavara':0,'soma':0,
            'tuesday':1,'mangalbar':1,'mangalavara':1,'mangala':1,
            'wednesday':2,'budhabar':2,'budhavara':2,'budha':2,
            'thursday':3,'bihibar':3,'guruvāra':3,'guruvara':3,'guru':3,'brhaspativara':3,
            'friday':4,'sukrabar':4,'shukravara':4,'sukravara':4,'shukra':4,
            'saturday':5,'shanibar':5,'shanivara':5,'shani':5,
            'sunday':6,'aitabar':6,'ravivara':6,'ravi':6}

def normal(s: str) -> str:
    s = unicodedata.normalize('NFKD',str(s)).lower()
    return ''.join(ch for ch in s if not unicodedata.combining(ch)).strip().replace('ā','a')

def month_number(value: str | None) -> int | None:
    if not value or normal(value) in ('any','unknown','none','-'): return None
    v = normal(value).replace(' ','').replace('-','')
    for i, terms in MONTH_ALIASES.items():
        if v in terms: return i
    raise ValueError(f'Unknown month {value!r}; try Ashadha or Dilla')

def paksha_name(value: str) -> str:
    try: return PAKSHA[normal(value)]
    except KeyError: raise ValueError(f'Unknown paksha: {value}') from None

def weekday_number(value: str | None) -> int | None:
    if not value or normal(value) in ('any','none','unknown','-'): return None
    key = normal(value).replace(' ','')
    if key not in WEEKDAYS: raise ValueError(f'Unknown weekday {value!r}')
    return WEEKDAYS[key]

def jd(d: date) -> float:
    return swe.julday(d.year,d.month,d.day,0,swe.GREG_CAL)

def sunmoon(t: float, sidereal=False) -> float:
    return swe.calc_ut(t,swe.SUN,SID_FLAGS if sidereal else FLAGS)[0][0]

def elong(t: float) -> float:
    moon = swe.calc_ut(t,swe.MOON,FLAGS)[0][0]
    return (moon - sunmoon(t))%360

def signed_phase(t: float) -> float:
    return ((elong(t)+180)%360)-180

@lru_cache(maxsize=8192)
def new_moon(k: int) -> float:
    t = 2451550.09765 + 29.530588853*k
    for _ in range(12):
        err = signed_phase(t)
        if abs(err) < 0.0000001: break
        # Numeric angular derivative, accounts for non-uniform lunar velocity.
        deriv = (signed_phase(t+0.01)-signed_phase(t-0.01))/0.02
        t -= err/deriv
    return t

def lunation_index(t: float) -> int:
    k = round((t-2451550.09765)/29.530588853)
    while new_moon(k)>t: k-=1
    while new_moon(k+1)<=t: k+=1
    return k

def month_for_k(k: int) -> tuple[int,bool,int]:
    """Month index, intercalary marker, # solar sign boundaries during lunation.

    0-ingress gets the name of the NEXT ingress-bearing month (adhika first).
    2-ingress gives a warning: kshaya month not fully modeled.
    """
    a,b=new_moon(k),new_moon(k+1)
    s0=math.floor((sunmoon(a+1e-5,True)%360)/30)
    s1=math.floor((sunmoon(b-1e-5,True)%360)/30)
    count=(s1-s0)%12
    if count==0:
        for j in range(k+1,k+4):
            na,nb=new_moon(j),new_moon(j+1)
            x=math.floor((sunmoon(na+1e-5,True)%360)/30)
            y=math.floor((sunmoon(nb-1e-5,True)%360)/30)
            if (y-x)%12:
                return (y+5)%12,True,0
        raise RuntimeError('Could not find following solar ingress')
    return (s1+5)%12,False,count

def sunrise(d: date, lon=KTM[0],lat=KTM[1],alt=KTM[2]) -> float:
    # Search from local midnight, not UTC midnight.
    start=jd(d)-UTC_OFFSET_HOURS/24
    status, values = swe.rise_trans(start,swe.SUN,swe.CALC_RISE,(lon,lat,alt),0,15,FLAGS)
    if status != 0: raise ValueError(f'No sunrise found for {d}')
    return values[0]

def tithi_at(t: float) -> tuple[str,int]:
    # tithi 1-30: bright 1..15 then dark 1..15.
    idx=min(29,int(elong(t)/12))
    return ('shukla',idx+1) if idx < 15 else ('krishna',idx-14)

def year_start_k(ce_year: int) -> int:
    """NS year starts with Kartika lunation in autumn CE year.
    Uses date and ordinary Kartika month-name, not a fixed Gregorian date.
    """
    center=lunation_index(jd(date(ce_year,11,1)))
    possible=[]
    for k in range(center-3,center+4):
        index, adhika, count=month_for_k(k)
        if index==0 and not adhika:
            diff=abs(new_moon(k)-jd(date(ce_year,11,1)))
            possible.append((diff,k))
    if not possible: raise RuntimeError(f'No Kartika month found for {ce_year}')
    return min(possible)[1]

@dataclass(frozen=True)
class Candidate:
    gregorian: str
    weekday: str
    ns_year: int
    month: str
    newar_month: str
    paksha: str
    tithi: int
    intercalary: bool
    solar_ingresses: int
    model: str = 'astronomical_baseline_v1'
    notes: str = 'Proleptic Gregorian; modern sunrise and Lahiri sidereal convention; matched selected late-Malla dated records, not universally verified'


def convert(ns_year: int, paksha: str, tithi: int, month: str|None=None,
            weekday: str|None=None, intercalary: bool|None=None,
            lon:float=KTM[0],lat:float=KTM[1],alt:float=KTM[2]) -> list[Candidate]:
    """Find matching civil dates; no match is NOT evidence of inscription error."""
    if not (1 <= ns_year <= 1800): raise ValueError('NS year must be 1..1800')
    if not 1<=tithi<=15: raise ValueError('Tithi number must be 1..15 in a paksha')
    p=paksha_name(paksha)
    m=month_number(month)
    w=weekday_number(weekday)
    # NS 0 began in autumn CE 879; e.g. NS 857 begins in autumn CE 1736.
    # In the historical era numbering used here, autumn CE year = NS + 879.
    start_ce=879+ns_year
    k0=year_start_k(start_ce)
    k1=year_start_k(start_ce+1)
    start_d=date(*swe.revjul(new_moon(k0)-UTC_OFFSET_HOURS/24,swe.GREG_CAL)[:3])-timedelta(days=2)
    end_d=date(*swe.revjul(new_moon(k1)-UTC_OFFSET_HOURS/24,swe.GREG_CAL)[:3])+timedelta(days=2)
    out=[]
    d=start_d
    while d<=end_d:
        rise=sunrise(d,lon,lat,alt)
        k=lunation_index(rise)
        if k0<=k<k1:
            idx, leap, count=month_for_k(k)
            pk, ti=tithi_at(rise)
            if ((m is None or m==idx) and pk==p and ti==tithi
                and (w is None or d.weekday()==w)
                and (intercalary is None or leap==intercalary)):
                out.append(Candidate(d.isoformat(),d.strftime('%A'),ns_year,NAMES[idx],
                                     NEWAR[idx],pk,ti,leap,count))
        d+=timedelta(days=1)
    return out


def parse_inscription(s: str) -> dict:
    """Parse romanized 'NS 822 Asada Sukla 15 [Friday]' (not full OCR/Nepal script)."""
    pieces=re.split(r'\s+',s.strip())
    if pieces and pieces[0].lower() in ('ns','n.s.','n.s','nepal-sambat'):
        pieces=pieces[1:]
    if not pieces: raise ValueError('Empty historical date')
    year=int(pieces.pop(0))
    if not pieces: raise ValueError('Provide paksha and tithi')
    pak_idx=next((i for i,x in enumerate(pieces) if normal(x) in PAKSHA),None)
    if pak_idx is None: raise ValueError('Paksha missing: use Sukla or Krishna')
    month=' '.join(pieces[:pak_idx]) or None
    pak=pieces[pak_idx]
    if pak_idx+1>=len(pieces): raise ValueError('Tithi missing')
    ti=int(pieces[pak_idx+1])
    day=' '.join(pieces[pak_idx+2:]) or None
    return dict(ns_year=year,month=month,paksha=pak,tithi=ti,weekday=day)
