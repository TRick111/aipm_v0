#!/usr/bin/env python3
"""Generate a daily Gmail reply-needed summary report.

This job reads yesterday's inbox messages via gws CLI, classifies whether each
message likely needs a reply, and writes a markdown report into today's Flow
work folder.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple


NO_REPLY_SENDER_HINTS = (
    "no-reply",
    "noreply",
    "donotreply",
    "notification",
    "notifications",
)

NO_REPLY_SUBJECT_HINTS = (
    "receipt",
    "領収書",
    "invoice",
    "請求",
    "newsletter",
    "メルマガ",
    "verification code",
    "認証コード",
    "otp",
    "ワンタイム",
)

NO_REPLY_BODY_HINTS = (
    "本メールは配信専用",
    "本メールは送信専用",
    "ご返信を承ることができません",
    "返信いただいても回答できません",
    "直接返信いただいても回答できません",
)

REPLY_NEEDED_SUBJECT_HINTS = (
    "ご確認",
    "確認お願いします",
    "ご返信",
    "返信",
    "至急",
    "お願い",
    "request",
    "follow up",
    "follow-up",
    "action required",
    "対応",
)


@dataclass
class MailRecord:
    message_id: str
    date: str
    sender: str
    subject: str
    snippet: str
    needs_reply: bool
    reason: str


def run_cmd(args: List[str]) -> str:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(args)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate daily Gmail reply report")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Repository root. If omitted, auto-detected.",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Override today's date (YYYY-MM-DD) for testing.",
    )
    return parser.parse_args()


def detect_project_root(script_path: Path) -> Path:
    for parent in [script_path.parent, *script_path.parents]:
        if (parent / "Flow").exists() and (parent / "Stock").exists():
            return parent
    raise RuntimeError("Could not detect repository root containing Flow/ and Stock/.")


def get_today(override: str | None) -> date:
    if override:
        return datetime.strptime(override, "%Y-%m-%d").date()
    return date.today()


def list_yesterday_messages(start_day: date, end_day: date) -> List[str]:
    query = f'in:inbox after:{start_day.isoformat()} before:{end_day.isoformat()}'
    params = {"userId": "me", "q": query, "maxResults": 200}
    output = run_cmd(
        [
            "gws",
            "gmail",
            "users",
            "messages",
            "list",
            "--params",
            json.dumps(params, ensure_ascii=False),
            "--format",
            "json",
        ]
    )
    payload = json.loads(output or "{}")
    messages = payload.get("messages", []) or []
    return [m.get("id") for m in messages if m.get("id")]


def read_message(message_id: str) -> Dict[str, Any]:
    output = run_cmd(
        [
            "gws",
            "gmail",
            "+read",
            "--id",
            message_id,
            "--headers",
            "--format",
            "json",
        ]
    )
    return json.loads(output or "{}")


def header_value(message: Dict[str, Any], key: str) -> str:
    direct_key = key.lower()
    if direct_key == "from":
        sender = message.get("from")
        if isinstance(sender, dict):
            name = str(sender.get("name", "")).strip()
            email = str(sender.get("email", "")).strip()
            return f"{name} <{email}>".strip() if name else email
        if isinstance(sender, str):
            return sender.strip()
    if direct_key in {"subject", "date"}:
        value = message.get(direct_key)
        if isinstance(value, str):
            return value.strip()

    headers = message.get("headers")
    if isinstance(headers, dict):
        return str(headers.get(key, "")).strip()
    if isinstance(headers, list):
        for item in headers:
            if str(item.get("name", "")).lower() == key.lower():
                return str(item.get("value", "")).strip()
    return ""


def classify_message(sender: str, subject: str, snippet: str) -> Tuple[bool, str]:
    sender_l = sender.lower()
    subject_l = subject.lower()
    snippet_l = snippet.lower()

    if any(hint in sender_l for hint in NO_REPLY_SENDER_HINTS):
        return False, "差出人が自動送信系"
    if any(hint in subject_l for hint in NO_REPLY_SUBJECT_HINTS):
        return False, "件名が通知/案内系"
    if any(hint.lower() in snippet_l for hint in NO_REPLY_BODY_HINTS):
        return False, "本文に返信不可の記載"
    if any(hint in subject_l for hint in REPLY_NEEDED_SUBJECT_HINTS):
        return True, "件名に返信要求の示唆"
    if any(word in snippet_l for word in ("返信", "ご確認", "ご連絡", "please reply", "let me know")):
        return True, "本文スニペットに返信要求の示唆"
    return False, "明確な返信要求が見当たらない"


def to_mail_record(message_id: str, message: Dict[str, Any]) -> MailRecord:
    sender = header_value(message, "From")
    subject = header_value(message, "Subject")
    received_date = header_value(message, "Date")
    raw_snippet = message.get("snippet") or message.get("body_text") or ""
    snippet = " ".join(str(raw_snippet).split())[:240]
    needs_reply, reason = classify_message(sender=sender, subject=subject, snippet=snippet)
    return MailRecord(
        message_id=message_id,
        date=received_date or "-",
        sender=sender or "-",
        subject=subject or "(件名なし)",
        snippet=snippet or "-",
        needs_reply=needs_reply,
        reason=reason,
    )


def render_report(today: date, target_day: date, rows: List[MailRecord]) -> str:
    need = [r for r in rows if r.needs_reply]
    no_need = [r for r in rows if not r.needs_reply]
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"# Gmail返信要否レポート（{target_day.isoformat()}受信分）",
        "",
        f"- 生成日時: {generated}",
        f"- 対象日: {target_day.isoformat()}",
        f"- 総メール数: {len(rows)}",
        f"- 返信必要: {len(need)}",
        f"- 返信不要: {len(no_need)}",
        "",
        "## 判定ロジック（簡易）",
        "- 自動送信系・通知系（no-reply、領収書、メルマガ等）を返信不要として扱う",
        "- 件名/本文に返信依頼の示唆があるものを返信必要として扱う",
        "- 最終判断は手動確認を前提とする",
        "",
        "## 返信必要メール",
    ]

    if not need:
        lines.extend(["- 該当なし", ""])
    else:
        for idx, r in enumerate(need, 1):
            lines.extend(
                [
                    f"### {idx}. {r.subject}",
                    f"- 差出人: {r.sender}",
                    f"- 受信日時: {r.date}",
                    f"- 判定理由: {r.reason}",
                    f"- メッセージID: `{r.message_id}`",
                    f"- スニペット: {r.snippet}",
                    "",
                ]
            )

    lines.append("## 返信不要メール")
    if not no_need:
        lines.append("- 該当なし")
    else:
        lines.append("")
        lines.append("| 件名 | 差出人 | 判定理由 |")
        lines.append("|---|---|---|")
        for r in no_need:
            subject = r.subject.replace("|", " ")
            sender = r.sender.replace("|", " ")
            reason = r.reason.replace("|", " ")
            lines.append(f"| {subject} | {sender} | {reason} |")

    lines.extend(
        [
            "",
            "## 次アクション",
            "- 返信必要メールを確認し、必要に応じて当日対応する",
            "- 判定ミスがあればルールを更新する",
        ]
    )
    return "\n".join(lines) + "\n"


def ensure_output_dir(project_root: Path, today: date) -> Path:
    month = today.strftime("%Y%m")
    day = today.strftime("%Y-%m-%d")
    output_dir = project_root / "Flow" / month / day / "定期実行"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def main() -> int:
    args = parse_args()
    script_path = Path(__file__).resolve()
    project_root = args.project_root or detect_project_root(script_path)
    today = get_today(args.today)
    target_day = today - timedelta(days=1)
    end_day = today

    message_ids = list_yesterday_messages(start_day=target_day, end_day=end_day)
    rows: List[MailRecord] = []
    for message_id in message_ids:
        payload = read_message(message_id)
        rows.append(to_mail_record(message_id=message_id, message=payload))

    report = render_report(today=today, target_day=target_day, rows=rows)
    output_dir = ensure_output_dir(project_root, today)
    output_path = output_dir / f"日次_Gmail返信要否レポート_{today.isoformat()}.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Report generated: {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
