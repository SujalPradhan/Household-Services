from celery_instance import celery_app
from mail_service import send_message

# We'll define tasks without the FlaskTask base class first
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

@celery_app.task
def daily_reminder():
    # Import inside the function to avoid circular imports
    from models import ServiceProfessional
    from app import app
    
    # Use Flask app context explicitly
    with app.app_context():
        professionals = ServiceProfessional.query.all()
        for professional in professionals:
            to = professional.name + "@abc.com"
            subject = "Daily Reminder to check your profile for new Service Requests"
            send_message(to, subject, "Hello")
        
        return "OK"