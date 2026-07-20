# Dataset notes

These CSV files are a normalized extract of the anonymized retail dataset supplied for the Sapiens Solutions course project. Store, receipt, material, promotion and coupon identifiers are course identifiers; the source contains no customer names or contact details.

The source workbook was converted into the repository schema as follows:

| CSV | Source sheet | Transformation |
| --- | --- | --- |
| `stores.csv` | `Магазины` | Store code and generic display name |
| `promo_types.csv` | `Тип акции` | Promotion type code and description |
| `promos.csv` | `Акции` | Promotion, material, discount type and value |
| `bills_head.csv` | `Чеки` | One row per receipt with store and date |
| `bills_item.csv` | `Чеки` | Lines grouped by receipt and material; revenue and quantity are summed |
| `traffic.csv` | `Трафик` | Hourly frames grouped into daily store traffic |
| `coupons.csv` | `coupons` | Coupon links retained only when the receipt line and promotion exist |

The raw workbook is not part of the repository. This keeps the example focused on the pipeline and avoids distributing obsolete training-environment connection details embedded in the accompanying course documents.
