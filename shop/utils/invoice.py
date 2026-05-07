import io
from datetime import datetime
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

def val(x):
    """Helper to return '-' if value is empty."""
    return str(x) if x else "-"

def generate_invoice(order):
    """
    Generates a PDF invoice for the given order matching the strict layout.
    Saves it to order.invoice_file.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=10*mm,
        bottomMargin=10*mm
    )
    
    styles = getSampleStyleSheet()
    style_n = styles["Normal"]
    style_b = ParagraphStyle('Bold', parent=style_n, fontName='Helvetica-Bold')
    style_title = ParagraphStyle('Title', parent=style_b, fontSize=14)
    
    story = []

    # --- HEADER BLOCK (Company + Metadata) ---
    # Left: Company Info | Right: Metadata Table
    company_info = [
        [Paragraph("<b>OCHRE SPIRITS PRIVATE LIMITED</b>", style_title)],
        [Paragraph("Full Address: 123 Spirit Lane, Indiranagar,<br/>Bengaluru, Karnataka - 560038", style_n)],
        [Paragraph(f"GSTIN: {getattr(settings, 'COMPANY_GSTIN', '-')}", style_n)],
        [Paragraph("State Name: Karnataka, Code: 29", style_n)],
        [Paragraph(f"Email: {settings.CONTACT_EMAIL}", style_n)],
    ]
    
    meta_data = [
        ["Invoice No.", str(order.uuid.hex[:8].upper()), "Dated", val(order.created_at.strftime('%d-%b-%y') if order.created_at else "-")],
        ["Delivery Note", val(getattr(order, "delivery_note", "")), "Mode/Terms of Payment", val(getattr(order, "mode_of_payment", ""))], # type: ignore
        ["Reference No & Date", val(getattr(order, "reference_no", "")), "Other References", val(getattr(order, "other_references", ""))], # type: ignore
        ["Buyer's Order No.", val(getattr(order, "buyer_order_no", "")), "Dated", val(getattr(order, "delivery_note_date", ""))], # type: ignore
        ["Dispatch Doc No.", val(getattr(order, "dispatch_doc_no", "")), "Delivery Note Date", val(getattr(order, "delivery_note_date", ""))], # type: ignore
        ["Dispatched through", val(getattr(order, "dispatched_through", "")), "Destination", val(getattr(order, "destination", ""))], # type: ignore
    ]
    
    meta_table = Table(meta_data, colWidths=[30*mm, 35*mm, 40*mm, 35*mm])
    meta_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    header_data = [
        [Table(company_info, colWidths=[60*mm]), meta_table]
    ]
    
    header_table = Table(header_data, colWidths=[65*mm, 140*mm])
    header_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(header_table)

    # --- CONSIGNEE + BUYER BLOCK ---
    consignee_buyer_data = [
        [Paragraph("<b>Consignee (Ship to)</b>", style_b), Paragraph("<b>Buyer (Bill to)</b>", style_b)],
        [
            Paragraph(f"{val(order.user.get_full_name() if order.user else 'Guest')}<br/>Address: {val(getattr(order, 'shipping_address', '-'))}<br/>GSTIN/UIN: -<br/>State Name: {val(getattr(order, 'shipping_state', '-'))}", style_n),
            Paragraph(f"{val(order.user.get_full_name() if order.user else 'Guest')}<br/>Address: {val(getattr(order, 'billing_address', '-'))}<br/>GSTIN/UIN: -<br/>State Name: {val(getattr(order, 'billing_state', '-'))}", style_n)
        ]
    ]
    cb_table = Table(consignee_buyer_data, colWidths=[97.5*mm, 97.5*mm])
    cb_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(cb_table)

    # --- ITEM TABLE ---
    item_header = ["Sl\nNo", "Description of Goods", "HSN/SAC", "Quantity", "Rate", "per", "Disc %", "Amount"]
    item_rows = [item_header]
    
    subtotal = 0
    items = order.items.all() if hasattr(order, "items") else []
    for i, item in enumerate(items, 1):
        qty = getattr(item, 'qty', 1)
        price = getattr(item, 'unit_price', 0)
        line_total = qty * price
        subtotal += line_total
        
        item_rows.append([
            str(i),
            Paragraph(val(item.title), style_n),
            val(getattr(item, 'hsn_code', '-')),
            f"{qty} Nos",
            f"{price:.2f}",
            "Nos",
            "-",
            f"{line_total:.2f}"
        ])

    for _ in range(max(0, 10 - len(items))):
        item_rows.append(["", "", "", "", "", "", "", ""])

    grand_total = order.total
    tax_amt = order.tax_total

    item_rows.append(["", "CGST", "", "", "", "", "", f"{tax_amt/2:.2f}"])
    item_rows.append(["", "SGST", "", "", "", "", "", f"{tax_amt/2:.2f}"])
    item_rows.append(["", Paragraph("Total", style_b), "", f"{sum(getattr(i,'qty',1) for i in items)} Nos", "", "", "", f"{grand_total:.2f}"])

    item_table = Table(item_rows, colWidths=[10*mm, 70*mm, 20*mm, 20*mm, 20*mm, 15*mm, 15*mm, 25*mm])
    item_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('ALIGN', (0,0), (2,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(item_table)

    footer_data = [
        [Paragraph(f"Amount Chargeable (in words):<br/><b>INR {grand_total:.2f}</b>", style_n), ""],
        [Paragraph("<b>Declaration:</b><br/>We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.", style_n), 
         Paragraph("for <b>OCHRE SPIRITS PRIVATE LIMITED</b><br/><br/><br/>Authorised Signatory", style_n)]
    ]
    
    footer_table = Table(footer_data, colWidths=[120*mm, 75*mm])
    footer_table.setStyle(TableStyle([('GRID', (0,0), (-1,0), 0.5, colors.black), ('GRID', (0,1), (0,1), 0.5, colors.black), ('GRID', (1,1), (1,1), 0.5, colors.black), ('ALIGN', (1,1), (1,1), 'RIGHT'), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(footer_table)
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("This is a Computer Generated Invoice", style_n))

    doc.build(story)
    order.invoice_file.save(f"Invoice_{order.uuid.hex[:8].upper()}.pdf", ContentFile(buffer.getvalue()), save=True)
    buffer.close()
