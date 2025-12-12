# Data Integrity Report
**Date**: 2025-12-12 10:14:54
**Source**: `c:\dev\ai-command-center\demodata\ZRFI005.XLSX`

## 1. Global Reconciliation
| Metric | Source (Excel) | Database (MySQL) | Variance | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Row Count** | 112 | 112 | 0 | Pass |
| **Total Amount** | 44,539,570,303.00 | 44,539,570,303.00 | 0.00 | Pass |

## 2. Deep Dive (Top Customer)
**Customer**: `Công Ty TNHH Vạn Lộc Hà Nội` (Code: `1200000087`)

| Metric | Excel Value | DB Value | Match? |
| :--- | :--- | :--- | :--- |
| Total Debt | 7,506,556,908.00 | 7,506,556,908.00 | ✅ |
| 1-30 Days | 1,154,383,691.00 | 1,154,383,691.00 | ✅ |
| 31-60 Days | 1,090,420,514.00 | 1,090,420,514.00 | ✅ |
| > 180 Days | 532,315,694.00 | 532,315,694.00 | ✅ |

## 3. Snapshot Verification
**Latest Snapshot Date Used**: `2025-12-12`