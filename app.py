"""Structured Gradio interface for historical NS date candidate reconstruction."""
import gradio as gr
from nschron.core import convert, NAMES, NEWAR

MONTH_CHOICES = [(f'{NAMES[i]} / {NEWAR[i]}', NAMES[i]) for i in range(12)]
TITHI_NAMES = (
    'Pratipadā (Pratipada)', 'Dvitīyā (Dwitiya)', 'Tṛtīyā (Tritiya)',
    'Caturthī (Chaturthi)', 'Pañcamī (Panchami)', 'Ṣaṣṭhī (Shashthi)',
    'Saptamī (Saptami)', 'Aṣṭamī (Ashtami)', 'Navamī (Navami)',
    'Daśamī (Dashami)', 'Ekādaśī (Ekadashi)', 'Dvādaśī (Dwadashi)',
    'Trayodaśī (Trayodashi)', 'Caturdaśī (Chaturdashi)',
    'Pūrṇimā (Purnima) / Amāvasyā (Amavasya)'
)
WEEKDAY_CHOICES = [
    ('Unknown / not recorded', None),
    ('Monday / Somavāra', 'monday'), ('Tuesday / Maṅgalavāra', 'tuesday'),
    ('Wednesday / Budhavāra', 'wednesday'), ('Thursday / Guruvāra', 'thursday'),
    ('Friday / Śukravāra', 'friday'), ('Saturday / Śanivāra', 'saturday'),
    ('Sunday / Ravivāra', 'sunday'),
]


def tithi_choices(paksha):
    names = list(TITHI_NAMES)
    names[-1] = ('Pūrṇimā (full moon)' if paksha == 'shukla'
                 else 'Amāvasyā (new moon)')
    return [(f'{n + 1:02d} — {name}', n + 1) for n, name in enumerate(names)]


def process(year, month, paksha, tithi, weekday, adhika):
    try:
        if year is None or int(year) != year:
            raise ValueError('Enter a whole-number Nepal Sambat year.')
        vals = convert(
            ns_year=int(year), month=month, paksha=paksha, tithi=int(tithi),
            weekday=weekday,
            intercalary={
                'Any / unknown': None,
                'Ordinary month only': False,
                'Intercalary month only': True,
            }[adhika],
        )
        rows = [[x.gregorian, x.weekday, x.month, x.newar_month,
                 x.paksha, x.tithi, 'Yes' if x.intercalary else 'No',
                 x.solar_ingresses] for x in vals]
        return rows, (f'{len(rows)} candidate(s) using astronomical_baseline_v1. '
                      'Proleptic Gregorian dates; tested against selected late-Malla Capuchin-era records. Not universally validated.')
    except (ValueError, RuntimeError, OverflowError) as exc:
        return [], f'Error: {exc}'


with gr.Blocks(title='Nepal Sambat Historical Chronology — Experimental') as demo:
    gr.Markdown(
        '# Historical Nepal Sambat date finder\n'
        '**Research prototype.** Choose the standardized meaning, regardless of spelling '
        'in the manuscript. Dates are *proleptic Gregorian*. The model reproduces selected '
        'late-Malla documentary dates, but broader historical validity remains under study.'
    )
    with gr.Row():
        year = gr.Number(label='Nepal Sambat year', value=822, precision=0)
        month = gr.Dropdown(
            [('Unknown / not recorded', None)] + MONTH_CHOICES,
            value=NAMES[8], label='Lunar month — Sanskrit / Newar',
            info='Leave unknown when the source omits the month.',
        )
    with gr.Row():
        paksha = gr.Dropdown(
            [('Śukla / Sukla / Sudi — bright', 'shukla'),
             ('Kṛṣṇa / Krishna / Badi — dark', 'krishna')],
            value='shukla', label='Pakṣa (lunar fortnight)',
        )
        tithi = gr.Dropdown(tithi_choices('shukla'), value=15,
                            label='Tithi — number and traditional name')
    with gr.Row():
        weekday = gr.Dropdown(WEEKDAY_CHOICES, value=None, label='Weekday (optional)')
        leap = gr.Dropdown(
            ['Any / unknown', 'Ordinary month only', 'Intercalary month only'],
            value='Any / unknown', label='Month occurrence (optional)'
        )
    go = gr.Button('Find Gregorian candidates', variant='primary')
    grid = gr.Dataframe(
        headers=['Gregorian', 'Weekday', 'Month', 'Newar', 'Paksha', 'Tithi',
                 'Adhika', 'Solar ingresses'], interactive=False,
    )
    msg = gr.Textbox(label='Interpretation', interactive=False)
    paksha.change(
        lambda p, t: gr.update(choices=tithi_choices(p), value=t),
        [paksha, tithi], [tithi],
    )
    go.click(process, [year, month, paksha, tithi, weekday, leap], [grid, msg])

if __name__ == '__main__':
    demo.launch()
