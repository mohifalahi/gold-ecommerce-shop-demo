import os
import smtplib
import ssl
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task
from dotenv import load_dotenv
from fpdf import FPDF
import logging
logger = logging.getLogger(__name__)

load_dotenv()


@shared_task
def text_to_pdf(parameter, output_dir, filename):
    try:
        pdf_path = os.path.join(output_dir, f"{filename}.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add text
        text = """\
        Dear {},
        Your Order has been successfully placed.
        Thank you for shopping with us.
        """.format(parameter)

        pdf.multi_cell(0, 10, text)
        
        # Save to file
        pdf.output(pdf_path)
        print(f"PDF generated successfully at: {pdf_path}")
    
    except Exception as e:
        print(f"error generating PDF: {e}")
        return pdf_path


@shared_task
def send_email(receiver_email, parameter):
    smtp_server = os.getenv('MAIL_SERVER')
    port = os.getenv('MAIL_SERVER_PORT')
    sender_email = os.getenv('MAIL_SERVER_USERNAME')
    password = os.getenv('MAIL_SERVER_PASSWORD')

    message = MIMEMultipart("alternative")
    message["Subject"] = "Order Confirmation"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = """\
    Dear Customer,
    Your Order with Order ID {} has been successfully placed.
    Thank you for shopping with us.
    """.format(parameter)

    part1 = MIMEText(text, "plain")

    message.attach(part1)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        try:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
        except Exception as e:
            print(e)


@shared_task
def send_email_with_pdf(receiver_email, output_dir, filename):

    pdf_dir = os.path.join(output_dir, f"{filename}.pdf")

    # Retry mechanism to wait for the file creation
    retry_count = 5
    while retry_count > 0:
        if os.path.exists(pdf_dir):
            break
        time.sleep(1)  # Wait 1 second before retrying
        retry_count -= 1
        print("retry:", retry_count)
    
    if not os.path.exists(pdf_dir):
        print(f"File not found after retries: {pdf_dir}")
        return  # Exit the task if the file does not exist

    smtp_server = os.getenv('MAIL_SERVER')
    port = os.getenv('MAIL_SERVER_PORT')
    sender_email = os.getenv('MAIL_SERVER_USERNAME')
    password = os.getenv('MAIL_SERVER_PASSWORD')

    message = MIMEMultipart()
    message["Subject"] = "Order Confirmation"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = """\
    Dear Customer,
    Your Order has been successfully placed.
    Thank you for shopping with us.
    """

    part1 = MIMEText(text, "plain")

    message.attach(part1)

    with open(pdf_dir, "rb") as pdf_file:
        attach_pdf = MIMEApplication(pdf_file.read(), _subtype="pdf")
        attach_pdf.add_header('Content-Disposition', f'attachment; filename=f"{filename}.pdf"')
        message.attach(attach_pdf)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        try:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
        except Exception as e:
            print(e)