#!/usr/bin/env python3
"""Split the URLs in an AWS Trust & Safety trademark notice into
with-phone-number and without-phone-number groups.

Usage: python3 -I split_urls.py < notice.txt

Reads the pasted notice from stdin. Prints plain text sections:
case ID, report count, marks, each URL group, phone numbers, flags.
"""
import re
import sys

PHONE = re.compile(r"(?<!\d)(?:1-?)?(\d{3})-(\d{3})-(\d{4})(?!\d)")
MARK = re.compile(r"using trademark\s+(.+?)\s+without authorization", re.I)
CASE = re.compile(r"Case\s*(?:ID|Number)\s*:?\s*([A-Za-z0-9-]+)", re.I)
REPORT_SPLIT = re.compile(r"^---\s*Report\s+(\d+)\s*---\s*$", re.M)
SITE = re.compile(r"Infringing Site:\s*(\S+)")
URL_LINE = re.compile(r"^(https?://\S+)$", re.M)


def refang(url):
    url = url.replace("hxxp", "http").replace("[://]", "://")
    url = url.replace("[.]", ".").replace("[:]", ":")
    return url


def normalize(url):
    url = refang(url.strip())
    if not re.match(r"https?://", url):
        url = "http://" + url
    return url


def kind(url):
    path = url.split("://", 1)[1].split("/", 1)[-1]
    if path.startswith("unanswered/"):
        return "unanswered"
    if path.startswith("profile/"):
        return "profile"
    if "/answer/" in path:
        return "answer"
    return "question"


def phones(url):
    slug = url.split("://", 1)[1]
    return sorted({"{}-{}-{}".format(*m.groups()) for m in PHONE.finditer(slug)})


def main():
    text = sys.stdin.read()
    case = CASE.search(text)
    parts = REPORT_SPLIT.split(text)
    reports = []  # (number, url, mark)
    for i in range(1, len(parts), 2):
        body = parts[i + 1]
        site = SITE.search(body)
        mark = MARK.search(body)
        if site:
            reports.append((int(parts[i]), normalize(site.group(1)),
                            mark.group(1).strip() if mark else "?"))
    header = URL_LINE.findall(text)

    seen, ordered, marks = set(), [], {}
    for _, url, mark in reports:
        marks.setdefault(url, mark)
        if url not in seen:
            seen.add(url)
            ordered.append(url)
    missing_from_reports = [u for u in dict.fromkeys(header) if u not in seen]
    if not reports:
        ordered = list(dict.fromkeys(header))

    with_phone = [u for u in ordered if phones(u)]
    no_phone = [u for u in ordered if not phones(u)]

    print("CASE: " + (case.group(1) if case else "not found"))
    print(f"REPORTS: {len(reports)}  UNIQUE URLS: {len(ordered)}")
    print("MARKS: " + ", ".join(sorted({m for m in marks.values()})))
    if len(reports) != len(ordered):
        print(f"NOTE: {len(reports) - len(ordered)} duplicate report(s)")
    if missing_from_reports:
        print("NOTE: URLs in the header but not in any report:")
        for u in missing_from_reports:
            print("  " + u)

    for title, group in (("WITH PHONE NUMBER", with_phone),
                         ("WITHOUT PHONE NUMBER", no_phone)):
        print(f"\n== {title} ({len(group)}) ==")
        for u in group:
            tag = kind(u)
            nums = ",".join(phones(u))
            print(f"[{tag}] {u}" + (f"  <{nums}>" if nums else ""))

    nums = sorted({p for u in ordered for p in phones(u)})
    print(f"\n== PHONE NUMBERS ({len(nums)}) ==")
    for n in nums:
        print(n)

    profiles = [u for u in ordered if kind(u) == "profile"]
    to_check = [u for u in ordered if kind(u) in ("answer", "question")]
    print(f"\n== PROFILES, suspend ({len(profiles)}) ==")
    for u in profiles:
        print(u)
    print(f"\n== ANSWER/QUESTION PAGES, check for fake support numbers ({len(to_check)}) ==")
    for u in to_check:
        print(u)


if __name__ == "__main__":
    main()
