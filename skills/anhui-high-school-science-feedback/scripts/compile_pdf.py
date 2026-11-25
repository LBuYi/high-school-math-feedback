"""Compile trusted XeLaTeX or plain UTF-8 family feedback and inspect rendered PDF pages."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import DictionaryObject


COMPLETE_FEEDBACK_SECTIONS = {
    "training": ("原错题", "知识梳理", "方法小结", "同类练习"),
    "student_solutions": ("原错题", "知识点", "原题解答", "同类练习解析", "方法回顾"),
}

TEX_TEXT_ESCAPES = str.maketrans({
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "&": r"\&",
    "^": r"\textasciicircum{}",
    "~": r"\textasciitilde{}",
    "'": r"\textquotesingle{}",
    '"': r"\textquotedbl{}",
    "-": "{-}",
    "\x60": r"\textasciigrave{}",
})


def family_tex(body, student, header_left, header_right):
    template = Path(__file__).resolve().parents[1] / "assets" / "preamble.tex"
    paragraphs = re.split(r"\n[ \t]*\n", body.strip())
    lines = [
        template.read_text(encoding="utf-8").rstrip(),
        r"\renewcommand{\printheaderleft}{" + header_left.translate(TEX_TEXT_ESCAPES) + "}",
        r"\renewcommand{\printheaderright}{" + header_right.translate(TEX_TEXT_ESCAPES) + "}",
        r"\begin{document}",
        r"\doctitle{家长反馈}{" + student.translate(TEX_TEXT_ESCAPES) + "}",
    ]
    for paragraph in paragraphs:
        if paragraph.strip():
            lines.append(" ".join(paragraph.splitlines()).translate(TEX_TEXT_ESCAPES) + r"\par")
    return "\n".join([*lines, r"\end{document}", ""])


def family_text_matches(pages, body, student, header_left, header_right):
    header = "".join((header_left + header_right).split())
    title = "家长反馈" + "".join(student.split())
    body_pages = []
    for index, page in enumerate(pages, 1):
        content = "".join(page.split()).removeprefix(header).removesuffix(str(index))
        if index == 1:
            content = content.removeprefix(title)
        body_pages.append(content)
    return "".join(body_pages) == "".join(body.split())


def check_complete_sections(pages, kind):
    expected = COMPLETE_FEEDBACK_SECTIONS.get(kind)
    if expected is None:
        return []
    groups = []
    for page in pages:
        for line in page.splitlines():
            heading = "".join(line.split())
            if kind == "student_solutions" and heading == "知识点与错处":
                heading = "知识点"
            if heading == expected[0]:
                groups.append([heading])
            elif groups and heading in expected:
                groups[-1].append(heading)
    if not groups:
        return [f"Missing section for complete {kind}: {expected[0]}"]
    issues = []
    for index, headings in enumerate(groups, 1):
        if tuple(headings) != expected:
            issues.append(f"Complete {kind}, group {index}: expected {', '.join(expected)}; found {', '.join(headings)}")
    return issues


def executable(value):
    found = shutil.which(value)
    if found:
        return found
    path = Path(value).expanduser()
    if path.is_file():
        return str(path.resolve())
    raise FileNotFoundError(f"Executable not found: {value}")


def run_logged(command, cwd, log_path):
    result = subprocess.run(command, cwd=cwd, capture_output=True, timeout=180, check=False)
    log_path.write_bytes(result.stdout + b"\n" + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}); inspect {log_path}")


def inspect_font_resources(resources, visited):
    """Yield font names and embedding status, including within imported PDF forms."""
    resources = resources.get_object()
    if id(resources) in visited:
        return
    visited.add(id(resources))
    fonts = resources.get("/Font", DictionaryObject()).get_object()
    for tag, reference in fonts.items():
        font = reference.get_object()
        name = str(font.get("/BaseFont", tag))
        if font.get("/Subtype") == "/Type3":
            yield name, bool(font.get("/CharProcs"))
            continue
        descendant_fonts = font.get("/DescendantFonts")
        if descendant_fonts:
            font = descendant_fonts.get_object()[0].get_object()
        descriptor = font.get("/FontDescriptor")
        embedded = descriptor is not None and any(
            key in descriptor.get_object() for key in ("/FontFile", "/FontFile2", "/FontFile3")
        )
        yield name, embedded
    xobjects = resources.get("/XObject", DictionaryObject()).get_object()
    for reference in xobjects.values():
        form = reference.get_object()
        if form.get("/Subtype") == "/Form" and "/Resources" in form:
            yield from inspect_font_resources(form["/Resources"], visited)


def inspect_print_layout(reader, expect_a4=False):
    """Check effective page dimensions and the fonts referenced by page/form resources."""
    a4_width = 210 * 72 / 25.4
    a4_height = 297 * 72 / 25.4
    sizes = []
    fonts = {}
    issues = []
    for index, page in enumerate(reader.pages, 1):
        # The visible box and rotation determine the layout a reader displays.
        box = page.cropbox
        width = float(box.width) * page.user_unit
        height = float(box.height) * page.user_unit
        if page.rotation % 180:
            width, height = height, width
        sizes.append([round(width, 2), round(height, 2)])
        if expect_a4 and (abs(width - a4_width) > 1 or abs(height - a4_height) > 1):
            issues.append(f"Page {index}: expected A4 portrait, found {width:.2f} x {height:.2f} pt")
        if "/Resources" in page:
            for name, embedded in inspect_font_resources(page["/Resources"], set()):
                fonts[name] = fonts.get(name, True) and embedded
    issues.extend(f"Font not embedded: {name}" for name in sorted(fonts) if not fonts[name])
    return {"visible_page_sizes_pt": sizes, "font_resources": dict(sorted(fonts.items()))}, issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="trusted .tex or UTF-8 .txt for family_feedback")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--kind", required=True,
                        choices=["training", "student_solutions", "retest", "teacher", "family_feedback"])
    parser.add_argument("--student", required=True)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--complete-feedback", action="store_true",
                        help="check the required headings for a complete training or student solutions PDF")
    parser.add_argument("--expect-a4", action="store_true", help="require a portrait A4 visible page on every page")
    parser.add_argument("--engine", default="xelatex")
    parser.add_argument("--renderer", default="pdftoppm")
    parser.add_argument("--header-left", default="理学优课高中部")
    parser.add_argument("--header-right")
    args = parser.parse_args()
    source, out = args.source.resolve(), args.out_dir.resolve()
    is_family = args.kind == "family_feedback"
    suffix = ".txt" if is_family else ".tex"
    if not source.is_file() or source.suffix.lower() != suffix:
        parser.error(f"Input must be an existing {suffix} file")
    body = None
    if is_family:
        body = source.read_text(encoding="utf-8-sig")
        if not body.strip():
            parser.error("Family feedback text must not be empty")
    if args.header_right is None:
        args.header_right = "家长反馈" if is_family else "针对补充训练"
    if not args.student.strip():
        parser.error("--student must not be empty")
    if args.expected_pages is not None and args.expected_pages < 1:
        parser.error("--expected-pages must be positive")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        parser.error("Output directory must be empty or new; use a new version directory")
    engine, renderer = executable(args.engine), executable(args.renderer)
    out.mkdir(parents=True, exist_ok=True)
    report = {"kind": args.kind, "student": args.student, "source": str(source),
              "automated_status": "failed", "visual_status": "pending", "issues": []}
    report_path = out / "pdf-check-report.json"
    try:
        tex = source
        if is_family:
            tex = out / f"{source.stem}.tex"
            tex.write_text(family_tex(body, args.student, args.header_left, args.header_right), encoding="utf-8")
        command = [engine, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
                   "-file-line-error", f"-output-directory={out}", str(tex)]
        for number in (1, 2):
            print(f"Compiling pass {number} ...", flush=True)
            run_logged(command, tex.parent, out / f"compile-pass-{number}.txt")
        pdf = out / f"{tex.stem}.pdf"
        if not pdf.is_file() or pdf.stat().st_size == 0:
            raise RuntimeError("Compiler did not produce a nonempty PDF")
        reader = PdfReader(str(pdf), strict=True)
        if reader.is_encrypted:
            raise RuntimeError("Encrypted output cannot be reviewed")
        pages = [page.extract_text() or "" for page in reader.pages]
        if not pages:
            raise RuntimeError("PDF has no pages")
        report.update({"pdf": str(pdf), "page_count": len(pages)})
        report["print_layout"], layout_issues = inspect_print_layout(reader, args.expect_a4)
        report["issues"].extend(layout_issues)
        if args.expected_pages is not None and len(pages) != args.expected_pages:
            report["issues"].append(f"Expected {args.expected_pages} pages, found {len(pages)}")
        for index, page in enumerate(pages, 1):
            compact = re.sub(r"\s+", "", page)
            for header in (args.header_left, args.header_right):
                if re.sub(r"\s+", "", header) not in compact:
                    report["issues"].append(f"Page {index}: missing header {header}")
        text = "\n".join(pages)
        compact = re.sub(r"\s+", "", text)
        if re.sub(r"\s+", "", args.student) not in compact:
            report["issues"].append("Student name not found in extracted text")
        if is_family:
            matches = family_text_matches(pages, body, args.student, args.header_left, args.header_right)
            report["family_feedback_matches_source"] = matches
            if not matches:
                report["issues"].append("Family PDF body differs from the source TXT")
        if args.complete_feedback:
            report["issues"].extend(check_complete_sections(pages, args.kind))
        if args.kind in ("training", "student_solutions"):
            headings = {"".join(line.split()) for page in pages for line in page.splitlines()}
            for heading in ("原答摘录", "知识点与原答", "原题可核读范围与原答"):
                if heading in headings:
                    report["issues"].append(f"Student PDF contains a teacher-only section: {heading}")
        if args.kind != "teacher":
            for term in ("错因假设", "题源映射", "教师核对", "AI生成", "审核记录", "SymPy"):
                if term in compact:
                    report["issues"].append(f"Student-facing content contains internal phrase: {term}")
        if args.kind == "student_solutions" and "复测" in compact:
            report["issues"].append("Student training solutions mention retest; check for answer leakage")
        latex_log = (out / f"{tex.stem}.log").read_text(encoding="utf-8", errors="replace")
        report["layout_warnings"] = [line for line in latex_log.splitlines()
                                     if re.search(r"Overfull \\[hv]box|Missing character:", line)]
        if report["layout_warnings"]:
            report["issues"].append("LaTeX overflow or missing glyphs require repair")
        render_dir = out / "pages"
        render_dir.mkdir()
        print(f"Rendering {len(pages)} pages ...", flush=True)
        run_logged([renderer, "-png", "-scale-to", "1800", str(pdf), str(render_dir / "page")],
                   tex.parent, out / "render-log.txt")
        images = sorted(render_dir.glob("page-*.png"))
        if len(images) != len(pages) or any(image.stat().st_size == 0 for image in images):
            report["issues"].append("Rendered page count/size does not match PDF")
        report["page_images"] = [str(image) for image in images]
        if report["issues"]:
            raise RuntimeError("Automatic checks need repair; see pdf-check-report.json")
        report["automated_status"] = "passed"
    except Exception as exc:
        report["error"] = str(exc)
        raise
    finally:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "pdf": report["pdf"],
                      "automated_status": "passed", "visual_status": "pending"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
