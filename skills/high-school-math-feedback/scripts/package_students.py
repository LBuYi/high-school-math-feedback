"""Package reviewed materials for teacher handoff or one student's initial assignment."""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path, PureWindowsPath

from pypdf import PdfReader


SUFFIXES = {"training": "学生训练.pdf", "student_solutions": "训练解析.pdf",
            "feedback": "学习反馈.txt", "retest": "独立复测.pdf"}


def checked_name(value):
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("Student name must be a nonempty, trimmed string")
    if re.search(r'[<>:"/\\|?*\x00-\x1f]', value) or value.endswith((".", " ")):
        raise ValueError(f"Unsafe student name: {value!r}")
    if value in (".", "..") or re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", value, re.I):
        raise ValueError(f"Reserved student name: {value!r}")
    return value


def read_source(root, value, extension):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Source paths must be nonempty strings")
    win_path = PureWindowsPath(value)
    if Path(value).is_absolute() or win_path.drive or win_path.root or "\\" in value:
        raise ValueError("Use relative paths with forward slashes inside the manifest folder")
    path = (root / value).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Missing source or path outside manifest folder: {value}")
    if path.suffix.lower() != extension:
        raise ValueError(f"Wrong source extension: {value}")
    payload = path.read_bytes()
    if extension == ".pdf":
        reader = PdfReader(io.BytesIO(payload), strict=True)
        if reader.is_encrypted or not reader.pages:
            raise ValueError(f"Unreadable or empty PDF: {value}")
    elif not payload.decode("utf-8-sig").strip():
        raise ValueError(f"Empty feedback: {value}")
    return payload


def package(manifest_path, output, include_retest=False, *, assignment_for=None):
    if assignment_for is not None:
        assignment_for = checked_name(assignment_for)
        if include_retest:
            raise ValueError("Package the retest separately from the initial assignment.")
    manifest_path, output = Path(manifest_path).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    if output.suffix.lower() != ".zip":
        raise ValueError("Output must end in .zip")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    students = manifest.get("students")
    if not isinstance(students, list) or not students:
        raise ValueError("Manifest needs a nonempty students array")
    root, names, entries = manifest_path.parent, set(), {}
    kinds = ["training", "student_solutions", "feedback"]
    if assignment_for is not None:
        kinds = ["training"]
    elif include_retest:
        kinds.append("retest")
    for student in students:
        if not isinstance(student, dict):
            raise ValueError("Each student must be an object")
        unknown = set(student) - ({"name"} | set(SUFFIXES))
        if unknown:
            raise ValueError(f"Unsupported student fields: {sorted(unknown)}")
        name = checked_name(student.get("name"))
        if name.casefold() in names:
            raise ValueError(f"Duplicate student name: {name}")
        names.add(name.casefold())
        if assignment_for is not None and name != assignment_for:
            continue
        for kind in kinds:
            if kind not in student:
                raise ValueError(f"{name}: missing {kind}")
            suffix = SUFFIXES[kind]
            entry = f"{name}/{name}_{suffix}"
            entries[entry] = read_source(root, student[kind], Path(suffix).suffix)
    if not entries:
        raise ValueError(f"Student not found in the manifest: {assignment_for!r}")
    output.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            created = True
            for entry, payload in entries.items():
                archive.writestr(entry, payload)
        with zipfile.ZipFile(output) as archive:
            if archive.testzip() is not None or set(archive.namelist()) != set(entries):
                raise RuntimeError("ZIP integrity or file list mismatch")
            if len(archive.namelist()) != len(entries):
                raise RuntimeError("ZIP contains duplicate entries")
            for entry, original in entries.items():
                if hashlib.sha256(archive.read(entry)).digest() != hashlib.sha256(original).digest():
                    raise RuntimeError(f"ZIP content mismatch: {entry}")
    except Exception:
        if created:
            output.unlink(missing_ok=True)
        raise
    report = {"archive": str(output), "students": 1 if assignment_for is not None else len(students),
              "files": len(entries), "include_retest": include_retest, "bytes": output.stat().st_size,
              "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "integrity": "passed"}
    if assignment_for is not None:
        report["assignment_for"] = assignment_for
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--include-retest", action="store_true")
    mode.add_argument("--assignment-for", metavar="STUDENT", help="Pack only this student's training PDF.")
    args = parser.parse_args()
    report = package(args.manifest, args.output, args.include_retest, assignment_for=args.assignment_for)
    print(json.dumps(report, ensure_ascii=False, indent=2))
