from django.http import HttpResponse, FileResponse
from reportlab.graphics.charts.barcharts import HorizontalBarChart, VerticalBarChart
from reportlab.graphics.shapes import Drawing
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageTemplate, BaseDocTemplate)
from django.db.models import Sum
from django.db.models import Count
from reportlab.lib.styles import getSampleStyleSheet , ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle 
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.utils import timezone
from django.conf import settings
from fpdf import FPDF
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import os
import base64
# Define a class for our custom FPDF object
from patrol.models import Attendance
from manager.models import Patrol
from core.models import MembershipFee
from collections import defaultdict
from member.models import Hike , Camp , Project , Badge , Requirement

""" later imports """

# from weasyprint import HTML
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.colors import black, white
from reportlab.pdfbase.pdfmetrics import stringWidth
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
from datetime import datetime
from patrol.models import Attendance
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from manager.models import Patrol


""" pypdf solution not working os error """
class PyFPF(FPDF):

    # Initialize the document with header and footer
    def __init__(self):
        super().__init__()
        self.header_text = "My Header"
        self.footer_text = "Page {0}/{{nb}} - My Footer".format(self.page_no())

    # Add the header to each page
    def header(self):
        # Set the font and size for the header
        self.set_font('Arial', 'B', 12)
        # Add the header text
        self.cell(0, 10, self.header_text, 0, 0, 'L')
        # Move the cursor to the right
        self.cell(0, 10, "", 0, 0, 'R')
        # Add the page number
        self.cell(0, 10, str(self.page_no()), 0, 0, 'R')
        # Add a line below the header
        self.line(10, 20, self.w-10, 20)

    # Add the footer to each page
    def footer(self):
        # Set the font and size for the footer
        self.set_font('Arial', '', 8)
        # Add the footer text
        self.cell(0, 10, self.footer_text, 0, 0, 'C')

def generate_pdf():
    # Create a new PyFPF object
    pdf = PyFPF()

    # Add a page to the document
    pdf.add_page()

    # Set the font and size for the table header
    pdf.set_font('Arial', 'B', 12)

    # Create a data table
    data = [['Name', 'Age', 'Gender'],
            ['John', '25', 'Male'],
            ['Jane', '30', 'Female'],
            ['Jack', '20', 'Male'],
            ['Jill', '35', 'Female']]

    # Set the width of each column in the table
    col_width = pdf.w / 3.5

    # Loop through the data and add it to the table
    for row in data:
        for item in row:
            # Add the item to the table cell
            pdf.cell(col_width, 10, str(item), border=1)
        # Move to the next line
        pdf.ln()
        
    # Output the PDF file to a byte stream
    pdf_bytes = BytesIO()
    pdf.output(dest='F' , name='attendance.pdf')
    pdf_bytes.flush()
    
    # Save the PDF file to the server
    file_path = os.path.join(settings.MEDIA_ROOT, 'attendance.pdf')
    # with open(file_path, 'wb') as f:
    #     f.write(pdf_bytes.getvalue())


    # Create an HTTP response with the PDF file
    response = HttpResponse(pdf_bytes.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance.pdf"'
    response['Content-Length'] = pdf_bytes.tell()

    # os.remove(file_path)

    return response

""" html to pdf solution not working os error"""

def generate_member_attendance_report_htm2pdf(year, member):

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

""" pandas solution not working os error """

def generate_member_attendance_report_pandas(year, member):
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

def generate_member_attendance_report_weasyprint(year, member):
    # Load the Jinja2 template
    template = get_template('matreport.html')

    # Get the data for the report
    attendances = Attendance.objects.filter(
        member__id=member.id, date__year=year).order_by('title', 'date', 'time')

    # Render the template with the data
    context = {'year': year, 'member': member, 'attendences': attendances}
    html = template.render(context)

    # Create a PDF from the HTML using weasyprint
    pdf_file_name = f'attendance_report{member}_{year}.pdf'
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, pdf_file_name)

    #HTML(string=html).write_pdf(pdf_file_path)

    # Read the PDF into a response object
    with open(pdf_file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={pdf_file_name}'

    # Delete the PDF file
    os.remove(pdf_file_path)

    return response

""" write member attendance report to pdf """
def generate_member_attendance_report_new(year, member):
    
    # get attendance for table
    attendances = Attendance.objects.filter(
        member__id=member.id, date__year=year).order_by('title', 'date', 'time')

    # Create a buffer to store the PDF file
    buffer = BytesIO()

    # Create the PDF document object
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Define the contents of the header
    header_text = f'<u>{member} Attendance Report ({year})</u>'

    # Define the styles for the header and footer
    styles = getSampleStyleSheet()
    header_style = styles['Heading1']
    header = Paragraph(header_text, header_style)
    footer_style = styles['Normal']

    # Define the contents of the header and footer
    header_text = f'<h1>RCSG</h1> </br> <h1 class="report-title"><u>{member} Attendance Report ({year})</u></h1>'
    footer_text = f'This Report was Generated by RCSG MIS on {timezone.now().strftime("%m/%d/%Y %I:%M %p")}'
    footer = Paragraph(footer_text, footer_style)
    
    # Define the contents of the table
    data = [['#', 'Title', 'Date', 'Time']]
    
    # add attendances to table
    if attendances.exists():
        for i, attendance in enumerate(attendances):
            title = 'Sat' if attendance.title == '' else attendance.title
            date = attendance.date.strftime("%m/%d")
            time = attendance.time.strftime("%I:%M %p")
            data.append([str(i+1), title, date, time])
            
    # set colWidths of report
    col_widths = [doc.width/10]*1 + [doc.width*5/10]*1 + [doc.width/6]*2

    # Define the table style
    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("SPAN", (0, 0), (0, 0)),
        ('BACKGROUND', (0, 2), (-1, -1), '#FFFFFF'),  # Data row background color
        ('TEXTCOLOR', (0, 2), (-1, -1), '#000000'),  # Data row text color
        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),  # Data row font
        ('FONTSIZE', (0, 2), (-1, -1), 10),  # Data row font size
        ('BOTTOMPADDING', (0, 2), (-1, 1), 8),  # Data row bottom padding
        # Last data row bottom border
        ('LINEBELOW', (0, -1), (-1, -1), 1, '#CCCCCC'),
        ('INNERGRID', (0, 1), (-1, -1), 0.25, '#CCCCCC')  # Inner grid lines
    ])

    # Define the elements to be included in the PDF document
    elements = []
    elements.append(header)
    elements.append(Spacer(1, 0.25*inch))
    

    # get count of total attendance
    count_total = Attendance.objects.filter(
        member__id=member.id, date__year=year).count()

    # Add count of total attendance to the PDF document
    if count_total:
        elements.append(Paragraph(
            f'<b><i>Total Attendance:</i></b>  {count_total}', styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
    else:
        elements.append(
            Paragraph('No attendance records found.', styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))

    # get count of Saturday attendance
    count_saturday = Attendance.objects.filter(
        member__id=member.id, date__year=year, title='').\
        values('title').annotate(total_attendance=Count('id'))


    # Add count of Saturday attendance to the PDF document
    if count_saturday:
        elements.append(Paragraph(
            f'<b><i>Saturday Attendance:</i></b>   {count_saturday[0]["total_attendance"]}', styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
    else:
        elements.append(
            Paragraph('No Saturday attendance records found.', styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    
    
    elements.append(table)
    elements.append(Spacer(1, 0.25*inch))
    elements.append(footer)

    # new function to add page numbers
    def add_page_numbers(canvas, doc, telephone_number, address):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        page_num = f'Page {doc.page}'
        center = 3  # change this value as per your requirement
        canvas.drawString(inch/2 - len(page_num)*2.5, 0.4*inch, page_num)
        canvas.drawCentredString(center*inch, 0.4*inch, telephone_number)
        canvas.drawCentredString(6.25*inch, 0.4*inch, address)
        canvas.restoreState()

    # new add
    doc.build(elements, onFirstPage=lambda canvas, doc: add_page_numbers(canvas, doc, '091-3135024', 'Richmond College,Richmond Hill, Galle'),
              onLaterPages=lambda canvas, doc: add_page_numbers(canvas, doc, '091-3135024', 'Richmond College,Richmond Hill, Galle'))
    
    buffer.seek(0)

    # Return the PDF file as a response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=attendance_report{member}_{year}.pdf'
    return response

""" write attendance report to pdf file """
def generate_patrol_attendance_report_new(year, patrol):

    # get attendance for patrol
    try:
        patrol = Patrol.objects.get(pk=patrol.id)
        print(f'{patrol.id} patrol found')

    except:
        print("Patrol not found")

    try:
        attendances = Attendance.objects.filter(
            member__patrol=patrol.id, date__year=year
        ).order_by("title", "member", "date", "time")

    except:
        print("No attendances found")
        attendances = None

    buffer = BytesIO()

    # Create the PDF document object
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Define the contents of the header
    header_text = f'<u>{patrol} Attendance Report ({year})</u>'
    
    # Define the styles for the header and footer
    styles = getSampleStyleSheet()
    header_style = styles['Heading1']
    header = Paragraph(header_text, header_style)
    footer_style = styles['Normal']
    
    # Define the contents of the header and footer
    header_text = f'<h1>RCSG</h1> </br> <h1 class="report-title"><u>{ patrol } Attendance Report ({ year })</u></h1>'
    footer_text = f'This Report was Generated by RCSG MIS on {timezone.now().strftime("%m/%d/%Y %I:%M %p")}'
    footer = Paragraph(footer_text, footer_style)
    
    # Define a dictionary to store the count of each title
    title_counts = defaultdict(int)
    for attendance in attendances:
        attendance.title = 'Saturdays' if attendance.title == '' else attendance.title
        title = attendance.title.strip()
        #if title != '':
        title_counts[title] += 1
    

    # Convert the dictionary to a list of lists for table formatting
    title_table_data = [['Title', 'Count']]
    for title, count in title_counts.items():
        title_table_data.append([title, str(count)])

    # Define the column widths and table style
    title_col_widths = [doc.width*7/10, doc.width*3/10]
    title_table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), '#FFFFFF'),  # Data row background color
        ('TEXTCOLOR', (0, 1), (-1, -1), '#000000'),  # Data row text color
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Data row font
        ('FONTSIZE', (0, 1), (-1, -1), 10),  # Data row font size
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),  # Data row bottom padding
        ('LINEBELOW', (0, 0), (-1, 0), 1, '#CCCCCC'),  # Header underline
        # Last data row bottom border
        ('LINEBELOW', (0, -1), (-1, -1), 1, '#CCCCCC'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, '#CCCCCC')  # Inner grid lines
    ])

    # Create the table
    title_table = Table(title_table_data, colWidths=title_col_widths)
    title_table.setStyle(title_table_style)


    # Define the contents of the table
    data = [['#', 'Member', 'Title', 'Date', 'Time']]

    # add attendances to table
    if attendances.exists():
        for i , attendance in enumerate(attendances):
            member = attendance.member
            title = 'Saturday' if attendance.title == '' else attendance.title
            date = attendance.date.strftime("%m/%d")
            time = attendance.time.strftime("%I:%M %p")
            data.append([str(i+1), member, title, date, time])

    # set colWidths of report
    col_widths = [doc.width/10]*1 + [doc.width*2/10] * \
        1 + [doc.width*5/10]*1 + [doc.width/10]*2
    
    # Define the table style
    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("SPAN", (0, 0), (0, 0)),
        ('BACKGROUND', (0, 2), (-1, -1), '#FFFFFF'),  # Data row background color
        ('TEXTCOLOR', (0, 2), (-1, -1), '#000000'),  # Data row text color
        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),  # Data row font
        ('FONTSIZE', (0, 2), (-1, -1), 10),  # Data row font size
        ('BOTTOMPADDING', (0, 2), (-1, 1), 8),  # Data row bottom padding
        # Last data row bottom border
        ('LINEBELOW', (0, -1), (-1, -1), 1, '#CCCCCC'),
        ('INNERGRID', (0, 1), (-1, -1), 0.25, '#CCCCCC')  # Inner grid lines
    ])
    
    # Define the elements to be included in the PDF document
    elements = []
    elements.append(header)
    elements.append(Spacer(1, 0.25*inch))
    
    # get count of total attendance
    
    count_total = attendances.count()

    # Add count of total attendance to the PDF document
    if count_total:
        elements.append(Paragraph(
            f'<b><i>Total Attendance:</i></b>  {count_total}', styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
    else:
        elements.append(
            Paragraph('No attendance records found.', styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
    
    # create table 
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    
    # tite of title_table
    elements.append(
        Paragraph('<b><u>Count of Attendance for each Event</u></b>', styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    
    elements.append(title_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # tite of info_table
    elements.append(
        Paragraph('<b><u>Detailed Attendance Table</u></b>', styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    
    elements.append(table)
    elements.append(Spacer(1, 0.25*inch))
    elements.append(footer)
    
    # new function to add page numbers
    def add_page_numbers(canvas, doc, telephone_number, address):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        page_num = f'Page {doc.page}'
        center = 3  # change this value as per your requirement
        canvas.drawString(inch/2 - len(page_num)*2.5, 0.4*inch, page_num)
        canvas.drawCentredString(center*inch, 0.4*inch, telephone_number)
        canvas.drawCentredString(6.25*inch, 0.4*inch, address)
        canvas.restoreState()

    # new add
    doc.build(elements, onFirstPage=lambda canvas, doc: add_page_numbers(canvas, doc, '091-3135024', 'Richmond College,Richmond Hill, Galle'),
              onLaterPages=lambda canvas, doc: add_page_numbers(canvas, doc, '091-3135024', 'Richmond College,Richmond Hill, Galle'))
    buffer.seek(0)
    
    # Return the PDF file as a response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=attendance_report{member}_{year}.pdf'
    return response

""" write a new function to generate attendance report for a given year and title """
def generate_event_attendance_report_new(year, title):

    # Get attendance for table
    attendances = Attendance.objects.filter(title=title, date__year=year).order_by(
        "member__patrol__name", "member"
    )

    # Create a buffer to store the PDF file
    buffer = BytesIO()
    
    title = 'Saturday Meeting' if title == '' else title 

    # Create the PDF document object
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Define the contents of the header and footer
    header_text = f"<h1><u>{title} Attendance Report ({year})</u></h1>"
    styles = getSampleStyleSheet()
    header_style = styles["Heading1"]
    header = Paragraph(header_text, header_style)
    footer_style = styles["Normal"]
    footer_text = f"This Report was Generated by RCSG MIS on {timezone.now().strftime('%m/%d/%Y %I:%M %p')}"
    footer = Paragraph(footer_text, footer_style)

    # Define the contents of the table
    data = [["#.", "Name", "Patrol", "Details"]]

    # Add attendances to table
    if attendances.exists():
        for i, attendance in enumerate(attendances):
            member_name = attendance.member
            patrol_name = attendance.member.patrol.name if attendance.member.patrol is not None else ""
            date = attendance.date.strftime("%m/%d")
            time = attendance.time.strftime("%I:%M %p")
            data.append([str(i+1), member_name, patrol_name, f"{date} {time}"])

    # Set colWidths of report
    col_widths = [doc.width/20]*1 + [doc.width*7/20] * \
        1 + [doc.width*5/20]*1 + [doc.width*5/20]*1

    # Define the table style
    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("SPAN", (0, 0), (0, 0)),
        ('BACKGROUND', (0, 2), (-1, -1), '#FFFFFF'),  # Data row background color
        ('TEXTCOLOR', (0, 2), (-1, -1), '#000000'),  # Data row text color
        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),  # Data row font
        ('FONTSIZE', (0, 2), (-1, -1), 10),  # Data row font size
        ('BOTTOMPADDING', (0, 2), (-1, 1), 8),  # Data row bottom padding
        # Last data row bottom border
        ('LINEBELOW', (0, -1), (-1, -1), 1, '#CCCCCC'),
        ('INNERGRID', (0, 1), (-1, -1), 0.25, '#CCCCCC')  # Inner grid lines
    ])

    # Define the elements to be included in the PDF document
    elements = []
    elements.append(header)
    elements.append(Spacer(1, 0.25*inch))

    # Add count of total attendance to the PDF document
    count_total = attendances.count()
    if count_total:
        elements.append(Paragraph(
            f"<b><i>Total Attendance:</i></b> {count_total}", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))
    else:
        elements.append(
            Paragraph("No attendance records found.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    
    # create table
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)

    elements.append(Spacer(1, 0.25*inch))

    elements.append(table)
    elements.append(Spacer(1, 0.25*inch))
    elements.append(footer)

       
    # new function to add page numbers 
    def add_page_numbers(canvas, doc, telephone_number, address):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        page_num = f'Page {doc.page}'
        center = 3  # change this value as per your requirement
        canvas.drawString(inch/2 - len(page_num)*2.5, 0.4*inch, page_num)
        canvas.drawCentredString(center*inch, 0.4*inch, telephone_number)
        canvas.drawCentredString(6.25*inch, 0.4*inch, address)
        canvas.restoreState()
    
    # new add
    doc.build(elements, onFirstPage=lambda canvas, doc: add_page_numbers(canvas, doc, '091-3135024', 'Richmond College,Richmond Hill, Galle'),
              onLaterPages=lambda canvas, doc: add_page_numbers(canvas, doc, '091-3135024', 'Richmond College,Richmond Hill, Galle'))

    
    buffer.seek(0)

    # Return the PDF file as a response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=attendance_report{title}_{year}.pdf'
    return response

""" generate membership fee paid report """

def generate_membership_fee_paid_report_new(year):
    # Get membership fees paid for table
    memberships = MembershipFee.objects.filter(for_year__year=year, is_paid=True).order_by(
        "member__patrol__name", "member"
    )
    
    print(memberships)

    # Create a buffer to store the PDF file
    buffer = BytesIO()

    # Create the PDF document object
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Define the contents of the header and footer
    header_text = f"<h1><u>Membership Fees Paid Report ({year})</u></h1>"
    styles = getSampleStyleSheet()
    header_style = styles["Heading1"]
    header = Paragraph(header_text, header_style)
    footer_style = styles["Normal"]
    footer_text = f"This Report was Generated by RCSG MIS on {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
    footer = Paragraph(footer_text, footer_style)

    # Define the contents of the table
    data = [["#", "Name", "Patrol", "Amount Paid"]]

        
    # Set column widths of the table
    col_widths = [doc.width/20]*1 + [doc.width*7/20] * \
        1 + [doc.width*5/20]*1 + [doc.width*5/20]*1

    # Define the style of the table
    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("SPAN", (0, 0), (0, 0)),
        ('BACKGROUND', (0, 2), (-1, -1), '#FFFFFF'),  # Data row background color
        ('TEXTCOLOR', (0, 2), (-1, -1), '#000000'),  # Data row text color
        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),  # Data row font
        ('FONTSIZE', (0, 2), (-1, -1), 10),  # Data row font size
        ('BOTTOMPADDING', (0, 2), (-1, 1), 8),  # Data row bottom padding
        # Last data row bottom border
        ('LINEBELOW', (0, -1), (-1, -1), 1, '#CCCCCC'),
        ('INNERGRID', (0, 1), (-1, -1), 0.25, '#CCCCCC')  # Inner grid lines
    ])

    # Define the elements to be included in the PDF document
    elements = []
    elements.append(header)
    elements.append(Spacer(1, 0.25*inch))
    

    # Add total amount paid to the PDF document
    total_amount_paid = memberships.aggregate(Sum('amount'))['amount__sum']
    if total_amount_paid:
        elements.append(Paragraph(
            f"<b>Total Amount Received:</b>   Rs. {total_amount_paid}", styles["Normal"]))    
    else:
        total_amount_paid = 0 if total_amount_paid is None else total_amount_paid
        elements.append(Paragraph(
            f"<b>Total Amount Received:</b>   Rs. { total_amount_paid }", styles["Normal"]))  
    elements.append(Spacer(0.5, 0.25*inch)) 
     
    membership_paid_count = memberships.count() 
    if membership_paid_count:
        elements.append(Paragraph(
            f"<b>Number of Members Paid:</b>   {membership_paid_count}", styles["Normal"]))
    else:
        # Show "No membership fees paid records found" message
        membership_paid_count = 0 if membership_paid_count is None else membership_paid_count
        elements.append(Paragraph(
            f"<b>Total Amount Received:</b>   Rs. { membership_paid_count }", styles["Normal"]))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add membership fee records to the table
    if memberships.exists():
        for i, membership in enumerate(memberships):
            member_name = membership.member
            patrol_name = membership.member.patrol.name if membership.member.patrol is not None else ""
            amount_paid = f"Rs. {membership.amount}"
            data.append([str(i+1), member_name, patrol_name, amount_paid])
    # else:
    #     # Show "No membership fees paid records found" message
    #     # data.append(["", "", "", ""])
    #     # data.append(["", "No membership fees paid records found.", "", ""])
    #     elements.append(Paragraph(
    #         '<b><i>No membership fee records found.</i></b>',styles["Normal"]))
    
    if data.__len__() > 1:
        # Add the table to the PDF document
        table = Table(data, colWidths=col_widths)
        table.setStyle(table_style)
        elements.append(table)  
    else:
        elements.append(Paragraph(
            f'<b><i>No membership fee paid records found for year {year}</i></b>',styles["Normal"]))

   
    elements.append(Spacer(1, 0.25*inch))
    elements.append(footer)

    # Function to add page numbers
    def add_page_numbers(canvas, doc, telephone_number, address):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        page_num = f'Page {doc.page}'
        center = 3  # change this value as per your requirement
        canvas.drawString(inch/2 - len(page_num)*2.5, 0.4*inch, page_num)
        canvas.drawCentredString(center*inch, 0.4*inch, telephone_number)
        canvas.drawCentredString(6.25*inch, 0.4*inch, address)
        canvas.restoreState()

    # Build the PDF document and add the page numbers
    doc.build(elements,
              onFirstPage=lambda canvas, doc: add_page_numbers(
                  canvas, doc, 'Tel: 091-3135024', 'Address: Richmond College,Richmond Hill, Galle'),
              onLaterPages=lambda canvas, doc: add_page_numbers(
                  canvas, doc, 'Tel: 091-3135024', 'Address: Richmond College,Richmond Hill, Galle'))

    buffer.seek(0)

    # Return the PDF file as a response
    response = HttpResponse(buffer, content_type='application/pdf')
    response[
        'Content-Disposition'] = f'attachment; filename=membership_fees_paid_report_{year}.pdf'
    return response

""" generate_event_list_report_new(year) - Generates a PDF report of all hikes, camps, and projects for the given year. """

def generate_event_list_report_new(year):
    # Get hikes, camps, and projects for the given year
    hikes = Hike.objects.filter(year__year=year).order_by("date")
    camps = Camp.objects.filter(date__year=year).order_by("date")
    projects = Project.objects.filter(date__year=year).order_by("date")

    # Create a buffer to store the PDF file
    buffer = BytesIO()

    # Create the PDF document object
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Define the contents of the header and footer
    header_text = f"<h1><u>Event List Report ({year})</u></h1>"
    styles = getSampleStyleSheet()
    header_style = styles["Heading1"]
    header = Paragraph(header_text, header_style)
    footer_style = styles["Normal"]
    footer_text = f"This report was generated by RCSG MIS on {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
    footer = Paragraph(footer_text, footer_style)

    
    # Define the styles of the tables
    table_header_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("SPAN", (0, 0), (0, 0))
    ])

    table_data_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#CCCCCC")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#000000")),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.HexColor("#000000"))
    ])

    # Define the elements to be included in the PDF document
    elements = []
    elements.append(header)
    elements.append(Spacer(1, 0.25*inch))
    
    # Create a bar chart showing counts of hikes, camps, and projects
    chart_data = [(len(hikes), len(camps), len(projects))]
    drawing = Drawing(400, 200)
    bc = VerticalBarChart()
    bc.width = 400
    bc.height = 200
    bc.data = chart_data
    bc.strokeColor = colors.black
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(len(hikes), len(camps), len(projects)) + 1
    bc.valueAxis.valueStep = 1  # set the step size to 1
    bc.valueAxis.labelTextFormat = '%d'  # format labels as integers
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 45
    bc.categoryAxis.categoryNames = ['Hikes', 'Camps', 'Projects']
    drawing.add(bc)
    elements.append(
        Paragraph("<b><u>Event Compraison</u></b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(drawing)
    elements.append(Spacer(1, 0.25*inch))

    # Add hikes table to the PDF document
    if hikes.exists():
        data = [["#", "Title", "Date", "Time", "Location"]]
        for i, hike in enumerate(hikes):
            data.append([str(i+1), hike.title, hike.date.strftime("%m/%d/%Y"),
                        hike.time.strftime("%I:%M %p"), hike.location])
        table = Table(data)  # colWidths=col_widths
        table.setStyle(table_header_style)
        table.setStyle(table_data_style)
        elements.append(Paragraph("<b><u>Hikes</u></b>", styles["Heading2"]))
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))
    else:
        elements.append(Paragraph("<b><u>Hikes</u></b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"No hikes found for the year { year }.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    if camps.exists():
        data = [["#", "Title", "Date", "Time", "Nights", "Location"]]
        for i, camp in enumerate(camps):
            data.append([str(i+1), camp.title, camp.date.strftime("%m/%d/%Y"),
                        camp.time.strftime("%I:%M %p"), camp.nights, camp.location])
        table = Table(data)
        table.setStyle(table_header_style)
        table.setStyle(table_data_style)
        elements.append(Spacer(1, 0.25*inch))
        elements.append(Paragraph("<b><u>Camps</u></b>", styles["Heading2"]))
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))

    else:
        elements.append(Paragraph("<b><u>Camps</u></b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"No camps found for the year { year }.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    # Add projects table to the PDF document
    if projects.exists():
        data = [["#", "Title", "Date", "Time", "Location"]]
        for i, project in enumerate(projects):
            data.append([str(i+1), project.title, project.date.strftime("%m/%d/%Y"),
                        project.time.strftime("%I:%M %p"), project.location])
        table = Table(data)
        table.setStyle(table_header_style)
        table.setStyle(table_data_style)
        elements.append(Spacer(1, 0.25*inch))
        elements.append(Paragraph("<b><u>Projects</u></b>", styles["Heading2"]))
        elements.append(table)
    else:
        elements.append(Paragraph("<b><u>Projects</u></b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"No projects found for the year { year }.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    # If no events found, add message to the PDF document
    if not hikes.exists() and not camps.exists() and not projects.exists():
        elements.append(
            Paragraph("No events found for the given year.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    # append footer to the elements
    elements.append(Spacer(1, 0.25*inch))
    elements.append(footer)

    # Function to add page numbers
    def add_page_numbers(canvas, doc, telephone_number, address):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        page_num = f'Page {doc.page}'
        center = 3  # change this value as per your requirement
        canvas.drawString(inch/2 - len(page_num)*2.5, 0.4*inch, page_num)
        canvas.drawCentredString(center*inch, 0.4*inch, telephone_number)
        canvas.drawCentredString(6.25*inch, 0.4*inch, address)
        canvas.restoreState()

    # Build the PDF document and return as an HTTP response
    doc.build(elements,
              onFirstPage=lambda canvas, doc: add_page_numbers(
                  canvas, doc, f'Tel: 091-3135024', f'Address: Richmond College,Richmond Hill, Galle'),
              onLaterPages=lambda canvas, doc: add_page_numbers(
                  canvas, doc, f'Tel: 091-3135024', f'Address: Richmond College,Richmond Hill, Galle'))

    buffer.seek(0)
    
    # Create HTTP response with PDF file attached
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=event_list_report_of_{year}.pdf"
    response.write(buffer.getvalue())

    # Close the buffer and return the HTTP response
    buffer.close()
    return response

""" generate event list report no page numbers"""

def generate_event_list_report_new_no_pagenumbers(year):
    # Get hikes, camps, and projects for the given year
    hikes = Hike.objects.filter(year__year=year).order_by("date")
    camps = Camp.objects.filter(date__year=year).order_by("date")
    projects = Project.objects.filter(date__year=year).order_by("date")

    # Create a buffer to store the PDF file
    buffer = BytesIO()

    # Create the PDF document object
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Define the contents of the header and footer
    header_text = f"<h1><u>Event List Report ({year})</u></h1>"
    styles = getSampleStyleSheet()
    header_style = styles["Heading1"]
    header = Paragraph(header_text, header_style)
    footer_style = styles["Normal"]
    footer_text = f"This report was generated by RCSG MIS on {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
    footer = Paragraph(footer_text, footer_style)

    # Define the styles of the tables
    table_header_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("SPAN", (0, 0), (0, 0))
    ])

    table_data_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#CCCCCC")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#000000")),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.HexColor("#000000"))
    ])

    # Define the elements to be included in the PDF document
    elements = []
    elements.append(header)
    elements.append(Spacer(1, 0.25*inch))

    # Add hikes table to the PDF document
    if hikes.exists():
        data = [["#", "Title", "Date", "Time", "Location"]]
        for i, hike in enumerate(hikes):
            data.append([str(i+1), hike.title, hike.date.strftime("%m/%d/%Y"),
                        hike.time.strftime("%I:%M %p"), hike.location])
        table = Table(data)
        table.setStyle(table_header_style)
        table.setStyle(table_data_style)
        elements.append(Paragraph("<b>Hikes</b>", styles["Heading2"]))
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))
    else:
        elements.append(Paragraph("<b>Hikes</b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"No hikes found for the year { year }.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    if camps.exists():
        data = [["#", "Title", "Date", "Time", "Nights", "Location"]]
        for i, camp in enumerate(camps):
            data.append([str(i+1), camp.title, camp.date.strftime("%m/%d/%Y"),
                        camp.time.strftime("%I:%M %p"), camp.nights, camp.location])
        table = Table(data)
        table.setStyle(table_header_style)
        table.setStyle(table_data_style)
        elements.append(Spacer(1, 0.25*inch))
        elements.append(Paragraph("<b>Camps</b>", styles["Heading2"]))
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))

    else:
        elements.append(Paragraph("<b>Camps</b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"No camps found for the year { year }.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    # Add projects table to the PDF document
    if projects.exists():
        data = [["#", "Title", "Date", "Time", "Location"]]
        for i, project in enumerate(projects):
            data.append([str(i+1), project.title, project.date.strftime("%m/%d/%Y"),
                        project.time.strftime("%I:%M %p"), project.location])
        table = Table(data)
        table.setStyle(table_header_style)
        table.setStyle(table_data_style)
        elements.append(Spacer(1, 0.25*inch))
        elements.append(Paragraph("<b>Projects</b>", styles["Heading2"]))
        elements.append(table)
    else:
        elements.append(Paragraph("<b>Projects</b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"No projects found for the year { year }.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    # If no events found, add message to the PDF document
    if not hikes.exists() and not camps.exists() and not projects.exists():
        elements.append(
            Paragraph("No events found for the given year.", styles["Normal"]))

    # Add page number to the footer

    # append footer to the elements
    elements.append(Spacer(1, 0.25*inch))
    elements.append(footer)

    # Build the PDF document and return as an HTTP response
    doc.build(elements)

    # Create HTTP response with PDF file attached
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=event_list_report_{year}.pdf"
    response.write(buffer.getvalue())

    # Close the buffer and return the HTTP response
    buffer.close()
    return response

""" generate event list report no page numbers"""

def generate_event_list_report_new_no_pagenumbers(year):
    # Get hikes, camps, and projects for the given year
    hikes = Hike.objects.filter(year__year=year).order_by("date")
    camps = Camp.objects.filter(date__year=year).order_by("date")
    projects = Project.objects.filter(date__year=year).order_by("date")

    # Create a buffer to store the PDF file
    buffer = BytesIO()

    # Create the PDF document object
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Define the contents of the header and footer
    header_text = f"<h1><u>Event List Report ({year})</u></h1>"
    styles = getSampleStyleSheet()
    header_style = styles["Heading1"]
    header = Paragraph(header_text, header_style)
    footer_style = styles["Normal"]
    footer_text = f"This report was generated by RCSG MIS on {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
    footer = Paragraph(footer_text, footer_style)

    # Define the styles of the tables
    table_header_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("SPAN", (0, 0), (0, 0))
    ])

    table_data_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#CCCCCC")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#000000")),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.HexColor("#000000"))
    ])

    # Define the elements to be included in the PDF document
    elements = []
    elements.append(header)
    elements.append(Spacer(1, 0.25*inch))

    # Add hikes table to the PDF document
    if hikes.exists():
        data = [["#", "Title", "Date", "Time", "Location"]]
        for i, hike in enumerate(hikes):
            data.append([str(i+1), hike.title, hike.date.strftime("%m/%d/%Y"),
                        hike.time.strftime("%I:%M %p"), hike.location])
        table = Table(data)
        table.setStyle(table_header_style)
        table.setStyle(table_data_style)
        elements.append(Paragraph("<b>Hikes</b>", styles["Heading2"]))
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))
    else:
        elements.append(Paragraph("<b>Hikes</b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"No hikes found for the year { year }.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    if camps.exists():
        data = [["#", "Title", "Date", "Time", "Nights", "Location"]]
        for i, camp in enumerate(camps):
            data.append([str(i+1), camp.title, camp.date.strftime("%m/%d/%Y"),
                        camp.time.strftime("%I:%M %p"), camp.nights, camp.location])
        table = Table(data)
        table.setStyle(table_header_style)
        table.setStyle(table_data_style)
        elements.append(Spacer(1, 0.25*inch))
        elements.append(Paragraph("<b>Camps</b>", styles["Heading2"]))
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))

    else:
        elements.append(Paragraph("<b>Camps</b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"No camps found for the year { year }.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    # Add projects table to the PDF document
    if projects.exists():
        data = [["#", "Title", "Date", "Time", "Location"]]
        for i, project in enumerate(projects):
            data.append([str(i+1), project.title, project.date.strftime("%m/%d/%Y"),
                        project.time.strftime("%I:%M %p"), project.location])
        table = Table(data)
        table.setStyle(table_header_style)
        table.setStyle(table_data_style)
        elements.append(Spacer(1, 0.25*inch))
        elements.append(Paragraph("<b>Projects</b>", styles["Heading2"]))
        elements.append(table)
    else:
        elements.append(Paragraph("<b>Projects</b>", styles["Heading2"]))
        elements.append(
            Paragraph(f"No projects found for the year { year }.", styles["Normal"]))
        elements.append(Spacer(1, 0.25*inch))

    # If no events found, add message to the PDF document
    if not hikes.exists() and not camps.exists() and not projects.exists():
        elements.append(
            Paragraph("No events found for the given year.", styles["Normal"]))

    # Add page number to the footer

    # append footer to the elements
    elements.append(Spacer(1, 0.25*inch))
    elements.append(footer)

    # Build the PDF document and return as an HTTP response
    doc.build(elements)

    # Create HTTP response with PDF file attached
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=event_list_report_{year}.pdf"
    response.write(buffer.getvalue())

    # Close the buffer and return the HTTP response
    buffer.close()
    return response

""" pyfpdf solution not working os error """

class AttendancePDF(FPDF):
    def header(self):
        # Logo and header text
        logo_path = os.path.abspath(
            "D:/Projects/SDP/p/proj/v4/manager/static/logo/logo.png")
        self.image(logo_path, 10, 8, 33)  # ⚜️
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Attendance Report', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        # Page number
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def table(self, header, data):
        # Column widths and table borders
        w = [70, 40, 40]
        self.set_font('Arial', 'B', 12)
        for i, h in enumerate(header):
            self.cell(w[i], 7, h, 1, 0, 'C')
        self.ln()
        self.set_font('Arial', '', 10)
        for row in data:
            for i, cell in enumerate(row):
                self.cell(w[i], 6, str(cell), 1, 0, 'C')
            self.ln()


def generate_member_attendance_report_fpdf(year, member):
    attendances = Attendance.objects.filter(
        member__id=member.id, date__year=year).order_by('title', 'date', 'time')

    pdf = AttendancePDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Header
    header = ['Title', 'Date', 'Time']
    pdf.table(header, [])

    # Data rows
    data = [[a.title, a.date.strftime(
        "%m/%d"), a.time.strftime("%I:%M %p")] for a in attendances]
    pdf.table([], data)

    # create a temporary file to save the PDF
    pdf_path = os.path.abspath(
        "D:/Projects/SDP/p/proj/v4/manager/static/logo/attendance.pdf")

    pdf.output(dest='F', name=pdf_path)

    # create a FileResponse and delete the temporary file

    try:
        file = open(pdf_path, 'rb')
        response = FileResponse(file)
        return response
    finally:
        os.remove(pdf_path)
        file.close()


# Determine start date for monthly join count data (6 years ago)
    start_date = datetime.now().replace(year=datetime.now().year - 6, month=1, day=1)

    # Query User model for monthly join counts
    join_counts = User.objects.annotate(
        year=ExtractYear('date_joined'),
        month=Cast(ExtractMonth('date_joined'), output_field=CharField()),
    ).filter(date_joined__gte=start_date).values('year', 'month').annotate(count=Count('id')).order_by('year', 'month')

    # Organize join counts by year
    yearly_join_counts = {}
    for count in join_counts:
        year = count['year']
        if year not in yearly_join_counts:
            yearly_join_counts[year] = [0] * 12
        monthly_count = yearly_join_counts[year][int(count['month']) - 1]
        yearly_join_counts[year][int(count['month']) -
                                 1] = monthly_count + count['count']

    # Get the list of all years with join counts
    years = list(yearly_join_counts.keys())

    # Create list of months and join counts for all years
    months = [datetime.strptime(str(i+1), '%m').strftime('%B')
              for i in range(12)]
    join_data_all_years = [[yearly_join_counts[year][i]
                            for year in years] for i in range(12)]

    # Plot line graphs
    fig, ax = plt.subplots()
    for i in range(len(years)):
        ax.plot(months, join_data_all_years[i], label=years[i])
    ax.set_xlabel('Month')
    ax.set_ylabel('Frequency of Registering')
    ax.set_title(
        f'Frequency of Registering each Month ({start_date:%B %Y} - {datetime.now():%B %Y})')
    ax.legend()

    # Set the x-axis limits to the first and last month displayed
    ax.set_xlim([datetime.strptime('January', '%B'),
                datetime.strptime('December', '%B')])

    # Save the line graph as a PNG image
    plt.savefig('frequency_of_registering.png')
