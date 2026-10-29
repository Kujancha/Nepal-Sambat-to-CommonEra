# Nepal Sambat Chronology

**A Python tool for finding Gregorian date candidates from historical Nepal Sambat (NS) dates.** Designed with Malla-period inscriptions, chronicles, manuscript colophons, and other dated records in mind.

> **Research status — v0.4.5:** The astronomical baseline reproduces several reported late-Malla-era Capuchin/Nepal Sambat date correspondences. These records helped calibrate the program and are **not** an independent blind validation set. Earlier periods, historical calendrical practice, and uncertain readings still require investigation. Treat results as **date candidates**, not definitive historical judgments.

## Features

- Convert NS **year + lunar month + pakṣa + tithi** into candidate **proleptic Gregorian** dates.
- Select **Sanskrit / Newar month names** and **traditional / numerical tithis** in a Gradio interface, avoiding spelling-dependent input.
- Leave the lunar month **unknown** and receive all matching candidates.
- Optionally filter by **weekday** and **intercalary-month status**.
- Use the web interface or a JSON-producing command-line tool.
- Consult a machine-readable table of documented agreements and unresolved discrepancies.

## Get started

Requires **Python 3.10+**. Install from a local clone of this repository.

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[ui,dev]"
python app.py
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[ui,dev]'
python app.py
```

Open the local Gradio address shown in the terminal. To run the automated tests:

```bash
python -m pytest -q
```

For a CLI-only install, use `python -m pip install -e .` and then:

```bash
nschron NS 864 Bhadra Shukla 1
nschron NS 865 Asada Krishna 6
nschron NS 870 Chaitra Krishna 10 Friday
nschron NS 822 Sukla 15
```

The CLI prints candidate dates as JSON. For dates recorded without a month, the program may return multiple candidates. A missing result is not proof that an inscription is wrong.

## Historical concordances and open questions

The following are **reported historical dates used during development** and are maintained as regression tests. They are not source-critical editions of the original documents, and the source calendars/transcriptions still need full archival checking.

| Document or event | Recorded NS date | Reported Western date | Model output | Assessment |
|---|---|---|---|---|
| Capuchin house grant, Kathmandu | NS 862 Mārga Śukla 10 | 17 Dec 1741 | 17 Dec 1741 | Exact numerical concordance, assuming the *bright-half* reading |
| Capuchin house grant, Patan | NS 874 Caitra Kṛṣṇa 6 | 12 Apr 1754 | 12 Apr 1754 | Exact numerical concordance |
| Ranajit Malla's letter to the Pope | NS 864 Bhādra Śukla 1 | 7 Sep 1744 | 7 Sep 1744 | Exact numerical concordance |
| Francesco della Penna's death | NS 865 Āṣāḍha Kṛṣṇa 6 | 20 Jul 1745 | 20 Jul 1745 | Concordant with corrected date; epitaph year and other published calculations disputed |
| Jaya Prakash Malla's restoration, *Thyāsaphu* | NS 870 Caitra Kṛṣṇa 10, Friday | 30 Apr 1750, inferred from Tranquillus | 1 May 1750, Friday | NS weekday agrees; European event synchronism not settled |
| Capuchin house, Bhaktapur | NS 858 Kārtika Śukla 7 | 31 Oct 1737 | No sunrise-tithi candidate | Unresolved; modeled seventh tithi is skipped at sunrise |
| Jaya Prakash Malla decree | NS 857 Āśvina 15, pakṣa not given | 24 Oct 1737 | 23 Oct 1737 if Kṛṣṇa 15 | Unresolved one-day discrepancy under that reading |

See [`data/historical_concordances.csv`](data/historical_concordances.csv) for structured records and qualifications. These dates are **not hardcoded as special cases into the conversion algorithm**.

### Important distinction: development data vs independent tests

The reported Capuchin correspondences informed corrections to the year mapping and month indexing. Matching them shows that the implementation reproduces known examples; it does **not** establish general accuracy. Future validation should use previously unseen, consecutively logged inscriptions—including failed matches—and preferably independent weekdays or dual-dated documents. The weekday and tithi in one inscription may themselves come from the same historical calendar maker.

## How the astronomical model works

The current baseline uses [Swiss Ephemeris](https://www.astro.com/swisseph/) (Moshier calculations) to reconstruct solar and lunar positions. It computes lunar elongation, assigns the sunrise tithi, identifies amānta lunations and sidereal solar ingresses, and labels lunar months according to an implemented modern-style convention. It then searches the candidate dates for the requested NS year and filters by the supplied fields.

**Assumptions and limits:**

- The reference location is Kathmandu. Civil-day handling uses a fixed **UTC+05:45**, which is **anachronistic for the Malla period** and may affect borderline days. This needs improvement.
- The model uses **Lahiri sidereal reckoning**, an **amānta** month system, and an ordinary **Kārtika-based** year boundary. These choices are not proven to reproduce every medieval Newar rule.
- Historical mean/true astronomical methods, regional conventions, alternative intercalary-month naming (including hypotheses discussed by Petech and Regmi), omitted months, and ΔT uncertainty are not exhaustively modeled.
- A tithi can be **skipped or repeated at sunrise**. Some real historical date expressions may refer to events rather than the sunrise-assigned civil date.
- Results are **proleptic Gregorian**, even for years when many European sources used Julian dating. Verify the Western date style and whether it is the date of the event, document, or subsequent report.
- Textual ambiguities, scribal errors and scholarly reconstructions should be documented, not silently corrected to make an answer match.

In short: **astronomical consistency and historical calendar practice are related but distinct research questions**.

## Contributing inscriptions and validation evidence

Contributions are welcome, especially from **earlier Malla centuries** and from sources with recorded weekdays or independently dated parallel documents. For each record, please include where possible:

1. The **exact date wording** (including original script or a photograph/transcription), plus normalized NS year, month, pakṣa and tithi.
2. The **weekday**, if present; whether it was withheld when testing; and **all program candidates**, not only the successful ones.
3. The **source title, edition, volume/page, inscription identifier**, and any editorial corrections.
4. Any Western date **with its calendar style (Julian/Gregorian/unknown)** and whether it records the event itself or a later report.
5. A note indicating **exact, approximate, inferred, or disputed** dating.

Use [`data/validation_template.csv`](data/validation_template.csv) as a starting point. Open a GitHub issue or pull request with the evidence. Please avoid uploading copyrighted full-book scans without permission; citations and short transcriptions are preferable.

## References and further research

- *Christian Settlements in eighteen century nepal* by Vanini for the CE dates by the Capuchins and NS date by the Newars for the same document
- Mary Shepherd Slusser, *Nepal Mandala* (calendar discussion and historical context).
- D. R. Regmi, *Medieval Nepal*; Luciano Petech, *Mediaeval History of Nepal* (chronological and intercalation questions).

Bibliographic details and exact pages for each concordance remain a documentation task. Please do not treat the above list as a completed critical apparatus.

## Licensing and public distribution

**No license has been selected for this project's own source code yet.** Before publishing it as an open-source project, choose and add a `LICENSE` file. **Swiss Ephemeris / `pyswisseph` has separate licensing requirements**: review its current license and comply with all applicable conditions before releasing or distributing this project. Do not assume that choosing an MIT license for this repository overrides a dependency's license. Contributors and users should check the terms themselves.

## Project status

**v0.4.5 is an experimental historical-research tool.** Its value lies in producing inspectable, reproducible candidate dates and documenting when they agree—or disagree—with historical evidence.
