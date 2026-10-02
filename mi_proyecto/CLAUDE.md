# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the development server
python manage.py runserver

# Apply database migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Run tests
python manage.py test procesador_excel
```

## Architecture

This is a Django 4.2 project with a single app (`procesador_excel`) that processes dental consultation Excel/CSV files and renders aggregated statistics tables.

**Request flow:** File upload → pandas processing in the view → HTML table rendered via `display.html`.

**Three upload endpoints** at `/excel/upload/`, `/excel/upload2/`, `/excel/upload3/`, each targeting a different report format:

- `upload_excel` — full breakdown by sex × age range × `relaciontemporal` (primera/segunda vez)
- `upload_excel2` — first-visit-only (`primeravezanio == 1`) breakdown by sex × age range
- `upload_excel3` — comprehensive dental procedure totals (placa bacteriana, cepillado, resinas, amalgamas, etc.) with column-name normalization to tolerate variant spellings (e.g. `piezatemp` / `piezatemporal` / `dientetemp`)

**Expected input columns** (all three views): `nombreprestador`, `primerapellidoprestador`, `segundoapellidoprestador`, `curpprestador`, `edad`, `sexo`. `upload_excel3` also normalizes `piezatemp`/`piezaperm` aliases and defaults missing optional columns to 0.

**Output shape:** Each view produces a `display_df` where **columns = `curpprestador` (dentist CURP)** and **rows = metric labels**. A `nombres_df` row with the dentist's full name is prepended via `pd.concat`.

**Templates** live in `templates/` at the project root (not inside the app), configured via `TEMPLATES[0]['DIRS']` in `settings.py`.

**Database:** SQLite (`db.sqlite3`). No models are currently defined; all data processing is in-memory via pandas.
