#!/usr/bin/env python3
"""
Core Dataset 2 Generator: Primary Qualitative Data (Context & Richness)

Generates synthetic, anonymized qualitative data for the topic:
"Leveraging Machine Learning to Examine Innovation Adoption and Constraints in Nigerian SMEs: Implications for Performance and Growth."

Outputs under the dataset root:
- participants/participants.csv
- interviews/*.txt + metadata/*.json
- fgds/*.txt + metadata/*.json
- codebook/codebook.json + codebook.csv
- coding/*.json (coded segments linking excerpts to code IDs)
- memos/*.txt (analytic memos per interview and per FGD)
- consent/*.json (consent summaries per interviewee)
- logs/generation_log.json
- core_dataset_2.zip (archive of the dataset for easy download)

This script uses only the Python standard library.
"""
from __future__ import annotations

import csv
import json
import os
import random
import re
import shutil
import string
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

DATASET_ROOT = Path(__file__).resolve().parent
PARTICIPANTS_DIR = DATASET_ROOT / "participants"
INTERVIEWS_DIR = DATASET_ROOT / "interviews"
INTERVIEWS_META_DIR = INTERVIEWS_DIR / "metadata"
FGDS_DIR = DATASET_ROOT / "fgds"
FGDS_META_DIR = FGDS_DIR / "metadata"
CODEBOOK_DIR = DATASET_ROOT / "codebook"
CODING_DIR = DATASET_ROOT / "coding"
MEMOS_DIR = DATASET_ROOT / "memos"
CONSENT_DIR = DATASET_ROOT / "consent"
LOGS_DIR = DATASET_ROOT / "logs"

RANDOM_SEED = 43127

# Configuration
NUM_INTERVIEWS = 26  # between 20-30
NUM_FGDS = 5         # between 4-6
FGD_PARTICIPANTS_RANGE = (6, 8)  # per group

SECTORS = [
    "Technology",
    "Agribusiness",
    "Retail",
    "Manufacturing",
    "Services",
    "Healthcare",
    "Logistics",
    "Hospitality",
]

REGIONS = [
    "Lagos",
    "Abuja",
    "Kano",
    "Port Harcourt",
    "Enugu",
    "Ibadan",
    "Kaduna",
    "Benin City",
    "Aba",
    "Maiduguri",
]

SIZES = ["Micro", "Small", "Medium"]
GENDERS = ["Female", "Male"]
YEARS_IN_BUSINESS_RANGE = (2, 25)

TECHNOLOGIES = [
    "Point-of-Sale (POS)",
    "WhatsApp Business",
    "E-commerce platform",
    "Inventory management software",
    "Solar power system",
    "Cloud accounting",
    "Customer Relationship Management (CRM)",
    "Mobile money",
    "Data analytics dashboard",
    "Basic machine learning forecast",
    "IoT cold-chain sensor",
    "Digital marketing tools",
]

BARRIERS = [
    "Power outages",
    "Broadband cost",
    "Unreliable internet",
    "FX volatility",
    "Policy uncertainty",
    "Import restrictions",
    "Skills gap",
    "Cybersecurity concerns",
    "Trust in vendors",
    "Access to finance",
    "High generator cost",
]

OUTCOMES = [
    "Sales increase",
    "Cost reduction",
    "Customer retention",
    "Operational efficiency",
    "Reduced stock-outs",
    "Faster order fulfillment",
    "Better cashflow visibility",
]

STRATEGIES = [
    "Pilot then scale",
    "Peer learning",
    "Staff training",
    "Vendor negotiation",
    "Alternative power",
    "Bundle financing",
    "Partnership with fintech",
    "Use interns/NYSC",
]

POLICY_TOPICS = [
    "Tax compliance",
    "Regulatory licenses",
    "CBN cashless policy",
    "Data protection",
    "Import duty waivers",
    "Government grants",
]

# Codebook hierarchy
CODEBOOK = {
    "Drivers": {
        "Market_Pressure": {},
        "Customer_Demand": {},
        "Competition": {},
        "Efficiency_Gains": {},
    },
    "Barriers": {
        "Power_Outage": {},
        "Broadband_Cost": {},
        "Internet_Reliability": {},
        "FX_Volatility": {},
        "Policy_Uncertainty": {},
        "Skills_Gap": {},
        "Financing": {},
        "Cybersecurity_Trust": {},
    },
    "Capabilities": {
        "Digital_Skills": {},
        "Data_Analytics": {},
        "IT_Support": {},
    },
    "Strategies": {
        "Pilot_Scale": {},
        "Training": {},
        "Partnerships": {},
        "Alternative_Power": {},
        "Vendor_Management": {},
        "Financing_Options": {},
    },
    "Outcomes": {
        "Sales_Increase": {},
        "Cost_Reduction": {},
        "Customer_Retention": {},
        "Operational_Efficiency": {},
        "Stockout_Reduction": {},
        "Faster_Fulfillment": {},
        "Cashflow_Visibility": {},
    },
    "Policy_Environment": {
        "Tax": {},
        "Licensing": {},
        "Cashless": {},
        "Data_Privacy": {},
        "Import_Duty": {},
        "Grants_Programs": {},
    },
}

# Utility text pools
FIRST_NAMES = [
    "Amina", "Chinedu", "Ifeoma", "Tunde", "Halima", "Seyi", "Ngozi", "Emeka",
    "Kehinde", "Hauwa", "Bisi", "Funmi", "Maryam", "Ibrahim", "Fatima", "Zainab",
    "Yemi", "Tokunbo", "Ada", "Hassan", "Kola", "Sade", "Kunle", "Blessing",
]
LAST_NAMES = [
    "Olawale", "Okeke", "Bello", "Mohammed", "Eze", "Afolayan", "Ojo", "Balogun",
    "Danladi", "Okon", "Ekanem", "Adewale", "Aliyu", "Okoro", "Umar", "Ogundipe",
]

QUOTES_TEMPLATES = [
    "We first tried {tech} in 20{year_last}. At the time, {driver} mattered because {reason}.",
    "The biggest issue was {barrier}. Without steady power in {region}, costs kept rising.",
    "Our sales changed after {tech}—we saw {outcome} within {months} months.",
    "Policy-wise, {policy} shaped our move. We adjusted by {strategy}.",
    "Data helped; even a {ml} gave us clearer demand patterns during {season}.",
]

REASONS = [
    "customers were asking for digital receipts",
    "competitors moved online and took some market share",
    "manual reconciliation wasted staff time",
    "we needed visibility across branches",
    "we wanted to stop stock-outs during festive seasons",
]

SEASONS = ["Sallah", "Christmas", "Back-to-school", "New Year", "Easter"]

ML_VARIANTS = [
    "basic ML forecast",
    "simple regression model",
    "Excel-based trendline",
    "moving-average model",
    "low-code AutoML",
]

INTRO_TEMPLATES = [
    "I manage a {size} {sector} business in {region}. We started in {start_year} and currently employ {employees} people. Our main products revolve around {product}.",
    "I own a {size} enterprise in {region} operating within {sector}. We've been around since {start_year}, serving mostly {customers}.",
]

PRODUCTS = [
    "packaged grains and oil",
    "pharmaceutical retail",
    "tailored fashion items",
    "local logistics and dispatch",
    "light manufacturing of plastics",
    "software consulting and training",
    "restaurant and outdoor catering",
    "solar installation and maintenance",
]

CUSTOMERS = [
    "walk-in customers",
    "wholesale buyers",
    "SMEs across Lagos and Ogun",
    "schools and clinics",
    "online shoppers on Instagram",
]

PARAGRAPH_FILLERS = [
    "At first, staff pushed back, worrying the new system might expose mistakes. We ran a hands-on demo and set clear SOPs.",
    "Connectivity was patchy. We configured offline modes so work didn't stop during outages.",
    "Cashflow was tight. We phased licensing costs and negotiated quarterly payments.",
    "Training interns helped us build internal champions. It reduced dependence on vendors.",
    "We tracked KPIs like order cycle time, stock variance, and customer repeat rate.",
]

FGD_OPENERS = [
    "Moderator: Let's start with the biggest constraints to adopting digital tools in your sector.",
    "Moderator: How has policy or regulation helped or hindered your adoption journey?",
    "Moderator: What practical strategies have actually worked for you?",
]

FGD_PROBES = [
    "And how did you pay for it—own funds, loans, or vendor financing?",
    "Did alternative power (solar/inverter) change the cost-benefit?",
    "Which training or support made the most difference?",
]

FGD_CROWD_REACTIONS = [
    "[Murmurs of agreement]",
    "[Laughter]",
    "[Multiple participants nod]",
    "[Short pause]",
]


def ensure_dirs() -> None:
    for d in [
        PARTICIPANTS_DIR,
        INTERVIEWS_DIR,
        INTERVIEWS_META_DIR,
        FGDS_DIR,
        FGDS_META_DIR,
        CODEBOOK_DIR,
        CODING_DIR,
        MEMOS_DIR,
        CONSENT_DIR,
        LOGS_DIR,
    ]:
        d.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def random_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def choose_tech_stack() -> List[str]:
    # 2-4 technologies, include at least one analytics-ish tool 50% of the time
    k = random.randint(2, 4)
    techs = random.sample(TECHNOLOGIES, k=k)
    if not any("analytics" in t.lower() or "machine" in t.lower() for t in techs):
        if random.random() < 0.5:
            techs.append(random.choice([t for t in TECHNOLOGIES if "analytics" in t.lower() or "machine" in t.lower()]))
    return list(dict.fromkeys(techs))


def generate_participants(n: int) -> List[Dict[str, Any]]:
    participants: List[Dict[str, Any]] = []
    for idx in range(1, n + 1):
        sector = random.choice(SECTORS)
        size = random.choices(SIZES, weights=[0.5, 0.35, 0.15])[0]
        region = random.choice(REGIONS)
        gender = random.choice(GENDERS)
        years = random.randint(*YEARS_IN_BUSINESS_RANGE)
        start_year = datetime.now().year - years
        employees = {
            "Micro": random.randint(3, 9),
            "Small": random.randint(10, 49),
            "Medium": random.randint(50, 199),
        }[size]
        techs = choose_tech_stack()
        adoption_level = random.choices(["Low", "Medium", "High"], weights=[0.35, 0.45, 0.2])[0]
        barriers = ", ".join(random.sample(BARRIERS, k=random.randint(2, 4)))
        outcomes = ", ".join(random.sample(OUTCOMES, k=random.randint(1, 3)))
        pid = f"INT_{idx:03d}"
        participants.append({
            "participant_id": pid,
            "pseudonym": random_name(),
            "sector": sector,
            "size": size,
            "region": region,
            "gender": gender,
            "years_in_business": years,
            "start_year": start_year,
            "employees": employees,
            "adoption_level": adoption_level,
            "technologies": "; ".join(techs),
            "primary_barriers": barriers,
            "reported_outcomes": outcomes,
            "from_survey_sample": True,
        })
    return participants


def write_participants_csv(participants: List[Dict[str, Any]]) -> Path:
    out_path = PARTICIPANTS_DIR / "participants.csv"
    fieldnames = list(participants[0].keys()) if participants else [
        "participant_id","pseudonym","sector","size","region","gender",
        "years_in_business","start_year","employees","adoption_level",
        "technologies","primary_barriers","reported_outcomes","from_survey_sample"
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(participants)
    return out_path


def synth_paragraph(text: str) -> str:
    # Ensure proper sentence punctuation and spacing
    text = text.strip()
    if not text.endswith((".", "!", "?")):
        text += "."
    return text


def generate_interview_text(p: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    # Returns transcript text and a list of generated quotes (for coding)
    year_last = random.randint(6, 9)  # 2016-2019 range last digit
    tech = random.choice([t.strip() for t in p["technologies"].split(";")])
    driver = random.choice(["market pressure", "customer demand", "efficiency needs", "competition"])
    reason = random.choice(REASONS)
    barrier = random.choice(BARRIERS)
    outcome = random.choice(OUTCOMES)
    months = random.randint(3, 12)
    policy = random.choice(POLICY_TOPICS)
    strategy = random.choice(STRATEGIES)
    ml = random.choice(ML_VARIANTS)
    season = random.choice(SEASONS)

    intro = random.choice(INTRO_TEMPLATES).format(
        size=p["size"], sector=p["sector"], region=p["region"], start_year=p["start_year"],
        employees=p["employees"], product=random.choice(PRODUCTS), customers=random.choice(CUSTOMERS)
    )

    quotes = []
    paragraphs = [synth_paragraph(intro)]

    for tmpl in QUOTES_TEMPLATES:
        q = tmpl.format(
            tech=tech, year_last=year_last, driver=driver, reason=reason,
            barrier=barrier, region=p["region"], outcome=outcome, months=months,
            policy=policy, strategy=strategy, ml=ml, season=season
        )
        quotes.append({
            "participant_id": p["participant_id"],
            "quote": q,
            "tech": tech,
            "barrier": barrier,
            "outcome": outcome,
            "policy": policy,
            "strategy": strategy,
        })
        paragraphs.append(synth_paragraph(q))
        paragraphs.append(random.choice(PARAGRAPH_FILLERS))

    # Add closing reflection
    closing = (
        f"Looking back, the combination of {tech} and {strategy.lower()} mattered most. "
        f"We still struggle with {barrier.lower()}, but we track metrics and keep training."
    )
    paragraphs.append(synth_paragraph(closing))

    # Construct transcript with speaker tags
    lines = []
    interviewer_prompts = [
        "Tell me the story of when you decided to adopt it.",
        "What were the biggest hurdles, and how did you navigate them?",
        "How did this specifically affect your sales, costs, or relationships?",
        "What role did policy or regulation play?",
        "How do you use data or analytics today?",
    ]

    # Interleave interviewer prompts with participant responses
    lines.append(f"Interviewer: {interviewer_prompts[0]}")
    lines.append(f"{p['pseudonym']}: {paragraphs[0]}")
    for i, para in enumerate(paragraphs[1:1+len(QUOTES_TEMPLATES)*2], start=1):
        prompt = interviewer_prompts[i % len(interviewer_prompts)]
        lines.append(f"Interviewer: {prompt}")
        lines.append(f"{p['pseudonym']}: {para}")
    lines.append(f"Interviewer: Any closing thoughts for other SMEs?")
    lines.append(f"{p['pseudonym']}: {paragraphs[-1]}")

    transcript = "\n".join(lines) + "\n"
    return transcript, quotes


def write_interview(p: Dict[str, Any], transcript: str) -> Tuple[Path, Path]:
    txt_path = INTERVIEWS_DIR / f"{p['participant_id']}.txt"
    meta_path = INTERVIEWS_META_DIR / f"{p['participant_id']}.json"
    with txt_path.open("w", encoding="utf-8") as f:
        f.write(transcript)
    meta = {
        "participant_id": p["participant_id"],
        "pseudonym": p["pseudonym"],
        "sector": p["sector"],
        "size": p["size"],
        "region": p["region"],
        "technologies": [t.strip() for t in p["technologies"].split(";")],
        "adoption_level": p["adoption_level"],
        "interview_date": datetime.now().strftime("%Y-%m-%d"),
        "length_lines": transcript.count("\n") + 1,
        "audio_recorded": random.random() < 0.85,
    }
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return txt_path, meta_path


def write_consent(p: Dict[str, Any]) -> Path:
    consent = {
        "participant_id": p["participant_id"],
        "pseudonym": p["pseudonym"],
        "consent_given": True,
        "audio_recorded": True if random.random() < 0.85 else False,
        "anonymization": {
            "remove_names": True,
            "replace_locations": True,
            "mask_financials": True,
        },
        "consent_date": datetime.now().strftime("%Y-%m-%d"),
        "contact_for_followup": False,
    }
    path = CONSENT_DIR / f"{p['participant_id']}_consent.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(consent, f, indent=2)
    return path


def flatten_codebook(cb: Dict[str, Any]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    def walk(prefix: List[str], node: Dict[str, Any]):
        if not node:
            code_id = "/".join(prefix)
            rows.append({"code_id": code_id, "parent": "/".join(prefix[:-1]) if len(prefix) > 1 else "", "label": prefix[-1]})
            return
        for k, v in node.items():
            walk(prefix + [k], v)
    for k, v in cb.items():
        walk([k], v)
    return rows


def write_codebook(cb: Dict[str, Any]) -> Tuple[Path, Path]:
    json_path = CODEBOOK_DIR / "codebook.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(cb, f, indent=2)
    csv_path = CODEBOOK_DIR / "codebook.csv"
    rows = flatten_codebook(cb)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["code_id", "parent", "label"])
        writer.writeheader()
        writer.writerows(rows)
    return json_path, csv_path


def auto_code_quotes(quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Simple rule-based coding for generated quotes
    coded = []
    for i, q in enumerate(quotes):
        applied: List[str] = []
        text = q["quote"].lower()
        if "market" in text or "competition" in text:
            applied.append("Drivers/Market_Pressure")
        if "customer" in text:
            applied.append("Drivers/Customer_Demand")
        if "efficien" in text:
            applied.append("Drivers/Efficiency_Gains")
        if "power" in text:
            applied.append("Barriers/Power_Outage")
        if "broadband" in text or "internet" in text:
            applied.append("Barriers/Internet_Reliability")
        if "fx" in text:
            applied.append("Barriers/FX_Volatility")
        if "policy" in text:
            applied.append("Barriers/Policy_Uncertainty")
        if "skill" in text or "training" in text:
            applied.append("Capabilities/Digital_Skills")
        if "pilot" in text:
            applied.append("Strategies/Pilot_Scale")
        if "solar" in text or "generator" in text:
            applied.append("Strategies/Alternative_Power")
        if "sales" in text:
            applied.append("Outcomes/Sales_Increase")
        if "cost" in text:
            applied.append("Outcomes/Cost_Reduction")
        if "retention" in text or "relationship" in text:
            applied.append("Outcomes/Customer_Retention")
        if "cashless" in text:
            applied.append("Policy_Environment/Cashless")
        # Always ensure at least one code
        if not applied:
            applied.append("Drivers/Competition")
        coded.append({
            "text": q["quote"],
            "applied_codes": applied,
            "participant_id": q["participant_id"],
        })
    return coded


def write_coding(participant_id: str, coded_segments: List[Dict[str, Any]]) -> Path:
    path = CODING_DIR / f"{participant_id}_codes.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump({"participant_id": participant_id, "segments": coded_segments}, f, indent=2)
    return path


def write_memo_for_interview(p: Dict[str, Any], coded_segments: List[Dict[str, Any]]) -> Path:
    top_codes: Dict[str, int] = {}
    for seg in coded_segments:
        for c in seg["applied_codes"]:
            top_codes[c] = top_codes.get(c, 0) + 1
    top_sorted = sorted(top_codes.items(), key=lambda kv: kv[1], reverse=True)[:5]
    memo_lines = [
        f"Case memo for {p['participant_id']} ({p['pseudonym']})",
        f"Sector: {p['sector']} | Size: {p['size']} | Region: {p['region']}",
        f"Adoption level: {p['adoption_level']} | Tech: {p['technologies']}",
        "",
        "Salient codes:",
    ]
    for code, cnt in top_sorted:
        memo_lines.append(f"- {code}: {cnt}")
    memo_lines += [
        "",
        "Notable excerpts:",
    ]
    for seg in coded_segments[:3]:
        memo_lines.append(f"• \"{seg['text']}\"")
    memo_lines.append("")
    memo_lines.append("Analyst reflection: Adoption driven by pragmatic efficiency gains; power/internet constraints shape ROI.")
    path = MEMOS_DIR / f"{p['participant_id']}_memo.txt"
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(memo_lines) + "\n")
    return path


def generate_fgd_transcript(group_id: str, participants: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
    # Construct a synthetic FGD transcript with moderator and multiple participants
    lines = []
    lines.append(f"FGD {group_id} | Sector: {participants[0]['sector']} | Participants: {len(participants)}")
    lines.append("")
    # Opening round
    opener = random.choice(FGD_OPENERS)
    lines.append(opener)
    lines.append(random.choice(FGD_CROWD_REACTIONS))

    for round_idx in range(3):
        probe = random.choice(FGD_PROBES)
        lines.append("")
        lines.append(f"Moderator: {probe}")
        # 3-5 contributions per round
        speakers = random.sample(participants, k=min(len(participants), random.randint(3, 5)))
        for sp in speakers:
            claimed_barrier = random.choice(BARRIERS)
            claimed_strategy = random.choice(STRATEGIES)
            claimed_outcome = random.choice(OUTCOMES)
            tech = random.choice([t.strip() for t in sp["technologies"].split(";")])
            utter = (
                f"{sp['pseudonym']}: In our {sp['size'].lower()} setup, {claimed_barrier.lower()} was tough. "
                f"We used {claimed_strategy.lower()} around {tech.lower()}, and saw {claimed_outcome.lower()}."
            )
            lines.append(utter)
        if random.random() < 0.6:
            lines.append(random.choice(FGD_CROWD_REACTIONS))

    # Closing
    lines.append("")
    lines.append("Moderator: If you could change one policy item, what would it be?")
    for sp in random.sample(participants, k=min(len(participants), 3)):
        lines.append(f"{sp['pseudonym']}: {random.choice(POLICY_TOPICS)} needs clearer guidance for SMEs.")

    transcript = "\n".join(lines) + "\n"
    meta = {
        "fgd_id": group_id,
        "sector": participants[0]['sector'],
        "participant_ids": [p['participant_id'] for p in participants],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "length_lines": transcript.count("\n") + 1,
        "location": random.choice(["Zoom", "LCCI Lagos", "Abuja Hub", "Kano Co-work"]),
        "moderator": random_name(),
    }
    return transcript, meta


def write_fgd(group_id: str, transcript: str, meta: Dict[str, Any]) -> Tuple[Path, Path]:
    txt_path = FGDS_DIR / f"{group_id}.txt"
    meta_path = FGDS_META_DIR / f"{group_id}.json"
    with txt_path.open("w", encoding="utf-8") as f:
        f.write(transcript)
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return txt_path, meta_path


def archive_dataset() -> Path:
    archive_path = DATASET_ROOT / "core_dataset_2"
    # Remove existing archive to avoid appending
    if (DATASET_ROOT / "core_dataset_2.zip").exists():
        (DATASET_ROOT / "core_dataset_2.zip").unlink()
    shutil.make_archive(str(archive_path), "zip", root_dir=DATASET_ROOT)
    return DATASET_ROOT / "core_dataset_2.zip"


def main() -> None:
    random.seed(RANDOM_SEED)
    ensure_dirs()

    # Participants
    participants = generate_participants(NUM_INTERVIEWS)
    participants_csv = write_participants_csv(participants)

    # Interviews + coding + memos + consent
    total_quotes = 0
    for p in participants:
        transcript, quotes = generate_interview_text(p)
        write_interview(p, transcript)
        coded = auto_code_quotes(quotes)
        write_coding(p["participant_id"], coded)
        write_memo_for_interview(p, coded)
        write_consent(p)
        total_quotes += len(quotes)

    # Codebook
    write_codebook(CODEBOOK)

    # FGDs: group by sector, 4-6 FGDs total, each 6-8 participants
    sector_to_participants: Dict[str, List[Dict[str, Any]]] = {}
    for p in participants:
        sector_to_participants.setdefault(p["sector"], []).append(p)

    fgd_ids = []
    sectors = list(sector_to_participants.keys())
    random.shuffle(sectors)
    selected_sectors = sectors[:NUM_FGDS] if len(sectors) >= NUM_FGDS else sectors
    for i, sector in enumerate(selected_sectors, start=1):
        pool = sector_to_participants[sector]
        k = min(len(pool), random.randint(*FGD_PARTICIPANTS_RANGE))
        chosen = random.sample(pool, k=k)
        group_id = f"FGD_{i:02d}"
        transcript, meta = generate_fgd_transcript(group_id, chosen)
        write_fgd(group_id, transcript, meta)
        # FGD memo
        memo_lines = [
            f"FGD memo for {group_id} | Sector: {sector}",
            f"Participants: {', '.join([p['participant_id'] for p in chosen])}",
            "Themes: power and internet constraints; phased adoption; financing via vendors; policy ambiguity.",
        ]
        with (MEMOS_DIR / f"{group_id}_memo.txt").open("w", encoding="utf-8") as f:
            f.write("\n".join(memo_lines) + "\n")
        fgd_ids.append(group_id)

    # Logs
    log = {
        "generated_at": datetime.now().isoformat(),
        "random_seed": RANDOM_SEED,
        "num_interviews": NUM_INTERVIEWS,
        "num_fgds": len(fgd_ids),
        "num_quotes": total_quotes,
        "participants_csv": str(participants_csv.relative_to(DATASET_ROOT)),
        "fgd_ids": fgd_ids,
    }
    with (LOGS_DIR / "generation_log.json").open("w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    # Archive for easy download
    archive_path = archive_dataset()
    print(f"Dataset generated at: {DATASET_ROOT}")
    print(f"Archive created: {archive_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
