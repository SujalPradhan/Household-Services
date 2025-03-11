<template>
  <div class="customer-requests">
    <div class="page-header">
      <h1>My Service Requests</h1>
      <div class="filter-controls">
        <div class="filter-group">
          <label>Filter by Status:</label>
          <select v-model="statusFilter" class="filter-select" @change="applyFilters">
            <option value="">All Statuses</option>
            <option value="REQUESTED">Requested</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="COMPLETED">Completed</option>
            <option value="CLOSED">Closed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading your service requests...</p>
    </div>
    
    <div v-else-if="filteredRequests.length === 0" class="no-data">
      <p>No service requests found.</p>
      <router-link to="/customer/services" class="btn btn-primary">
        <i class="fas fa-plus"></i> Request a Service
      </router-link>
    </div>
    
    <div v-else class="requests-list">
      <div v-for="request in filteredRequests" :key="request.id" class="request-card" :class="{ 'selected': selectedRequest && selectedRequest.id === request.id }">
        <div class="request-header">
          <h3>{{ request.service_name }}</h3>
          <span class="status-badge" :class="getStatusClass(request.status)">
            {{ request.status }}
          </span>
        </div>
        
        <div class="request-body">
          <div class="detail-row">
            <span class="detail-label">Requested on:</span>
            <span class="detail-value">{{ formatDate(request.date_of_request) }}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Professional:</span>
            <span class="detail-value">{{ request.professional_name || 'Not assigned yet' }}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Price:</span>
            <span class="detail-value price">₹{{ formatPrice(request.price) }}</span>
          </div>
          
          <div v-if="request.remarks" class="detail-row">
            <span class="detail-label">Remarks:</span>
            <span class="detail-value remarks">{{ truncateText(request.remarks, 100) }}</span>
          </div>
        </div>
        
        <div class="request-actions">
          <button @click="viewRequestDetails(request)" class="btn btn-view">
            View Details
          </button>
          
          <div class="status-actions" v-if="request.status === 'REQUESTED'">
            <button @click="cancelRequest(request)" class="btn btn-cancel">
              Cancel Request
            </button>
          </div>
          
          <div class="status-actions" v-if="request.status === 'ACCEPTED'">
            <button @click="markAsCompleted(request)" class="btn btn-complete">
              Mark as Completed
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Request Details Modal -->
    <div v-if="selectedRequest" class="modal-overlay" @click.self="closeRequestDetails">
      <div class="modal-content">
        <button class="close-btn" @click="closeRequestDetails">×</button>
        
        <div class="modal-header">
          <h2>Service Request Details</h2>
          <span class="status-badge" :class="getStatusClass(selectedRequest.status)">
            {{ selectedRequest.status }}
          </span>
        </div>
        
        <div class="request-details">
          <div class="detail-section">
            <h3>Service Information</h3>
            <div class="detail-item">
              <span class="detail-label">Service:</span>
              <span class="detail-value">{{ selectedRequest.service_name }}</span>
            </div>
            
            <div class="detail-item">
              <span class="detail-label">Type:</span>
              <span class="detail-value">{{ selectedRequest.service_type }}</span>
            </div>
            
            <div class="detail-item">
              <span class="detail-label">Price:</span>
              <span class="detail-value price">₹{{ formatPrice(selectedRequest.price) }}</span>
            </div>
          </div>
          
          <div class="detail-section">
            <h3>Request Information</h3>
            <div class="detail-item">
              <span class="detail-label">Requested on:</span>
              <span class="detail-value">{{ formatDate(selectedRequest.date_of_request, true) }}</span>
            </div>
            
            <div class="detail-item" v-if="selectedRequest.preferred_date">
              <span class="detail-label">Preferred Date:</span>
              <span class="detail-value">{{ formatDate(selectedRequest.preferred_date, true) }}</span>
            </div>
            
            <div class="detail-item">
              <span class="detail-label">Professional:</span>
              <span class="detail-value">{{ selectedRequest.professional_name || 'Not assigned yet' }}</span>
            </div>
            
            <div class="detail-item" v-if="selectedRequest.professional_email">
              <span class="detail-label">Professional Email:</span>
              <span class="detail-value">{{ selectedRequest.professional_email }}</span>
            </div>
            
            <div class="detail-item" v-if="selectedRequest.remarks">
              <span class="detail-label">Remarks:</span>
              <div class="detail-value remarks">{{ selectedRequest.remarks }}</div>
            </div>
          </div>
          
          <div class="detail-section" v-if="selectedRequest.status === 'REQUESTED' || selectedRequest.status === 'ACCEPTED'">
            <h3>Actions</h3>
            <div class="detail-actions">
              <button 
                v-if="selectedRequest.status === 'REQUESTED'"
                @click="cancelRequest(selectedRequest)" 
                class="btn btn-danger"
              >
                <i class="fas fa-times-circle"></i> Cancel Request
              </button>
              
              <button 
                v-if="selectedRequest.status === 'ACCEPTED'"
                @click="markAsCompleted(selectedRequest)" 
                class="btn btn-success"
              >
                <i class="fas fa-check-circle"></i> Mark as Completed
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Status Update Modal -->
    <div v-if="statusUpdateRequest" class="modal-overlay" @click.self="closeStatusUpdateModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeStatusUpdateModal">×</button>
        <h2>{{ statusUpdateAction.title }}</h2>
        <p>{{ statusUpdateAction.message }}</p>
        
        <div class="form-group" v-if="statusUpdateAction.showRemarks">
          <label for="statusUpdateRemarks">Additional Comments:</label>
          <textarea
            id="statusUpdateRemarks"
            v-model="statusUpdateForm.remarks"
            class="form-control"
            placeholder="Add any feedback or comments about the service..."
          ></textarea>
        </div>
        
        <div class="modal-actions">
          <button @click="closeStatusUpdateModal" class="btn btn-secondary">Cancel</button>
          <button 
            @click="submitStatusUpdate" 
            class="btn"
            :class="statusUpdateAction.btnClass"
            :disabled="statusUpdateProcessing"
          >
            <i class="fas" :class="statusUpdateProcessing ? 'fa-spinner fa-spin' : statusUpdateAction.btnIcon"></i>
            {{ statusUpdateAction.btnText }}
          </button>
        </div>
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

export default {
  name: 'CustomerRequests',
  data() {
    return {
      serviceRequests: [],
      filteredRequests: [],
      loading: true,
      statusFilter: '',
      selectedRequest: null,
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
      statusUpdateProcessing: false,
      notification: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      }
    };
  },
  computed: {
    highlightedRequestId() {
      return parseInt(this.$route.query.id);
    }
  },
  methods: {
    async fetchServiceRequests() {
      try {
        this.loading = true;
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Authorization token not found');
        }
        
        const response = await axios.get('http://127.0.0.1:5000/customer/dashboard', {
          headers: {
            Authorization: token
          }
        });
        
        // Process the service history to ensure we have all needed fields
        this.serviceRequests = (response.data.service_history || []).map(req => {
          // Add price field if missing (for backward compatibility)
          if (!req.hasOwnProperty('price')) {
            console.log('Price missing for request:', req.id);
          }
          
          // Return the request with guaranteed price field
          return {
            ...req,
            // Use actual price from service_request or default to 0
            price: req.price || 0
          };
        });
        
        this.applyFilters();
        
        // If we have a request ID in the URL, find and select that request
        if (this.highlightedRequestId) {
          const highlighted = this.serviceRequests.find(req => req.id === this.highlightedRequestId);
          if (highlighted) {
            this.viewRequestDetails(highlighted);
          }
        }
      } catch (error) {
        console.error("Error fetching service requests:", error);
        this.showNotification({
          message: "Failed to load service requests. Please try again later.",
          type: "error"
        });
      } finally {
        this.loading = false;
      }
    },
    
    applyFilters() {
      let filtered = [...this.serviceRequests];
      
      // Apply status filter
      if (this.statusFilter) {
        filtered = filtered.filter(req => req.status.toUpperCase() === this.statusFilter);
      }
      
      // Sort by most recent first
      filtered.sort((a, b) => new Date(b.date_of_request) - new Date(a.date_of_request));
      
      this.filteredRequests = filtered;
    },
    
    viewRequestDetails(request) {
      this.selectedRequest = { ...request };
    },
    
    closeRequestDetails() {
      this.selectedRequest = null;
    },
    
    formatDate(dateString, includeTime = false) {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      
      if (includeTime) {
        return new Intl.DateTimeFormat('en-US', {
          year: 'numeric',
          month: 'short',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        }).format(date);
      }
      
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit'
      }).format(date);
    },
    
    formatPrice(price) {
      // Ensure price is treated as a number and properly formatted
      return price !== undefined && price !== null ? 
        parseFloat(price).toFixed(2) : '0.00';
    },
    
    getStatusClass(status) {
      switch (status?.toLowerCase()) {
        case 'requested': return 'status-requested';
        case 'accepted': return 'status-accepted';
        case 'completed': return 'status-completed';
        case 'cancelled': return 'status-cancelled';
        case 'closed': return 'status-closed';
        default: return '';
      }
    },
    
    truncateText(text, maxLength) {
      if (!text) return '';
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    },
    
    // Status update methods
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
    
    markAsCompleted(request) {
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
        
        // Add the price to the success message if available
        const priceInfo = this.statusUpdateRequest.price ? 
          ` at price ₹${this.formatPrice(this.statusUpdateRequest.price)}` : '';
        
        this.showNotification({
          message: `Service request has been ${this.statusUpdateAction.status.toLowerCase()} successfully${priceInfo}!`,
          type: 'success'
        });
        
        // Close the modals
        this.closeStatusUpdateModal();
        this.closeRequestDetails();
        
        // Refresh data
        await this.fetchServiceRequests();
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
    
    // Notification handling
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
  },
  watch: {
    statusFilter() {
      this.applyFilters();
    }
  },
  mounted() {
    this.fetchServiceRequests();
  }
};
</script>

<style scoped>
.customer-requests {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.page-header h1 {
  margin: 0;
  color: var(--light-color);
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-select {
  padding: 8px 12px;
  border-radius: 5px;
  background-color: var(--dark-color);
  color: var(--light-color);
  border: 1px solid var(--border-color, rgba(255,255,255,0.1));
}

/* Requests List */
.requests-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
}

.request-card {
  background-color: var(--dark-color);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.request-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.3);
}

.request-card.selected {
  border: 2px solid var(--primary-color);
}

.request-header {
  background-color: rgba(0,0,0,0.2);
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--primary-color);
}

.request-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--light-color);
}

.request-body {
  padding: 15px;
}

.detail-row {
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-weight: 600;
  color: var(--muted-color);
  margin-bottom: 3px;
}

.detail-value {
  color: var(--light-color);
}

.detail-value.price {
  color: #2ecc71;
  font-weight: 600;
}

.detail-value.remarks {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 8px;
  border-radius: 5px;
  margin-top: 5px;
  white-space: pre-wrap;
}

.request-actions {
  padding: 10px 15px;
  background-color: rgba(0, 0, 0, 0.1);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-actions {
  display: flex;
  gap: 10px;
}

/* Status Badge Styles */
.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-requested {
  background-color: #3498db;
  color: white;
}

.status-accepted {
  background-color: #f39c12;
  color: white;
}

.status-completed {
  background-color: #2ecc71;
  color: white;
}

.status-cancelled {
  background-color: #e74c3c;
  color: white;
}

.status-closed {
  background-color: #95a5a6;
  color: white;
}

/* Button Styles */
.btn {
  padding: 8px 15px;
  border-radius: 5px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-view {
  color: var(--primary-color);
  background: none;
  padding: 6px 10px;
  font-size: 0.9rem;
}

.btn-view:hover {
  text-decoration: underline;
}

.btn-cancel {
  background-color: #e74c3c;
  color: white;
}

.btn-cancel:hover {
  background-color: #c0392b;
}

.btn-complete {
  background-color: #2ecc71;
  color: white;
}

.btn-complete:hover {
  background-color: #27ae60;
}

.btn-success {
  background-color: #2ecc71;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #27ae60;
  transform: translateY(-2px);
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c0392b;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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
  max-width: 600px;
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  margin: 0;
  color: var(--light-color);
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h3 {
  color: var(--light-color);
  font-size: 1.1rem;
  margin-top: 0;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-item {
  margin-bottom: 12px;
}

.detail-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

/* Form Styles */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: var(--light-color);
}

.form-control {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  background-color: var(--dark-color);
  color: var(--light-color);
  border: 1px solid var(--border-color, rgba(255,255,255,0.1));
}

.modal-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Loading, Empty States */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-data {
  text-align: center;
  padding: 40px;
  background-color: var(--dark-color);
  border-radius: 10px;
  color: var(--muted-color);
}

.no-data .btn {
  margin-top: 15px;
  padding: 10px 20px;
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 5px;
}

.no-data .btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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
  border-left: 4px solid #2ecc71;
}

.toast.error {
  border-left: 4px solid #e74c3c;
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
  color: #2ecc71;
}

.toast.error i {
  color: #e74c3c;
}

.toast-close {
  cursor: pointer;
}

/* Responsive Styles */
@media (min-width: 768px) {
  .detail-row {
    flex-direction: row;
    align-items: center;
  }
  
  .detail-label {
    width: 130px;
    margin-bottom: 0;
    margin-right: 10px;
  }
  
  .detail-value {
    flex: 1;
  }
  
  .detail-value.remarks {
    margin-left: 140px;
    margin-top: 5px;
    width: calc(100% - 140px);
  }
}

@media (max-width: 576px) {
  .request-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .request-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .status-actions {
    width: 100%;
  }
  
  .status-actions .btn {
    flex: 1;
  }
}
</style>
