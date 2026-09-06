#!/usr/bin/env python3
"""Car2Me: pending Yandex Form responses vs already generated reports."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import openpyxl
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install: pip install openpyxl") from exc

ROOT = Path(__file__).resolve().parents[1]
ANSWERS_DIR = ROOT / "Ответы"
REPORTS_DIR = ROOT / "Отчёты"
PROCESSED_FILE = ANSWERS_DIR / "processed.json"

ID_COLUMN = "ID"
TIME_COLUMN = "Время создания"
NAME_COLUMN = "Как к вам обращаться?"

FRONTMATTER_ID = re.compile(
    r"^---\s*\ncar2me_response_id:\s*(\d+)\s*\n---\s*\n",
    re.MULTILINE,
)


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_filename(name: str) -> str:
    cleaned = name.strip()
    for ch in '<>:"/\\|?*':
        cleaned = cleaned.replace(ch, "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:80] or "client"


def allocate_report_paths(name: str) -> tuple[Path, Path]:
    """Имя файла = как в форме. Если занято — Имя-2, Имя-3 …"""
    base = safe_filename(name)
    md = REPORTS_DIR / f"{base}.md"
    pdf = REPORTS_DIR / f"{base}.pdf"
    if not md.exists() and not pdf.exists():
        return md, pdf
    n = 2
    while True:
        md = REPORTS_DIR / f"{base}-{n}.md"
        pdf = REPORTS_DIR / f"{base}-{n}.pdf"
        if not md.exists() and not pdf.exists():
            return md, pdf
        n += 1


def report_paths_for(_response_id: str, name: str) -> tuple[Path, Path]:
    return allocate_report_paths(name)


def load_processed() -> dict:
    if not PROCESSED_FILE.exists():
        return {}
    return json.loads(PROCESSED_FILE.read_text(encoding="utf-8"))


def save_processed(data: dict) -> None:
    ANSWERS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def latest_xlsx() -> Path | None:
    files = sorted(ANSWERS_DIR.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def read_rows(xlsx: Path) -> list[dict[str, str]]:
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb.active
    rows_iter = ws.iter_rows(values_only=True)
    header = next(rows_iter, None)
    if not header:
        wb.close()
        return []

    columns = [str(c).strip() if c is not None else "" for c in header]
    out: list[dict[str, str]] = []
    for row in rows_iter:
        if not row or all(v is None or str(v).strip() == "" for v in row):
            continue
        item: dict[str, str] = {}
        for i, col in enumerate(columns):
            if not col:
                continue
            val = row[i] if i < len(row) else None
            item[col] = "" if val is None else str(val).strip()
        if item.get(ID_COLUMN):
            out.append(item)
    wb.close()
    return out


def sync_from_reports(processed: dict) -> dict:
    if not REPORTS_DIR.exists():
        return processed
    for md in REPORTS_DIR.glob("*.md"):
        rid: str | None = None
        m = re.match(r"^(\d+)-", md.stem)
        if m:
            rid = m.group(1)
        else:
            fm = FRONTMATTER_ID.search(md.read_text(encoding="utf-8")[:500])
            if fm:
                rid = fm.group(1)
        if not rid or rid in processed:
            continue
        pdf = md.with_suffix(".pdf")
        processed[rid] = {
            "processed_at": datetime.fromtimestamp(md.stat().st_mtime, timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
            "report_md": str(md.relative_to(ROOT)).replace("\\", "/"),
            "report_pdf": str(pdf.relative_to(ROOT)).replace("\\", "/") if pdf.exists() else None,
            "source": "auto-from-reports-dir",
        }
    return processed


def pending_rows(*, resync: bool = True) -> tuple[Path | None, list[dict], list[dict], dict]:
    xlsx = latest_xlsx()
    if not xlsx:
        return None, [], [], load_processed()

    rows = read_rows(xlsx)
    processed = load_processed()
    if resync:
        processed = sync_from_reports(processed)
        save_processed(processed)

    pending = [r for r in rows if r[ID_COLUMN] not in processed]
    done = [r for r in rows if r[ID_COLUMN] in processed]
    return xlsx, pending, done, processed


def cmd_pending(args: argparse.Namespace) -> int:
    xlsx, pending, done, _ = pending_rows(resync=not args.no_sync)
    if not xlsx:
        print("Нет .xlsx в папке Ответы")
        return 1

    summary = {
        "xlsx": str(xlsx.relative_to(ROOT)).replace("\\", "/"),
        "total_in_export": len(pending) + len(done),
        "pending_count": len(pending),
        "done_count": len(done),
        "pending": pending,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Файл: {xlsx.name}")
        print(f"В экспорте: {summary['total_in_export']} · готово: {len(done)} · новых: {len(pending)}")
        for row in pending:
            print(
                f"  [{row[ID_COLUMN]}] {row.get(TIME_COLUMN, '')} · "
                f"{row.get(NAME_COLUMN, '')} · {row.get('Email', '')}"
            )
        if not pending:
            print("Новых заявок нет.")
    return 0


def cmd_row(args: argparse.Namespace) -> int:
    xlsx = latest_xlsx()
    if not xlsx:
        print("Нет .xlsx в папке Ответы", file=sys.stderr)
        return 1
    for row in read_rows(xlsx):
        if row[ID_COLUMN] == args.response_id:
            payload = json.dumps(row, ensure_ascii=False, indent=2)
            if args.out:
                Path(args.out).write_text(payload + "\n", encoding="utf-8")
                print(args.out)
            else:
                print(payload)
            return 0
    print(f"ID {args.response_id} не найден в {xlsx.name}", file=sys.stderr)
    return 1


def cmd_mark(args: argparse.Namespace) -> int:
    processed = load_processed()
    if args.response_id in processed and not args.force:
        print(f"ID {args.response_id} уже обработан. --force чтобы перезаписать.")
        return 1

    entry = {
        "processed_at": utc_now_iso(),
        "report_md": args.md.replace("\\", "/") if args.md else None,
        "report_pdf": args.pdf.replace("\\", "/") if args.pdf else None,
        "email": args.email,
        "name": args.name,
        "source": "manual-mark",
    }
    processed[args.response_id] = {k: v for k, v in entry.items() if v}
    save_processed(processed)
    print(f"OK: {args.response_id} отмечен как обработанный")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    processed = sync_from_reports(load_processed())
    save_processed(processed)
    xlsx = latest_xlsx()
    print(f"processed.json: {len(processed)} записей")
    if xlsx:
        print(f"latest xlsx: {xlsx.name}")
    if args.json:
        print(json.dumps(processed, ensure_ascii=False, indent=2))
    else:
        for rid, meta in sorted(processed.items(), key=lambda x: x[1].get("processed_at", "")):
            print(f"  {rid} · {meta.get('processed_at', '')} · {meta.get('report_md', '—')}")
    return 0


def cmd_suggest_path(args: argparse.Namespace) -> int:
    md, pdf = report_paths_for(args.response_id, args.name or "client")
    print(
        json.dumps(
            {
                "md": str(md.relative_to(ROOT)).replace("\\", "/"),
                "pdf": str(pdf.relative_to(ROOT)).replace("\\", "/"),
                "filename_base": md.stem,
            },
            ensure_ascii=False,
        )
    )
    return 0


def cmd_pdf(args: argparse.Namespace) -> int:
    from md_to_pdf import md_to_pdf

    md_path = Path(args.md_path)
    if not md_path.is_absolute():
        md_path = ROOT / md_path
    pdf_path = Path(args.pdf_path) if args.pdf_path else md_path.with_suffix(".pdf")
    if not pdf_path.is_absolute():
        pdf_path = ROOT / pdf_path
    if not md_path.exists():
        print(f"Not found: {md_path}", file=sys.stderr)
        return 1
    out = md_to_pdf(md_path, pdf_path)
    print(f"OK: {out} ({out.stat().st_size // 1024} KB)")
    return 0


def main(argv: list[str] | None = None) -> int:
    configure_stdout()
    parser = argparse.ArgumentParser(description="Car2Me: очередь ответов формы")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_pending = sub.add_parser("pending", help="Список необработанных ответов")
    p_pending.add_argument("--json", action="store_true")
    p_pending.add_argument("--no-sync", action="store_true")
    p_pending.set_defaults(func=cmd_pending)

    p_row = sub.add_parser("row", help="Один ответ по ID (JSON)")
    p_row.add_argument("response_id")
    p_row.add_argument("--out", help="Записать JSON в файл")
    p_row.set_defaults(func=cmd_row)

    p_mark = sub.add_parser("mark", help="Отметить ответ обработанным")
    p_mark.add_argument("response_id")
    p_mark.add_argument("--md")
    p_mark.add_argument("--pdf")
    p_mark.add_argument("--email")
    p_mark.add_argument("--name")
    p_mark.add_argument("--force", action="store_true")
    p_mark.set_defaults(func=cmd_mark)

    p_status = sub.add_parser("status", help="Журнал обработанных")
    p_status.add_argument("--json", action="store_true")
    p_status.set_defaults(func=cmd_status)

    p_path = sub.add_parser("suggest-path", help="Пути отчёта по имени клиента")
    p_path.add_argument("response_id")
    p_path.add_argument("--name", default="client")
    p_path.set_defaults(func=cmd_suggest_path)

    p_pdf = sub.add_parser("pdf", help="Markdown → PDF")
    p_pdf.add_argument("md_path")
    p_pdf.add_argument("pdf_path", nargs="?")
    p_pdf.set_defaults(func=cmd_pdf)

    args = parser.parse_args(argv)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ANSWERS_DIR.mkdir(parents=True, exist_ok=True)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
