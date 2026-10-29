from nschron.core import parse_inscription,convert,new_moon,elong,tithi_at,month_number

def test_parser():
    assert parse_inscription('NS 822 Asada Sukla 15')['month']=='Asada'
    assert parse_inscription('NS 822 Sukla 15 Friday')['weekday']=='Friday'
    assert month_number('Dilla')==8

def test_new_moon():
    for k in (-3700,-1000,0,300):
        assert min(elong(new_moon(k)),360-elong(new_moon(k)))<0.0001

def test_examples():
    rows=convert(822,'Sukla',15,'Asada')
    assert rows and all(r.ns_year==822 and r.month=='Ashadha' and r.paksha=='shukla' and r.tithi==15 for r in rows)
    assert all(r.gregorian.startswith('1702') for r in rows)

def test_missing_month():
    rows=convert(822,'Sukla',15)
    assert len(rows)>=11
    assert all(r.tithi==15 for r in rows)


def test_ns_year_mapping_historical_inputs():
    # Year checks only: historical CE dates require separate source validation.
    assert all(x.gregorian.startswith('1737') for x in convert(857,'shukla',15,'Ashvina'))
    assert all(x.gregorian.startswith('1737') for x in convert(857,'krishna',15,'Ashvina'))
    assert all(x.gregorian.startswith('1744') for x in convert(864,'shukla',1,'Bhadra'))
    assert all(x.gregorian.startswith('1750') for x in convert(870,'krishna',10,'Chaitra'))


def test_historical_synchronisms_v04():
    # Document dates supplied by researcher; concordance is conditional on calendar style.
    def days(y, p, t, m):
        return [r.gregorian for r in convert(y, p, t, m)]
    assert '1744-09-07' in days(864, 'shukla', 1, 'Bhadra')
    assert '1754-04-12' in days(874, 'krishna', 6, 'Chaitra')
    assert '1741-12-17' in days(862, 'shukla', 10, 'Margashirsha')
    assert '1737-10-23' in days(857, 'krishna', 15, 'Ashvina')
    assert days(858, 'shukla', 7, 'Kartika') == []  # tithi skipped at sunrise


def test_historical_month_index_after_refix():
    from datetime import date
    from nschron.core import sunrise, lunation_index, month_for_k
    assert month_for_k(lunation_index(sunrise(date(1737,10,31))))[0] == 0
    assert month_for_k(lunation_index(sunrise(date(1741,12,17))))[0] == 1
    assert month_for_k(lunation_index(sunrise(date(1754,4,12))))[0] == 5
