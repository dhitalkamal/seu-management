"""Reportlab-backed PDF generator for volunteer certificates."""

from __future__ import annotations

import io
import uuid
from datetime import datetime

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

from apps.volunteers.domain.repositories import ICertificatePdfGenerator


class ReportlabCertificatePdfGenerator(ICertificatePdfGenerator):
    """Generates a styled A4 PDF certificate using reportlab."""

    def generate(
        self,
        *,
        certificate_id: uuid.UUID,
        volunteer_name: str,
        event_name: str,
        role_name: str,
        hours_worked: float | None,
        rating: int | None,
        issued_at: datetime,
        verify_url: str,
    ) -> bytes:
        """Build and return the PDF bytes for the certificate."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        story = [
            Spacer(1, 2 * cm),
            Paragraph("Certificate of Volunteer Participation", styles["Title"]),
            Spacer(1, 0.5 * cm),
            Paragraph(f"This certifies that <b>{volunteer_name}</b> volunteered at", styles["Normal"]),
            Paragraph(f"<b>{event_name}</b> in the role of <b>{role_name}</b>.", styles["Normal"]),
            Spacer(1, 0.5 * cm),
        ]

        if hours_worked is not None:
            story.append(Paragraph(f"Hours worked: {hours_worked}", styles["Normal"]))
        if rating is not None:
            story.append(Paragraph(f"Performance rating: {rating}/5", styles["Normal"]))

        story += [
            Spacer(1, 0.5 * cm),
            Paragraph(f"Issued: {issued_at.strftime('%d %B %Y')}", styles["Normal"]),
            Paragraph(f"Certificate ID: {certificate_id}", styles["Normal"]),
            Spacer(1, 1 * cm),
            self._build_qr_image(verify_url),
            Spacer(1, 0.3 * cm),
            Paragraph("Scan the QR code to verify this certificate.", styles["Normal"]),
        ]

        doc.build(story)
        return buffer.getvalue()

    @staticmethod
    def _build_qr_image(verify_url: str) -> Image:
        """Generate a QR code image element for the given URL."""
        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(verify_url)
        qr.make(fit=True)
        pil_img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        return Image(buf, width=4 * cm, height=4 * cm)
