<template>
  <div class="customer-dashboard">
    <div class="dashboard-header">
      <div class="header-top">
        <h1>Customer Dashboard</h1>
        <button @click="logout" class="logout-btn">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
      <div v-if="customer" class="customer-welcome">
        <h2>Welcome, {{ customer.name }}</h2>
        <p>Email: {{ customer.email }}</p>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="navigation-tabs">
      <router-link to="/customer/dashboard" class="nav-tab" exact>Dashboard</router-link>
      <router-link to="/customer/services" class="nav-tab">Find Services</router-link>
      <router-link to="/customer/professionals" class="nav-tab">Find Professionals</router-link>
      <router-link to="/customer/requests" class="nav-tab">My Requests</router-link>
    </div>

    <router-view />
  </div>
</template>

<script>
import axios from 'axios';
import ServiceRequestForm from '../components/ServiceRequestForm.vue';

export default {
  components: {
    ServiceRequestForm
  },
  data() {
    return {
      isInitialLoad: true,
      customer: null,
      searchQuery: '',
      availableServices: [],
      filteredServices: [],
      loading: true,
      selectedService: null,
      professionals: [],
      loadingProfessionals: false,
      selectedProfessional: null,
      selectedProfessionalId: '',
      requestForm: {
        remarks: ''
      },
      requestProcessing: false,
      notification: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      },
      serviceRequests: [],
      loadingRequests: true,
      quickRequestService: null,
      statusUpdateRequest: null,
      statusUpdateAction: {
        title: '',
        message: '',
        status: '',
        btnText: '',
        btnIcon: '',
        btnClass: '',
        showRemarks: false
      },
      statusUpdateForm: {
        remarks: ''
      },
      statusUpdateProcessing: false
    };
  },
  methods: {
    async fetchDashboardData() {
      try {
        this.loading = true;
        this.loadingRequests = true;
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Authorization token not found');
        }
        
        const response = await axios.get('http://127.0.0.1:5000/customer/dashboard', {
          headers: {
            Authorization: token
          }
        });
        
        // Check if user is active
        if (response.data.customer_details && response.data.customer_details.active === false) {
          this.$router.push('/blocked');
          return;
        }
        
        // Get customer details
        this.customer = response.data.customer_details;
        
        // Process available services
        this.availableServices = response.data.available_services || [];
        this.filteredServices = [...this.availableServices];
        
        // Process service history
        this.serviceRequests = response.data.service_history || [];
        
      } catch (error) {
        console.error("Error fetching customer dashboard data:", error);
        this.showNotification({
          message: "Failed to load dashboard data. Please try again later.",
          type: "error"
        });
      } finally {
        this.loading = false;
        this.loadingRequests = false;
      }
    },
    
    async searchServices() {
      if (!this.searchQuery.trim()) {
        this.filteredServices = [...this.availableServices];
        return;
      }
      
      const query = this.searchQuery.toLowerCase();
      this.filteredServices = this.availableServices.filter(service => 
        service.name.toLowerCase().includes(query) || 
        (service.description && service.description.toLowerCase().includes(query))
      );
    },
    
    async viewServiceDetails(service) {
      this.selectedService = { ...service };
      this.selectedProfessional = null;
      this.requestForm.remarks = '';
      this.professionals = [];
      
      // Fetch professionals for this service type
      this.loadingProfessionals = true;
      try {
        const response = await axios.get(`http://127.0.0.1:5000/service/${service.id}/professionals`, {
          headers: {
            Authorization: sessionStorage.getItem('Authorization')
          }
        });
        this.professionals = response.data.professionals;
      } catch (error) {
        console.error("Error fetching professionals:", error);
        this.showNotification({
          message: "Failed to load professional data.",
          type: "error"
        });
      } finally {
        this.loadingProfessionals = false;
      }
    },
    
    async requestServiceDirectly(service) {
      this.quickRequestService = { ...service };
      this.selectedProfessionalId = '';
      this.requestForm.remarks = '';
      this.professionals = [];
      
      // Fetch professionals for this service type
      this.loadingProfessionals = true;
      try {
        const response = await axios.get(`http://127.0.0.1:5000/service/${service.id}/professionals`, {
          headers: {
            Authorization: sessionStorage.getItem('Authorization')
          }
        });
        this.professionals = response.data.professionals;
      } catch (error) {
        console.error("Error fetching professionals:", error);
        this.showNotification({
          message: "Failed to load professional data.",
          type: "error"
        });
      } finally {
        this.loadingProfessionals = false;
      }
    },
    
    selectProfessional(professional) {
      this.selectedProfessional = professional;
    },
    
    closeServiceModal() {
      this.selectedService = null;
      this.selectedProfessional = null;
      this.professionals = [];
    },
    
    closeQuickRequestModal() {
      this.quickRequestService = null;
      this.selectedProfessionalId = '';
      this.requestForm.remarks = '';
      this.professionals = [];
    },
    
    async requestService() {
      if (!this.selectedService || !this.selectedProfessional) {
        this.showNotification({
          message: "Please select a service and professional.",
          type: "error"
        });
        return;
      }
      
      this.requestProcessing = true;
      try {
        const response = await axios.post('http://127.0.0.1:5000/customer/services', {
          service_id: this.selectedService.id,
          professional_id: this.selectedProfessional.id,
          remarks: this.requestForm.remarks
        }, {
          headers: {
            Authorization: sessionStorage.getItem('Authorization')
          }
        });
        
        this.showNotification({
          message: "Service request created successfully!",
          type: "success"
        });
        
        // Close the modal
        this.closeServiceModal();
        
        // Refresh dashboard data
        await this.fetchDashboardData();
      } catch (error) {
        console.error("Error requesting service:", error);
        this.showNotification({
          message: error.response?.data?.error || error.message || "Service request failed",
          type: "error"
        });
      } finally {
        this.requestProcessing = false;
      }
    },
    
    handleRequestSuccess(result) {
      this.showNotification({
        message: result.message,
        type: "success"
      });
      
      // Close the modal
      this.closeQuickRequestModal();
      
      // Refresh dashboard data to show the new request
      this.fetchDashboardData();
    },
    
    handleRequestError(errorMessage) {
      this.showNotification({
        message: errorMessage,
        type: "error"
      });
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    },
    
    getStatusClass(status) {
      switch (status.toLowerCase()) {
        case 'requested': return 'requested';
        case 'assigned': return 'assigned';
        case 'closed': return 'closed';
        default: return '';
      }
    },
    
    truncateText(text, maxLength) {
      if (!text) return '';
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    },
    
    showNotification(options) {
      if (this.notification.timeout) {
        clearTimeout(this.notification.timeout);
      }
      this.notification = {
        show: true,
        message: options.message,
        type: options.type || 'success'
      };
      this.notification.timeout = setTimeout(() => {
        this.notification.show = false;
      }, 3000);
    },
    
    closeNotification() {
      if (this.notification.timeout) {
        clearTimeout(this.notification.timeout);
      }
      this.notification.show = false;
    },
    
    getNotificationIcon() {
      switch(this.notification.type) {
        case 'success':
          return 'fas fa-check-circle';
        case 'error':
          return 'fas fa-exclamation-circle';
        default:
          return 'fas fa-info-circle';
      }
    },
    
    markRequestAsCompleted(request) {
      this.statusUpdateRequest = request;
      this.statusUpdateForm.remarks = '';
      this.statusUpdateAction = {
        title: 'Mark Service as Completed',
        message: `Are you sure you want to mark the service "${request.service_name}" as completed?`,
        status: 'COMPLETED',
        btnText: 'Mark as Completed',
        btnClass: 'btn-success',
        btnIcon: 'fa-check-circle',
        showRemarks: true
      };
    },
    
    cancelRequest(request) {
      this.statusUpdateRequest = request;
      this.statusUpdateForm.remarks = '';
      this.statusUpdateAction = {
        title: 'Cancel Service Request',
        message: `Are you sure you want to cancel the service request for "${request.service_name}"?`,
        status: 'CANCELLED',
        btnText: 'Cancel Request',
        btnClass: 'btn-danger',
        btnIcon: 'fa-times-circle',
        showRemarks: true
      };
    },
    
    closeStatusUpdateModal() {
      this.statusUpdateRequest = null;
      this.statusUpdateForm.remarks = '';
      this.statusUpdateProcessing = false;
    },
    
    async submitStatusUpdate() {
      if (!this.statusUpdateRequest) return;
      
      this.statusUpdateProcessing = true;
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Not authenticated');
        }
        
        await axios.put(`http://127.0.0.1:5000/customer/services/${this.statusUpdateRequest.id}`, {
          service_status: this.statusUpdateAction.status,
          remarks: this.statusUpdateForm.remarks
        }, {
          headers: {
            Authorization: token
          }
        });
        
        this.showNotification({
          message: `Service request has been ${this.statusUpdateAction.status.toLowerCase()} successfully!`,
          type: 'success'
        });
        
        // Close the modal
        this.closeStatusUpdateModal();
        
        // Refresh dashboard data
        await this.fetchDashboardData();
      } catch (error) {
        console.error("Error updating service request status:", error);
        this.showNotification({
          message: error.response?.data?.error || error.message || "Failed to update service request status",
          type: 'error'
        });
      } finally {
        this.statusUpdateProcessing = false;
      }
    },
    formatPrice(price) {
      return price ? parseFloat(price).toFixed(2) : '0.00';
    },
    logout() {
      // Clear authentication token
      sessionStorage.removeItem('Authorization');
      
      // Call logout endpoint
      axios.post('http://127.0.0.1:5000/signout')
        .catch(err => console.error("Logout error:", err));
      
      // Set refresh flag before redirecting
      sessionStorage.setItem('dashboard_refreshed', 'false');
      
      // Redirect to landing page instead of login
      this.$router.push('/');
    },
    handleAuthChange(event) {
      if (event.detail.isAuthenticated) {
        // If user just authenticated, mark for refresh
        sessionStorage.setItem('dashboard_refreshed', 'false');
      }
    }
  },
  mounted() {
    // Check if this is the initial page load or a refresh
    const hasRefreshed = sessionStorage.getItem('dashboard_refreshed');
    
    if (!hasRefreshed && this.isInitialLoad) {
      // Set the flag to prevent infinite refresh loop
      sessionStorage.setItem('dashboard_refreshed', 'true');
      // Reload the entire page to remount App.vue
      window.location.reload();
    } else {
      // Clear the flag for next visit
      sessionStorage.removeItem('dashboard_refreshed');
      // Fetch dashboard data
      this.fetchDashboardData();
    }
    
    // Listen for global auth changes
    window.addEventListener('global-auth-change', this.handleAuthChange);
  },
  beforeDestroy() {
    window.removeEventListener('global-auth-change', this.handleAuthChange);
  },
  created() {
    // Check if we're on the parent route and redirect to dashboard
    if (this.$route.path === '/customer') {
      this.$router.push('/customer/dashboard');
    }
  }
};
</script>

<style scoped>
.customer-dashboard {
  color: var(--light-color);
  padding: 20px;
  padding-top: 0;
  margin: 0;
}

.dashboard-header {
  margin-bottom: 30px;
}

h1, h2, h3 {
  color: var(--light-color);
  margin-top: 0;
}

.customer-welcome {
  margin-top: 10px;
  background-color: var(--secondary-color);
  padding: 15px;
  border-radius: 5px;
  border-left: 4px solid var(--primary-color);
}

.search-section {
  margin-bottom: 30px;
}

.search-container {
  display: flex;
  max-width: 500px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: none;
  border-radius: 5px 0 0 5px;
  background-color: var(--dark-color);
  color: var(--light-color);
}

.search-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0 20px;
  border-radius: 0 5px 5px 0;
  cursor: pointer;
}

/* Services Grid */
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.service-card {
  background-color: var(--dark-color);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.3);
}

.service-header {
  background-color: #221728;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--primary-color);
}

.service-header h3 {
  margin: 0;
  font-size: 1.2rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70%;
}

.service-price {
  background-color: var(--primary-color);
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.9rem;
}

.service-body {
  padding: 15px;
}

.service-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  color: var(--muted-color);
  font-size: 0.9rem;
}

.meta-item i {
  margin-right: 5px;
  color: var(--primary-color);
}

.service-description {
  color: var(--muted-color);
  margin: 10px 0;
}

.service-footer {
  padding: 10px 15px;
  background-color: rgba(0, 0, 0, 0.1);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 10px;
  justify-content: space-between;
}

.btn-info {
  background-color: var(--info-color, #17a2b8);
  color: white;
}

.btn-info:hover {
  background-color: #138496;
}

/* History Section */
.history-section {
  margin-top: 40px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  background-color: var(--dark-color);
  border-radius: 8px;
  overflow: hidden;
}

.history-header {
  background-color: #221728;
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--primary-color);
}

.history-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.history-body {
  padding: 15px;
}

.history-body p {
  margin: 5px 0;
  color: var(--muted-color);
}

.status-badge {
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-badge.requested {
  background-color: #17a2b8;
  color: white;
}

.status-badge.assigned {
  background-color: #ffc107;
  color: #212529;
}

.status-badge.closed {
  background-color: #28a745;
  color: white;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background-color: var(--secondary-color);
  width: 90%;
  max-width: 700px;
  border-radius: 10px;
  padding: 25px;
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 24px;
  background: none;
  border: none;
  color: var(--light-color);
  cursor: pointer;
}

.service-details h2 {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.detail-item {
  margin-bottom: 15px;
}

.detail-label {
  font-weight: bold;
  color: var(--light-color);
  display: block;
  margin-bottom: 5px;
}

.detail-value {
  color: var(--muted-color);
}

.detail-value.price {
  color: var(--primary-color);
  font-weight: bold;
  font-size: 1.2rem;
}

.detail-value.description {
  white-space: pre-line;
  line-height: 1.5;
}

/* Professionals Section */
.professionals-section {
  margin-top: 30px;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}

.professionals-section h3 {
  margin-bottom: 10px;
}

.select-hint {
  color: var(--muted-color);
  margin-bottom: 15px;
  font-style: italic;
}

.professionals-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.professional-card {
  background-color: var(--dark-color);
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.3s, transform 0.3s;
}

.professional-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.professional-card.selected {
  border-color: var(--primary-color);
  background-color: rgba(96, 73, 90, 0.3);
}

.professional-card h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: var(--light-color);
}

.professional-meta p {
  margin: 5px 0;
  color: var(--muted-color);
  font-size: 0.9rem;
}

.professional-description {
  margin-top: 10px;
  color: var(--muted-color);
  font-size: 0.9rem;
  font-style: italic;
}

/* Form Styles */
.service-request-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  background-color: var(--dark-color);
  color: var(--light-color);
  border: 1px solid var(--border-color);
}

.modal-actions {
  margin-top: 25px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 10px 18px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
  letter-spacing: 0.3px;
  min-width: 120px;
  position: relative;
  overflow: hidden;
}

.btn:before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.btn:hover:before {
  left: 100%;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-primary {
  background: linear-gradient(135deg, #7e57c2, #60495A);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #8e67d2, #70596A);
}

.btn-info {
  background: linear-gradient(135deg, #29b6f6, #0288d1);
  color: white;
}

.btn-info:hover {
  background: linear-gradient(135deg, #39c6ff, #1298e1);
}

.btn-success {
  background: linear-gradient(135deg, #4caf50, #2e7d32);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #5cb860, #3e8d42);
}

.btn-danger {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #f55a4e, #e33e3e);
}

.btn-secondary {
  background: linear-gradient(135deg, #78909c, #546e7a);
  color: white;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #8ca0ac, #647c8a);
}

/* Loading States */
.loading-container, .loading-professionals {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 30px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(96, 73, 90, 0.3);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

.spinner.small {
  width: 30px;
  height: 30px;
  border-width: 3px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Empty States */
.no-history, .no-services, .no-professionals {
  color: var(--muted-color);
  border-radius: 8px;
  background-color: var(--dark-color);
  text-align: center;
  padding: 40px;
}

/* Toast Notification */
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  min-width: 300px;
  max-width: 400px;
  background-color: white;
  color: #333;
  border-radius: 5px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  animation: slideIn 0.3s ease-in-out;
  z-index: 1001;
}

@keyframes slideIn {
  from { transform: translateY(100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.toast.success {
  border-left: 4px solid #28a745;
}

.toast.error {
  border-left: 4px solid #dc3545;
}

.toast-content {
  display: flex;
  align-items: center;
}

.toast-content i {
  font-size: 1.2rem;
  margin-right: 10px;
}

.toast.success i {
  color: #28a745;
}

.toast.error i {
  color: #dc3545;
}

.toast-close {
  cursor: pointer;
}

/* Add header styling for logout button */
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.logout-btn {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.logout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #f55a4e, #e33e3e);
}

.request-price {
  color: #8e67d2;
  font-weight: bold;
  background-color: rgba(142, 103, 210, 0.1);
  padding: 3px 8px;
  border-radius: 4px;
  display: inline-block;
  border: 1px solid rgba(142, 103, 210, 0.3);
}

/* Navigation Tabs - Improved styling */
.navigation-tabs {
  display: flex;
  margin-bottom: 25px;
  background-color: var(--secondary-color);
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  padding: 5px;
  position: relative;
}

.nav-tab {
  padding: 12px 20px;
  color: var(--muted-color);
  text-decoration: none;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  text-align: center;
  flex: 1;
  letter-spacing: 0.3px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.nav-tab::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  background: linear-gradient(to right, #60495A, #7e57c2);
  transition: width 0.3s ease;
}

.nav-tab:hover {
  color: var(--light-color);
}

.nav-tab:hover::before {
  width: 40px;
}

.nav-tab.router-link-active, 
.nav-tab.router-link-exact-active {
  color: white;
  background-color: var(--dark-color);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
}

.nav-tab.router-link-active::before, 
.nav-tab.router-link-exact-active::before {
  width: 60px;
}

/* Add icons to tabs */
.nav-tab::after {
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  margin-left: 8px;
  font-size: 0.9rem;
}

/* Icon for each tab */
.nav-tab[to="/customer/dashboard"]::before {
  content: "\f0e4"; /* dashboard icon */
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  margin-right: 8px;
}

.nav-tab[to="/customer/services"]::before {
  content: "\f7d9"; /* tools icon */
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  margin-right: 8px;
}

.nav-tab[to="/customer/professionals"]::before {
  content: "\f2bb"; /* id card icon */
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  margin-right: 8px;
}

.nav-tab[to="/customer/requests"]::before {
  content: "\f46d"; /* clipboard list icon */
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  margin-right: 8px;
}

@media (max-width: 768px) {
  .navigation-tabs {
    overflow-x: auto;
    white-space: nowrap;
    padding: 5px;
    justify-content: flex-start;
    flex-wrap: nowrap;
    gap: 5px;
  }
  
  .nav-tab {
    padding: 10px 15px;
    font-size: 0.9rem;
    flex: 0 0 auto;
    min-width: 120px;
  }
  
  .nav-tab::before {
    display: none;
  }
}
</style>
