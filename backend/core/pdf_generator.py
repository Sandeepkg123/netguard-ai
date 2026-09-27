import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.shapes import Drawing, Circle, Wedge


class PDFReportGenerator:

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "ReportTitle",
            parent=self.styles["Title"],
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            spaceAfter=20,
        )

        self.heading_style = ParagraphStyle(
            "ReportHeading",
            parent=self.styles["Heading1"],
            fontSize=16,
            leading=20,
            spaceBefore=10,
            spaceAfter=10,
        )

        self.subheading_style = ParagraphStyle(
            "ReportSubheading",
            parent=self.styles["Heading2"],
            fontSize=12,
            leading=16,
            spaceBefore=8,
            spaceAfter=6,
        )

        self.body_style = ParagraphStyle(
            "ReportBody",
            parent=self.styles["BodyText"],
            fontSize=9,
            leading=14,
            spaceAfter=8,
        )

        self.mono_style = ParagraphStyle(
            "Monospace",
            parent=self.styles["BodyText"],
            fontName="Courier",
            fontSize=8,
            leading=12,
            leftIndent=8,
            spaceAfter=5,
        )

        self.small_style = ParagraphStyle(
            "Small",
            parent=self.styles["BodyText"],
            fontSize=8,
            leading=11,
            spaceAfter=4,
        )

    def generate(
        self,
        audit: dict,
        filename: str,
    ) -> str:

        output_path = os.path.join(
            self.output_dir,
            filename,
        )

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )

        story = []

        # Cover
        self._add_cover(story, audit)

        story.append(PageBreak())

        # Executive summary
        self._add_executive_summary(story, audit)

        story.append(PageBreak())

        # Findings
        self._add_findings(story, audit)

        story.append(PageBreak())

        # Passed controls
        self._add_passed_controls(story, audit)

        doc.build(story)

        return output_path

    # ---------------------------------------------------------
    # COVER
    # ---------------------------------------------------------

    def _add_cover(self, story, audit):

        story.append(Spacer(1, 20 * mm))

        story.append(
            Paragraph(
                "Network Security Compliance Audit",
                self.title_style,
            )
        )

        story.append(
            Paragraph(
                "AI-Driven Multi-Vendor Network Security Compliance Auditor",
                self.body_style,
            )
        )

        story.append(Spacer(1, 12 * mm))

        metadata = [
            [
                "Device",
                self._safe(audit.get("hostname") or "Unknown"),
            ],
            [
                "Vendor",
                self._safe(audit.get("vendor") or "Unknown"),
            ],
            [
                "Operating System",
                self._safe(audit.get("os") or "Unknown"),
            ],
            [
                "Framework",
                self._safe(audit["framework"]["name"]),
            ],
            [
                "Framework Version",
                self._safe(
                    audit["framework"].get("version") or "N/A"
                ),
            ],
            [
                "Audit Date",
                self._safe(
                    str(
                        audit.get("created_at")
                        or datetime.now()
                    )
                ),
            ],
        ]

        table = Table(
            metadata,
            colWidths=[
                55 * mm,
                105 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor("#E8E8E8"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(table)

        story.append(Spacer(1, 12 * mm))

        score = float(audit.get("score", 0))

        story.append(
            Paragraph(
                f"Compliance Score: {score:.2f}%",
                ParagraphStyle(
                    "Score",
                    parent=self.title_style,
                    fontSize=22,
                ),
            )
        )

        # -------------------------
        # Donut chart
        # -------------------------

        passed = int(audit.get("passed", 0))
        failed = int(audit.get("failed", 0))

        story.append(
            self._create_donut_chart(
                passed=passed,
                failed=failed,
            )
        )

        story.append(Spacer(1, 6 * mm))

        score_data = [
            [
                f"Passed: {passed}",
                f"Failed: {failed}",
                f"Total: {passed + failed}",
            ]
        ]

        score_table = Table(
            score_data,
            colWidths=[
                50 * mm,
                50 * mm,
                50 * mm,
            ],
        )

        score_table.setStyle(
            TableStyle(
                [
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                ]
            )
        )

        story.append(score_table)

    # ---------------------------------------------------------
    # DONUT CHART
    # ---------------------------------------------------------

    def _create_donut_chart(
        self,
        passed: int,
        failed: int,
    ):
        drawing = Drawing(160, 120)

        total = passed + failed

        # No audit controls
        if total == 0:
            drawing.add(
                Circle(
                    80,
                    60,
                    40,
                    fillColor=colors.HexColor("#9E9E9E"),
                    strokeColor=colors.white,
                    strokeWidth=1,
                )
            )

            drawing.add(
                Circle(
                    80,
                    60,
                    22,
                    fillColor=colors.white,
                    strokeColor=colors.white,
                )
            )

            return drawing

        # Calculate angles
        passed_angle = (passed / total) * 360

        # PASS portion
        if passed > 0:
            drawing.add(
                Wedge(
                    80,
                    60,
                    40,
                    90,
                    90 + passed_angle,
                    fillColor=colors.HexColor("#2E7D32"),
                    strokeColor=colors.white,
                    strokeWidth=1,
                )
            )

        # FAIL portion
        if failed > 0:
            drawing.add(
                Wedge(
                    80,
                    60,
                    40,
                    90 + passed_angle,
                    450,
                    fillColor=colors.HexColor("#C62828"),
                    strokeColor=colors.white,
                    strokeWidth=1,
                )
            )

        # Create the hole in the middle
        drawing.add(
            Circle(
                80,
                60,
                22,
                fillColor=colors.white,
                strokeColor=colors.white,
            )
        )

        return drawing

    # ---------------------------------------------------------
    # EXECUTIVE SUMMARY
    # ---------------------------------------------------------

    def _add_executive_summary(
        self,
        story,
        audit,
    ):

        story.append(
            Paragraph(
                "Executive Summary",
                self.heading_style,
            )
        )

        findings = audit.get(
            "findings",
            [],
        )

        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }

        for finding in findings:

            severity = (
                finding.get(
                    "severity",
                    "LOW",
                )
                .upper()
            )

            if severity in severity_counts:
                severity_counts[severity] += 1

        severity_data = [
            ["Severity", "Count"],
            [
                "Critical",
                severity_counts["CRITICAL"],
            ],
            [
                "High",
                severity_counts["HIGH"],
            ],
            [
                "Medium",
                severity_counts["MEDIUM"],
            ],
            [
                "Low",
                severity_counts["LOW"],
            ],
        ]

        table = Table(
            severity_data,
            colWidths=[
                70 * mm,
                40 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#333333"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (1, -1),
                        "CENTER",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),

                    # Critical
                    (
                        "BACKGROUND",
                        (0, 1),
                        (0, 1),
                        colors.HexColor("#B71C1C"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 1),
                        (0, 1),
                        colors.white,
                    ),

                    # High
                    (
                        "BACKGROUND",
                        (0, 2),
                        (0, 2),
                        colors.HexColor("#E65100"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 2),
                        (0, 2),
                        colors.white,
                    ),

                    # Medium
                    (
                        "BACKGROUND",
                        (0, 3),
                        (0, 3),
                        colors.HexColor("#F9A825"),
                    ),

                    # Low
                    (
                        "BACKGROUND",
                        (0, 4),
                        (0, 4),
                        colors.HexColor("#2E7D32"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 4),
                        (0, 4),
                        colors.white,
                    ),
                ]
            )
        )

        story.append(table)

        story.append(
            Spacer(
                1,
                10 * mm,
            )
        )

        story.append(
            Paragraph(
                "Top Risks",
                self.subheading_style,
            )
        )

        failed_findings = [
            finding
            for finding in findings
            if finding.get("status") == "FAIL"
        ]

        for finding in failed_findings[:5]:

            story.append(
                Paragraph(
                    (
                        f"<b>"
                        f"{self._safe(finding.get('control_id'))}"
                        f"</b> — "
                        f"{self._safe(finding.get('title'))}"
                    ),
                    self.body_style,
                )
            )

            severity = (
                finding.get(
                    "severity",
                    "UNKNOWN",
                )
                .upper()
            )

            severity_color = self._severity_color(
                severity
            )

            severity_style = ParagraphStyle(
                f"Severity_{severity}",
                parent=self.small_style,
                textColor=severity_color,
            )

            story.append(
                Paragraph(
                    f"<b>Severity:</b> {self._safe(severity)}",
                    severity_style,
                )
            )

    # ---------------------------------------------------------
    # FINDINGS
    # ---------------------------------------------------------

    def _add_findings(
        self,
        story,
        audit,
    ):

        story.append(
            Paragraph(
                "Findings Detail",
                self.heading_style,
            )
        )

        findings = audit.get(
            "findings",
            [],
        )

        for index, finding in enumerate(
            findings,
            start=1,
        ):

            status = finding.get(
                "status",
                "UNKNOWN",
            )

            severity = (
                finding.get(
                    "severity",
                    "UNKNOWN",
                )
                .upper()
            )

            heading = (
                f"{index}. "
                f"{self._safe(finding.get('control_id'))}"
                f" — "
                f"{self._safe(finding.get('title'))}"
            )

            story.append(
                Paragraph(
                    heading,
                    self.subheading_style,
                )
            )

            # -------------------------
            # Finding metadata
            # -------------------------

            details = [
                [
                    "Status",
                    self._safe(status),
                ],
                [
                    "Severity",
                    self._safe(severity),
                ],
                [
                    "SBM Field",
                    self._safe(
                        finding.get(
                            "sbm_field",
                            "",
                        )
                    ),
                ],
                [
                    "Actual Value",
                    self._safe(
                        str(
                            finding.get(
                                "actual_value"
                            )
                        )
                    ),
                ],
                [
                    "Expected Value",
                    self._safe(
                        str(
                            finding.get(
                                "expected_value"
                            )
                        )
                    ),
                ],
            ]

            table = Table(
                details,
                colWidths=[
                    45 * mm,
                    115 * mm,
                ],
            )

            table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (0, -1),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (0, -1),
                            colors.HexColor("#F2F2F2"),
                        ),

                        # Severity cell
                        (
                            "BACKGROUND",
                            (1, 1),
                            (1, 1),
                            self._severity_color(
                                severity
                            ),
                        ),
                        (
                            "TEXTCOLOR",
                            (1, 1),
                            (1, 1),
                            colors.white,
                        ),

                        # Status cell
                        (
                            "BACKGROUND",
                            (1, 0),
                            (1, 0),
                            (
                                colors.HexColor("#2E7D32")
                                if status == "PASS"
                                else colors.HexColor("#C62828")
                            ),
                        ),
                        (
                            "TEXTCOLOR",
                            (1, 0),
                            (1, 0),
                            colors.white,
                        ),
                    ]
                )
            )

            story.append(table)

            story.append(
                Spacer(
                    1,
                    5 * mm,
                )
            )

            # -------------------------
            # Description
            # -------------------------

            if finding.get("description"):

                story.append(
                    Paragraph(
                        (
                            "<b>Description:</b> "
                            f"{self._safe(finding['description'])}"
                        ),
                        self.body_style,
                    )
                )

            # -------------------------
            # Remediation
            # -------------------------

            remediation = finding.get(
                "remediation"
            )

            if remediation:

                story.append(
                    Paragraph(
                        "Security Risk",
                        self.subheading_style,
                    )
                )

                story.append(
                    Paragraph(
                        self._safe(
                            remediation.get(
                                "risk_explanation",
                                "",
                            )
                        ),
                        self.body_style,
                    )
                )

                story.append(
                    Paragraph(
                        "Fix Commands",
                        self.subheading_style,
                    )
                )

                # Each command gets its own row
                command_data = []

                for command in remediation.get(
                    "fix_commands",
                    [],
                ):

                    command_data.append(
                        [
                            Paragraph(
                                self._safe(
                                    command
                                ),
                                self.mono_style,
                            )
                        ]
                    )

                if command_data:

                    command_table = Table(
                        command_data,
                        colWidths=[
                            155 * mm,
                        ],
                    )

                    command_table.setStyle(
                        TableStyle(
                            [
                                (
                                    "BACKGROUND",
                                    (0, 0),
                                    (-1, -1),
                                    colors.HexColor("#F5F5F5"),
                                ),
                                (
                                    "BOX",
                                    (0, 0),
                                    (-1, -1),
                                    0.5,
                                    colors.grey,
                                ),
                                (
                                    "INNERGRID",
                                    (0, 0),
                                    (-1, -1),
                                    0.25,
                                    colors.lightgrey,
                                ),
                                (
                                    "LEFTPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    8,
                                ),
                                (
                                    "RIGHTPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    8,
                                ),
                                (
                                    "TOPPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    5,
                                ),
                                (
                                    "BOTTOMPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    2,
                                ),
                            ]
                        )
                    )

                    story.append(
                        command_table
                    )

                story.append(
                    Spacer(
                        1,
                        4 * mm,
                    )
                )

                # -------------------------
                # Verification
                # -------------------------

                story.append(
                    Paragraph(
                        "Verification Command",
                        self.subheading_style,
                    )
                )

                verification = remediation.get(
                    "verification_command",
                    "",
                )

                verification_table = Table(
                    [
                        [
                            Paragraph(
                                self._safe(
                                    verification
                                ),
                                self.mono_style,
                            )
                        ]
                    ],
                    colWidths=[
                        155 * mm,
                    ],
                )

                verification_table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, -1),
                                colors.HexColor("#F5F5F5"),
                            ),
                            (
                                "BOX",
                                (0, 0),
                                (-1, -1),
                                0.5,
                                colors.grey,
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                8,
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                8,
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                2,
                            ),
                        ]
                    )
                )

                story.append(
                    verification_table
                )

                # -------------------------
                # Caveat
                # -------------------------

                if remediation.get("caveat"):

                    story.append(
                        Spacer(
                            1,
                            3 * mm,
                        )
                    )

                    story.append(
                        Paragraph(
                            (
                                "<b>Caveat:</b> "
                                f"{self._safe(remediation['caveat'])}"
                            ),
                            self.body_style,
                        )
                    )

            story.append(
                Spacer(
                    1,
                    8 * mm,
                )
            )

    # ---------------------------------------------------------
    # PASSED CONTROLS
    # ---------------------------------------------------------

    def _add_passed_controls(
        self,
        story,
        audit,
    ):

        story.append(
            Paragraph(
                "Passed Controls",
                self.heading_style,
            )
        )

        passed = [
            finding
            for finding in audit.get(
                "findings",
                [],
            )
            if finding.get("status") == "PASS"
        ]

        if not passed:

            story.append(
                Paragraph(
                    "No controls passed in this audit.",
                    self.body_style,
                )
            )

            return

        data = [
            [
                "Control ID",
                "Title",
                "Severity",
            ]
        ]

        for finding in passed:

            data.append(
                [
                    self._safe(
                        finding.get(
                            "control_id",
                            "",
                        )
                    ),
                    self._safe(
                        finding.get(
                            "title",
                            "",
                        )
                    ),
                    self._safe(
                        finding.get(
                            "severity",
                            "",
                        )
                    ),
                ]
            )

        table = Table(
            data,
            colWidths=[
                35 * mm,
                95 * mm,
                30 * mm,
            ],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#333333"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(table)

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _severity_color(severity: str):

        severity = severity.upper()

        colors_map = {
            "CRITICAL": colors.HexColor("#B71C1C"),
            "HIGH": colors.HexColor("#E65100"),
            "MEDIUM": colors.HexColor("#F9A825"),
            "LOW": colors.HexColor("#2E7D32"),
        }

        return colors_map.get(
            severity,
            colors.grey,
        )

    @staticmethod
    def _safe(value):

        if value is None:
            return "None"

        return (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )