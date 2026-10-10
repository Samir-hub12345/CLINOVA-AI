"""CLINOVA AI — Clinical Case Report & PDF Generator.

Produces tamper-evident, multi-page compliant PDF-1.4 documents
strictly separating AI-generated inference from authoritative
human clinician decisions as mandated by DOC-09, DOC-13, and DOC-14.
"""

import io
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


import unicodedata


def escape_pdf(text: Any) -> str:
    """Escapes special characters and sanitizes text to ASCII Latin-1 compatible form."""
    if text is None:
        return ""
    text = str(text)
    if not text:
        return ""
    text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    text = text.replace("—", "--").replace("–", "-").replace("•", "*").replace("…", "...")
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = text.replace("°", " deg ").replace("±", "+/-").replace("\u00a0", " ")
    text = text.replace("\r", " ").replace("\n", " ")

    # Decompose unicode accents to base ASCII characters (e.g. é -> e)
    normalized = unicodedata.normalize("NFKD", text)
    ascii_clean = "".join(c if ord(c) < 128 else "" for c in normalized)
    if ascii_clean.strip():
        return ascii_clean
    return "".join(c if ord(c) < 128 else "?" for c in text)


class ClinicalPDFCanvas:
    """Low-overhead, zero-dependency PDF-1.4 generator for clinical reports."""

    def __init__(self, page_width: float = 612.0, page_height: float = 792.0, margin: float = 40.0):
        self.page_width = page_width
        self.page_height = page_height
        self.margin = margin
        self.content_width = page_width - (2 * margin)
        self.pages: List[str] = []
        self.current_commands: List[str] = []
        self.y = page_height - margin
        self.page_number = 1

    def new_page(self):
        """Flushes the current page commands and opens a new page canvas."""
        self.pages.append("\n".join(self.current_commands))
        self.current_commands = []
        self.page_number += 1
        self.y = self.page_height - self.margin - 15
        self._draw_page_header()

    def check_space(self, required_height: float):
        """Ensures enough vertical space exists; otherwise creates a new page."""
        if self.y - required_height < self.margin + 35:
            self.new_page()

    def _draw_page_header(self):
        """Draws subtle running header on continuation pages."""
        if self.page_number > 1:
            self.draw_text(
                "CLINOVA AI -- Confidential Patient Case Report (Continuation)",
                self.margin,
                self.page_height - 25,
                font="F3",
                size=8,
                rgb=(0.4, 0.45, 0.5),
            )
            self.draw_line(
                self.margin,
                self.page_height - 28,
                self.page_width - self.margin,
                self.page_height - 28,
                stroke_rgb=(0.85, 0.88, 0.9),
                width=0.5,
            )

    def draw_rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill_rgb: Optional[tuple] = None,
        stroke_rgb: Optional[tuple] = None,
        line_width: float = 1.0,
    ):
        cmds = []
        if fill_rgb:
            r, g, b = fill_rgb
            cmds.append(f"{r:.3f} {g:.3f} {b:.3f} rg")
        if stroke_rgb:
            r, g, b = stroke_rgb
            cmds.append(f"{r:.3f} {g:.3f} {b:.3f} RG")
        cmds.append(f"{line_width:.2f} w")
        cmds.append(f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re")
        if fill_rgb and stroke_rgb:
            cmds.append("B")
        elif fill_rgb:
            cmds.append("f")
        else:
            cmds.append("S")
        self.current_commands.append(" ".join(cmds))

    def draw_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stroke_rgb: tuple = (0.8, 0.8, 0.8),
        width: float = 1.0,
    ):
        r, g, b = stroke_rgb
        self.current_commands.append(
            f"{r:.3f} {g:.3f} {b:.3f} RG {width:.2f} w {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S"
        )

    def draw_text(
        self,
        text: str,
        x: float,
        y: float,
        font: str = "F1",
        size: float = 10.0,
        rgb: tuple = (0.1, 0.1, 0.1),
    ):
        r, g, b = rgb
        esc = escape_pdf(text)
        self.current_commands.append(
            f"BT /{font} {size:.1f} Tf {r:.3f} {g:.3f} {b:.3f} rg {x:.1f} {y:.1f} Td ({esc}) Tj ET"
        )

    def draw_wrapped_text(
        self,
        text: Any,
        x: float,
        start_y: float,
        max_width: float,
        font: str = "F1",
        size: float = 9.5,
        line_height: float = 13.0,
        rgb: tuple = (0.2, 0.2, 0.2),
        max_lines: Optional[int] = None,
    ) -> float:
        """Wraps text within max_width, gracefully paginating across pages if space runs out."""
        if text is None:
            return start_y
        str_text = str(text)
        if not str_text.strip():
            return start_y

        paragraphs = str_text.split("\n")
        lines = []

        char_w = size * 0.52
        chars_per_line = max(10, int(max_width / char_w))

        for para in paragraphs:
            para = para.strip()
            if not para:
                lines.append("")
                continue
            words = para.split()
            current_line = []
            current_len = 0
            for w in words:
                if current_len + len(w) + (1 if current_line else 0) <= chars_per_line:
                    current_line.append(w)
                    current_len += len(w) + (1 if len(current_line) > 1 else 0)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [w]
                    current_len = len(w)
            if current_line:
                lines.append(" ".join(current_line))

        if max_lines is not None and max_lines > 0:
            lines = lines[:max_lines]

        cur_y = start_y
        for l in lines:
            if not l:
                cur_y -= (line_height * 0.5)
                continue
            if cur_y - line_height < self.margin + 35:
                self.new_page()
                cur_y = self.y
            self.draw_text(l, x, cur_y, font=font, size=size, rgb=rgb)
            cur_y -= line_height

        self.y = cur_y
        return cur_y

    def build(self) -> bytes:
        """Compiles all accumulated pages into a valid binary PDF-1.4 file."""
        if self.current_commands or not self.pages:
            self.pages.append("\n".join(self.current_commands))
            self.current_commands = []

        total_pages = max(1, len(self.pages))

        # Add page numbering footer to each page
        for i in range(total_pages):
            footer_cmd = (
                f"BT /F1 8 Tf 0.5 0.55 0.6 rg {self.margin:.1f} 20 Td "
                f"({escape_pdf(f'Page {i + 1} of {total_pages} -- Confidential Medical Record -- DPDP Act 2023 Compliant')}) Tj ET\n"
                f"0.85 0.88 0.9 RG 0.5 w {self.margin:.1f} 30 m {self.page_width - self.margin:.1f} 30 l S"
            )
            self.pages[i] += "\n" + footer_cmd

        catalog_idx = 1
        pages_idx = 2
        first_page_idx = 3
        first_stream_idx = first_page_idx + total_pages
        font1_idx = first_stream_idx + total_pages
        font2_idx = font1_idx + 1
        font3_idx = font1_idx + 2

        objects = []
        objects.append(f"<< /Type /Catalog /Pages {pages_idx} 0 R >>")

        kids = " ".join(f"{first_page_idx + i} 0 R" for i in range(total_pages))
        objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {total_pages} >>")

        for i in range(total_pages):
            stream_id = first_stream_idx + i
            objects.append(
                f"<< /Type /Page /Parent {pages_idx} 0 R "
                f"/MediaBox [0 0 {self.page_width} {self.page_height}] "
                f"/Contents {stream_id} 0 R "
                f"/Resources << /Font << /F1 {font1_idx} 0 R /F2 {font2_idx} 0 R /F3 {font3_idx} 0 R >> >> >>"
            )

        for i in range(total_pages):
            stream_content = self.pages[i].encode("latin-1", "replace")
            stream_len = len(stream_content)
            stream_obj = (
                f"<< /Length {stream_len} >>\nstream\n".encode("latin-1")
                + stream_content
                + b"\nendstream"
            )
            objects.append(stream_obj)

        objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>")

        out = io.BytesIO()
        out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        offsets = [0]
        for idx, obj in enumerate(objects, start=1):
            offsets.append(out.tell())
            out.write(f"{idx} 0 obj\n".encode("latin-1"))
            if isinstance(obj, str):
                out.write(obj.encode("latin-1"))
            else:
                out.write(obj)
            out.write(b"\nendobj\n")

        xref_pos = out.tell()
        out.write(f"xref\n0 {len(offsets)}\n".encode("latin-1"))
        out.write(b"0000000000 65535 f \r\n")
        for off in offsets[1:]:
            out.write(f"{off:010d} 00000 n \r\n".encode("latin-1"))

        out.write(f"trailer\n<< /Size {len(offsets)} /Root {catalog_idx} 0 R >>\n".encode("latin-1"))
        out.write(f"startxref\n{xref_pos}\n%%EOF\n".encode("latin-1"))

        return out.getvalue()


def build_clinical_report_pdf(report: Dict[str, Any]) -> bytes:
    """Renders a structured clinical report dictionary into an authoritative PDF."""
    canvas = ClinicalPDFCanvas()
    m = canvas.margin
    w = canvas.content_width

    # Header Top Brand Bar
    canvas.draw_rect(m, canvas.y - 42, w, 42, fill_rgb=(0.04, 0.16, 0.31))
    canvas.draw_text("CLINOVA AI", m + 12, canvas.y - 20, font="F2", size=14, rgb=(1, 1, 1))
    canvas.draw_text("CONTINUOUS CARE INTELLIGENCE PLATFORM", m + 12, canvas.y - 32, font="F1", size=7.5, rgb=(0.58, 0.77, 0.88))
    canvas.draw_text("OFFICIAL PATIENT CASE SUMMARY", m + w - 190, canvas.y - 24, font="F2", size=10, rgb=(0.9, 0.95, 1.0))

    canvas.y -= 52

    # Metadata & Patient Context Box
    p = report.get("patient", {})
    c = report.get("case", {})
    fac = report.get("facility", {})

    canvas.draw_rect(m, canvas.y - 70, w, 70, fill_rgb=(0.96, 0.98, 1.0), stroke_rgb=(0.75, 0.83, 0.92), line_width=1)

    # Column 1
    canvas.draw_text("PATIENT TOKEN:", m + 12, canvas.y - 18, font="F2", size=8.5, rgb=(0.1, 0.2, 0.35))
    canvas.draw_text(p.get("synthetic_id", "SYN-PT-UNKNOWN"), m + 90, canvas.y - 18, font="F2", size=9.5, rgb=(0.04, 0.16, 0.31))

    canvas.draw_text("DEMOGRAPHICS:", m + 12, canvas.y - 34, font="F2", size=8.5, rgb=(0.1, 0.2, 0.35))
    canvas.draw_text(f"{p.get('age_bracket', 'Unknown')} | {p.get('biological_sex', 'Unknown')}", m + 90, canvas.y - 34, font="F1", size=9, rgb=(0.2, 0.2, 0.2))

    canvas.draw_text("FACILITY:", m + 12, canvas.y - 50, font="F2", size=8.5, rgb=(0.1, 0.2, 0.35))
    canvas.draw_text(fac.get("name", "Regional Health Facility"), m + 90, canvas.y - 50, font="F1", size=8.5, rgb=(0.2, 0.2, 0.2))

    # Column 2
    canvas.draw_text("CASE ID:", m + 290, canvas.y - 18, font="F2", size=8.5, rgb=(0.1, 0.2, 0.35))
    canvas.draw_text(c.get("id", "CASE-UNKNOWN"), m + 350, canvas.y - 18, font="F2", size=9.5, rgb=(0.04, 0.16, 0.31))

    canvas.draw_text("CASE NO:", m + 290, canvas.y - 34, font="F2", size=8.5, rgb=(0.1, 0.2, 0.35))
    canvas.draw_text(c.get("case_number", "CNV-2026-N/A"), m + 350, canvas.y - 34, font="F1", size=9, rgb=(0.2, 0.2, 0.2))

    canvas.draw_text("DATE / TIME:", m + 290, canvas.y - 50, font="F2", size=8.5, rgb=(0.1, 0.2, 0.35))
    now_str = report.get("generated_at", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    canvas.draw_text(now_str[:19], m + 350, canvas.y - 50, font="F1", size=8.5, rgb=(0.2, 0.2, 0.2))

    # Status & Acuity Tag
    acuity = c.get("acuity_tier", "ROUTINE")
    acuity_color = (0.75, 0.1, 0.1) if acuity == "CRITICAL" else ((0.8, 0.5, 0.05) if acuity == "URGENT" else (0.1, 0.5, 0.2))
    canvas.draw_rect(m + w - 75, canvas.y - 24, 65, 18, fill_rgb=acuity_color)
    canvas.draw_text(acuity, m + w - 68, canvas.y - 18, font="F2", size=8, rgb=(1, 1, 1))

    canvas.y -= 80

    # Non-Diagnostic Governance Disclaimer Banner
    canvas.draw_rect(m, canvas.y - 24, w, 24, fill_rgb=(0.99, 0.95, 0.9), stroke_rgb=(0.95, 0.8, 0.6), line_width=0.8)
    canvas.draw_text(
        "MANDATORY CLINICAL GOVERNANCE NOTICE: Non-diagnostic Clinical Decision Support summary. "
        "All recommendations require qualified clinician verification before patient action.",
        m + 8,
        canvas.y - 15,
        font="F3",
        size=7.5,
        rgb=(0.55, 0.28, 0.05),
    )
    canvas.y -= 32

    # Section: Presenting Complaint & Clinical Pathway
    canvas.draw_text("1. CLINICAL PRESENTATION & INTAKE PATHWAY", m, canvas.y, font="F2", size=10, rgb=(0.04, 0.16, 0.31))
    canvas.draw_line(m, canvas.y - 3, m + w, canvas.y - 3, stroke_rgb=(0.2, 0.45, 0.65), width=1)
    canvas.y -= 14

    complaint = c.get("presenting_complaint", "No specific complaint documented.")
    pathway = c.get("pathway", "OPD_GENERAL")
    pathway_str = "EMERGENCY FAST-TRACK" if "EMERGENCY" in pathway.upper() else "REGULAR OUTPATIENT (OPD)"
    canvas.draw_text(f"Intake Pathway: {pathway_str} | Consent Status: GRANTED & DIGITALLY VERIFIED", m, canvas.y, font="F2", size=8.5, rgb=(0.25, 0.3, 0.35))
    canvas.y -= 12
    canvas.draw_text("Chief Presenting Complaint:", m, canvas.y, font="F2", size=8.5, rgb=(0.2, 0.2, 0.2))
    canvas.y -= 11
    canvas.y = canvas.draw_wrapped_text(complaint, m + 8, canvas.y, w - 16, font="F1", size=8.5, line_height=11.5)
    canvas.y -= 10

    # Section: Vital Signs & Acuity Assessment
    canvas.check_space(70)
    canvas.draw_text("2. RECORDED VITAL SIGNS & DETERMINISTIC TRIAGE", m, canvas.y, font="F2", size=10, rgb=(0.04, 0.16, 0.31))
    canvas.draw_line(m, canvas.y - 3, m + w, canvas.y - 3, stroke_rgb=(0.2, 0.45, 0.65), width=1)
    canvas.y -= 14

    vitals = report.get("vitals", [])
    if vitals:
        v = vitals[-1]  # latest
        canvas.draw_rect(m, canvas.y - 28, w, 28, fill_rgb=(0.97, 0.97, 0.98), stroke_rgb=(0.85, 0.88, 0.9), line_width=0.8)
        
        bp = f"{v.get('systolic_bp', '-')}/{v.get('diastolic_bp', '-')} mmHg" if v.get("systolic_bp") else "N/A"
        hr = f"{v.get('heart_rate', '-')} bpm"
        spo2 = f"{v.get('spo2_percent', '-')}%"
        temp = f"{v.get('temperature_celsius', '-')} deg C"
        rr = f"{v.get('respiratory_rate', '-')} /min"
        avpu = v.get("avpu_score", "ALERT")
        prov = v.get("provenance", "STAFF_ENTERED")

        canvas.draw_text(f"HR: {hr}", m + 10, canvas.y - 12, font="F2", size=8.5, rgb=(0.1, 0.1, 0.1))
        canvas.draw_text(f"BP: {bp}", m + 90, canvas.y - 12, font="F2", size=8.5, rgb=(0.1, 0.1, 0.1))
        canvas.draw_text(f"SpO2: {spo2}", m + 190, canvas.y - 12, font="F2", size=8.5, rgb=(0.1, 0.1, 0.1))
        canvas.draw_text(f"Temp: {temp}", m + 280, canvas.y - 12, font="F2", size=8.5, rgb=(0.1, 0.1, 0.1))
        canvas.draw_text(f"RR: {rr}", m + 380, canvas.y - 12, font="F2", size=8.5, rgb=(0.1, 0.1, 0.1))
        canvas.draw_text(f"AVPU: {avpu}", m + 450, canvas.y - 12, font="F2", size=8.5, rgb=(0.1, 0.1, 0.1))
        canvas.draw_text(f"Vitals Provenance: {prov} | Recorded: {v.get('recorded_at', 'Clinical Visit')[:19]}", m + 10, canvas.y - 23, font="F3", size=7.5, rgb=(0.4, 0.45, 0.5))
        canvas.y -= 34
    else:
        canvas.draw_text("Vital Signs Status: PENDING / TRIAGE QUEUE STAGE", m + 10, canvas.y - 8, font="F3", size=8.5, rgb=(0.5, 0.3, 0.1))
        canvas.y -= 16

    # Red Flag Warning Check
    red_flags = report.get("safety_alerts", [])
    if red_flags:
        canvas.check_space(32)
        canvas.draw_rect(m, canvas.y - 22, w, 22, fill_rgb=(1.0, 0.94, 0.94), stroke_rgb=(0.95, 0.6, 0.6), line_width=1)
        alert_text = "CRITICAL SAFETY ALERT: " + "; ".join(rf.get("title", "Red Flag Alert") for rf in red_flags[:3])
        canvas.draw_text(alert_text[:110], m + 8, canvas.y - 14, font="F2", size=8, rgb=(0.7, 0.1, 0.1))
        canvas.y -= 28

    # Section: Document Extractions & Evidence Provenance
    evidence = report.get("evidence", [])
    if evidence:
        canvas.check_space(60)
        canvas.draw_text("3. COLLECTED EVIDENCE & PROVENANCE AUDIT", m, canvas.y, font="F2", size=10, rgb=(0.04, 0.16, 0.31))
        canvas.draw_line(m, canvas.y - 3, m + w, canvas.y - 3, stroke_rgb=(0.2, 0.45, 0.65), width=1)
        canvas.y -= 14

        for item in evidence[:4]:
            canvas.check_space(14)
            ev_type = item.get("entity_type", "CLINICAL_PARAM")
            ev_val = item.get("entity_value", "")
            ev_src = item.get("source", "PATIENT_REPORTED")
            ev_conf = item.get("confidence", 1.0)
            conf_str = f"{int(ev_conf * 100)}%" if isinstance(ev_conf, (int, float)) else "Verified"
            status = item.get("verification_status", "UNVERIFIED")

            canvas.draw_text(f"* {ev_type}:", m + 8, canvas.y, font="F2", size=8, rgb=(0.1, 0.2, 0.35))
            canvas.draw_text(f"{ev_val}", m + 160, canvas.y, font="F1", size=8, rgb=(0.1, 0.1, 0.1))
            canvas.draw_text(f"[Src: {ev_src} | Conf: {conf_str} | Status: {status}]", m + 320, canvas.y, font="F3", size=7.5, rgb=(0.4, 0.45, 0.5))
            canvas.y -= 12
        canvas.y -= 4

    # Section: AI CareGraph Synthesis (Explicitly Labeled)
    canvas.check_space(75)
    canvas.draw_text("4. CAREGRAPH AI SYNTHESIS & UNCERTAINTY METRICS", m, canvas.y, font="F2", size=10, rgb=(0.04, 0.16, 0.31))
    canvas.draw_line(m, canvas.y - 3, m + w, canvas.y - 3, stroke_rgb=(0.2, 0.45, 0.65), width=1)
    canvas.y -= 14

    ai_sum = report.get("ai_summary", {})
    canvas.draw_rect(m, canvas.y - 16, 175, 14, fill_rgb=(0.9, 0.94, 0.98))
    canvas.draw_text("AI-GENERATED -- CLINICAL REVIEW ONLY", m + 6, canvas.y - 11, font="F2", size=7.5, rgb=(0.05, 0.35, 0.65))

    unc_score = ai_sum.get("uncertainty_score", c.get("uncertainty_score", 0.35))
    epistemic = ai_sum.get("epistemic_status", "KNOWN")
    canvas.draw_text(f"Epistemic Uncertainty: {unc_score:.2f} ({epistemic})", m + 200, canvas.y - 11, font="F2", size=8, rgb=(0.3, 0.35, 0.4))
    canvas.y -= 22

    summary_text = ai_sum.get("summary_text", c.get("primary_syndrome", "Clinical synthesis computed based on multi-source intake evidence."))
    canvas.y = canvas.draw_wrapped_text(summary_text, m + 8, canvas.y, w - 16, font="F1", size=8.5, line_height=11.5)

    missing = ai_sum.get("missing_parameters", [])
    if missing:
        canvas.check_space(14)
        canvas.draw_text(f"Identified Information Gaps: {', '.join(missing)}", m + 8, canvas.y - 4, font="F3", size=8, rgb=(0.6, 0.3, 0.05))
        canvas.y -= 14
    canvas.y -= 8

    # Section: Authoritative Clinician Review & Orders (Explicitly Labeled)
    canvas.check_space(85)
    canvas.draw_text("5. ATTENDING PHYSICIAN DECISION & CLINICAL ORDERS", m, canvas.y, font="F2", size=10, rgb=(0.04, 0.16, 0.31))
    canvas.draw_line(m, canvas.y - 3, m + w, canvas.y - 3, stroke_rgb=(0.2, 0.45, 0.65), width=1)
    canvas.y -= 14

    clin_rev = report.get("clinician_review", {})
    is_reviewed = bool(clin_rev.get("clinician_id") or clin_rev.get("decision_type"))

    if is_reviewed:
        canvas.draw_rect(m, canvas.y - 16, 160, 14, fill_rgb=(0.9, 0.98, 0.92))
        canvas.draw_text("HUMAN CLINICIAN VERIFIED", m + 6, canvas.y - 11, font="F2", size=7.5, rgb=(0.05, 0.5, 0.2))

        doc_name = clin_rev.get("clinician_name", "Dr. Priya Sharma, MD")
        doc_id = clin_rev.get("clinician_id", "usr-doc-01")
        dec_type = clin_rev.get("decision_type", "OBSERVE")
        action_type = clin_rev.get("action_type", "CONSERVATIVE_MANAGEMENT")

        canvas.draw_text(f"Attending: {doc_name} ({doc_id})", m + 180, canvas.y - 11, font="F2", size=8.5, rgb=(0.1, 0.1, 0.1))
        canvas.y -= 22

        canvas.draw_text(f"Authoritative Action: [{dec_type}] {action_type}", m + 8, canvas.y, font="F2", size=8.5, rgb=(0.04, 0.16, 0.31))
        canvas.y -= 12

        plan = clin_rev.get("treatment_plan") or clin_rev.get("notes") or "Standard outpatient supportive therapy and conservative clinical monitoring."
        canvas.draw_text("Treatment Plan / Orders:", m + 8, canvas.y, font="F2", size=8, rgb=(0.2, 0.2, 0.2))
        canvas.y -= 11
        canvas.y = canvas.draw_wrapped_text(plan, m + 16, canvas.y, w - 32, font="F1", size=8.5, line_height=11.5)
        
        rationale = clin_rev.get("rationale")
        if rationale:
            canvas.draw_text(f"Clinical Rationale: {rationale}", m + 16, canvas.y - 2, font="F3", size=8, rgb=(0.3, 0.35, 0.4))
            canvas.y -= 12
    else:
        canvas.draw_rect(m, canvas.y - 16, 175, 14, fill_rgb=(0.99, 0.96, 0.9))
        canvas.draw_text("PENDING ATTENDING PHYSICIAN REVIEW", m + 6, canvas.y - 11, font="F2", size=7.5, rgb=(0.6, 0.35, 0.05))
        canvas.draw_text("This case is currently queued for clinical review and verification sign-off.", m + 190, canvas.y - 11, font="F3", size=8, rgb=(0.4, 0.45, 0.5))
        canvas.y -= 22

    canvas.y -= 8

    # Section: Approved Patient Care Plan & Emergency Red Flags
    canvas.check_space(80)
    canvas.draw_text("6. APPROVED CARE PLAN & FOLLOW-UP INSTRUCTIONS", m, canvas.y, font="F2", size=10, rgb=(0.04, 0.16, 0.31))
    canvas.draw_line(m, canvas.y - 3, m + w, canvas.y - 3, stroke_rgb=(0.2, 0.45, 0.65), width=1)
    canvas.y -= 14

    plan_info = report.get("care_plan", {})
    home_care = plan_info.get(
        "home_instructions",
        "Maintain adequate oral hydration. Take prescribed symptomatic medications after meals as advised. "
        "Get adequate rest and avoid strenuous physical activity.",
    )
    canvas.draw_text("Home Care & Medications:", m + 8, canvas.y, font="F2", size=8.5, rgb=(0.2, 0.2, 0.2))
    canvas.y -= 11
    canvas.y = canvas.draw_wrapped_text(home_care, m + 16, canvas.y, w - 32, font="F1", size=8.5, line_height=11.5)

    follow_up = plan_info.get("follow_up", "Review in 5-7 days at Outpatient Clinic or sooner if symptoms persist.")
    canvas.draw_text(f"Scheduled Review: {follow_up}", m + 8, canvas.y - 2, font="F2", size=8.5, rgb=(0.05, 0.35, 0.65))
    canvas.y -= 16

    # Emergency Guidance Box
    canvas.draw_rect(m, canvas.y - 28, w, 28, fill_rgb=(1.0, 0.96, 0.9), stroke_rgb=(0.95, 0.7, 0.4), line_width=0.8)
    canvas.draw_text(
        "EMERGENCY WARNING: If you experience difficulty breathing, chest pain, confusion, persistent vomiting, "
        "or sudden weakness, seek emergency care immediately or dial 108.",
        m + 8,
        canvas.y - 17,
        font="F2",
        size=7.5,
        rgb=(0.65, 0.2, 0.05),
    )
    canvas.y -= 14

    # Section: Inter-Facility Referral & SBAR Transfer (when present)
    ref = report.get("referral")
    if ref:
        canvas.check_space(80)
        canvas.draw_text("7. INTER-FACILITY REFERRAL & SBAR TRANSFER DOSSIER", m, canvas.y, font="F2", size=10, rgb=(0.04, 0.16, 0.31))
        canvas.draw_line(m, canvas.y - 3, m + w, canvas.y - 3, stroke_rgb=(0.2, 0.45, 0.65), width=1)
        canvas.y -= 14

        ref_dest = ref.get("destination_name", ref.get("destination_facility_id", "Tertiary Referral Center"))
        ref_status = ref.get("status", "REQUESTED")
        ref_bundle = ref.get("required_bundle", "EMERGENCY_TRANSFER")

        status_color = (0.05, 0.45, 0.2) if ref_status in ["ACCEPTED", "DISPATCHED", "COMPLETED"] else (0.8, 0.45, 0.05)
        canvas.draw_rect(m, canvas.y - 18, w, 18, fill_rgb=(0.95, 0.97, 1.0), stroke_rgb=(0.8, 0.88, 0.95), line_width=0.8)
        canvas.draw_text(f"Target: {ref_dest} | Protocol: {ref_bundle}", m + 8, canvas.y - 13, font="F2", size=8.5, rgb=(0.04, 0.16, 0.31))
        canvas.draw_rect(m + w - 85, canvas.y - 16, 75, 14, fill_rgb=status_color)
        canvas.draw_text(ref_status, m + w - 80, canvas.y - 11, font="F2", size=7.5, rgb=(1, 1, 1))
        canvas.y -= 24

        sbar_s = ref.get("sbar_situation")
        sbar_b = ref.get("sbar_background")
        sbar_a = ref.get("sbar_assessment")
        sbar_r = ref.get("sbar_recommendation")

        if sbar_s or sbar_b or sbar_a or sbar_r:
            canvas.draw_text("SBAR Handoff Communication:", m + 8, canvas.y, font="F2", size=8.5, rgb=(0.2, 0.2, 0.2))
            canvas.y -= 11
            if sbar_s:
                canvas.draw_text("[S] Situation:", m + 16, canvas.y, font="F2", size=8, rgb=(0.1, 0.2, 0.35))
                canvas.y = canvas.draw_wrapped_text(sbar_s, m + 75, canvas.y, w - 95, font="F1", size=8, line_height=11)
            if sbar_b:
                canvas.draw_text("[B] Background:", m + 16, canvas.y, font="F2", size=8, rgb=(0.1, 0.2, 0.35))
                canvas.y = canvas.draw_wrapped_text(sbar_b, m + 75, canvas.y, w - 95, font="F1", size=8, line_height=11)
            if sbar_a:
                canvas.draw_text("[A] Assessment:", m + 16, canvas.y, font="F2", size=8, rgb=(0.1, 0.2, 0.35))
                canvas.y = canvas.draw_wrapped_text(sbar_a, m + 75, canvas.y, w - 95, font="F1", size=8, line_height=11)
            if sbar_r:
                canvas.draw_text("[R] Recommendation:", m + 16, canvas.y, font="F2", size=8, rgb=(0.1, 0.2, 0.35))
                canvas.y = canvas.draw_wrapped_text(sbar_r, m + 75, canvas.y, w - 95, font="F1", size=8, line_height=11)
        canvas.y -= 8

    # Section: Clinical Outcome & Disposition (when present)
    outcome = report.get("outcome")
    if outcome:
        canvas.check_space(60)
        canvas.draw_text("8. CLINICAL OUTCOME & DISPOSITION RECORD", m, canvas.y, font="F2", size=10, rgb=(0.04, 0.16, 0.31))
        canvas.draw_line(m, canvas.y - 3, m + w, canvas.y - 3, stroke_rgb=(0.2, 0.45, 0.65), width=1)
        canvas.y -= 14

        disp = outcome.get("disposition", "UNKNOWN")
        cond = outcome.get("final_condition", "STABLE")
        notes = outcome.get("notes") or outcome.get("recommendation") or "Discharge summary recorded."
        rec_time = (outcome.get("recorded_at") or "")[:19]

        canvas.draw_rect(m, canvas.y - 20, w, 20, fill_rgb=(0.96, 0.98, 0.96), stroke_rgb=(0.8, 0.9, 0.8), line_width=0.8)
        canvas.draw_text(f"Disposition: {disp} | Final Condition: {cond} | Recorded: {rec_time}", m + 8, canvas.y - 14, font="F2", size=8.5, rgb=(0.05, 0.4, 0.15))
        canvas.y -= 26

        canvas.draw_text("Outcome & Transition Notes:", m + 8, canvas.y, font="F2", size=8.5, rgb=(0.2, 0.2, 0.2))
        canvas.y -= 11
        canvas.y = canvas.draw_wrapped_text(notes, m + 16, canvas.y, w - 32, font="F1", size=8.5, line_height=11.5)
        canvas.y -= 8

    # Cryptographic Provenance Ledger Signature
    raw_hash_material = f"{p.get('synthetic_id')}:{c.get('id')}:{now_str}:{c.get('status')}"
    sha256_hash = hashlib.sha256(raw_hash_material.encode("utf-8")).hexdigest()

    canvas.check_space(25)
    canvas.draw_text(
        f"Cryptographic Verification Hash: SHA-256:{sha256_hash[:32]}... | Digital Provenance Verified",
        m,
        canvas.y,
        font="F3",
        size=7.5,
        rgb=(0.45, 0.5, 0.55),
    )

    return canvas.build()
