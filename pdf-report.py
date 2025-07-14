import json
from fpdf import FPDF
from datetime import datetime

# Load JSON data
with open("outputs/output.json", "r") as f:
    report_data = json.load(f)

# Extract fields
blast_center = report_data["blast_center"]
blast_radius = report_data["blast_radius"]
estimate_explosive_type = report_data["estimate_explosive_type"]
human_damage_report = report_data["human_damage_report"]
object_data = report_data.get("objects_detected", [])
summary = report_data.get("summary", {})

# Initialize PDF
pdf = FPDF()
pdf.add_page()

# Title
pdf.set_font("Arial", 'B', 16)
pdf.cell(0, 10, "ForenSight Blast Analysis Report", ln=True, align="C")
pdf.ln(5)

# Timestamp
pdf.set_font("Arial", size=12)
pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
pdf.ln(5)

# Blast details
pdf.cell(0, 10, f"Blast Center: {blast_center}", ln=True)
pdf.cell(0, 10, f"Blast Radius: {blast_radius:.2f} meters", ln=True)
pdf.cell(0, 10, f"Estimated Explosive Type: {estimate_explosive_type}", ln=True)
pdf.ln(10)

# Image output
pdf.image("outputs/output.jpg", w=180)
pdf.ln(10)

# Human Damage Report Table
pdf.set_font("Arial", 'B', 12)
pdf.cell(40, 10, "Person", 1)
pdf.cell(50, 10, "Distance (m)", 1)
pdf.cell(90, 10, "Status", 1)
pdf.ln()

pdf.set_font("Arial", size=12)
for idx, person in enumerate(human_damage_report, 1):
    pdf.cell(40, 10, f"#{idx}", 1)
    pdf.cell(50, 10, f"{person['distance_m']:.2f}", 1)
    pdf.cell(90, 10, person['status'], 1)
    pdf.ln()

pdf.ln(10)

# Summary Section
pdf.set_font("Arial", 'B', 12)
pdf.cell(0, 10, "Summary:", ln=True)
pdf.set_font("Arial", size=12)
pdf.cell(0, 10, f"People Before: {summary.get('people_before', 'N/A')}", ln=True)
pdf.cell(0, 10, f"People Visible After: {summary.get('people_visible_after', 'N/A')}", ln=True)
pdf.cell(0, 10, f"People Lost: {summary.get('people_lost', 'N/A')}", ln=True)
pdf.ln(10)

# Save the PDF
pdf.output("outputs/output.pdf")