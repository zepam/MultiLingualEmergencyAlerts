#!/usr/bin/env python3
import json
import csv
from pathlib import Path
from datetime import datetime, date

PATH = Path("/home/jen/MultiLingualEmergencyAlerts/output_file.json")

STALE_DAYS = 30  # change as you like

def parse_date(s):
    if not s:
        return None
    s = str(s).strip()
    try:
        # supports YYYY-MM-DD and ISO datetimes
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        return None

def iter_records(data):
    """
    Yield (service, language, alert, prompt, count, latest_date)
    Works for both:
      service->language->alert->prompt->list
      service->language->alert->list
    """
    for service, svc_v in data.items():
        if not isinstance(svc_v, dict):
            continue
        for language, lang_v in svc_v.items():
            if not isinstance(lang_v, dict):
                continue
            for alert, alert_v in lang_v.items():
                if isinstance(alert_v, list):
                    items = alert_v
                    latest = None
                    for it in items:
                        if isinstance(it, dict):
                            d = parse_date(it.get("date"))
                            if d and (latest is None or d > latest):
                                latest = d
                    yield service, language, alert, "-", len(items), latest

                elif isinstance(alert_v, dict):
                    for prompt, items in alert_v.items():
                        if not isinstance(items, list):
                            continue
                        latest = None
                        for it in items:
                            if isinstance(it, dict):
                                d = parse_date(it.get("date"))
                                if d and (latest is None or d > latest):
                                    latest = d
                        yield service, language, alert, prompt, len(items), latest

def pivot_sum(rows, row_key, col_key, value_key):
    # returns (row_labels, col_labels, table_dict[(r,c)] = value)
    row_labels = sorted({r[row_key] for r in rows})
    col_labels = sorted({r[col_key] for r in rows})
    table = {(rl, cl): 0 for rl in row_labels for cl in col_labels}
    for r in rows:
        table[(r[row_key], r[col_key])] += r[value_key]
    return row_labels, col_labels, table

def print_pivot(title, row_labels, col_labels, table, row_name):
    # simple fixed-width printing
    col_w = max(8, max(len(c) for c in col_labels))
    row_w = max(len(row_name), max(len(r) for r in row_labels))
    print("\n" + title)
    print("-" * len(title))
    header = f"{row_name:<{row_w}}  " + "  ".join(f"{c:>{col_w}}" for c in col_labels) + f"  {'TOTAL':>8}"
    print(header)
    print("-" * len(header))

    for r in row_labels:
        vals = [table[(r, c)] for c in col_labels]
        total = sum(vals)
        line = f"{r:<{row_w}}  " + "  ".join(f"{v:>{col_w}d}" for v in vals) + f"  {total:>8d}"
        print(line)

def write_csv(path, header, rows):
    with open(Path("data") / path.name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))

    # Flatten to records
    recs = []
    for service, language, alert, prompt, count, latest in iter_records(data):
        recs.append({
            "service": service,
            "language": language,
            "alert": alert,
            "prompt": prompt,
            "count": count,
            "latest": latest,  # date or None
        })

    # ---- Pivot 1: language x service (sum of counts) ----
    rlabels, clabels, table = pivot_sum(recs, "language", "service", "count")
    print_pivot("Total responses by language x service", rlabels, clabels, table, "language")

    # ---- Pivot 2: alert x service (sum of counts) ----
    rlabels2, clabels2, table2 = pivot_sum(recs, "alert", "service", "count")
    print_pivot("Total responses by alert x service", rlabels2, clabels2, table2, "alert")

    # ---- Freshness report (most recent per service/language/alert/prompt) ----
    today = date.today()
    freshness_rows = []
    for r in sorted(recs, key=lambda x: (x["service"], x["language"], x["alert"], x["prompt"])):
        latest = r["latest"]
        stale = ""
        age_days = ""
        if latest:
            age = (today - latest).days
            age_days = str(age)
            stale = "STALE" if age > STALE_DAYS else ""
        freshness_rows.append((
            r["service"], r["language"], r["alert"], r["prompt"],
            r["count"],
            latest.isoformat() if latest else "",
            age_days,
            stale
        ))

    print("\nFreshness (most recent date per service/language/alert/prompt)")
    print("--------------------------------------------------------")
    print("service\tlanguage\talert\tprompt\tcount\tlatest\tage_days\tstale")
    for row in freshness_rows:
        print("\t".join(map(str, row)))

    # ---- Write CSV outputs ----
    out_dir = PATH.parent
    write_csv(out_dir / "pivot_language_service.csv",
              ["language"] + clabels + ["TOTAL"],
              [
                  [lang] + [table[(lang, svc)] for svc in clabels] + [sum(table[(lang, svc)] for svc in clabels)]
                  for lang in rlabels
              ])

    write_csv(out_dir / "pivot_alert_service.csv",
              ["alert"] + clabels2 + ["TOTAL"],
              [
                  [alert] + [table2[(alert, svc)] for svc in clabels2] + [sum(table2[(alert, svc)] for svc in clabels2)]
                  for alert in rlabels2
              ])

    write_csv(out_dir / "freshness_report.csv",
              ["service", "language", "alert", "prompt", "count", "latest", "age_days", "stale"],
              freshness_rows)

    print(f"\nWrote CSVs to: {out_dir}")
    print("  pivot_language_service.csv")
    print("  pivot_alert_service.csv")
    print("  freshness_report.csv")

if __name__ == "__main__":
    main()