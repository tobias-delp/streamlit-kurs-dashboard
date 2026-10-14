# Sales & Service Dashboard

Ein interaktives Beispieldashboard für einen Streamlit-Kurs. Die Anwendung
wertet Bestellungen, Umsätze, Produkte, Lieferungen und Reklamationen aus und
zeigt dabei den praktischen Einsatz von Pandas, Plotly und Matplotlib.

## Funktionen

- Filter nach Land, Kundensegment und Bestelldatum
- Kennzahlen zu Umsatz, Bestellungen, Bestellwert und Lieferverzögerungen
- Umsatzentwicklung sowie Auswertungen nach Segment und Bestellstatus
- Analyse von Produktkategorien und Top-Produkten
- Auswertung von Versanddiensten und Reklamationsarten
- Vorschau und statistische Beschreibung der zugrunde liegenden CSV-Dateien
- Download der gefilterten Bestellungen als CSV

## Voraussetzungen

- [Python](https://www.python.org/) 3.14 oder neuer
- [uv](https://docs.astral.sh/uv/) als Paket- und Projektmanager

Alternativ kann die Anwendung mit Docker gestartet werden.

## Lokal starten

Repository klonen und in das Projektverzeichnis wechseln. Anschließend die
Abhängigkeiten installieren und Streamlit starten:

```bash
uv sync
uv run streamlit run src/streamlit_kurs_dashboard/app.py
```

Das Dashboard ist danach unter <http://localhost:8501> erreichbar.

## Mit Docker starten

```bash
docker build -t streamlit-kurs-dashboard .
docker run --rm -p 8501:8501 streamlit-kurs-dashboard
```

Anschließend kann das Dashboard unter <http://localhost:8501> geöffnet werden.

## Daten

Die Anwendung lädt beim Start sieben CSV-Dateien aus dem Ordner `data/`:

| Datei | Inhalt |
| --- | --- |
| `orders.csv` | Bestellungen und Bestellwerte |
| `customers.csv` | Kunden, Segmente und Regionen |
| `order_items.csv` | Bestellpositionen und Mengen |
| `products.csv` | Produktnamen und Produktdaten |
| `shipments.csv` | Lieferstatus und Lieferdauer |
| `complaints.csv` | Reklamationen und Reklamationsarten |
| `suppliers.csv` | Lieferantendaten |

Datumsfelder werden beim Einlesen konvertiert. Bestellungen werden über die
jeweiligen IDs mit Kunden sowie für einzelne Auswertungen mit Positionen,
Lieferungen und Reklamationen verknüpft.

## Projektstruktur

```text
.
├── data/                              # CSV-Datensätze
├── src/streamlit_kurs_dashboard/
│   ├── __init__.py
│   └── app.py                         # Streamlit-Anwendung
├── Dockerfile
├── pyproject.toml                     # Projekt und Abhängigkeiten
├── uv.lock                            # Festgeschriebene Versionen
└── README.md
```

## Lerninhalte

Das Projekt demonstriert unter anderem:

- Seitenlayout, Sidebar, Tabs, Kennzahlen und interaktive Filter in Streamlit
- Laden, Filtern, Gruppieren und Verknüpfen von Daten mit Pandas
- interaktive Linien-, Balken- und Donutdiagramme mit Plotly
- Balkendiagramme mit Matplotlib
- Caching mit `@st.cache_data`
- Tabellen, Slider, Auswahlfelder und CSV-Downloads

## Fragen für das Code-Review

- Warum wird `@st.cache_data` verwendet?
- Was bewirkt ein `merge` mit `how="left"`?
- Warum werden abhängige Tabellen über Bestell-IDs gefiltert?
- Wann eignet sich Plotly besser als Matplotlib?
- Wie könnte die Anwendung sinnvoll in mehrere Module aufgeteilt werden?
