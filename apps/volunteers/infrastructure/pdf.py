"""Reportlab-based PDF generator for volunteer certificates."""

from __future__ import annotations

import io

from apps.volunteers.domain.entities import CertificateEntity
from apps.volunteers.domain.repositories import ICertificatePdfGenerator


class ReportlabCertificatePdfGenerator(ICertificatePdfGenerator):
    """Generates a simple certificate PDF using reportlab."""

    def generate(self, certificate: CertificateEntity, volunteer_name: str, event_name: str) -> bytes:
        """Build and return the PDF bytes."""
        try:
            from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
            from reportlab.pdfgen import canvas  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError("reportlab is required to generate certificates.") from exc

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(width / 2, height - 150, "Certificate of Participation")

        c.setFont("Helvetica", 18)
        c.drawCentredString(width / 2, height - 220, "This certifies that")
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(width / 2, height - 260, volunteer_name)

        c.setFont("Helvetica", 18)
        c.drawCentredString(width / 2, height - 300, "has volunteered at")
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2, height - 340, event_name)

        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, 100, f"Verify at: {certificate.verify_url}")
        c.drawCentredString(width / 2, 80, f"Certificate ID: {certificate.id}")

        c.save()
        return buffer.getvalue()
