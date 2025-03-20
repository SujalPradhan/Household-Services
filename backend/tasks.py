from celery_instance import celery_app
from mail_service import send_message
from datetime import datetime, date, timedelta
import smtplib
from email.message import EmailMessage
from sqlalchemy import func, desc
from flask import render_template
from celery import shared_task
from models import Customer, ServiceRequest, Service, ServiceProfessional
from models import db
# We'll define tasks without the FlaskTask base class first
SMTP_HOST = "localhost"
SMTP_PORT = 1025
SENDER_EMAIL = "23f2004759@ds.study.iitm.ac.in"
SENDER_PASSWORD = ""


@celery_app.task
def create_resource_csv():
    # We'll use deferred imports to avoid circular dependencies
    from models import db, ServiceRequest, Customer, ServiceProfessional, Service, ServiceStatusEnum
    from app import app
    from io import StringIO
    import csv
    
    # Use Flask app context explicitly
    with app.app_context():
        # Query to get service requests with status 'closed' and join with related tables
        csv_data = db.session.query(
            ServiceRequest.id.label('id'),
            Customer.name.label('customer_name'),
            ServiceProfessional.name.label('professional_name'),
            Service.name.label('service_name'),
            ServiceRequest.service_status.label('status')
        ).join(Customer, ServiceRequest.customer_id == Customer.id) \
         .join(ServiceProfessional, ServiceRequest.professional_id == ServiceProfessional.id) \
         .join(Service, ServiceRequest.service_id == Service.id) \
         .filter(ServiceRequest.service_status == ServiceStatusEnum.CLOSED).all()

        # Create a CSV string
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(["ID", "Customer Name", "Professional Name", "Service Name", "Status"])
        cw.writerows([(row.id, row.customer_name, row.professional_name, row.service_name, row.status.name) for row in csv_data])
        output = si.getvalue()

        # Save the CSV data to a file
        file_path = 'closed_service_requests.csv'
        with open(file_path, 'w', newline='') as f:
            f.write(output)

        return file_path

# @celery_app.task
# def daily_reminder():
#     # Import inside the function to avoid circular imports
#     from models import ServiceProfessional
#     from app import app
    
#     # Use Flask app context explicitly
#     with app.app_context():
#         professionals = ServiceProfessional.query.all()
#         for professional in professionals:
#             to = professional.name + "@abc.com"
#             subject = "Daily Reminder - New Service Requests"
#             if professional.service_requests.filter(ServiceRequest.service_status == 'REQUESTED' | ServiceRequest.service_status == 'ACCEPTED').count() > 0:
#                 send_message(to, subject, "Hello Please login and see for any new Service Requests")    
        
#         return "OK"

@celery_app.task
def daily_reminder():
    # Import inside the function to avoid circular imports
    from models import ServiceProfessional, ServiceRequest, ServiceStatusEnum
    from mail_service import send_message
    from sqlalchemy import or_
    from app import app

    
    # Use Flask app context explicitly
    with app.app_context():
        # Get all professionals, not just user_id 12
        professionals = ServiceProfessional.query.all()
        for professional in professionals:
            # Find pending requests for this professional
            pending_requests = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional.id,
                or_(
                    ServiceRequest.service_status == ServiceStatusEnum.REQUESTED,
                    ServiceRequest.service_status == ServiceStatusEnum.ACCEPTED
                )
            ).all()
            
            # Only send email if there are pending requests
            if pending_requests:
                to = professional.name + "@abc.com"
                subject = "Daily Reminder - New Service Requests"
                message = (f"Hello {professional.name},\n\n"
                          f"You have {len(pending_requests)} pending service requests. "
                          f"Please login to your account to review them.\n\n"
                          f"Thank you!")
                
                # Uncomment this line to actually send the email
                send_message(to, subject, message)
                

        
        return "Reminders sent successfully"

@celery_app.task
def monthly_report_generator():
    """
    Generate and send monthly activity reports to customers
    Runs on the first day of each month
    """
    from app import app  # Import here to avoid circular imports
    
    with app.app_context():
        # Get current date information
        now = datetime.now()
        now_date = now.strftime("%d %B %Y")
        
        # Calculate first and last day of previous month
        first_day_prev_month = date(now.year, now.month, 1) - timedelta(days=1)
        first_day_prev_month = date(first_day_prev_month.year, first_day_prev_month.month, 1)
        last_day_prev_month = date(now.year, now.month, 1) - timedelta(days=1)
        
        # Get month name for report
        current_month = first_day_prev_month.strftime("%B")
        
        # Get all customers
        customers = Customer.query.all()
        
        for customer in customers:
            if not customer.name:
                continue
                
            # Calculate customer specific stats
            total_requests = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer.id,
            ).count()
            
            completed_requests = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer.id,
                ServiceRequest.service_status == 'CLOSED'
            ).count()
            
            # Get service type distribution
            service_distribution = db.session.query(
                Service.name, func.count(ServiceRequest.id)
            ).join(
                ServiceRequest, ServiceRequest.service_id == Service.id
            ).filter(
                ServiceRequest.customer_id == customer.id,
            ).group_by(Service.name).all()
            
            # Create data dict for the template
            data = {
                "customer_name": customer.name,
                "total_requests": total_requests,
                "completed_requests": completed_requests,
                "service_distribution": service_distribution,
                "current_month": current_month,
                "now_date": now_date
            }
            
            # Render HTML report
            rendered_report = render_template("monthly_report.html", data=data)
            
            # Send email with report - following the pattern of daily_reminder
            to = customer.name + "@abc.com"  # Dummy email for MailHog
            subject = f"{current_month} Monthly Activity Report - Household Services"
            # Send the rendered HTML report
            send_message(to, subject, rendered_report)
            print(f"Report sent to {to}")
                
        return {"message": f"{current_month} Monthly report sent successfully!"}