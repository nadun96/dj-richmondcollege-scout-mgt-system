# from weasyprint import HTML
from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string
import jinja2
import pdfkit
import os
from fpdf import FPDF
from xhtml2pdf import pisa
from django.template.loader import get_template
import pandas as pd
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from patrol.models import Attendance
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
# Pdf kit configuration
# pdfkit.configuration(
#     wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')


""" working solution no header,footer, page numbers, etc """


def generate_member_attendance_report(year, member):

    attendances = Attendance.objects.filter(
        member__id=member.id, date__year=year).order_by('title', 'date', 'time')

    print(attendances)

    """ start style code with table lines """

    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)

    data = [['Title', 'Date', 'Time']]

    for attendance in attendances:
        title = attendance.title
        date = attendance.date.strftime("%m/%d")
        time = attendance.time.strftime("%I:%M %p")
        data.append([title, date, time])

    table = Table(data)

    table.setStyle(TableStyle([
        # Header row background color
        ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),  # Header row text color
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Header row alignment
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('FONTSIZE', (0, 0), (-1, 0), 12),  # Header row font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Header row bottom padding
        ('BACKGROUND', (0, 1), (-1, -1), '#FFFFFF'),  # Data row background color
        ('TEXTCOLOR', (0, 1), (-1, -1), '#000000'),  # Data row text color
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Data row font
        ('FONTSIZE', (0, 1), (-1, -1), 10),  # Data row font size
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),  # Data row bottom padding
        ('LINEBELOW', (0, 0), (-1, 0), 1, '#000000'),  # Header row bottom border
        ('LINEABOVE', (0, 1), (-1, 1), 1, '#CCCCCC'),  # First data row top border
        # Last data row bottom border
        ('LINEBELOW', (0, -1), (-1, -1), 1, '#CCCCCC'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, '#CCCCCC')  # Inner grid lines
    ]))

    table.wrapOn(p, 500, 500)

    table.drawOn(p, 50, 650)

    p.showPage()

    p.save()

    # Set the buffer pointer to the beginning
    buffer.seek(0)

    # Return the PDF file as a response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=attendance_report{member}_{year}.pdf'
    return response


def generate_member_attendance_report_htm2pdf(year, member):
    """ html to pdf solution not working os error"""

    attendances = Attendance.objects.filter(
        member__id=member.id, date__year=year).order_by('title', 'date', 'time')

    data = [['Title', 'Date', 'Time']]

    for attendance in attendances:
        title = attendance.title
        date = attendance.date.strftime("%m/%d")
        time = attendance.time.strftime("%I:%M %p")
        data.append([title, date, time])

    df = pd.DataFrame(data[1:], columns=data[0])

    # Create a HTML string of the table
    html_table = df.to_html(index=False)

    # Set up the HTML file and template
    template_path = 'attendance_report_template.html'
    context = {'html_table': html_table}
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF buffer and write the PDF to it
    buffer = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), buffer)
    if not pdf.err:
        response = HttpResponse(
            buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="member_attendance_report.pdf"'
        return response
    buffer.close()
    return HttpResponse('Error generating report.')


def generate_member_attendance_report_pandas(year, member):
    """ pandas solution not working os error """
    # Filter attendance records for the given year and member
    attendances = Attendance.objects.filter(
        member__id=member.id, date__year=year).order_by('title', 'date', 'time')

    # Convert the attendance data to a Pandas DataFrame
    data = []
    for attendance in attendances:
        title = attendance.title
        date = attendance.date.strftime("%m/%d")
        time = attendance.time.strftime("%I:%M %p")
        data.append([title, date, time])
    df = pd.DataFrame(data, columns=['Title', 'Date', 'Time'])

    # Generate the PDF report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 10, 'Attendance Report for %s, %s' %
             (member, year))
    pdf.ln()
    pdf.set_font('Arial', 'B', 10)
    col_width = pdf.w / 3.5
    row_height = pdf.font_size * 1.5
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln()
    pdf.set_font('Arial', '', 10)
    for row in df.values:
        for col in row:
            pdf.cell(col_width, row_height, str(col), border=1)
        pdf.ln()

    # Save the PDF to a BytesIO buffer
    buffer = BytesIO()
    pdf.output(buffer, 'F')
    buffer.seek(0)

    # Return the PDF file as a response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=attendance_report{member}_{year}.pdf'
    return response


""" pdfkit solution not working os error"""


def generate_member_attendance_report_pdfkit(year, member):
    # Load the Jinja2 template
    loader = jinja2.FileSystemLoader(searchpath='./manager/templates/reports')
    tmemplateEnv = jinja2.Environment(loader=loader)

    # view all templates in the folder TO:TEST
    print(tmemplateEnv.loader.list_templates())

    # get the template
    template = tmemplateEnv.get_template('matreport.html')

    # Get the data for the report
    attendances = Attendance.objects.filter(
        member__id=member.id, date__year=year).order_by('title', 'date', 'time')

    # data = [{'title': a.title, 'date': a.date.strftime(
    #     "%m/%d"), 'time': a.time.strftime("%I:%M %p")} for a in attendances]

    # Render the template with the data
    context = {'year': year, 'member': member, 'attendences': attendances}
    html = template.render(context)

    # test output
    print(html)
    path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(
        wkhtmltopdf=path)

    # Set options for pdfkit
    options = {
        'page-size': 'Letter',
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'encoding': "UTF-8",
        'no-outline': None,
    }

    # Create a PDF from the HTML using pdfkit
    pdf_file_name = f'attendance_report{member}_{year}.pdf'

    print(" config pass ")
    # pdfkit.from_string(html, pdf_file_name,
    #                    configuration=config, css='style.css')

    # pdfkit.from_string(html, pdf_file_name, options=options,
    #                    configuration=config)
    pdfkit.from_string(html, pdf_file_name, configuration=config)

    print(" from string 2 pass ")

    # Read the PDF into a response object
    with open(pdf_file_name, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={pdf_file_name}'

    # Delete the PDF file
    os.remove(pdf_file_name)

    return response


""" using weasyprint not working in my os error """


# def generate_member_attendance_report_weasyprint(year, member):
#     # Load the Jinja2 template
#     template = get_template('matreport.html')

#     # Get the data for the report
#     attendances = Attendance.objects.filter(
#         member__id=member.id, date__year=year).order_by('title', 'date', 'time')

#     # Render the template with the data
#     context = {'year': year, 'member': member, 'attendences': attendances}
#     html = template.render(context)

#     # Create a PDF from the HTML using weasyprint
#     pdf_file_name = f'attendance_report{member}_{year}.pdf'
#     pdf_file_path = os.path.join(settings.MEDIA_ROOT, pdf_file_name)

#     HTML(string=html).write_pdf(pdf_file_path)

#     # Read the PDF into a response object
#     with open(pdf_file_path, 'rb') as f:
#         response = HttpResponse(f.read(), content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename={pdf_file_name}'

#     # Delete the PDF file
#     os.remove(pdf_file_path)

#     return response
