# Store: ទាដើមចេកម្ជូរ (Tua Deum Chek)

| Field     | Value |
| :--- | :--- |
| **Type**  | Dark Store (Express Delivery) |
| **ID**    | `tua_deum_chek` |
| **Active**| Yes |
| **Since** | 2026-01-22 |

## Contents

| File / Folder | Description |
| :--- | :--- |
| `index.html` | Live analytics dashboard (auto-generated, do not edit manually) |
| `store.json` | Store metadata (name, exchange rate, data file paths) |
| `data/revenue.csv` | Latest revenue data (overwritten on each update) |
| `data/phone_lead.csv` | Latest phone number acquisition data |
| `data/senders.csv` | Latest sender data |
| `data/archive/` | Dated snapshots of all past data files |
| `docs/` | SOPs, reports, and documentation specific to this store |

## Update Process

1. Export new CSV from ERPNext / SQL
2. Copy to `data/<type>.csv` (overwrite latest)
3. Also save a dated copy to `data/archive/<type>-YYYY-MM-DD.csv`
4. Run: `python ../../shared/generators/build_dashboard.py --store tua_deum_chek`
