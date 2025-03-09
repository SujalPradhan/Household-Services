<template>
  <div class="professional-requests">
    <h1>My Service Requests</h1>
    
    <div class="request-tabs">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'requested' }"
        @click="setActiveTab('requested')"
      >
        <span class="tab-icon"><i class="fas fa-clock"></i></span>
        New Requests
        <span v-if="newRequestsCount > 0" class="counter">{{ newRequestsCount }}</span>
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'accepted' }"
        @click="setActiveTab('accepted')"
      >
        <span class="tab-icon"><i class="fas fa-tools"></i></span>
        Ongoing Services
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'completed' }"
        @click="setActiveTab('completed')"
      >
        <span class="tab-icon"><i class="fas fa-check-circle"></i></span>
        Completed
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'closed' }"
        @click="setActiveTab('closed')"
      >
        <span class="tab-icon"><i class="fas fa-archive"></i></span>
        Closed
      </button>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading requests...</p>
    </div>
    
    <div v-else-if="filteredRequests.length === 0" class="empty-state">
      <i class="fas fa-search"></i>
      <p>No {{ activeTab }} service requests found.</p>
    </div>
    
    <div v-else class="requests-list">
      <div 
        v-for="request in filteredRequests" 
        :key="request.id" 
        class="request-card"
      >
        <div class="request-header">
          <h2>{{ request.service_name }}</h2>
          <div class="request-badge" :class="getStatusClass(request.status)">
            {{ request.status }}
          </div>
        </div>
        
        <div class="request-details">
          <div class="detail-row">
            <div class="detail-item">
              <div class="label">Customer:</div>
              <div class="value">{{ request.customer_name }}</div>
            </div>
            <div class="detail-item">
              <div class="label">Price:</div>
              <div class="value price">₹{{ request.price?.toFixed(2) }}</div>
            </div>
          </div>
          
          <div class="detail-row">
            <div class="detail-item">
              <div class="label">Requested On:</div>
              <div class="value">{{ formatDate(request.date_of_request) }}</div>
            </div>
            <div v-if="request.preferred_date" class="detail-item">
              <div class="label">Preferred Date:</div>
              <div class="value">{{ formatDate(request.preferred_date) }}</div>
            </div>
          </div>
          
          <div v-if="request.remarks" class="detail-item full-width">
            <div class="label">Remarks:</div>
            <div class="value">{{ request.remarks }}</div>
          </div>
        </div>
        
        <div class="request-actions">
          <!-- Actions for REQUESTED status -->
          <div v-if="request.status === 'REQUESTED'" class="action-buttons">
            <button 
              @click="acceptRequest(request)" 
              class="btn btn-primary"
            >
              <i class="fas fa-check"></i> Accept
            </button>
            <button 
              @click="rejectRequest(request)" 
              class="btn btn-danger"
            >
              <i class="fas fa-times"></i> Reject
            </button>
          </div>
          
          <!-- Actions for COMPLETED status -->
          <div v-if="request.status === 'COMPLETED'" class="action-buttons">
            <button 
              @click="closeRequest(request)" 
              class="btn btn-success"
            >
              Close Request
            </button>
          </div>
          
          <!-- Actions for ACCEPTED status -->
          <div v-if="request.status === 'ACCEPTED'" class="action-buttons">
            <button 
              @click="cancelRequest(request)" 
              class="btn btn-danger"
            >
              <i class="fas fa-ban"></i> Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Status Update Modal -->
    <div v-if="showStatusModal" class="modal-overlay" @click.self="closeStatusModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeStatusModal">×</button>
        <h2>{{ statusAction.title }}</h2>
        <p>{{ statusAction.message }}</p>
        
        <div class="form-group" v-if="statusAction.showRemarks">
          <label for="statusRemarks">Additional Comments:</label>
          <textarea
            id="statusRemarks"
            v-model="statusForm.remarks"
            class="form-control"
            placeholder="Add any feedback or comments about the service..."
          ></textarea>
        </div>
        
        <div class="modal-actions">
          <button @click="closeStatusModal" class="btn btn-secondary">Cancel</button>
          <button 
            @click="submitStatusUpdate" 
            class="btn"
            :class="statusAction.btnClass"
            :disabled="statusUpdateProcessing"
          >
            <i class="fas" :class="statusUpdateProcessing ? 'fa-spinner fa-spin' : statusAction.btnIcon"></i>
            {{ statusAction.btnText }}
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
  name: 'ProfessionalRequests',
  data() {
    return {
      requests: [],
      loading: true,
      activeTab: 'requested',
      notification: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      },
      showStatusModal: false,
      selectedRequest: null,
      statusAction: {
        title: '',
        message: '',
        status: '',
        btnText: '',
        btnClass: '',
        btnIcon: '',
        showRemarks: false
      },
      statusForm: {
        remarks: ''
      },
      statusUpdateProcessing: false
    };
  },
  computed: {
    filteredRequests() {
      if (!this.requests.length) return [];
      
      return this.requests.filter(req => {
        if (this.activeTab === 'requested') {
          return req.status === 'REQUESTED';
        } else if (this.activeTab === 'accepted') {
          return req.status === 'ACCEPTED';
        } else if (this.activeTab === 'completed') {
          return req.status === 'COMPLETED';
        } else if (this.activeTab === 'closed') {
          return req.status === 'CLOSED';
        }
        return true;
      });
    },
    newRequestsCount() {
      return this.requests.filter(req => req.status === 'REQUESTED').length;
    }
  },
  methods: {
    async fetchRequests() {
      this.loading = true;
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Authorization token not found');
        }
        
        const response = await axios.get('http://127.0.0.1:5000/professional/services', {
          headers: {
            Authorization: token
          }
        });
        
        this.requests = response.data || [];
        // Emit the count of new requests to the parent component
        this.$emit('new-requests-count', this.newRequestsCount);
        
      } catch (error) {
        console.error('Error fetching service requests:', error);
        this.showNotification({
          message: "Failed to load service requests. Please try again later.",
          type: "error"
        });
      } finally {
        this.loading = false;
      }
    },
    
    setActiveTab(tab) {
      this.activeTab = tab;
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
      switch (status?.toLowerCase()) {
        case 'requested': return 'requested';
        case 'accepted': return 'accepted';
        case 'completed': return 'completed';
        case 'closed': return 'closed';
        case 'cancelled': return 'cancelled';
        default: return '';
      }
    },
    
    acceptRequest(request) {
      this.selectedRequest = request;
      this.statusForm.remarks = '';
      this.statusAction = {
        title: 'Accept Service Request',
        message: `Do you want to accept the service request for "${request.service_name}"?`,
        status: 'ACCEPTED',
        btnText: 'Accept Request',
        btnClass: 'btn-primary',
        btnIcon: 'fa-check',
        showRemarks: true
      };
      this.showStatusModal = true;
    },
    
    rejectRequest(request) {
      this.selectedRequest = request;
      this.statusForm.remarks = '';
      this.statusAction = {
        title: 'Reject Service Request',
        message: `Are you sure you want to reject the service request for "${request.service_name}"?`,
        status: 'CANCELLED',
        btnText: 'Reject Request',
        btnClass: 'btn-danger',
        btnIcon: 'fa-times',
        showRemarks: true
      };
      this.showStatusModal = true;
    },
    
    cancelRequest(request) {
      this.selectedRequest = request;
      this.statusForm.remarks = '';
      this.statusAction = {
        title: 'Cancel Service Request',
        message: `Are you sure you want to cancel this ongoing service for "${request.service_name}"?`,
        status: 'CANCELLED',
        btnText: 'Cancel Request',
        btnClass: 'btn-danger',
        btnIcon: 'fa-ban',
        showRemarks: true
      };
      this.showStatusModal = true;
    },
    
    closeRequest(request) {
      this.selectedRequest = request;
      this.statusForm.remarks = '';
      this.statusAction = {
        title: 'Close Service Request',
        message: `Do you want to mark this service request for "${request.service_name}" as closed and finalized?`,
        status: 'CLOSED',
        btnText: 'Close Request',
        btnClass: 'btn-success',
        btnIcon: 'fa-archive',
        showRemarks: true
      };
      this.showStatusModal = true;
    },
    
    closeStatusModal() {
      this.showStatusModal = false;
      this.selectedRequest = null;
      this.statusForm.remarks = '';
    },
    
    async submitStatusUpdate() {
      if (!this.selectedRequest) return;
      
      this.statusUpdateProcessing = true;
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Not authenticated');
        }
        
        await axios.put(`http://127.0.0.1:5000/professional/services/${this.selectedRequest.id}`, {
          service_status: this.statusAction.status,
          remarks: this.statusForm.remarks
        }, {
          headers: {
            Authorization: token
          }
        });
        
        this.showNotification({
          message: `Service request ${this.statusAction.status.toLowerCase() === 'accepted' ? 'accepted' : 
                    this.statusAction.status.toLowerCase() === 'closed' ? 'closed' : 'cancelled'} successfully!`,
          type: 'success'
        });
        
        // Close the modal
        this.closeStatusModal();
        
        // Refresh requests data
        await this.fetchRequests();
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
    }
  },
  async mounted() {
    await this.fetchRequests();
  }
};
</script>

<style scoped>
.professional-requests {
  padding: 20px;
  color: var(--light-color, #BFC3BA);
}

h1 {
  margin-bottom: 20px;
  color: var(--light-color, #BFC3BA);
}

/* Request Tabs */
.request-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 10px 15px;
  background-color: var(--dark-color, #2F2235);
  border: none;
  border-radius: 5px;
  color: var(--light-color, #BFC3BA);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-btn.active {
  background-color: var(--primary-color, #60495A);
  color: white;
}

.tab-icon {
  font-size: 1.2rem;
}

.counter {
  background-color: var(--info-color, #17a2b8);
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  margin-left: 5px;
}

/* Request List */
.requests-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.request-card {
  background-color: var(--dark-color, #2F2235);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.request-header {
  background-color: #221728;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--primary-color, #60495A);
}

.request-header h2 {
  margin: 0;
  font-size: 1.3rem;
}

.request-badge {
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: bold;
}

.request-badge.requested {
  background-color: #17a2b8;
  color: white;
}

.request-badge.accepted {
  background-color: #ffc107;
  color: #212529;
}

.request-badge.completed {
  background-color: #28a745;
  color: white;
}

.request-badge.closed {
  background-color: #6c757d;
  color: white;
}

.request-badge.cancelled {
  background-color: #dc3545;
  color: white;
}

.request-details {
  padding: 15px;
}

.detail-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.detail-item {
  flex: 1;
}

.detail-item.full-width {
  flex-basis: 100%;
}

.label {
  font-size: 0.9rem;
  color: var(--muted-color, #8a8a8a);
  margin-bottom: 5px;
}

.value {
  font-weight: 500;
}

.value.price {
  color: var(--primary-color, #60495A);
  font-weight: bold;
  font-size: 1.1rem;
}

.request-actions {
  padding: 15px;
  background-color: rgba(0, 0, 0, 0.1);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Fix for overlapping buttons */
.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

/* Buttons - Updated Styles */
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
  max-width: 200px;  /* Add max-width to prevent overflow */
  text-align: center; /* Ensure text is centered */
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

.btn-danger {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #f55a4e, #e33e3e);
}

.btn-success {
  background: linear-gradient(135deg, #4caf50, #2e7d32);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #5cb860, #3e8d42);
}

.btn-secondary {
  background: linear-gradient(135deg, #78909c, #546e7a);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: linear-gradient(135deg, #8ca0ac, #647c8a);
}

/* Responsive Design - Update button style for mobile */
@media (max-width: 768px) {
  .detail-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .btn {
    width: 100%;
    max-width: none; /* Remove max-width constraint on mobile */
    justify-content: center;
    padding: 12px;
    font-size: 0.95rem;
  }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  color: var(--muted-color, #8a8a8a);
  background-color: var(--dark-color, #2F2235);
  border-radius: 10px;
  text-align: center;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  opacity: 0.7;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(96, 73, 90, 0.3);
  border-top: 4px solid var(--primary-color, #60495A);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Modal Overlay */
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
  background-color: var(--secondary-color, #3F3244);
  width: 90%;
  max-width: 500px;
  border-radius: 10px;
  padding: 25px;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 24px;
  color: var(--light-color, #BFC3BA);
  cursor: pointer;
}

.form-group {
  margin: 20px 0;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  background-color: var(--dark-color, #2F2235);
  color: var(--light-color, #BFC3BA);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
}

.modal-actions {
  margin-top: 25px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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
</style>
