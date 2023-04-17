from reportlab.platypus import Image, PageBreak, Paragraph
from django.db.models import CharField
from django.db.models.functions import ExtractYear, ExtractMonth, Cast
import numpy as np
import matplotlib.pyplot as plt
from reportlab.graphics.charts.barcharts import HorizontalBarChart, VerticalBarChart
from reportlab.graphics.shapes import Drawing
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle , Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak,
                                TableStyle, PageTemplate, BaseDocTemplate)
from django.db.models import Count, Subquery, OuterRef , Sum
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from django.db.models.functions import TruncMonth
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
from core.models import MembershipFee, User
from collections import defaultdict
from member.models import Hike, Camp, Project, Badge, Requirement
import calendar
""" generate_member_attendance_report """

def generate_member_attendance_report(year, member):
    attendances = Attendance.objects.filter(
        member__id=member.id, date__year=year).order_by('title', 'date', 'time')

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
        ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
        ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("SPAN", (0, 0), (-1, 0)),
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

""" generate_patrol_attendance_report """

def generate_patrol_attendance_report(year, patrol):

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

    p = canvas.Canvas(buffer, pagesize=letter)

    data = [['Member', 'Title', 'Date', 'Time']]

    for attendance in attendances:
        member = attendance.member
        title = attendance.title
        date = attendance.date.strftime("%m/%d")
        time = attendance.time.strftime("%I:%M %p")
        data.append([member, title, date, time])

    table = Table(data)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
                ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), "#FFFFFF"),
                ("TEXTCOLOR", (0, 1), (-1, -1), "#000000"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, 0), 1, "#000000"),
                ("LINEABOVE", (0, 1), (-1, 1), 1, "#CCCCCC"),
                ("LINEBELOW", (0, -1), (-1, -1), 1, "#CCCCCC"),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, "#CCCCCC"),
            ]
        )
    )

    table.wrapOn(p, 500, 500)
    table.drawOn(p, 50, 500)

    p.showPage()
    p.save()

    buffer.seek(0)

    response = HttpResponse(
        buffer, content_type="application/pdf"
    )
    response["Content-Disposition"] = (
        f"attachment; filename=attendance_report_{patrol}_{year}.pdf"
    )

    return response

""" generate_event_attendance_report """

def generate_event_attendance_report(year, title):

    print(year, title)

    try:
        attendances = Attendance.objects.filter(title=title, date__year=year).order_by(
            "member__patrol__name", "member"
        )
        
        print(attendances)

    except Attendance.DoesNotExist:
        print("Event not found")
        return None

    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)

    data = [["Member", "Patrol", "Date", "Time"]]

    for attendance in attendances:
        member = attendance.member
        patrol = member.patrol
        date = attendance.date.strftime("%m/%d")
        time = attendance.time.strftime("%I:%M %p")
        data.append([member, patrol, date, time])

    table = Table(data)

    print(table)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
                ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), "#FFFFFF"),
                ("TEXTCOLOR", (0, 1), (-1, -1), "#000000"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, 0), 1, "#000000"),
                ("LINEABOVE", (0, 1), (-1, 1), 1, "#CCCCCC"),
                ("LINEBELOW", (0, -1), (-1, -1), 1, "#CCCCCC"),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, "#CCCCCC"),
            ]
        )
    )
    if title == '':
        title = 'Saturday Meeting'
        
    # Add header to each page
    header = f"{title} Attendance Report - Year: {year}"
    p.setFont("Helvetica-Bold", 14)
    header_width = stringWidth(header, "Helvetica-Bold", 14)
    header_height = 50
    p.drawString((letter[0]-header_width)/2, letter[1]-header_height, header)
    
    # Add footer to each page
    footer_height = 50
    p.setFont("Helvetica", 12)
    page_num_width = stringWidth(str(p.getPageNumber()), "Helvetica", 12)
    p.drawString(letter[0]-50-page_num_width,
                footer_height/2, str(p.getPageNumber()))
        
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, -700, f"{title} Attendance Report")
    p.setFont("Helvetica", 12)
    p.drawString(50, -675, "Year: " + str(year))
    

    table.wrapOn(p, 0 , 0)
    
    table.drawOn(p, 50, 550)

    

    p.showPage()
    p.save()

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f"attachment; filename={title}_attendance_report_{year}.pdf"
    )

    return response

""" generate_member_attendance_report_new """

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

""" generate patrol attendance report new """

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
        # if title != '':
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
        for i, attendance in enumerate(attendances):
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

""" generate_event_attendance_report_new """

def generate_event_attendance_report_new(year, title):

    try:
        # Get attendance for table
        attendances = Attendance.objects.filter(title=title, date__year=year).order_by(
            "member__patrol__name", "member"
        )
        
        print(attendances)
        
        # attendance for each title   
        title_attendance = Attendance.objects.filter(date__year=year).values('title').annotate(count=Count('id'))
        
        for attendance in title_attendance:
            print(f"{attendance['title']}: {attendance['count']}")
            
        # Create a bar chart showing the attendance count for each title
        titles = [attendance['title'] for attendance in title_attendance if attendance['title'] != '']
        counts = [attendance['count']
                for attendance in title_attendance if attendance['title'] != '']
        
        fig, ax = plt.subplots()
        ax.bar(titles, counts)
        ax.set_xlabel('Title')
        ax.set_ylabel('Attendance Count')
        ax.set_title(f'Attendance by Event ({year})')
        plt.savefig('title_counts.png')

        # patrol wise attendance count

        patrol_attendances = Attendance.objects.filter(title=title, date__year=year).order_by(
            "member__patrol__name"
        ).values("member__patrol__name").annotate(count=Count("id"))

        for attendance in patrol_attendances:
            patrol_name = attendance["member__patrol__name"]
            count = attendance["count"]    
            print("Patrol Name:", patrol_name,"Count:", count)

        patrol_wise_data = [("Patrol Name", "Count")]
        for attendance in patrol_attendances:
            patrol_name = attendance["member__patrol__name"]
            count = attendance["count"]
            patrol_wise_data.append((patrol_name, count))


        # create table
        patrol_wiae_table = Table(patrol_wise_data)
        patrol_wiae_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))

        

        # Create a buffer to store the PDF file
        buffer = BytesIO()
        
        plt.savefig(buffer, format='png')
        buffer.seek(0)

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
        elements.append(Paragraph(
            f"<b><u>Comparison</u></b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.25*inch))
        elements.append(Image('title_counts.png', width=7*inch, height=5*inch))
        elements.append(Spacer(1, 0.25*inch))
        elements.append(PageBreak())
        # Add count of total attendance to the PDF document
        count_total = attendances.count()
        if count_total:
            elements.append(Paragraph(
                f"<b><i>Total Attendance:</i></b> {count_total}", styles["Normal"]))
            elements.append(Spacer(1, 0.25*inch))
            # create table
            table = Table(data, colWidths=col_widths)   
            table.setStyle(table_style)
            elements.append(
                Paragraph("<b><u>Patrol Wise Attendance</u></b>", styles["Heading2"]))
            elements.append(Spacer(1, 0.25*inch))
            elements.append(patrol_wiae_table)
            elements.append(Spacer(1, 0.25*inch))
            elements.append(
                Paragraph("<b><u>Detailed Attendance</u></b>", styles["Heading2"]))
            elements.append(Spacer(1, 0.25*inch))
            elements.append(table)
            elements.append(Spacer(1, 0.25*inch))
        else:
            elements.append(
                Paragraph("No attendance records found.", styles["Normal"]))
            elements.append(Spacer(1, 0.25*inch))

        elements.append(footer)
        table = Table(data, colWidths=col_widths)
        table.setStyle(table_style)


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
    except Exception as e:
        return HttpResponse(f"Error: {e}")

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
            f"<b>Number of Members Paid:</b>   { membership_paid_count }", styles["Normal"]))
    elements.append(Spacer(1, 0.25*inch))

    # Add membership fee records to the table
    if memberships.exists():
        for i, membership in enumerate(memberships):
            member_name = membership.member
            patrol_name = membership.member.patrol.name if membership.member.patrol is not None else ""
            amount_paid = f"Rs. {membership.amount}"
            data.append([str(i+1), member_name, patrol_name, amount_paid])

    if data.__len__() > 1:
        # Add the table to the PDF document
        table = Table(data, colWidths=col_widths)
        table.setStyle(table_style)
        elements.append(table)
    else:
        elements.append(Paragraph(
            f'<b><i>No membership fee paid records found for year {year}</i></b>', styles["Normal"]))

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
        elements.append(
            Paragraph("<b><u>Projects</u></b>", styles["Heading2"]))
        elements.append(table)
    else:
        elements.append(
            Paragraph("<b><u>Projects</u></b>", styles["Heading2"]))
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


""" generate user report """

def generate_user_report_new(year):
    try:
        # Get the data from the database
        pays = MembershipFee.objects.filter(for_year__year=year).select_related('member').select_related('member__user').values(
            'id', 'member__user__username', 'date', 'member__user__is_active', 'is_paid').order_by('-member__user__is_active', '-member__user__username')
        
        excluded_usernames = [pay['member__user__username'] for pay in pays]

        print(excluded_usernames)
        
        # is_active=True
        
        not_pays = User.objects.exclude(
            username__in=excluded_usernames
        ).select_related('Profile').values(
            'id', 'username', 'is_active','profile__patrol__name', 'profile__contact'
        ).order_by(
            '-id', '-username'
        )
        print(not_pays)
        
        users = User.objects.all().values(
            'id', 'username', 'is_active')

        # Create Buffer
        buffer = BytesIO()
        
        # Create a PDF document object using ReportLab library
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=72, leftMargin=72, topMargin=0.5*inch, bottomMargin=60)
        styles = getSampleStyleSheet()
        
        
        # Define the contents of the header and footer
        header_text = f"<h1><u>User Report ({year})</u></h1>"
        styles = getSampleStyleSheet()
        header_style = styles["Heading1"]
        header = Paragraph(header_text, header_style)
        
        # footer text
        footer_style = styles["Normal"]
        footer_text = f"This report was generated by RCSG MIS on {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
        footer = Paragraph(footer_text, footer_style)

        # Create a table for the membership fee data
        pays_data = [[
                    Paragraph('<b>Username</b>', styles['Normal']),
                    Paragraph('<b>Paid Date</b>', styles['Normal']),
                    Paragraph('<b>Active Status</b>', styles['Normal']),
                    Paragraph('<b>Paid Status</b>', styles['Normal'])
        ]]
        
        for pay in pays:
            is_paid = "Yes" if pay['is_paid'] else "No"
            is_active = "Yes" if pay['member__user__is_active'] else "No"
            pays_data.append([pay['member__user__username'],
                            pay['date'], is_active , is_paid])
        

        pays_table = Table(pays_data)
        
        # Create a table for the membership fee data
        not_pays_data = [[
            Paragraph('<b>Username</b>', styles['Normal']),
            Paragraph('<b>Active Status</b>', styles['Normal']),
            Paragraph('<b>Patrol</b>', styles['Normal']),
            Paragraph('<b>Contact</b>', styles['Normal'])
        ]]
        
        for pay in not_pays:
            is_active = "Yes" if pay['is_active'] else "No"
            patrol = pay['profile__patrol__name']
            contact = pay['profile__contact']
            not_pays_data.append([pay['username'], is_active, patrol, contact])
            
        not_pays_table = Table(not_pays_data)
        
        table_style = TableStyle([ 
            ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
            ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
            ("ALIGN", (0, 0), (-1, 0), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("SPAN", (0, 0), (0, 0)),("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#CCCCCC")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#000000")),
            ("ALIGN", (0, 0), (-1, 0), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.HexColor("#000000"))
        ])
        
        not_pays_table.setStyle(table_style)
        pays_table.setStyle(table_style)
        
        # Define the elements to be included in the PDF document
        elements = []
        elements.append(header)
        elements.append(Spacer(1, 0.25*inch))
        
        #######################################################
        # add graph header
        elements.append(
            Paragraph(f"<b><u>Membership Paid Months Stats for { year }</u></b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.25*inch))
        
        # add graph
        # Create a bar chart showing the number of paid and unpaid members per month
        pays_counts = MembershipFee.objects.filter(for_year__year=year).values(
            'date__month').annotate(count=Count('id')).order_by('date__month')
        not_pays_counts = User.objects.filter().exclude(username__in=excluded_usernames).values(
            'date_joined__month').annotate(count=Count('id')).order_by('date_joined__month')

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        pays_data = [0] * 12
        not_pays_data = [0] * 12

        for count in pays_counts:
            pays_data[count['date__month'] - 1] = count['count']

        for count in not_pays_counts:
            not_pays_data[count['date_joined__month'] - 1] = count['count']

        x = np.arange(len(months))
        width = 0.35

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/2, pays_data, width, label='Paid Members')
        rects2 = ax.bar(x + width/2, not_pays_data, width, label='Unpaid Members')

        ax.set_ylabel('Number of Members')
        ax.set_title(f'Membership Status ({year})')
        ax.set_xticks(x)
        ax.set_xticklabels(months)
        ax.legend()

        # Save the bar chart as a PNG image
        plt.savefig('membership_status.png')

        # Add the PNG image to the PDF document
        elements.append(Image('membership_status.png', 7*inch, 4*inch))
        ################################################################
        
        # Determine start year for join count graph (6 years ago)
        start_year = datetime.now().year - 6

        # Query User model for yearly join counts
        join_counts = User.objects.filter(date_joined__gte=datetime(start_year, 1, 1)).values(
            'date_joined__year').annotate(count=Count('id')).order_by('date_joined__year')

        # Create list of years and join counts
        years = [count['date_joined__year'] for count in join_counts]
        join_data = [count['count'] for count in join_counts]

        # Plot bar chart
        x = np.arange(len(years))
        fig, ax = plt.subplots()
        rects1 = ax.bar(x, join_data, label='New Members')
        ax.set_ylabel('Number of Members')
        ax.set_title(f'Yearly Join Counts ({start_year} - {datetime.now().year})')
        ax.set_xticks(x)
        ax.set_xticklabels(years)
        ax.legend()

        # Save the bar chart as a PNG image
        plt.savefig('join_counts.png')

        # Add the PNG image to the PDF document on a new page
        elements.append(PageBreak())
        elements.append(Paragraph('Yearly Join Counts:', styles['Heading2']))
        elements.append(Image('join_counts.png', 7*inch, 5*inch))
        elements.append(PageBreak())

        ####################################################
        
        # monthly joining frequency
        # Determine start year for monthly join count graph (6 years ago)

        join_counts = User.objects.annotate(
            month=TruncMonth('date_joined')
        ).values('month').annotate(count=Count('id')).order_by('month')

        # Group join counts by year
        yearwise_join_counts = {}
        for count in join_counts:
            year = count['month'].year
            if year not in yearwise_join_counts:
                yearwise_join_counts[year] = {'dates': [], 'counts': []}
            yearwise_join_counts[year]['dates'].append(count['month'])
            yearwise_join_counts[year]['counts'].append(count['count'])

        fig, ax = plt.subplots()
        for year, data in yearwise_join_counts.items():
            # Convert month numbers to month names
            month_names = [calendar.month_name[d.month] for d in data['dates']]    
            ax.plot(month_names, data['counts'], marker='o', label=str(year))

        ax.set_ylabel('Number of Users')
        ax.set_title(f'Monthly Joining Frequency ({start_year} - {datetime.now().year})')
        plt.xticks(rotation=45, fontsize=6)
        plt.legend()

        # Save the line chart as a PNG image
        plt.savefig('monthly_join_frequency.png')

        # Add the PNG image to the PDF document on a new page
        elements.append(Paragraph('Monthly Joining Frequency:', styles['Heading2']))
        elements.append(Image('monthly_join_frequency.png', 7*inch, 5*inch))
        elements.append(PageBreak())

        
        ############################### 
        
        # Add the table to the elements
        elements.append(
            Paragraph(f"<b><u>Membership Fee Not Paid Users for { year }</u></b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.25*inch))
        elements.append(not_pays_table)
        elements.append(Spacer(1, 0.25*inch))
        elements.append(PageBreak())
        
        # Add the table to the elements
        elements.append(
            Paragraph(f"<b><u>Membership Paid Users for { year }</u></b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.25*inch))
        elements.append(pays_table)
        elements.append(Spacer(1, 0.25*inch))
        elements.append(PageBreak())
        
        # Create a table for the user data
        users_data = [[
            Paragraph('<b>Username</b>', styles['Normal']),
            Paragraph('<b>Active Status</b>', styles['Normal'])
            ]]

        for user in users:
            is_active = "Yes" if user['is_active'] else "No"
            users_data.append([user['username'],is_active])

        users_table = Table(users_data)
        
        users_table.setStyle(table_style)
        
        elements.append(
            Paragraph("<b><u>All Users</u></b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.25*inch)) 
        elements.append(users_table)
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
        response["Content-Disposition"] = f"attachment; filename=user_report_of_{year}.pdf"
        response.write(buffer.getvalue())

        # Close the buffer and return the HTTP response
        buffer.close()
        return response
    except Exception as e:
        # send error message to the user
        response = HttpResponse( f"Error: {e}")
        return response