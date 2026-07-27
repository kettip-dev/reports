# shared/generators/

Shared Python utilities for regenerating store dashboards from CSV data.

## Scripts

| Script | Purpose |
| :--- | :--- |
| `build_dashboard.py` | Reads CSVs from `stores/<store>/data/` and writes `stores/<store>/index.html` |

## Usage

```bash
# Rebuild one store
python shared/generators/build_dashboard.py --store tua_deum_chek

# Future: rebuild all stores
python shared/generators/build_dashboard.py --all
```
