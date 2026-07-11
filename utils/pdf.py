import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from datetime import datetime
from utils.constants import format_etb

def generate_agreement_pdf(agreement_data: dict) -> bytes:
    """
    Generates a trade agreement PDF.
    agreement_data: dict with keys like producer_name, merchant_name, product_name, 
                    quantity, unit, price_etb, delivery_terms, payment_method.
    Returns: PDF as bytes.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "EthioChain Trade Agreement")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    p.line(50, height - 80, width - 50, height - 80)
    
    # Parties
    y = height - 110
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Parties Involved")
    y -= 20
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Producer: {agreement_data.get('producer_name', 'N/A')}")
    y -= 15
    p.drawString(50, y, f"Merchant: {agreement_data.get('merchant_name', 'N/A')}")
    
    # Product Details
    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Product & Pricing Details")
    y -= 20
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Product: {agreement_data.get('product_name', 'N/A')}")
    y -= 15
    p.drawString(50, y, f"Quantity: {agreement_data.get('quantity', 0)} {agreement_data.get('unit', 'units')}")
    y -= 15
    p.drawString(50, y, f"Total Price: {format_etb(agreement_data.get('price_etb', 0))}")
    
    # Terms
    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Terms & Conditions")
    y -= 20
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Delivery Terms: {agreement_data.get('delivery_terms', 'N/A')}")
    y -= 15
    p.drawString(50, y, f"Payment Method: {agreement_data.get('payment_method', 'N/A')}")
    
    # Signatures
    y -= 60
    p.line(50, y, 250, y)
    p.line(350, y, 550, y)
    y -= 15
    p.drawString(50, y, "Producer Signature")
    p.drawString(350, y, "Merchant Signature")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()
