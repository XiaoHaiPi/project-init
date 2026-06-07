from __future__ import annotations

import argparse
import html as html_lib
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence
from urllib.parse import quote


MEMORY_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MEMORY_DIR.parent
EXPERIMENTS_DIR = MEMORY_DIR / "experiments"
EXPERIMENTS_SITE_DIR = MEMORY_DIR / "experiments_4user"
ASSETS_DIR = MEMORY_DIR / "report_assets"


@dataclass
class ExperimentSummary:
    title: str
    stem: str
    page: Path
    source: Path
    run_time: str
    best_iter: str
    total_iter: str
    reference_log: str
    best_miou: str


def escape(text: object) -> str:
    return html_lib.escape(str(text), quote=True)


def generated_at() -> str:
    dt = datetime.now().astimezone()
    zone = dt.strftime("%z")
    if len(zone) == 5:
        zone = f"{zone[:3]}:{zone[3:]}"
    return dt.strftime("%Y-%m-%d %H:%M:%S ") + zone


def href_from(page: Path, target: Path) -> str:
    rel = os.path.relpath(target, start=page.parent).replace(os.sep, "/")
    return quote(rel, safe="/#:.?=&%")


def safe_href(raw: str) -> str:
    href = raw.strip()
    if re.match(r"(?i)^\s*javascript:", href):
        return "#"
    return escape(href)


def split_table_row(line: str) -> list[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    cells: list[str] = []
    buf: list[str] = []
    escaped = False
    for char in text:
        if char == "\\" and not escaped:
            escaped = True
            continue
        if char == "|" and not escaped:
            cells.append("".join(buf).strip())
            buf = []
            continue
        if escaped:
            buf.append("\\")
            escaped = False
        buf.append(char)
    if escaped:
        buf.append("\\")
    cells.append("".join(buf).strip())
    return cells


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def looks_like_table(lines: list[str], index: int) -> bool:
    return (
        index + 1 < len(lines)
        and lines[index].strip().startswith("|")
        and is_table_separator(lines[index + 1])
    )


def align_from_separator(cell: str) -> str:
    text = cell.strip()
    if text.startswith(":") and text.endswith(":"):
        return "center"
    if text.endswith(":"):
        return "right"
    return "left"


class MarkdownRenderer:
    def __init__(self) -> None:
        self.heading_ids: dict[str, int] = {}

    def inline(self, text: str) -> str:
        parts = re.split(r"(`[^`]*`)", text)
        rendered: list[str] = []
        for part in parts:
            if part.startswith("`") and part.endswith("`"):
                rendered.append(f"<code>{escape(part[1:-1])}</code>")
                continue
            segment = escape(part)
            segment = re.sub(
                r"\[([^\]]+)\]\(([^)]+)\)",
                lambda match: (
                    f'<a href="{safe_href(match.group(2))}">'
                    f"{match.group(1)}</a>"
                ),
                segment,
            )
            segment = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", segment)
            segment = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", segment)
            rendered.append(segment)
        return "".join(rendered)

    def heading_id(self, text: str) -> str:
        raw = re.sub(r"`([^`]+)`", r"\1", text)
        raw = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)
        slug = re.sub(r"[^A-Za-z0-9_-]+", "-", raw).strip("-").lower()
        if not slug:
            slug = "section"
        seen = self.heading_ids.get(slug, 0)
        self.heading_ids[slug] = seen + 1
        if seen:
            return f"{slug}-{seen + 1}"
        return slug

    def table(self, lines: list[str], index: int) -> tuple[str, int]:
        headers = split_table_row(lines[index])
        aligns = [align_from_separator(cell) for cell in split_table_row(lines[index + 1])]
        rows: list[list[str]] = []
        i = index + 2
        while i < len(lines) and lines[i].strip().startswith("|"):
            rows.append(split_table_row(lines[i]))
            i += 1

        column_count = len(headers)
        head = []
        for col, header in enumerate(headers):
            align = aligns[col] if col < len(aligns) else "left"
            head.append(
                f'<th scope="col" style="text-align:{align}">{self.inline(header)}</th>'
            )

        body_rows = []
        for row in rows:
            cells = row[:column_count] + [""] * max(0, column_count - len(row))
            rendered_cells = []
            for col, cell in enumerate(cells):
                label = headers[col] if col < len(headers) else "Field"
                align = aligns[col] if col < len(aligns) else "left"
                rendered_cells.append(
                    f'<td data-label="{escape(label)}" style="text-align:{align}">'
                    f"{self.inline(cell)}</td>"
                )
            body_rows.append("<tr>" + "".join(rendered_cells) + "</tr>")

        html = (
            '<div class="table-frame">'
            '<table class="data-table">'
            "<thead><tr>"
            + "".join(head)
            + "</tr></thead><tbody>"
            + "".join(body_rows)
            + "</tbody></table></div>"
        )
        return html, i

    def list_block(self, lines: list[str], index: int, ordered: bool) -> tuple[str, int]:
        pattern = r"^\s*\d+\.\s+" if ordered else r"^\s*[-*]\s+"
        tag = "ol" if ordered else "ul"
        items: list[str] = []
        i = index
        while i < len(lines) and re.match(pattern, lines[i]):
            item = re.sub(pattern, "", lines[i]).strip()
            items.append(f"<li>{self.inline(item)}</li>")
            i += 1
        return f"<{tag}>" + "".join(items) + f"</{tag}>", i

    def fenced_code(self, lines: list[str], index: int) -> tuple[str, int]:
        language = lines[index].strip().strip("`").strip()
        i = index + 1
        code_lines: list[str] = []
        while i < len(lines) and not lines[i].strip().startswith("```"):
            code_lines.append(lines[i])
            i += 1
        if i < len(lines):
            i += 1
        class_name = f' class="language-{escape(language)}"' if language else ""
        return f"<pre><code{class_name}>{escape(chr(10).join(code_lines))}</code></pre>", i

    def paragraph(self, lines: list[str], index: int) -> tuple[str, int]:
        chunks: list[str] = []
        i = index
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                break
            if stripped.startswith("```"):
                break
            if re.match(r"^#{1,6}\s+", stripped):
                break
            if looks_like_table(lines, i):
                break
            if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
                break
            chunks.append(stripped)
            i += 1
        return f"<p>{self.inline(' '.join(chunks))}</p>", i

    def render(self, markdown: str) -> str:
        lines = markdown.splitlines()
        blocks: list[str] = []
        i = 0
        while i < len(lines):
            stripped = lines[i].strip()
            if not stripped:
                i += 1
                continue
            if stripped.startswith("```"):
                block, i = self.fenced_code(lines, i)
                blocks.append(block)
                continue
            if looks_like_table(lines, i):
                block, i = self.table(lines, i)
                blocks.append(block)
                continue
            heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
            if heading:
                level = len(heading.group(1))
                text = heading.group(2).strip()
                hid = self.heading_id(text)
                blocks.append(
                    f'<h{level} id="{escape(hid)}">{self.inline(text)}</h{level}>'
                )
                i += 1
                continue
            if re.match(r"^\s*[-*]\s+", lines[i]):
                block, i = self.list_block(lines, i, ordered=False)
                blocks.append(block)
                continue
            if re.match(r"^\s*\d+\.\s+", lines[i]):
                block, i = self.list_block(lines, i, ordered=True)
                blocks.append(block)
                continue
            block, i = self.paragraph(lines, i)
            blocks.append(block)
        return "\n".join(blocks)


def render_markdown(markdown: str) -> str:
    return MarkdownRenderer().render(markdown)


def extract_title(markdown: str, default: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
    if not match:
        return default
    title = match.group(1).strip()
    if title.lower().startswith("experiment:"):
        title = title.split(":", 1)[1].strip()
    return title or default


def extract_run_info(markdown: str) -> dict[str, str]:
    match = re.search(r"^## Run Info\s*(.*?)(?=^##\s+|\Z)", markdown, flags=re.S | re.M)
    if not match:
        return {}
    info: dict[str, str] = {}
    for line in match.group(1).splitlines():
        row = re.match(r"^-\s+([^:：]+)[:：]\s*(.*)$", line.strip())
        if row:
            info[row.group(1).strip()] = row.group(2).strip()
    return info


def extract_global_miou(markdown: str) -> str:
    lines = markdown.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "### Global Metrics":
            probe = idx + 1
            while probe < len(lines) and not lines[probe].strip():
                probe += 1
            if looks_like_table(lines, probe):
                headers = split_table_row(lines[probe])
                rows: list[list[str]] = []
                j = probe + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    rows.append(split_table_row(lines[j]))
                    j += 1
                for metric in ("mIoU", "IoU"):
                    if metric in headers and rows:
                        pos = headers.index(metric)
                        if pos < len(rows[0]):
                            return rows[0][pos].strip()
    return ""


def run_time_datetime(run_time: str) -> datetime:
    match = re.search(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?", run_time)
    if not match:
        return datetime.min
    raw = match.group(0)
    fmt = "%Y-%m-%d %H:%M:%S" if raw.count(":") == 2 else "%Y-%m-%d %H:%M"
    try:
        return datetime.strptime(raw, fmt)
    except ValueError:
        return datetime.min


def run_time_sort_token(run_time: str) -> str:
    value = run_time_datetime(run_time)
    if value == datetime.min:
        return ""
    return value.strftime("%Y%m%d%H%M%S")


def experiment_run_time_sort_key(summary: ExperimentSummary) -> tuple[datetime, float]:
    return (run_time_datetime(summary.run_time), summary.source.stat().st_mtime)


def experiment_summary_from_markdown(source: Path, markdown: str) -> ExperimentSummary:
    title = extract_title(markdown, source.stem)
    run_info = extract_run_info(markdown)
    best_miou = extract_global_miou(markdown)
    return ExperimentSummary(
        title=title,
        stem=source.stem,
        page=EXPERIMENTS_SITE_DIR / f"{source.stem}.html",
        source=source,
        run_time=run_info.get("Run time", ""),
        best_iter=run_info.get("Best iter", ""),
        total_iter=run_info.get("Total iter", ""),
        reference_log=run_info.get("Reference log", ""),
        best_miou=best_miou,
    )


def experiment_summary_from_source(source: Path) -> ExperimentSummary:
    return experiment_summary_from_markdown(source, source.read_text(encoding="utf-8"))


def collect_experiment_summaries() -> list[ExperimentSummary]:
    return [
        experiment_summary_from_source(source)
        for source in sorted(EXPERIMENTS_DIR.glob("*.md"))
    ]


def count_rows_after_heading(markdown: str, heading: str) -> int:
    lines = markdown.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().lower() == f"## {heading}".lower():
            i = idx + 1
            while i < len(lines):
                if lines[i].strip().startswith("## "):
                    return 0
                if looks_like_table(lines, i):
                    count = 0
                    j = i + 2
                    while j < len(lines) and lines[j].strip().startswith("|"):
                        if any(cell.strip() for cell in split_table_row(lines[j])):
                            count += 1
                        j += 1
                    return count
                i += 1
    return 0


def count_idea_sections(markdown: str) -> dict[str, int]:
    return {
        "Active": count_rows_after_heading(markdown, "Active"),
        "Pending": count_rows_after_heading(markdown, "Pending"),
        "Verified": count_rows_after_heading(markdown, "Verified"),
    }


def collect_idea_counts() -> dict[str, int]:
    source = MEMORY_DIR / "ideas.md"
    return count_idea_sections(source.read_text(encoding="utf-8"))


def page_shell(output_path: Path, title: str, body: str, active: str) -> str:
    home_href = href_from(output_path, MEMORY_DIR / "index_4user.html")
    ideas_href = href_from(output_path, MEMORY_DIR / "ideas_4user.html")
    experiments_href = href_from(output_path, EXPERIMENTS_SITE_DIR / "index.html")
    css_href = href_from(output_path, ASSETS_DIR / "report.css")
    js_href = href_from(output_path, ASSETS_DIR / "report.js")

    def nav_link(label: str, href: str, key: str) -> str:
        current = ' aria-current="page"' if key == active else ""
        return f'<a href="{href}"{current}>{label}</a>'

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="{css_href}">
</head>
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <header class="site-header">
    <div class="site-shell site-nav">
      <a class="brand" href="{home_href}">{PROJECT_ROOT.name} Memory</a>
      <div class="nav-actions">
        <nav aria-label="Report navigation">
          {nav_link("Home", home_href, "home")}
          {nav_link("Ideas", ideas_href, "ideas")}
          {nav_link("Experiments", experiments_href, "experiments")}
        </nav>
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Toggle color theme">
          <span class="theme-toggle-icon" aria-hidden="true"></span>
          <span data-theme-label>Theme</span>
        </button>
      </div>
    </div>
  </header>
  <main id="content" class="site-shell">
{body}
  </main>
  <script src="{js_href}"></script>
</body>
</html>
"""


def stat_card(label: str, value: str, note: str = "") -> str:
    note_html = f"<span>{escape(note)}</span>" if note else ""
    return (
        '<div class="stat-card">'
        f"<b>{escape(value)}</b>"
        f"<small>{escape(label)}</small>"
        f"{note_html}</div>"
    )


def build_ideas(generated: str) -> tuple[Path, dict[str, int]]:
    source = MEMORY_DIR / "ideas.md"
    markdown = source.read_text(encoding="utf-8")
    counts = count_idea_sections(markdown)
    output = MEMORY_DIR / "ideas_4user.html"
    meta = (
        '<section class="report-hero">'
        "<p>Ideas</p>"
        "<h1>Research idea browser</h1>"
        '<div class="meta-line">'
        f'Source: <a href="{href_from(output, source)}"><code>memory/ideas.md</code></a>'
        f" | Generated: {escape(generated)}"
        "</div></section>"
    )
    summary = (
        '<section class="stat-grid" aria-label="Idea summary">'
        + stat_card("Active", str(counts["Active"]))
        + stat_card("Pending", str(counts["Pending"]))
        + stat_card("Verified", str(counts["Verified"]))
        + "</section>"
    )
    content = f'{meta}\n{summary}\n<section class="markdown-body">{render_markdown(markdown)}</section>'
    write_file(output, page_shell(output, "Research Ideas", content, "ideas"))
    return output, counts


def build_experiment_page(source: Path, generated: str) -> ExperimentSummary:
    markdown = source.read_text(encoding="utf-8")
    summary = experiment_summary_from_markdown(source, markdown)
    title = summary.title
    run_info = extract_run_info(markdown)
    output = summary.page
    index_href = href_from(output, EXPERIMENTS_SITE_DIR / "index.html")
    reference_log = summary.reference_log

    meta_items = [
        ("Run time", summary.run_time),
        ("Best iter", summary.best_iter),
        ("Total iter", summary.total_iter),
        ("Best mIoU", summary.best_miou),
        ("Reference log", reference_log),
        ("Reference config", run_info.get("Reference config", "")),
    ]
    stats = "".join(
        stat_card(label, value or "N/A") for label, value in meta_items[:4]
    )
    source_line = (
        '<div class="meta-line">'
        f'<a href="{index_href}">Experiment index</a>'
        f' | Source: <a href="{href_from(output, source)}"><code>{escape(os.path.relpath(source, MEMORY_DIR.parent).replace(os.sep, "/"))}</code></a>'
        f" | Generated: {escape(generated)}"
        "</div>"
    )
    if reference_log:
        source_line = source_line.replace(
            "</div>",
            f' | Log: <code>{escape(reference_log)}</code></div>',
        )

    hero = (
        '<section class="report-hero">'
        "<p>Experiment</p>"
        f"<h1>{escape(title)}</h1>"
        f"{source_line}</section>"
        f'<section class="stat-grid" aria-label="Experiment summary">{stats}</section>'
    )
    content = f'{hero}\n<section class="markdown-body">{render_markdown(markdown)}</section>'
    write_file(output, page_shell(output, title, content, "experiments"))
    return summary


def build_experiments(generated: str) -> list[ExperimentSummary]:
    summaries = []
    EXPERIMENTS_SITE_DIR.mkdir(parents=True, exist_ok=True)
    for source in sorted(EXPERIMENTS_DIR.glob("*.md")):
        summaries.append(build_experiment_page(source, generated))
    return summaries


def build_experiment_index(summaries: list[ExperimentSummary], generated: str) -> Path:
    output = EXPERIMENTS_SITE_DIR / "index.html"
    rows = []
    for item in sorted(summaries, key=experiment_run_time_sort_key, reverse=True):
        rows.append(
            "<tr>"
            f'<td data-label="Experiment"><a href="{href_from(output, item.page)}">{escape(item.title)}</a></td>'
            f'<td data-label="Run time" data-sort-value="{escape(run_time_sort_token(item.run_time))}">{escape(item.run_time or "N/A")}</td>'
            f'<td data-label="Best iter">{escape(item.best_iter or "N/A")}</td>'
            f'<td data-label="Total iter">{escape(item.total_iter or "N/A")}</td>'
            f'<td data-label="Best mIoU">{escape(item.best_miou or "N/A")}</td>'
            f'<td data-label="Reference log"><code>{escape(item.reference_log or "N/A")}</code></td>'
            f'<td data-label="Source"><a href="{href_from(output, item.source)}">Markdown</a></td>'
            "</tr>"
        )
    table = (
        '<div class="table-tools">'
        '<label for="experiment-filter">Filter experiments</label>'
        '<input id="experiment-filter" class="filter-input" type="search" '
        'data-filter-input data-filter-target="#experiments-table" '
        'placeholder="type config, metric, or log path">'
        '<span class="sort-badge">Run time desc</span>'
        "</div>"
        '<div class="table-frame">'
        '<table id="experiments-table" class="data-table" data-default-sort="run-time-desc">'
        "<thead><tr>"
        '<th>Experiment</th><th data-sort-key="run-time">Run time</th><th>Best iter</th>'
        "<th>Total iter</th><th>Best mIoU</th><th>Reference log</th><th>Source</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )
    body = (
        '<section class="report-hero">'
        "<p>Experiments</p>"
        "<h1>Experiment report index</h1>"
        f'<div class="meta-line">Generated: {escape(generated)} | Reports: {len(summaries)}</div>'
        "</section>"
        '<section class="stat-grid" aria-label="Experiment summary">'
        + stat_card("Reports", str(len(summaries)))
        + stat_card("Source folder", "memory/experiments")
        + stat_card("HTML folder", "memory/experiments_4user")
        + "</section>"
        + table
    )
    write_file(output, page_shell(output, "Experiment Reports", body, "experiments"))
    return output


def build_home(
    generated: str, idea_counts: dict[str, int], summaries: list[ExperimentSummary]
) -> Path:
    output = MEMORY_DIR / "index_4user.html"
    ideas_href = href_from(output, MEMORY_DIR / "ideas_4user.html")
    experiments_href = href_from(output, EXPERIMENTS_SITE_DIR / "index.html")
    latest = sorted(summaries, key=lambda row: row.source.stat().st_mtime, reverse=True)[:5]
    latest_rows = []
    for item in latest:
        latest_rows.append(
            "<tr>"
            f'<td data-label="Experiment"><a href="{href_from(output, item.page)}">{escape(item.title)}</a></td>'
            f'<td data-label="Best iter">{escape(item.best_iter or "N/A")}</td>'
            f'<td data-label="Best mIoU">{escape(item.best_miou or "N/A")}</td>'
            f'<td data-label="Run time">{escape(item.run_time or "N/A")}</td>'
            "</tr>"
        )
    latest_table = (
        '<div class="table-frame">'
        '<table class="data-table">'
        "<thead><tr><th>Experiment</th><th>Best iter</th><th>Best mIoU</th><th>Run time</th></tr></thead>"
        "<tbody>"
        + "".join(latest_rows)
        + "</tbody></table></div>"
    )
    body = (
        '<section class="report-hero">'
        "<p>Static reports</p>"
        f"<h1>{PROJECT_ROOT.name} memory browser</h1>"
        f'<div class="meta-line">Generated: {escape(generated)} | Source folder: <code>memory/</code></div>'
        "</section>"
        '<section class="link-grid" aria-label="Report sections">'
        f'<a class="link-card" href="{ideas_href}"><strong>Ideas</strong><span>{idea_counts["Active"]} active, {idea_counts["Pending"]} pending, {idea_counts["Verified"]} verified</span></a>'
        f'<a class="link-card" href="{experiments_href}"><strong>Experiments</strong><span>{len(summaries)} generated reports</span></a>'
        "</section>"
        "<h2>Recently updated experiments</h2>"
        f"{latest_table}"
    )
    write_file(output, page_shell(output, f"{PROJECT_ROOT.name} Memory Browser", body, "home"))
    return output


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def resolve_experiment_source(raw: str) -> Path:
    raw_path = Path(raw)
    candidates: list[Path] = []

    def add_candidate(path: Path) -> None:
        full_path = path if path.is_absolute() else PROJECT_ROOT / path
        if full_path not in candidates:
            candidates.append(full_path)

    if raw_path.suffix.lower() == ".md":
        add_candidate(raw_path)
    elif len(raw_path.parts) == 1:
        stem = raw_path.stem if raw_path.suffix else raw_path.name
        candidates.append(EXPERIMENTS_DIR / f"{stem}.md")
    else:
        add_candidate(raw_path.with_suffix(".md"))
        candidates.append(EXPERIMENTS_DIR / f"{raw_path.stem}.md")

    experiments_root = EXPERIMENTS_DIR.resolve()
    for candidate in candidates:
        source = candidate.resolve()
        if source.exists():
            if source.suffix.lower() != ".md":
                raise SystemExit(f"Experiment source is not Markdown: {source}")
            if source.parent.resolve() != experiments_root:
                raise SystemExit(
                    "Experiment source must be under memory/experiments: "
                    f"{source}"
                )
            return source
    raise SystemExit(f"Experiment Markdown not found: {raw}")


def unique_sources(raw_sources: Sequence[str]) -> list[Path]:
    sources: list[Path] = []
    seen: set[Path] = set()
    for raw in raw_sources:
        source = resolve_experiment_source(raw)
        if source not in seen:
            sources.append(source)
            seen.add(source)
    return sources


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build static HTML views for project memory Markdown records."
    )
    parser.add_argument(
        "--experiments",
        "--experiment",
        nargs="+",
        metavar="SOURCE",
        help=(
            "Render selected experiment Markdown files. SOURCE can be a config stem, "
            "a .py config name, or a path under memory/experiments."
        ),
    )
    parser.add_argument(
        "--ideas",
        action="store_true",
        help="Render memory/ideas_4user.html from memory/ideas.md.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    generated = generated_at()
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    if not args.experiments and not args.ideas:
        ideas_path, idea_counts = build_ideas(generated)
        summaries = build_experiments(generated)
        experiments_index = build_experiment_index(summaries, generated)
        home_path = build_home(generated, idea_counts, summaries)
        print(f"Generated {home_path}")
        print(f"Generated {ideas_path}")
        print(f"Generated {experiments_index}")
        print(f"Generated {len(summaries)} experiment pages")
        return

    experiment_pages: list[Path] = []
    experiments_index: Path | None = None
    if args.experiments:
        for source in unique_sources(args.experiments):
            summary = build_experiment_page(source, generated)
            experiment_pages.append(summary.page)
        summaries = collect_experiment_summaries()
        experiments_index = build_experiment_index(summaries, generated)
    else:
        summaries = collect_experiment_summaries()

    if args.ideas:
        ideas_path, idea_counts = build_ideas(generated)
    else:
        ideas_path = None
        idea_counts = collect_idea_counts()

    home_path = build_home(generated, idea_counts, summaries)
    print(f"Generated {home_path}")
    if ideas_path:
        print(f"Generated {ideas_path}")
    if experiments_index:
        print(f"Generated {experiments_index}")
    for page in experiment_pages:
        print(f"Generated {page}")
    if experiment_pages:
        print(f"Generated {len(experiment_pages)} selected experiment pages")


if __name__ == "__main__":
    main()
