<template>
  <div class="service-requests-dashboard">
    <div class="dashboard-header">
      <h2>Service Requests Management</h2>
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
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search by customer, service or professional" 
            class="form-control"
            @input="applyFilters"
          >
          <button class="btn btn-search">
            <i class="fas fa-search"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="loading-container" v-if="loading">
      <div class="spinner"></div>
      <p>Loading service requests...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button @click="fetchServiceRequests" class="btn btn-retry">Retry</button>
    </div>
    
    <div v-else-if="filteredRequests.length === 0" class="no-data">
      <p>No service requests found.</p>
    </div>
    
    <div v-else class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="sortBy('id')">ID <i :class="getSortIcon('id')"></i></th>
            <th @click="sortBy('service_name')">Service <i :class="getSortIcon('service_name')"></i></th>
            <th @click="sortBy('customer_name')">Customer <i :class="getSortIcon('customer_name')"></i></th>
            <th @click="sortBy('professional_name')">Professional <i :class="getSortIcon('professional_name')"></i></th>
            <th @click="sortBy('status')">Status <i :class="getSortIcon('status')"></i></th>
            <th @click="sortBy('date_of_request')">Date Requested <i :class="getSortIcon('date_of_request')"></i></th>
            <th @click="sortBy('price')">Price <i :class="getSortIcon('price')"></i></th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in sortedRequests" :key="request.id">
            <td>{{ request.id }}</td>
            <td>{{ request.service_name }}</td>
            <td>{{ request.customer_name }}</td>
            <td>{{ request.professional_name || 'Not Assigned' }}</td>
            <td>
              <span class="status-badge" :class="getStatusClass(request.status)">
                {{ request.status }}
              </span>
            </td>
            <td>{{ formatDate(request.date_of_request) }}</td>
            <td>₹{{ request.price }}</td>
            <td class="actions-cell">
              <button @click="showRequestDetails(request)" class="btn btn-expand btn-sm">
                <i class="fas fa-eye"></i> View Details
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Details Modal Popup -->
    <div v-if="selectedRequest" class="modal-overlay" @click.self="closeRequestDetails">
      <div class="modal-content details-modal">
        <button class="close-btn" @click="closeRequestDetails">&times;</button>
        <div class="modal-header">
          <h3>Service Request Details</h3>
          <span class="status-badge" :class="getStatusClass(selectedRequest.status)">
            {{ selectedRequest.status }}
          </span>
        </div>
        
        <div class="request-details">
          <div class="details-section">
            <h4>Request Information</h4>
            <div class="details-grid">
              <div class="detail-item">
                <span class="detail-label">Request ID:</span>
                <span class="detail-value">{{ selectedRequest.id }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Service:</span>
                <span class="detail-value">{{ selectedRequest.service_name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Price:</span>
                <span class="detail-value price">₹{{ selectedRequest.price }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Date Requested:</span>
                <span class="detail-value">{{ formatDate(selectedRequest.date_of_request, false) }}</span>
              </div>
              <div class="detail-item" v-if="selectedRequest.preferred_date">
                <span class="detail-label">Preferred Date:</span>
                <span class="detail-value">{{ formatDate(selectedRequest.preferred_date, false) }}</span>
              </div>
            </div>
          </div>
          
          <div class="details-columns">
            <div class="details-section">
              <h4>Customer Information</h4>
              <div class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Name:</span>
                  <span class="detail-value">{{ selectedRequest.customer_name }}</span>
                </div>
                <div class="detail-item" v-if="selectedRequest.customer_email">
                  <span class="detail-label">Email:</span>
                  <span class="detail-value">{{ selectedRequest.customer_email }}</span>
                </div>
              </div>
            </div>
            
            <div class="details-section">
              <h4>Professional Information</h4>
              <div v-if="selectedRequest.professional_name" class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Name:</span>
                  <span class="detail-value">{{ selectedRequest.professional_name }}</span>
                </div>
                <div class="detail-item" v-if="selectedRequest.professional_email">
                  <span class="detail-label">Email:</span>
                  <span class="detail-value">{{ selectedRequest.professional_email }}</span>
                </div>
              </div>
              <div v-else class="no-professional">
                <p>No professional assigned</p>
              </div>
            </div>
          </div>
          
          <div class="details-section">
            <h4>Remarks</h4>
            <div class="remarks-box">
              {{ selectedRequest.remarks || 'No remarks provided.' }}
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeRequestDetails" class="btn btn-primary">Close</button>
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
  name: 'AdminServiceRequests',
  data() {
    return {
      serviceRequests: [],
      filteredRequests: [],
      loading: true,
      error: null,
      expandedRequestId: null,
      searchQuery: '',
      statusFilter: '',
      sortKey: 'date_of_request',
      sortDirection: 'desc',
      notification: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      },
      selectedRequest: null,
    };
  },
  computed: {
    sortedRequests() {
      return [...this.filteredRequests].sort((a, b) => {
        let modifier = this.sortDirection === 'asc' ? 1 : -1;
        
        // Special handling for dates
        if (this.sortKey === 'date_of_request' || this.sortKey === 'preferred_date') {
          return new Date(a[this.sortKey]) > new Date(b[this.sortKey]) ? modifier : -modifier;
        }
        
        // Special handling for price (numeric)
        if (this.sortKey === 'price') {
          return parseFloat(a[this.sortKey]) > parseFloat(b[this.sortKey]) ? modifier : -modifier;
        }
        
        // For missing professional_name (can be null)
        if (this.sortKey === 'professional_name') {
          const aVal = a[this.sortKey] || '';
          const bVal = b[this.sortKey] || '';
          return aVal.localeCompare(bVal) * modifier;
        }
        
        // Normal string comparison
        if (typeof a[this.sortKey] === 'string' && typeof b[this.sortKey] === 'string') {
          return a[this.sortKey].localeCompare(b[this.sortKey]) * modifier;
        }
        
        // Default comparison
        if (a[this.sortKey] < b[this.sortKey]) return -1 * modifier;
        if (a[this.sortKey] > b[this.sortKey]) return 1 * modifier;
        return 0;
      });
    }
  },
  created() {
    this.fetchServiceRequests();
  },
  methods: {
    async fetchServiceRequests() {
      this.loading = true;
      this.error = null;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('No authorization token found');
        }
        
        const response = await axios.get('http://127.0.0.1:5000/admin/service-requests', {
          headers: {
            'Authorization': token
          }
        });
        
        this.serviceRequests = response.data;
        this.applyFilters(); // Initialize filtered requests
      } catch (error) {
        console.error('Error fetching service requests:', error);
        this.error = error.response?.data?.error || error.message || 'Failed to load service requests';
      } finally {
        this.loading = false;
      }
    },
    
    toggleRequestDetails(request) {
      if (this.expandedRequestId === request.id) {
        this.expandedRequestId = null;
      } else {
        this.expandedRequestId = request.id;
      }
    },
    
    applyFilters() {
      let filtered = [...this.serviceRequests];
      
      // Apply status filter
      if (this.statusFilter) {
        filtered = filtered.filter(req => 
          req.status.toUpperCase() === this.statusFilter.toUpperCase()
        );
      }
      
      // Apply search query
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase().trim();
        filtered = filtered.filter(req => 
          (req.service_name && req.service_name.toLowerCase().includes(query)) ||
          (req.customer_name && req.customer_name.toLowerCase().includes(query)) ||
          (req.professional_name && req.professional_name.toLowerCase().includes(query))
        );
      }
      
      this.filteredRequests = filtered;
    },
    
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortKey = key;
        this.sortDirection = 'asc';
      }
    },
    
    getSortIcon(key) {
      if (this.sortKey !== key) return 'fas fa-sort';
      return this.sortDirection === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
    },
    
    formatDate(dateString, short = true) {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      if (short) {
        return new Intl.DateTimeFormat('en-US', {
          year: 'numeric',
          month: 'short',
          day: '2-digit'
        }).format(date);
      }
      
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    },
    
    getStatusClass(status) {
      const statusLower = String(status).toLowerCase();
      if (statusLower === 'requested') return 'status-requested';
      if (statusLower === 'accepted') return 'status-accepted';
      if (statusLower === 'completed') return 'status-completed';
      if (statusLower === 'cancelled') return 'status-cancelled';
      if (statusLower === 'closed') return 'status-closed';
      return '';
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
        case 'warning':
          return 'fas fa-exclamation-triangle';
        default:
          return 'fas fa-info-circle';
      }
    },
    
    showRequestDetails(request) {
      this.selectedRequest = { ...request };
    },
    
    closeRequestDetails() {
      this.selectedRequest = null;
    },
  }
};
</script>

<style scoped>
.service-requests-dashboard {
  color: var(--light-color);
  margin: 0;
  padding: 0;
}

.dashboard-header {
  margin-bottom: 20px;
  margin-top: 0;
  padding-top: 0;
}

.filter-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
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
  border: 1px solid var(--border-color);
  min-width: 150px;
}

.search-bar {
  display: flex;
  max-width: 400px;
  flex: 1;
}

.form-control {
  flex: 1;
  padding: 10px 15px;
  border: none;
  border-radius: 5px 0 0 5px;
  background-color: var(--dark-color);
  color: var(--light-color);
}

.form-control:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--primary-color);
}

.btn-search {
  background-color: var(--primary-color);
  border: none;
  border-radius: 0 5px 5px 0;
  padding: 0 15px;
  color: white;
  cursor: pointer;
}

/* Table Styles */
.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--dark-color);
  border-radius: 5px;
  overflow: hidden;
  margin-top: 20px;
}

.data-table th, .data-table td {
  padding: 12px 15px;
  border-bottom: 1px solid var(--secondary-color);
}

.data-table th {
  background-color: #221728;
  color: var(--light-color);
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  user-select: none;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th:hover {
  background-color: #332639;
}

.data-table tbody tr {
  transition: background-color 0.3s;
}

.data-table tbody tr:hover {
  background-color: #3A2D40;
}

/* Status Badge */
.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: capitalize;
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

/* Expanded Details */
.expanded {
  background-color: #332639;
}

.details-row {
  background-color: #221728;
}

.request-details {
  padding: 15px 20px;
}

.details-section {
  margin-bottom: 20px;
}

.details-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: var(--light-color);
  font-size: 1.1rem;
  border-bottom: 1px solid var(--primary-color);
  padding-bottom: 5px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 10px;
}

.detail-item {
  margin-bottom: 10px;
}

.detail-label {
  font-weight: 600;
  color: var(--muted-color);
  margin-right: 10px;
  display: block;
  margin-bottom: 3px;
}

.detail-value {
  color: var(--light-color);
}

.detail-value.price {
  color: #2ecc71;
  font-weight: 600;
}

.remarks-box {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 5px;
  padding: 15px;
  white-space: pre-wrap;
  color: var(--light-color);
}

.details-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.no-professional {
  color: var(--muted-color);
  font-style: italic;
}

.details-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

/* Buttons */
.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 0.9rem;
}

.btn-expand {
  background-color: var(--primary-color);
  color: white;
}

.btn-collapse {
  background-color: var(--secondary-color);
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.actions-cell {
  text-align: center;
}

/* Loading, Error, Empty states */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
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

.error-message {
  padding: 20px;
  background-color: var(--danger-bg);
  border-radius: 5px;
  text-align: center;
  color: var(--danger-color);
}

.error-message i {
  font-size: 24px;
  margin-bottom: 10px;
}

.btn-retry {
  margin-top: 10px;
  background-color: var(--primary-color);
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  color: white;
  cursor: pointer;
}

.no-data {
  padding: 40px;
  text-align: center;
  color: var(--muted-color);
  background-color: var(--dark-color);
  border-radius: 5px;
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
  z-index: 1000;
}

@keyframes slideIn {
  from { transform: translateY(100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.toast.success {
  border-left: 4px solid var(--success-color);
}

.toast.error {
  border-left: 4px solid var(--danger-color);
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
  color: var(--success-color);
}

.toast.error i {
  color: var(--danger-color);
}

.toast-close {
  cursor: pointer;
  font-size: 0.9rem;
  padding: 5px;
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
  background-color: var(--secondary-color, #2F2235);
  width: 90%;
  max-width: 800px;
  border-radius: 10px;
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  background: none;
  border: none;
  font-size: 28px;
  color: var(--light-color, #BFC3BA);
  cursor: pointer;
  z-index: 2;
}

.modal-header {
  background-color: var(--dark-color, #221728);
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--primary-color, #60495A);
}

.modal-header h3 {
  margin: 0;
  color: var(--light-color, #BFC3BA);
}

.request-details {
  padding: 20px;
}

.details-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.modal-footer {
  padding: 15px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Enhance existing styles */
.btn-expand {
  background: var(--primary-color, #60495A);
  color: white;
}

.btn-expand:hover {
  background: #70596A;
}

/* Make sure details modal has proper scrolling */
.details-modal {
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.request-details {
  flex: 1;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .details-columns {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }
}
</style>
