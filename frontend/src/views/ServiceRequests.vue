<template>
  <div class="service-requests">
    <div class="page-header">
      <h2>My Service Requests</h2>
      <button @click="refreshRequests" class="refresh-btn" :disabled="loading">
        <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-sync-alt'"></i>
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>
    
    <!-- Filter controls -->
    <div class="filter-controls">
      <div class="filter-group">
        <label>Filter by Status:</label>
        <select v-model="statusFilter" class="filter-select">
          <option value="all">All Requests</option>
          <option value="requested">New Requests</option>
          <option value="accepted">Accepted</option>
          <option value="completed">Completed</option>
          <option value="closed">Closed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Sort by:</label>
        <select v-model="sortBy" class="filter-select">
          <option value="date_desc">Date (Newest First)</option>
          <option value="date_asc">Date (Oldest First)</option>
          <option value="status">Status</option>
        </select>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading your service requests...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button @click="fetchRequests" class="btn btn-retry">Retry</button>
    </div>
    
    <!-- Empty state -->
    <div v-else-if="!filteredRequests.length" class="empty-state">
      <i class="fas fa-inbox fa-3x"></i>
      <p>{{ 
        statusFilter === 'all' 
          ? 'You have no service requests yet.' 
          : `No ${statusFilter} requests found.`
      }}</p>
    </div>
    
    <!-- Request List -->
    <div v-else class="request-list">
      <div v-for="request in filteredRequests" :key="request.id" class="request-card">
        <div class="request-header">
          <h3>{{ request.service_name }}</h3>
          <span class="status-badge" :class="getStatusClass(request.status)">
            {{ request.status }}
          </span>
        </div>
        
        <div class="request-body">
          <div class="request-info">
            <div class="info-row">
              <strong>Customer:</strong> {{ request.customer_name }}
            </div>
            <div class="info-row">
              <strong>Price:</strong> ₹{{ request.price > 0 ? request.price.toFixed(2) : 'N/A' }}
            </div>
            <div class="info-row">
              <strong>Requested on:</strong> {{ formatDate(request.date_of_request) }}
            </div>
            <div class="info-row" v-if="request.preferred_date">
              <strong>Preferred Date:</strong> {{ formatDate(request.preferred_date) }}
            </div>
            <div class="info-row" v-if="request.remarks">
              <strong>Remarks:</strong> {{ request.remarks }}
            </div>
          </div>
          
          <div class="request-actions">
            <!-- Accept button -->
            <button 
              v-if="request.status.toLowerCase() === 'requested'"
              @click="acceptRequest(request)" 
              class="btn btn-accept btn-lg"
              :disabled="processingId === request.id"
            >
              <i class="fas" :class="processingId === request.id ? 'fa-spinner fa-spin' : 'fa-check'"></i>
              Accept Request
            </button>
            
            <!-- Close button -->
            <button 
              v-if="request.status.toLowerCase() === 'completed'"
              @click="closeRequest(request)" 
              class="btn btn-close"
              :disabled="processingId === request.id"
            >
              <i class="fas" :class="processingId === request.id ? 'fa-spinner fa-spin' : 'fa-check-circle'"></i>
              Close Request
            </button>
            
            <!-- Cancel button -->
            <button 
              v-if="['requested', 'accepted'].includes(request.status.toLowerCase())"
              @click="cancelRequest(request)" 
              class="btn btn-cancel"
              :disabled="processingId === request.id"
            >
              <i class="fas" :class="processingId === request.id ? 'fa-spinner fa-spin' : 'fa-times'"></i>
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="cancelConfirmation">
      <div class="modal-content">
        <h3>{{ confirmTitle }}</h3>
        <p>{{ confirmMessage }}</p>
        
        <div class="modal-actions">
          <button @click="cancelConfirmation" class="btn btn-secondary">Cancel</button>
          <button @click="confirmAction" class="btn" :class="confirmButtonClass">
            {{ confirmButtonText }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Toast Notification -->
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
  name: 'ServiceRequests',
  data() {
    return {
      requests: [],
      loading: true,
      error: null,
      statusFilter: 'all',
      sortBy: 'date_desc',
      processingId: null,
      
      // Confirmation modal
      showConfirmModal: false,
      confirmTitle: '',
      confirmMessage: '',
      confirmButtonText: '',
      confirmButtonClass: '',
      pendingAction: null,
      pendingRequest: null,
      
      // Notification
      notification: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      }
    };
  },
  computed: {
    filteredRequests() {
      // First, filter by status if needed
      let result = this.requests;
      if (this.statusFilter !== 'all') {
        result = result.filter(req => req.status.toLowerCase() === this.statusFilter);
      }
      
      // Then sort the results
      return result.sort((a, b) => {
        if (this.sortBy === 'date_desc') {
          return new Date(b.date_of_request) - new Date(a.date_of_request);
        } 
        else if (this.sortBy === 'date_asc') {
          return new Date(a.date_of_request) - new Date(b.date_of_request);
        }
        else if (this.sortBy === 'status') {
          return a.status.localeCompare(b.status);
        }
        return 0;
      });
    }
  },
  created() {
    this.fetchRequests();
  },
  methods: {
    async fetchRequests() {
      this.loading = true;
      this.error = null;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Not authenticated');
        }
        
        const response = await axios.get('http://127.0.0.1:5000/professional/requests', {
          headers: {
            'Authorization': token
          }
        });
        
        this.requests = response.data || [];
        
        // Count new requests and emit to parent
        const newRequestsCount = this.requests.filter(req => 
          req.status.toLowerCase() === 'requested'
        ).length;
        
        this.$emit('new-requests-count', newRequestsCount);
      } catch (error) {
        console.error('Error fetching service requests:', error);
        this.error = error.response?.data?.error || error.message || 'Failed to load service requests.';
      } finally {
        this.loading = false;
      }
    },
    
    refreshRequests() {
      this.fetchRequests();
    },
    
    // Format a date for display
    formatDate(dateString) {
      if (!dateString) return 'Not specified';
      
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    },
    
    // Get CSS class for status badges
    getStatusClass(status) {
      switch(status.toLowerCase()) {
        case 'requested': return 'status-requested';
        case 'accepted': return 'status-accepted';
        case 'completed': return 'status-completed';
        case 'closed': return 'status-closed';
        case 'cancelled': return 'status-cancelled';
        default: return '';
      }
    },
    
    // Action handlers
    acceptRequest(request) {
      console.log("Accepting request:", request.id); // Add debug logging
      this.showConfirmationModal(
        'Accept Request',
        `Are you sure you want to accept the service request for "${request.service_name}" from ${request.customer_name}?`,
        'Accept',
        'btn-accept',
        () => this.updateRequestStatus(request, 'ACCEPTED')
      );
    },
    
    closeRequest(request) {
      this.showConfirmationModal(
        'Close Request',
        `Are you sure you want to close the service request for "${request.service_name}" from ${request.customer_name}?`,
        'Close',
        'btn-close',
        () => this.updateRequestStatus(request, 'CLOSED')
      );
    },
    
    cancelRequest(request) {
      this.showConfirmationModal(
        'Cancel Request',
        `Are you sure you want to cancel the service request for "${request.service_name}" from ${request.customer_name}?`,
        'Cancel',
        'btn-danger',
        () => this.updateRequestStatus(request, 'CANCELLED')
      );
    },
    
    // API operations
    async updateRequestStatus(request, status) {
      this.processingId = request.id;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Not authenticated');
        }
        
        console.log(`Updating request ${request.id} to status: ${status}`); // Debug logging
        
        const response = await axios.put(`http://127.0.0.1:5000/professional/requests/${request.id}`, 
          { service_status: status },
          { headers: { 'Authorization': token } }
        );
        
        console.log("API Response:", response.data); // Debug logging
        
        // Show success message
        this.showNotification({
          message: `Request successfully ${status.toLowerCase()}.`,
          type: 'success'
        });
        
        // Update the request status locally for immediate feedback
        const updatedRequest = this.requests.find(r => r.id === request.id);
        if (updatedRequest) {
          updatedRequest.status = status.toLowerCase();
        }
        
        // Refresh the request list
        await this.fetchRequests();
      } catch (error) {
        console.error(`Error updating request status:`, error);
        this.showNotification({
          message: error.response?.data?.error || error.message || `Failed to update request status.`,
          type: 'error'
        });
      } finally {
        this.processingId = null;
      }
    },
    
    // Modal functions
    showConfirmationModal(title, message, buttonText, buttonClass, action) {
      this.confirmTitle = title;
      this.confirmMessage = message;
      this.confirmButtonText = buttonText;
      this.confirmButtonClass = buttonClass;
      this.pendingAction = action;
      this.showConfirmModal = true;
    },
    
    confirmAction() {
      if (this.pendingAction) {
        this.pendingAction();
      }
      this.showConfirmModal = false;
    },
    
    cancelConfirmation() {
      this.showConfirmModal = false;
      this.pendingAction = null;
    },
    
    // Notification methods
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
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        default: return 'fas fa-info-circle';
      }
    }
  }
};
</script>

<style scoped>
.service-requests {
  color: var(--light-color);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.refresh-btn {
  background-color: #60495A;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #4d3a49;
}

.refresh-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Filter controls */
.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #2F2235;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-select {
  background-color: var(--dark-color);
  color: var(--light-color);
  border: 1px solid #60495A;
  padding: 8px;
  border-radius: 5px;
}

/* Loading and empty states */
.loading-container, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  background-color: #2F2235;
  border-radius: 8px;
  color: var(--muted-color);
}

.empty-state i {
  color: #60495A;
  margin-bottom: 15px;
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error state */
.error-message {
  padding: 20px;
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.2);
  color: #dc3545;
  border-radius: 8px;
  text-align: center;
}

.btn-retry {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  margin-top: 15px;
  cursor: pointer;
}

/* Request cards */
.request-list {
  display: grid;
  gap: 20px;
}

.request-card {
  background-color: #2F2235;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.request-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #221728;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.request-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.status-badge {
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-requested {
  background-color: #17a2b8;
  color: white;
}

.status-accepted {
  background-color: #ffc107;
  color: #212529;
}

.status-completed {
  background-color: #28a745;
  color: white;
}

.status-closed {
  background-color: #6c757d;
  color: white;
}

.status-cancelled {
  background-color: #dc3545;
  color: white;
}

.request-body {
  padding: 15px;
}

.info-row {
  margin-bottom: 8px;
  color: var(--muted-color);
}

.info-row strong {
  color: var(--light-color);
  display: inline-block;
  width: 120px;
}

.request-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
  justify-content: flex-end;
}

/* Button Styles */
.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-accept {
  background-color: #28a745; /* Change to green for better visibility */
  color: white;
  font-weight: bold;
  transition: all 0.3s ease;
  border: none;
}

.btn-accept:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.btn-close {
  background-color: #28a745;
  color: white;
}

.btn-close:hover:not(:disabled) {
  background-color: #218838;
}

.btn-cancel {
  background-color: #dc3545;
  color: white;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Enhanced button styles */
.btn-lg {
  padding: 10px 20px;
  font-size: 1.1rem;
}

/* Confirmation Modal */
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
  max-width: 500px;
  border-radius: 10px;
  padding: 25px;
  text-align: center;
}

.modal-content h3 {
  margin-top: 0;
  color: var(--light-color);
}

.modal-content p {
  margin-bottom: 20px;
  color: var(--muted-color);
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
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

/* Highlight new requests */
.request-card.new-request {
  border-left: 4px solid #28a745;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-select {
    flex-grow: 1;
  }
  
  .info-row strong {
    width: auto;
    margin-right: 8px;
  }
}
</style>
