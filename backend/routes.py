from flask_restful import Resource
from flask import request, make_response, jsonify
from flask_security.utils import hash_password
from models import db, User, Customer, ServiceProfessional, user_datastore, ServiceRequest, Service, ServiceStatusEnum, Admin, ServiceTypeEnum
from flask_security import logout_user
from flask_security.utils import verify_password
from flask_security import login_user
from flask_security import auth_required, roles_accepted
from flask_security import current_user
from flask import session
from datetime import datetime  # Correct import
from caching import cache

class SignUp(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "No data provided"}), 400)

        email = data.get('email')
        password = data.get('password')
        role_name = data.get('role')
        name = data.get('name')
        pincode = data.get('pincode')
        
        # If name isn't provided directly but firstName and lastName are (for backward compatibility)
        if not name and (data.get('firstName') or data.get('lastName')):
            firstName = data.get('firstName', '')
            lastName = data.get('lastName', '')
            name = f"{firstName} {lastName}".strip()

        if not email or not password or not role_name or not name:
            return make_response(jsonify({"error": "Email, password, role, and name are required"}), 400)

        if role_name not in ['admin', 'professional', 'customer']:
            return make_response(jsonify({"error": "Invalid role"}), 400)

        if User.query.filter_by(email=email).first():
            return make_response(jsonify({"error": "User already exists"}), 400)

        # Create User with pincode
        new_user = user_datastore.create_user(
            email=email, 
            password=hash_password(password), 
            active=True,
            pincode=pincode
        )
        role = user_datastore.find_role(role_name)
        if role:
            user_datastore.add_role_to_user(new_user, role)

        # Insert into Customer or ServiceProfessional Table
        if role_name == "customer":
            new_customer = Customer(
                user_id=new_user.id, 
                name=name
            )
            db.session.add(new_customer)
        elif role_name == "professional":
            service_type = data.get("service_type", "General")
            experience = data.get("experience", 0)
            description = data.get("description", "")

            new_professional = ServiceProfessional(
                user_id=new_user.id, 
                name=name, 
                service_type=service_type, 
                experience=experience, 
                description=description, 
                approved=False, 
                blocked=False
            )
            db.session.add(new_professional)

        db.session.commit()
        return make_response(jsonify({
            "message": "User Signed in", 
            "email": new_user.email, 
            "role": role_name,
            "pincode": pincode
        }), 201)


class SignIn(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "No data provided"}), 400)

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return make_response(jsonify({"error": "Email and password are required"}), 400)

        user = User.query.filter_by(email=email).first()
        if not user or not verify_password(password, user.password):
            return make_response(jsonify({"error": "Invalid email or password"}), 401)
            
        # Check if user is active before allowing login
        if not user.active:
            return make_response(jsonify({"error": "Your account has been deactivated. Please contact support."}), 403)

        login_user(user)

        role = user.roles[0].name

        user_data = {
            "email": user.email, 
            "role": role, 
            "authentication_token": user.get_auth_token() if hasattr(user, 'get_auth_token') else None,
            "pincode": user.pincode  # Include pincode in response
        }

        if role.lower() == "customer":
            customer = Customer.query.filter_by(user_id=user.id).first()
            if customer:
                user_data["name"] = customer.name
        elif role == "professional":
            professional = ServiceProfessional.query.filter_by(user_id=user.id).first()
            if professional:
                # Convert ServiceTypeEnum to string before including in response
                user_data.update({
                    "name": professional.name,
                    "service_type": professional.service_type.name if professional.service_type else None,
                    "experience": professional.experience,
                    "description": professional.description,
                    "approved": professional.approved,
                    "blocked": professional.blocked,
                    "active": user.active  # Include the user active status
                })
                
                # If professional is blocked or user is inactive, mark them as blocked in the response
                if professional.blocked or not user.active:
                    user_data["blocked"] = True
        elif role == "admin":
            admin = Admin.query.filter_by(user_id=user.id).first()
            if admin:
                user_data["name"] = admin.name
                
        return make_response(jsonify({
            "message": "Signed in successfully!",
            "user": user_data
        }), 200)


class SignOut(Resource):
    def post(self):
        try:
            # Check if user is authenticated before trying to log them out
            if current_user.is_authenticated:
                # Check if the current user is a professional before logout
                is_professional = False
                for role in current_user.roles:
                    if role.name == 'professional':
                        is_professional = True
                        break
                
                # # If it's a professional, clear their cache
                # if is_professional:
                #     professional = ServiceProfessional.query.filter_by(user_id=current_user.id).first()
                #     if professional:
                #         cache.delete('ProfessionalServiceRequests.get')
                
                logout_user()  # Logs out the current user
            
            # Clear session even if not authenticated
            cache.clear()
            
            return make_response(jsonify({"message": "Signed out successfully"}), 200)
        except Exception as e:
            # Log the error
            print(f"Error during signout: {str(e)}")
            # Return success anyway to prevent client issues
            return make_response(jsonify({"message": "Signed out", "note": "Session may have already expired"}), 200)

class CustomerDashboard(Resource):
    @auth_required('token')
    @roles_accepted('customer')
    def get(self):
        customer = Customer.query.filter_by(user_id=current_user.id).first()
        if not customer:
            return make_response(jsonify({"error": "Customer profile not found"}), 404)

        # Customer details
        customer_details = {
            "name": customer.name,
            "email": current_user.email,
            "active": current_user.active
        }

        # Available list of services
        services = Service.query.all()
        available_services = [{
            "id": service.id,
            "name": service.name,
            "price": service.price,
            "description": service.description,
            "service_type": service.service_type.name
        } for service in services]

        # History/log of current/past services
        service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
        service_history = [{
            "id": request.id,
            "service_name": request.service.name,
            "professional_name": request.professional.name if request.professional else "Not assigned",
            "remarks": request.remarks,
            "status": request.service_status.name,
            "date_of_request": request.date_of_request,
            "price": request.price  # Include the actual price from the service request
        } for request in service_requests]

        return make_response(jsonify({
            "customer_details": customer_details,
            "available_services": available_services,
            "service_history": service_history
        }), 200)

class CustomerServices(Resource):
    @auth_required('token')
    @roles_accepted('customer')
    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "No data provided"}), 400)

        service_id = data.get('service_id')
        professional_id = data.get('professional_id')
        remarks = data.get('remarks', '')
        preferred_date_str = data.get('preferred_date')
        # Get price from request data, fall back to service price if not provided
        custom_price = data.get('price')
        
        if not service_id:
            return make_response(jsonify({"error": "Service ID is required"}), 400)

        customer = Customer.query.filter_by(user_id=current_user.id).first()
        if not customer:
            return make_response(jsonify({"error": "Customer profile not found"}), 404)

        service = Service.query.get(service_id)
        if not service:
            return make_response(jsonify({"error": "Service not found"}), 404)
        
        # Parse preferred date if provided
        preferred_date = None
        if preferred_date_str:
            try:
                preferred_date = datetime.fromisoformat(preferred_date_str.replace('Z', '+00:00'))
            except ValueError:
                return make_response(jsonify({"error": "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400)

        # If professional_id is provided, validate it and check service type
        professional = None
        if professional_id:
            professional = ServiceProfessional.query.get(professional_id)
            if not professional:
                return make_response(jsonify({"error": "Service Professional not found"}), 404)
            
            # Check if professional handles the service type
            if professional.service_type != service.service_type:
                return make_response(jsonify({"error": "Professional does not provide this type of service"}), 400)
            
            # Check if professional is approved and not blocked
            if not professional.approved or professional.blocked:
                return make_response(jsonify({"error": "Selected professional is not available"}), 400)

        # Create service request with price from request data or fallback to service price
        price_to_use = custom_price if custom_price is not None else service.price
        
        # Log the price being used for debugging
        print(f"Creating service request with price: {price_to_use} (custom: {custom_price is not None}, base: {service.price})")
        
        new_service_request = ServiceRequest(
            service_id=service.id,
            customer_id=customer.id,
            professional_id=professional.id if professional else None,
            remarks=remarks,
            service_status=ServiceStatusEnum.REQUESTED,  # Always starts as REQUESTED
            preferred_date=preferred_date,
            price=price_to_use  # Use custom price from frontend if provided
        )

        db.session.add(new_service_request)
        db.session.commit()

        return make_response(jsonify({
            "message": "Service request created successfully",
            "request_id": new_service_request.id
        }), 201)

    @auth_required('token')
    @roles_accepted('customer')
    def put(self, request_id):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "No data provided"}), 400)

        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return make_response(jsonify({"error": "Service request not found"}), 404)
            
        # Check if the request belongs to the current customer
        customer = Customer.query.filter_by(user_id=current_user.id).first()
        if not customer or service_request.customer_id != customer.id:
            return make_response(jsonify({"error": "Unauthorized access to this service request"}), 403)

        # Handle status transitions for customer
        if 'service_status' in data:
            requested_status = data['service_status'].upper()
            current_status = service_request.service_status.name
            
            # Customers can only mark a request as COMPLETED if it's currently ACCEPTED
            if requested_status == 'COMPLETED':
                if current_status != 'ACCEPTED':
                    return make_response(jsonify({
                        "error": "Can only mark a request as COMPLETED when it's currently ACCEPTED"
                    }), 400)
                service_request.service_status = ServiceStatusEnum.COMPLETED
            # Customers can cancel a request that is REQUESTED or ACCEPTED
            elif requested_status == 'CANCELLED':
                if current_status not in ['REQUESTED', 'ACCEPTED']:
                    return make_response(jsonify({
                        "error": "Can only cancel a request that is REQUESTED or ACCEPTED"
                    }), 400)
                service_request.service_status = ServiceStatusEnum.CANCELLED
            else:
                return make_response(jsonify({
                    "error": f"Invalid status transition requested: '{requested_status}'. Customers can only mark requests as COMPLETED or CANCELLED."
                }), 400)

        # Update other fields
        if 'remarks' in data:
            service_request.remarks = data['remarks']

        db.session.commit()

        return make_response(jsonify({"message": "Service request updated successfully"}), 200)

    @auth_required('token')
    @roles_accepted('customer')
    def delete(self, request_id):
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return make_response(jsonify({"error": "Service request not found"}), 404)

        service_request.service_status = ServiceStatusEnum.CLOSED
        db.session.commit()

        return make_response(jsonify({"message": "Service request closed successfully"}), 200)

class SearchServices(Resource):
    @auth_required('token')
    @roles_accepted('customer')
    def get(self):
        query_params = request.args
        services = Service.query

        if 'location' in query_params:
            services = services.filter(Service.location.ilike(f"%{query_params['location']}%"))
        if 'name' in query_params:
            services = services.filter(Service.name.ilike(f"%{query_params['name']}%"))
        if 'pin_code' in query_params:
            services = services.filter(Service.pin_code == query_params['pin_code'])

        service_list = [{
            "id": service.id,
            "name": service.name,
            "price": service.price,
            "time_required": service.time_required,
            "description": service.description
        } for service in services.all()]

        return jsonify(service_list)

class SearchProfessionals(Resource):
    @auth_required('token')
    @roles_accepted('customer', 'admin')
    def get(self):
        query_params = request.args
        professionals = ServiceProfessional.query

        if 'name' in query_params:
            professionals = professionals.filter(ServiceProfessional.name.ilike(f"%{query_params['name']}%"))
        if 'service_type' in query_params:
            service_type = query_params['service_type'].upper()
            if service_type in [e.name for e in ServiceTypeEnum]:
                professionals = professionals.filter(ServiceProfessional.service_type == ServiceTypeEnum[service_type])
        if 'location' in query_params:
            professionals = professionals.filter(ServiceProfessional.location.ilike(f"%{query_params['location']}%"))
        if 'pincode' in query_params:
            # Get user_ids with matching pincode
            user_ids = [u.id for u in User.query.filter_by(pincode=query_params['pincode']).all()]
            professionals = professionals.filter(ServiceProfessional.user_id.in_(user_ids))
        
        # Only show approved and non-blocked professionals to customers
        if current_user.roles[0].name == "customer":
            professionals = professionals.filter(ServiceProfessional.approved == True)
            professionals = professionals.filter(ServiceProfessional.blocked == False)

        professional_list = [{
            "id": professional.id,
            "name": professional.name,
            "email": professional.user.email,
            "service_type": professional.service_type.name,
            "experience": professional.experience,
            "description": professional.description,
            "approved": professional.approved,
            "blocked": professional.blocked
        } for professional in professionals.all()]

        return jsonify(professional_list)

class adminDashboard(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def get(self):
        admin = Admin.query.filter_by(user_id=current_user.id).first()
        if not admin:
            return {"message": "Admin profile not found"}, 404

        return {
            "admin_name": admin.name,
            "email": current_user.email,
        }

class adminService(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "No data provided"}), 400)

        name = data.get('name')
        price = data.get('price')
        # time_required removed
        description = data.get('description', '')
        service_type_str = data.get('service_type')

        if not name or not price or not service_type_str:
            return make_response(jsonify({"error": "Name, price, and service type are mandatory"}), 400)

        # Validate service_type
        try:
            service_type = ServiceTypeEnum[service_type_str.upper()]
        except KeyError:
            return make_response(jsonify({"error": f"Invalid service type. Must be one of: {[e.name for e in ServiceTypeEnum]}"}), 400)

        new_service = Service(
            name=name,
            price=price,
            # time_required removed
            description=description,
            service_type=service_type,
            created_at=datetime.utcnow()
        )

        db.session.add(new_service)
        db.session.commit()

        return make_response(jsonify({"message": "Service added successfully"}), 201)

    @auth_required('token')
    @roles_accepted('admin')
    def put(self, service_id):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "No data provided"}), 400)

        service = Service.query.get(service_id)
        if not service:
            return make_response(jsonify({"error": "Service not found"}), 404)

        service.name = data.get('name', service.name)
        service.price = data.get('price', service.price)
        # time_required removed
        service.description = data.get('description', service.description)
        
        # Handle service type update
        service_type_str = data.get('service_type')
        if service_type_str:
            try:
                service.service_type = ServiceTypeEnum[service_type_str.upper()]
            except KeyError:
                return make_response(jsonify({"error": f"Invalid service type. Must be one of: {[e.name for e in ServiceTypeEnum]}"}), 400)

        db.session.commit()

        return make_response(jsonify({"message": "Service updated successfully"}), 200)

    @auth_required('token')
    @roles_accepted('admin')
    def delete(self, service_id):
        try:
            service = Service.query.get(service_id)
            if not service:
                return make_response(jsonify({"error": "Service not found"}), 404)
            
            # Find related service requests
            related_requests = ServiceRequest.query.filter_by(service_id=service_id).all()
            
            # Option 1: Delete all related service requests first
            for req in related_requests:
                db.session.delete(req)
            
            # Then delete the service
            db.session.delete(service)
            db.session.commit()
            
            return make_response(jsonify({
                "message": "Service deleted successfully", 
                "related_requests_deleted": len(related_requests)
            }), 200)
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting service: {str(e)}")
            import traceback
            traceback.print_exc()
            return make_response(jsonify({"error": str(e)}), 500)

    @auth_required('token')
    @roles_accepted('admin')
    def get(self, service_id=None):
        if service_id:
            service = Service.query.get(service_id)
            if not service:
                return make_response(jsonify({"error": "Service not found"}), 404)
            return jsonify({
                "id": service.id,
                "name": service.name,
                "price": service.price,
                # time_required removed
                "description": service.description,
                "service_type": service.service_type.name,
                "created_at": service.created_at
            })
        else:
            services = Service.query.all()
            return jsonify([{
                "id": service.id,
                "name": service.name,
                "price": service.price,
                # time_required removed
                "description": service.description,
                "service_type": service.service_type.name,
                "created_at": service.created_at
            } for service in services])

class adminCustomers(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def get(self):
        customers = Customer.query.all()
        customer_list = [{
            "id": customer.id,
            "user_id": customer.user_id,
            "name": customer.name,
            "email": customer.user.email,
            "active": customer.user.active
        } for customer in customers]
        return jsonify(customer_list)

    @auth_required('token')
    @roles_accepted('admin')
    def put(self, customer_id):
        try:
            data = request.get_json()
            print(f"Received PUT request for customer_id: {customer_id} with data: {data}")
            
            # First find the customer to get the user_id
            customer = Customer.query.get(customer_id)
            if not customer:
                print(f"Customer not found with id: {customer_id}")
                return make_response(jsonify({"error": f"Customer not found with id: {customer_id}"}), 404)
            
            # Now get the actual user record
            user = User.query.get(customer.user_id)
            if not user:
                print(f"User not found with id: {customer.user_id}")
                return make_response(jsonify({"error": f"User record not found with id: {customer.user_id}"}), 404)

            # If 'active' is in the request body, use that value; otherwise toggle
            if 'active' in data:
                user.active = bool(data['active'])
            else:
                user.active = not user.active
                
            db.session.commit()

            status_text = "activated" if user.active else "deactivated"
            return make_response(jsonify({
                "message": f"User account {status_text} successfully",
                "active": user.active,
                "user_id": user.id,
                "customer_id": customer.id,
                "name": customer.name,
                "email": user.email
            }), 200)
        except Exception as e:
            db.session.rollback()
            print(f"Error updating customer status: {str(e)}")
            import traceback
            traceback.print_exc()
            return make_response(jsonify({"error": str(e)}), 500)

class adminProfessional(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def get(self):
        professionals = ServiceProfessional.query.all()
        professional_list = [{
            "id": professional.id,
            "user_id": professional.user_id,
            "name": professional.name,
            "email": professional.user.email,
            "service_type": professional.service_type.value,
            "experience": professional.experience,
            "description": professional.description,
            "approved": professional.approved,
            "blocked": professional.blocked
        } for professional in professionals]
        return jsonify(professional_list)

    @auth_required('token')
    @roles_accepted('admin')
    def put(self, professional_id):
        professional = ServiceProfessional.query.get(professional_id)
        if not professional:
            return make_response(jsonify({"error": "Professional not found"}), 404)

        data = request.get_json()
        if 'approved' in data:
            professional.approved = data['approved']
        if 'blocked' in data:
            professional.blocked = data['blocked']
        db.session.commit()
        return make_response(jsonify({"message": f"Professional status updated successfully"}), 200)

# Add a new endpoint for finding professionals by service type
class ProfessionalsByServiceType(Resource):
    @auth_required('token')
    @roles_accepted('customer', 'admin')
    def get(self, service_id):
        service = Service.query.get(service_id)
        if not service:
            return make_response(jsonify({"error": "Service not found"}), 404)
            
        professionals = ServiceProfessional.query.filter_by(service_type=service.service_type)
        
        # Filter for approved and non-blocked professionals for customers
        if current_user.roles[0].name == "customer":
            professionals = professionals.filter_by(approved=True, blocked=False)

        professionals_list = [{
            "id": professional.id,
            "name": professional.name,
            "service_type": professional.service_type.name,
            "experience": professional.experience,
            "description": professional.description
        } for professional in professionals.all()]
        
        return jsonify({
            "service": {
                "id": service.id,
                "name": service.name,
                "service_type": service.service_type.name
            },
            "professionals": professionals_list
        })

# Professional Service Requests class
class ProfessionalServiceRequests(Resource):
    @auth_required('token')
    @roles_accepted('professional')
    @cache.cached(timeout=30, key_prefix='ProfessionalServiceRequests.get')
    def get(self):
        # Get the current professional
        professional = ServiceProfessional.query.filter_by(user_id=current_user.id).first()
        if not professional:
            return make_response(jsonify({"error": "Professional profile not found"}), 404)

        # Get all service requests assigned to this professional
        service_requests = ServiceRequest.query.filter_by(professional_id=professional.id).all()
        
        requests_list = []
        for req in service_requests:
            service = req.service
            customer = req.customer
            
            requests_list.append({
                "id": req.id,
                "service_id": req.service_id,
                "service_name": service.name if service else "Unknown",
                "customer_id": req.customer_id,
                "customer_name": customer.name if customer else "Unknown",
                "status": req.service_status.name,
                "price": req.price,
                "remarks": req.remarks,
                "date_of_request": req.date_of_request,
                "preferred_date": req.preferred_date
            })
        
        return jsonify(requests_list)

    @auth_required('token')
    @roles_accepted('professional')
    def put(self, request_id):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "No data provided"}), 400)

        # Get the current professional
        professional = ServiceProfessional.query.filter_by(user_id=current_user.id).first()
        if not professional:
            return make_response(jsonify({"error": "Professional profile not found"}), 404)

        # Get the service request
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return make_response(jsonify({"error": "Service request not found"}), 404)

        # Check if the service request is assigned to this professional
        if service_request.professional_id != professional.id:
            return make_response(jsonify({"error": "This service request is not assigned to you"}), 403)

        # Handle status transitions for professional
        if 'service_status' in data:
            requested_status = data['service_status'].upper()
            current_status = service_request.service_status.name
            
            # Professionals can ACCEPT a request that is REQUESTED
            if requested_status == 'ACCEPTED':
                if current_status != 'REQUESTED':
                    return make_response(jsonify({
                        "error": "Can only ACCEPT a request that is currently REQUESTED"
                    }), 400)
                service_request.service_status = ServiceStatusEnum.ACCEPTED
            # Professionals can CLOSE a request that is COMPLETED
            elif requested_status == 'CLOSED':
                if current_status != 'COMPLETED':
                    return make_response(jsonify({
                        "error": "Can only CLOSE a request that is currently COMPLETED"
                    }), 400)
                service_request.service_status = ServiceStatusEnum.CLOSED
            
            # Professionals can CANCEL a request that is REQUESTED or ACCEPTED
            elif requested_status == 'CANCELLED':
                if current_status not in ['REQUESTED', 'ACCEPTED']:
                    return make_response(jsonify({
                        "error": "Can only cancel a request that is REQUESTED or ACCEPTED"
                    }), 400)
                service_request.service_status = ServiceStatusEnum.CANCELLED
            else:
                return make_response(jsonify({
                    "error": f"Invalid status transition requested: '{requested_status}'. Professionals can only ACCEPT, CLOSE or CANCEL requests."
                }), 400)

        # Update other fields
        if 'remarks' in data:
            service_request.remarks = data['remarks']

        db.session.commit()
        cache.delete('ProfessionalServiceRequests.get')
        return make_response(jsonify({"message": "Service request updated successfully"}), 200)

# Add a new endpoint for the professional profile
class ProfessionalProfile(Resource):
    @auth_required('token')
    @roles_accepted('professional')
    def get(self):
        professional = ServiceProfessional.query.filter_by(user_id=current_user.id).first()
        if not professional:
            return make_response(jsonify({"error": "Professional profile not found"}), 404)
            
        return jsonify({
            "id": professional.id,
            "name": professional.name,
            "email": current_user.email,
            "service_type": professional.service_type.name,
            "experience": professional.experience,
            "description": professional.description,
            "approved": professional.approved,
            "blocked": professional.blocked,
            "active": current_user.active
        })

class ServiceRequests(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def get(self, service_id):
        service = Service.query.get(service_id)
        if not service:
            return make_response(jsonify({"error": "Service not found"}), 404)
        
        # Get all service requests for this service
        service_requests = ServiceRequest.query.filter_by(service_id=service_id).all()
        
        requests_list = []
        for req in service_requests:
            customer = req.customer
            professional = req.professional
            
            requests_list.append({
                "id": req.id,
                "customer_id": req.customer_id,
                "customer_name": customer.name if customer else "Unknown",
                "professional_id": req.professional_id,
                "professional_name": professional.name if professional else None,
                "status": req.service_status.name,
                "price": req.price,
                "remarks": req.remarks,
                "date_of_request": req.date_of_request,
                "preferred_date": req.preferred_date
            })
        
        return jsonify(requests_list)

class AllServiceRequests(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def get(self):
        try:
            # Fetch all service requests
            service_requests = ServiceRequest.query.all()
            
            requests_list = []
            for req in service_requests:
                customer = req.customer
                professional = req.professional
                service = req.service
                
                requests_list.append({
                    "id": req.id,
                    "service_id": req.service_id,
                    "service_name": service.name if service else "Unknown",
                    "customer_id": req.customer_id,
                    "customer_name": customer.name if customer else "Unknown",
                    "customer_email": customer.user.email if customer and customer.user else None,
                    "professional_id": req.professional_id,
                    "professional_name": professional.name if professional else None,
                    "professional_email": professional.user.email if professional and professional.user else None,
                    "status": req.service_status.name,
                    "price": req.price,
                    "remarks": req.remarks,
                    "date_of_request": req.date_of_request,
                    "preferred_date": req.preferred_date
                })
            
            return jsonify(requests_list)
        except Exception as e:
            print(f"Error fetching service requests: {str(e)}")
            import traceback
            traceback.print_exc()
            return make_response(jsonify({"error": str(e)}), 500)
