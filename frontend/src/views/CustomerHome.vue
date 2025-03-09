<template>
  <div class="customer-dashboard">
    <div class="dashboard-header">
      <h1>Customer Dashboard</h1>
      <div v-if="customer" class="customer-welcome">
        <h2>Welcome, {{ customer.name }}</h2>
        <p>Email: {{ customer.email }}</p>
      </div>
    </div>

    <div class="search-section">
      <h2>Find Services</h2>
      <div class="search-container">
        <input 
          v-model="searchQuery" 
          placeholder="Search services by name" 
          class="search-input"
        />
        <button @click="searchServices" class="search-button">
          <i class="fas fa-search"></i> Search
        </button>
      </div>
    </div>

    <!-- Services Section -->
    <div class="services-section">
      <h2>Available Services</h2>
      
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>Loading services...</p>
      </div>
      
      <div v-else-if="filteredServices.length === 0" class="no-services">
        <p>No services found matching your criteria.</p>
      </div>
      
      <div v-else class="services-grid">
        <div 
          v-for="service in filteredServices" 
          :key="service.id" 
          class="service-card"
        >
          <div class="service-header">
            <h3>{{ service.name }}</h3>
            <span class="service-price">₹{{ service.price.toFixed(2) }}</span>
          </div>
          <div class="service-body">
            <div class="service-meta">
              <div class="meta-item">
                <i class="fas fa-tools"></i> {{ service.service_type }}
              </div>
            </div>
            <p class="service-description">{{ truncateText(service.description, 100) || 'No description provided.' }}</p>
          </div>
          <div class="service-footer">
            <button class="btn btn-info" @click="viewServiceDetails(service)">
              <i class="fas fa-info-circle"></i> Details
            </button>
            <button class="btn btn-primary" @click="requestServiceDirectly(service)">
              <i class="fas fa-plus"></i> Request Service
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Requests History -->
    <div class="history-section">
      <h2>My Service Requests</h2>
      
      <div v-if="loadingRequests" class="loading-container">
        <div class="spinner"></div>
        <p>Loading service requests...</p>
      </div>
      
      <div v-else-if="!serviceRequests || serviceRequests.length === 0" class="no-history">
        <p>You have no service request history.</p>
      </div>
      
      <div v-else class="history-list">
        <div v-for="request in serviceRequests" :key="request.id" class="history-item">
          <div class="history-header">
            <h3>{{ request.service_name }}</h3>
            <span class="status-badge" :class="getStatusClass(request.status)">
              {{ request.status }}
            </span>
          </div>
          <div class="history-body">
            <p><strong>Professional:</strong> {{ request.professional_name || 'Not assigned' }}</p>
            <p><strong>Requested on:</strong> {{ formatDate(request.date_of_request) }}</p>
            <p v-if="request.remarks"><strong>Remarks:</strong> {{ request.remarks }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Details Modal -->
    <div v-if="selectedService" class="modal-overlay" @click.self="closeServiceModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeServiceModal">×</button>
        
        <div class="service-details">
          <h2>{{ selectedService.name }}</h2>
          
          <div class="detail-item">
            <span class="detail-label">Price:</span>
            <span class="detail-value price">₹{{ selectedService.price.toFixed(2) }}</span>
          </div>
          
          <div class="detail-item">
            <span class="detail-label">Service Type:</span>
            <span class="detail-value">{{ selectedService.service_type }}</span>
          </div>
          
          <div class="detail-item">
            <span class="detail-label">Description:</span>
            <p class="detail-value description">{{ selectedService.description || 'No description provided.' }}</p>
          </div>
          
          <div class="professionals-section" v-if="professionals.length > 0">
            <h3>Available Professionals</h3>
            <p class="select-hint">Select a professional to request this service:</p>
            
            <div class="professionals-list">
              <div 
                v-for="professional in professionals" 
                :key="professional.id"
                class="professional-card"
                :class="{ 'selected': selectedProfessional && selectedProfessional.id === professional.id }"
                @click="selectProfessional(professional)"
              >
                <h4>{{ professional.name }}</h4>
                <div class="professional-meta">
                  <p><strong>Experience:</strong> {{ professional.experience }} {{ professional.experience === 1 ? 'year' : 'years' }}</p>
                  <p><strong>Specializes in:</strong> {{ professional.service_type }}</p>
                </div>
                <p v-if="professional.description" class="professional-description">
                  {{ truncateText(professional.description, 100) }}
                </p>
              </div>
            </div>
          </div>
          
          <div v-else-if="loadingProfessionals" class="loading-professionals">
            <div class="spinner small"></div>
            <p>Loading available professionals...</p>
          </div>
          
          <div v-else class="no-professionals">
            <p>No professionals available for this service type.</p>
          </div>

          <div class="service-request-form" v-if="selectedProfessional">
            <h3>Request Service</h3>
            <div class="form-group">
              <label for="remarks">Additional Notes:</label>
              <textarea 
                id="remarks" 
                v-model="requestForm.remarks" 
                placeholder="Any special requirements or information..."
                rows="3"
                class="form-control"
              ></textarea>
            </div>
          </div>
          
          <div class="modal-actions">
            <button 
              @click="closeServiceModal" 
              class="btn btn-secondary"
            >
              Cancel
            </button>
            <button 
              @click="requestService" 
              class="btn btn-primary"
              :disabled="!selectedProfessional || requestProcessing"
            >
              <span v-if="requestProcessing">
                <i class="fas fa-spinner fa-spin"></i> Processing...
              </span>
              <span v-else>
                Request Service
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Service Request Modal -->
    <div v-if="quickRequestService" class="modal-overlay" @click.self="closeQuickRequestModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeQuickRequestModal">×</button>
        <service-request-form 
          :service="quickRequestService"
          @success="handleRequestSuccess"
          @error="handleRequestError"
          @cancel="closeQuickRequestModal"
        />
      </div>
    </div>

    <!-- Notification Toast -->
    <div v-if="notification.show" class="toast" :class="notification.type">
      <div class="toast-content">
        <i :class="getNotificationIcon()"></i>
        <span>{{ notification.message }}</span>
      </div>
      <div class="toast-close" @click="closeNotification">
        <i class="fas fa-times"></i>
      </div>
    </div>
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
      quickRequestService: null
    };
  },
  async created() {
    this.fetchDashboardData();
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
        type: options.type || 'success',
        timeout: setTimeout(() => {
          this.notification.show = false;
        }, 5000)
      };
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
    }
  }
};
</script>

<style scoped>
.customer-dashboard {
  color: var(--light-color);
  padding: 20px;
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
  padding: 8px 15px;
  border-radius: 5px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  border: none;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #50384a;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Loading States */
.loading-container, 
.loading-professionals {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
}

.spinner {
  border: 4px solid rgba(96, 73, 90, 0.3);
  border-radius: 50%;
  border-top: 4px solid var(--primary-color);
  width: 40px;
  height: 40px;
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
.no-services, 
.no-history, 
.no-professionals {
  padding: 40px;
  text-align: center;
  background-color: var(--dark-color);
  border-radius: 8px;
  color: var(--muted-color);
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
  margin-right: 10px;
  font-size: 1.2rem;
}

.toast.success i {
  color: #28a745;
}

.toast.error i {
  color: #dc3545;
}

.toast-close {
  cursor: pointer;
  padding: 5px;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .professionals-list {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    padding: 20px;
  }
}

.quick-request-form {
  margin-top: 20px;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  padding-top: 20px;
}
</style>
