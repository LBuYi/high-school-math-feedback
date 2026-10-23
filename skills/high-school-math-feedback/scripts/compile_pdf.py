"""Compile trusted XeLaTeX, inspect PDF and render all pages. Human visual review remains pending."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from pypdf import PdfReader


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--kind", required=True, choices=["training", "student_solutions", "retest", "teacher"])
    parser.add_argument("--student", required=True)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--engine", default="xelatex")
    parser.add_argument("--renderer", default="pdftoppm")
    parser.add_argument("--header-left", default="理学优课高中部")
    parser.add_argument("--header-right", default="针对补充训练")
    args = parser.parse_args()
    tex, out = args.tex.resolve(), args.out_dir.resolve()
    if not tex.is_file() or tex.suffix.lower() != ".tex":
        parser.error("Input must be an existing trusted .tex file")
    if not args.student.strip():
        parser.error("--student must not be empty")
    if args.expected_pages is not None and args.expected_pages < 1:
        parser.error("--expected-pages must be positive")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        parser.error("Output directory must be empty or new; use a new version directory")
    engine, renderer = executable(args.engine), executable(args.renderer)
    out.mkdir(parents=True, exist_ok=True)
    report = {"kind": args.kind, "student": args.student, "source": str(tex),
              "automated_status": "failed", "visual_status": "pending", "issues": []}
    report_path = out / "pdf-check-report.json"
    try:
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
