"""Build reviewed high-school math materials from a local batch record."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import subprocess
import sys
from uuid import uuid4


DEFAULT_SKILL = Path(__file__).resolve().parent.parent
PDF_ROLES = {
    "training": "学生训练",
    "student_solutions": "学生解析",
    "retest": "独立复测",
    "teacher": "教师答案",
}
FILENAMES = {
    **{kind: title + ".pdf" for kind, title in PDF_ROLES.items()},
    "feedback": "家长反馈.txt",
    "card": "教师核对卡.md",
}
TEX_ESCAPE = {
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "\\": r"\textbackslash{}",
    "^": r"\textasciicircum{}", "~": r"\textasciitilde{}",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def atomic_write(path, content):
    draft = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        draft.write_text(content, encoding="utf-8")
        os.replace(draft, path)
    finally:
        draft.unlink(missing_ok=True)


@contextmanager
def lock(path):
    try:
        path.mkdir()
    except FileExistsError as exc:
        raise ValueError(f"目录已有运行锁，请核实前一任务状态：{path}") from exc
    try:
        yield
    finally:
        path.rmdir()


def checked_path(root, relative):
    win_path = PureWindowsPath(relative)
    if win_path.drive or win_path.root or "\\" in relative:
        raise ValueError(f"需要项目内的相对路径：{relative}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"文件不存在或超出目录：{relative}")
    return path


def source_file(workspace, item):
    path = checked_path(workspace, item["path"])
    if file_sha(path) != item["sha256"]:
        raise ValueError(f"原件内容与登记不符：{item['path']}")
    return path


def content_sha(question):
    return sha((question["prompt"] + "\n" + question["solution"]).encode("utf-8"))


def escape(text):
    return "".join(TEX_ESCAPE.get(char, char) for char in str(text))


def tex_doc(title, name, body):
    return (
        r"\input{preamble.tex}" + "\n" + r"\begin{document}" + "\n"
        + r"\doctitle{" + escape(title) + "}{" + escape(name) + "}\n"
        + "\n".join(body) + "\n" + r"\end{document}" + "\n"
    )


def answer_block(label, solution):
    return r"\solutionblock{" + escape(label) + "}{解：" + solution + "}"


def exercise_block(number, item, *, retest=False):
    label = "" if retest else ("（" + escape(item["level"]) + "）")
    space = "62mm" if retest else item.get("space", "43mm")
    if not re.fullmatch(r"[1-9][0-9]?mm", space):
        raise ValueError(f"作答区长度无效：{space}")
    return r"\questionwithspace{" + str(number) + "}{" + label + item["prompt"] + "}{" + space + "}"


def teacher_card(student, bank, workspace):
    evidence = student["card"]
    lines = [
        f"# {student['name']}｜教师核对卡", "",
        f"[原答与批改](<{(workspace / evidence['path']).as_posix()}>) · 第{evidence['page']}页",
        "", "## 本轮重点", "", student["focus"], "", "## 作答依据", "",
    ]
    lines.extend(
        f"- 原卷第{qid[1:]}题。{row['response']}。{row['mark']}。{row['process']}。"
        for qid, row in student["answers"].items()
    )
    lines.extend(
        f"- 原卷第{item['question'][1:]}题补充材料。{item['status']}。{item['note']}。 [原件](<{(workspace / item['path']).as_posix()}>)"
        for item in student.get("supplements", [])
    )
    lines.extend(["", "## 练习与复测", ""])
    number = 0
    for group in student["groups"]:
        for qid in group["practice"]:
            number += 1
            item = bank[qid]
            lines.append(f"- 训练第{number}题 {qid}，{item['goal']}。{item['source']}。")
    for number, qid in enumerate(student["retest"], 1):
        item = bank[qid]
        lines.append(f"- 复测第{number}题 {qid}，{item['goal']}。{item['source']}。")
    if student.get("retest_attempts"):
        lines.extend(["", "### 已收到的复测作答", ""])
        for attempt in student["retest_attempts"]:
            lines.append(
                f"- {attempt['date']}，{attempt['question']}。结果 {attempt['answer']}。"
                f"目标步骤 {attempt['step']}。独立性 {attempt['independence']}。"
                f"题面校验值 {attempt['paper_sha256'][:12]}。"
                f" [作答](<{(workspace / attempt['source']['path']).as_posix()}>)"
            )
        assigned = student.get("assigned_retest")
        if assigned:
            received = {
                row["question"] for row in student["retest_attempts"]
                if row["paper_sha256"] == assigned["sha256"]
            }
            missing = [qid for qid in assigned["question_ids"] if qid not in received]
            if missing:
                lines.append("仍待提交的复测题 " + "、".join(missing) + "。")
    lines.extend(["", student["criterion"], "", student["estimated_time"], "",
                  f"教学状态。{student['teaching_status']}",
                  f"发出前审核用时。{student['timing']['before'] or '待记录'}。",
                  f"复测后核对用时。{student['timing']['after'] or '待记录'}。", ""])
    return "\n".join(lines)


def student_documents(record, student, workspace):
    questions, bank = record["exam"]["items"], record["bank"]
    training, solutions = [], []
    number = 0
    for group in student["groups"]:
        original_number = group["original"]
        original = questions[original_number]
        label = "原卷第" + original_number[1:] + "题"
        heading = r"\parttitle{" + escape(group["title"]) + "}"
        training.append(heading)
        training.append(
            r"\originalquestion{" + label + "}{" + original["prompt"]
            + "}{" + student["answers"][original_number].get(
                "student_line_tex", escape(student["answers"][original_number]["student_line"])
            ) + "}"
        )
        if group.get("keypoints"):
            training.append(r"\keypoints{" + group["keypoints"] + "}")
        solutions.extend([heading, answer_block(label, original["solution"])])
        for qid in group["practice"]:
            number += 1
            item = bank[qid]
            training.append(exercise_block(number, item))
            solutions.append(answer_block(f"练习第{number}题", item["solution"]))
    retest = [r"请独立完成，保留必要过程。"]
    retest_answers = [r"\clearpage", r"\parttitle{独立复测答案}"]
    for number, qid in enumerate(student["retest"], 1):
        item = bank[qid]
        retest.append(exercise_block(number, item, retest=True))
        retest_answers.append(answer_block(f"第{number}题", item["solution"]))
    bodies = {
        "training": training, "student_solutions": solutions, "retest": retest,
        "teacher": solutions + retest_answers,
    }
    docs = {kind: tex_doc(title, student["name"], bodies[kind]) for kind, title in PDF_ROLES.items()}
    docs["feedback"] = student["feedback"].strip() + "\n"
    docs["card"] = teacher_card(student, bank, workspace)
    return docs


def collect(record, workspace):
    if record.get("schema_version") != 1:
        raise ValueError("批次记录版本须为 1")
    exam = record["exam"]
    source_file(workspace, exam["paper"])
    source_file(workspace, exam["key"])
    if not exam["items"] or not record["students"]:
        raise ValueError("需要已核对的原题与学生记录")
    bank = record["bank"]
    for qid, item in exam["items"].items():
        if item.get("checked_content_sha256") != content_sha(item):
            raise ValueError(f"共享原题 {qid} 的题面或解答有变化，请重新核验")
    seen_ids, used_cards = set(), set()
    jobs = {}
    pending = [{"student": None, "reason": note} for note in record.get("pending_class", [])]
    for student in record["students"]:
        sid = student["id"]
        if not re.fullmatch(r"[A-Za-z][0-9]{1,8}", sid) or sid.upper() in seen_ids:
            raise ValueError(f"学生编号须唯一，格式如 S01：{sid}")
        seen_ids.add(sid.upper())
        if student["pairing"] != "已配对" or student.get("exam_version") != exam["version"]:
            pending.append({"student": sid, "reason": "卷卡配对或原卷版本待核对"})
            continue
        evidence = student["card"]
        source_file(workspace, evidence)
        identity = evidence["sha256"], evidence["page"]
        if evidence["page"] < 1 or identity in used_cards:
            raise ValueError(f"{sid} 的原答页码无效或相同原答页已登记给另一人")
        used_cards.add(identity)
        pending.extend({"student": sid, "reason": note} for note in student.get("pending", []))
        for item in student.get("supplements", []):
            source_file(workspace, item)
            if item["status"] == "待核对":
                pending.append({"student": sid, "reason": item["note"]})
        if not student["answers"] or not student["groups"] or not student["retest"] or not student["feedback"].strip():
            raise ValueError(f"{sid} 缺已核对作答、练习、复测或家长反馈")
        if set(student["answers"]) - set(exam["items"]):
            raise ValueError(f"{sid} 的作答含未登记的原卷题号")
        training_ids = []
        for group in student["groups"]:
            if group["original"] not in student["answers"] or not group["practice"]:
                raise ValueError(f"{sid} 的某组练习缺原答或练习题")
            training_ids.extend(group["practice"])
        ids = training_ids + student["retest"]
        if len(ids) != len(set(ids)) or any(
            bank[qid].get("checked_content_sha256") != content_sha(bank[qid]) for qid in ids
        ):
            raise ValueError(f"{sid} 练习与复测有重复或尚无验题记录")
        for attempt in student.get("retest_attempts", []):
            source_file(workspace, attempt["source"])
            if attempt["question"] not in bank or not re.fullmatch(r"[0-9a-f]{64}", attempt["paper_sha256"]):
                raise ValueError(f"{sid} 的复测作答缺原复测题或题面校验值")
        for kind, body in student_documents(record, student, workspace).items():
            jobs[f"{sid}/{kind}"] = (student["name"], kind, body)
    return jobs, pending


def previous_manifest(out):
    path = out / "当前交付.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def verify_retest_versions(record, out, current):
    students = [s for s in record["students"] if s.get("assigned_retest") or s.get("retest_attempts")]
    if not students:
        return
    saved = [current, *(
        json.loads(path.read_text(encoding="utf-8")) for path in (out / "清单版本").glob("*.json")
    )]
    for student in students:
        sid = student["id"]
        packets = {
            item["sha256"]: item["question_ids"]
            for manifest in saved
            if manifest.get("batch_id") == record["batch_id"]
            for item in [manifest.get("files", {}).get(f"{sid}/retest", {})]
            if "question_ids" in item
        }
        assigned = student.get("assigned_retest")
        if assigned and packets.get(assigned["sha256"]) != assigned["question_ids"]:
            raise ValueError(f"{sid} 布置记录与生成的复测版本不符")
        for attempt in student.get("retest_attempts", []):
            if attempt["question"] not in packets.get(attempt["paper_sha256"], []):
                raise ValueError(f"{sid} 的复测作答无法关联本人当时使用的题面")


def prepare(record, out, skill, workspace, engine, renderer):
    jobs, pending = collect(record, workspace)
    previous = previous_manifest(out)
    if previous and previous["batch_id"] != record["batch_id"]:
        raise ValueError("输出目录已用于另一批次")
    verify_retest_versions(record, out, previous)
    preamble = (skill / "assets/preamble.tex").read_text(encoding="utf-8")
    compiler = skill / "scripts/compile_pdf.py"
    pdf_version = sha((preamble + file_sha(compiler) + engine + renderer).encode("utf-8"))
    changes, reused = {}, {}
    retest_questions = {student["id"]: student["retest"] for student in record["students"]}
    for key, job in jobs.items():
        name, kind, body = job
        old = previous.get("files", {}).get(key)
        fingerprint = sha((body + (pdf_version if kind in PDF_ROLES else "")).encode("utf-8"))
        if kind == "retest" and old and "question_ids" in old and old["question_ids"] != retest_questions[key.split("/")[0]]:
            changes[key] = (job, fingerprint)
            continue
        if old and old["fingerprint"] == fingerprint:
            path = (out / old["file"]).resolve()
            if path.is_relative_to(out) and path.is_file() and file_sha(path) == old["sha256"]:
                reused[key] = old
                continue
        changes[key] = (job, fingerprint)
    return changes, reused, pending, preamble, compiler


def execute_job(key, value, revision, out, compiler, engine, renderer):
    (name, kind, body), fingerprint = value
    sid, _ = key.split("/")
    folder = revision / sid
    folder.mkdir(parents=True, exist_ok=True)
    filename = FILENAMES[kind]
    result = {"name": name, "role": kind, "fingerprint": fingerprint}
    if kind in PDF_ROLES:
        tex = folder / "源稿" / Path(filename).with_suffix(".tex")
        tex.parent.mkdir(exist_ok=True)
        tex.write_text(body, encoding="utf-8")
        build = folder / "校验" / kind
        command = [
            sys.executable, "-X", "utf8", "-B", str(compiler), str(tex),
            "--out-dir", str(build), "--kind", kind, "--student", name,
            "--expect-a4", "--engine", engine, "--renderer", renderer,
        ]
        done = subprocess.run(command, capture_output=True, encoding="utf-8", timeout=240)
        if done.returncode:
            raise ValueError(f"{sid}/{kind} 编译或自动校验失败。{build}\n{done.stderr}")
        report = build / "pdf-check-report.json"
        checks = json.loads(report.read_text(encoding="utf-8"))
        output = folder / filename
        output.write_bytes((build / filename).read_bytes())
        result.update(pages=checks["page_count"], check=report.relative_to(out).as_posix())
    else:
        output = folder / filename
        output.write_text(body, encoding="utf-8")
    result.update(file=output.relative_to(out).as_posix(), sha256=file_sha(output))
    return key, result


def build(record_path, out, skill, args):
    out.mkdir(parents=True, exist_ok=True)
    with lock(out / ".build-lock"):
        raw = record_path.read_bytes()
        record = json.loads(raw)
        changes, files, pending, preamble, compiler = prepare(
            record, out, skill, args.workspace, args.engine, args.renderer
        )
        revision = None
        if changes:
            revision = out / f"版本-{uuid4().hex[:12]}"
            revision.mkdir()
            for sid in {key.split("/")[0] for key, (job, _) in changes.items() if job[1] in PDF_ROLES}:
                source = revision / sid / "源稿"
                source.mkdir(parents=True)
                (source / "preamble.tex").write_text(preamble, encoding="utf-8")
            with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                tasks = [
                    pool.submit(execute_job, key, value, revision, out, compiler, args.engine, args.renderer)
                    for key, value in changes.items()
                ]
                for task in tasks:
                    key, artifact = task.result()
                    files[key] = artifact
                    print(f"已生成 {key}", file=sys.stderr, flush=True)
        if not files:
            raise ValueError("本批暂无可生成材料，请先核对卷卡与作答。")
        manifest = {
            "schema_version": 1, "batch_id": record["batch_id"], "record_sha256": sha(raw),
            "files": dict(sorted(files.items())), "pending": pending,
            "scope": "本机生成与自动检查，教师布置及复测状态按批次记录",
        }
        for student in record["students"]:
            retest = files.get(f"{student['id']}/retest")
            if retest:
                retest["question_ids"] = student["retest"]
        with lock(record_path.with_name(".record-lock")):
            if sha(record_path.read_bytes()) != manifest["record_sha256"]:
                raise ValueError("生成期间批次记录有变动，请重新运行；上版清单仍有效。")
            snapshot_dir = out / "记录版本"
            snapshot_dir.mkdir(exist_ok=True)
            snapshot = snapshot_dir / (manifest["record_sha256"] + ".json")
            if not snapshot.exists():
                snapshot.write_bytes(raw)
            manifest["record_snapshot"] = snapshot.relative_to(out).as_posix()
            if manifest != previous_manifest(out):
                serialized = json_text(manifest)
                history = out / "清单版本"
                history.mkdir(exist_ok=True)
                atomic_write(history / (sha(serialized.encode("utf-8")) + ".json"), serialized)
                atomic_write(out / "当前交付.json", serialized)
        return {"generated": sorted(changes), "reused": len(files) - len(changes),
                "pending": pending, "manifest": str(out / "当前交付.json")}


def add_page(record_path, workspace, sid, page, question, note):
    page = page.resolve()
    if not page.is_relative_to(workspace) or not page.is_file():
        raise ValueError("请使用项目目录内已有的补交文件")
    digest = file_sha(page)
    with lock(record_path.with_name(".record-lock")):
        record = json.loads(record_path.read_bytes())
        matches = [row for row in record["students"] if row["id"] == sid]
        if len(matches) != 1 or question not in record["exam"]["items"] or not note.strip():
            raise ValueError("请提供有效的学生编号、原卷题号及页说明")
        student = matches[0]
        for row in record["students"]:
            prior = [row.get("card", {}), *row.get("supplements", [])]
            if any(item.get("sha256") == digest for item in prior):
                if row["id"] != sid:
                    raise ValueError("该文件已经登记给另一名学生，请核对归属")
                return {"student": sid, "added": False, "reason": "已有相同原件"}
        student.setdefault("supplements", []).append({
            "path": page.relative_to(workspace).as_posix(), "sha256": digest,
            "question": question, "note": note.strip(), "status": "待核对",
        })
        atomic_write(record_path, json_text(record))
    return {"student": sid, "added": True, "status": "待核对"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "build", "add-page"])
    parser.add_argument("record", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--workspace", type=Path, help="root for relative evidence paths; defaults to the record folder")
    parser.add_argument("--skill", type=Path, default=DEFAULT_SKILL)
    parser.add_argument("--engine", default="xelatex")
    parser.add_argument("--renderer", default="pdftoppm")
    parser.add_argument("--jobs", type=int, default=3, choices=range(1, 9))
    parser.add_argument("--student")
    parser.add_argument("--page", type=Path)
    parser.add_argument("--question")
    parser.add_argument("--note")
    args = parser.parse_args()
    record_path = args.record.resolve()
    args.workspace = (args.workspace or record_path.parent).resolve()
    out = (args.out or record_path.parent / "交付").resolve()
    skill = args.skill.resolve()
    try:
        if args.command == "add-page":
            if not all((args.student, args.page, args.question, args.note)):
                parser.error("add-page 需要 --student、--page、--question、--note")
            result = add_page(record_path, args.workspace, args.student, args.page, args.question, args.note)
        elif args.command == "check":
            record = json.loads(record_path.read_bytes())
            changes, reused, pending, _, _ = prepare(record, out, skill, args.workspace, args.engine, args.renderer)
            result = {"to_build": sorted(changes), "to_reuse": sorted(reused), "pending": pending}
        else:
            result = build(record_path, out, skill, args)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"{exc}\n")
    print(json_text(result), end="")


if __name__ == "__main__":
    main()
