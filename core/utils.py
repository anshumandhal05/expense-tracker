"""Core app — utility functions for PDF and CSV generation."""

import csv
from datetime import datetime

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def export_csv(queryset, filename="transactions.csv"):
    """Generate a CSV HttpResponse from a Transaction queryset."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Type", "Category", "Description", "Amount (₹)", "Payment Method"])

    for txn in queryset:
        writer.writerow(
            [
                txn.date.strftime("%Y-%m-%d"),
                txn.get_transaction_type_display(),
                txn.category.name if txn.category else "—",
                txn.description or "—",
                f"{txn.amount:.2f}",
                txn.get_payment_method_display(),
            ]
        )

    return response


def export_pdf(queryset, user, title="Transaction Report"):
    """Generate a styled PDF report using ReportLab."""
    response = HttpResponse(content_type="application/pdf")
    filename = f'expense_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(
        response, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm
    )
    styles = getSampleStyleSheet()
    story = []

    # ── Title ──
    title_style = ParagraphStyle(
        "title", parent=styles["Heading1"], fontSize=20, textColor=colors.HexColor("#6366f1"), spaceAfter=6
    )
    story.append(Paragraph(title, title_style))
    story.append(
        Paragraph(
            f'<font size="10" color="#6b7280">Generated for: {user.get_full_name() or user.username} &nbsp;|&nbsp; {datetime.now().strftime("%d %b %Y, %H:%M")}</font>',
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    # ── Summary row ──
    from django.db.models import Sum

    total_income = queryset.filter(transaction_type="INCOME").aggregate(s=Sum("amount"))["s"] or 0
    total_expense = queryset.filter(transaction_type="EXPENSE").aggregate(s=Sum("amount"))["s"] or 0
    balance = total_income - total_expense

    summary_data = [
        ["Total Income", "Total Expenses", "Net Balance"],
        [f"₹{total_income:,.2f}", f"₹{total_expense:,.2f}", f"₹{balance:,.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f5f3ff")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white]),
                ("ROUNDEDCORNERS", [3]),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Transaction Table ──
    story.append(Paragraph("Transaction Details", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * cm))

    headers = ["Date", "Type", "Category", "Description", "Amount (₹)", "Payment"]
    data = [headers]
    for txn in queryset:
        data.append(
            [
                txn.date.strftime("%d %b %Y"),
                txn.get_transaction_type_display(),
                txn.category.name if txn.category else "—",
                (txn.description or "—")[:35],
                f"₹{txn.amount:,.2f}",
                txn.get_payment_method_display(),
            ]
        )

    col_widths = [2.8 * cm, 2 * cm, 3.2 * cm, 5 * cm, 2.8 * cm, 2.2 * cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (4, 0), (4, -1), "RIGHT"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e5e7eb")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)

    doc.build(story)
    return response
