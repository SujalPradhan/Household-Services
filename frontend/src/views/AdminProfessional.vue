<template>
  <div class="admin-professionals">
    <h2>Professional Management</h2>
    
    <div class="search-bar">
      <div class="input-group">
        <input 
          type="text" 
          v-model="searchTerm" 
          placeholder="Search professionals..." 
          class="form-control"
          @input="filterProfessionals"
        >
        <button class="btn btn-search">
          <i class="fas fa-search"></i>
        </button>
      </div>
    </div>
    
    <div class="loading-container" v-if="loading">
      <div class="spinner"></div>
      <p>Loading professional data...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button @click="fetchProfessionals" class="btn btn-retry">Retry</button>
    </div>
    
    <div v-else-if="professionals.length === 0" class="no-data">
      <p>No professionals found.</p>
    </div>
    
    <div v-else class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="sortBy('id')">ID <i :class="getSortIcon('id')"></i></th>
            <th @click="sortBy('name')">Name <i :class="getSortIcon('name')"></i></th>
            <th @click="sortBy('email')">Email <i :class="getSortIcon('email')"></i></th>
            <th @click="sortBy('service_type')">Service Type <i :class="getSortIcon('service_type')"></i></th>
            <th @click="sortBy('experience')">Experience <i :class="getSortIcon('experience')"></i></th>
            <th>Approval Status</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="professional in sortedProfessionals" :key="professional.id" :class="{ 'blocked': professional.blocked }">
            <td>{{ professional.id }}</td>
            <td>{{ professional.name }}</td>
            <td>{{ professional.email }}</td>
            <td>{{ formatServiceType(professional.service_type) }}</td>
            <td>{{ professional.experience }} {{ professional.experience === 1 ? 'year' : 'years' }}</td>
            <td>
              <span class="status-badge" :class="professional.approved ? 'approved' : 'pending'">
                {{ professional.approved ? 'Approved' : 'Pending' }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="professional.blocked ? 'blocked' : 'active'">
                {{ professional.blocked ? 'Blocked' : 'Active' }}
              </span>
            </td>
            <td class="actions">
              <button 
                @click="toggleApproval(professional)" 
                class="btn" 
                :class="professional.approved ? 'btn-reject' : 'btn-approve'"
                :disabled="processingId === professional.id"
                :title="professional.approved ? 'Revoke approval' : 'Approve professional'"
              >
                <span v-if="processingId === professional.id && actionType === 'approval'">
                  <i class="fas fa-spinner fa-spin"></i>
                </span>
                <span v-else>
                  {{ professional.approved ? 'Revoke' : 'Approve' }}
                </span>
              </button>
              <button 
                @click="toggleBlock(professional)" 
                class="btn" 
                :class="professional.blocked ? 'btn-unblock' : 'btn-block'"
                :disabled="processingId === professional.id"
                :title="professional.blocked ? 'Unblock professional' : 'Block professional'"
              >
                <span v-if="processingId === professional.id && actionType === 'block'">
                  <i class="fas fa-spinner fa-spin"></i>
                </span>
                <span v-else>
                  {{ professional.blocked ? 'Unblock' : 'Block' }}
                </span>
              </button>
              <button 
                @click="viewDetails(professional)"
                class="btn btn-details"
                title="View details"
              >
                <i class="fas fa-info-circle"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Professional Details Modal -->
    <div v-if="selectedProfessional" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeModal">×</button>
        <h3>Professional Details</h3>
        <div class="professional-details">
          <div class="detail-row">
            <span class="detail-label">Name:</span>
            <span class="detail-value">{{ selectedProfessional.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Email:</span>
            <span class="detail-value">{{ selectedProfessional.email }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Service Type:</span>
            <span class="detail-value">{{ formatServiceType(selectedProfessional.service_type) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Experience:</span>
            <span class="detail-value">{{ selectedProfessional.experience }} {{ selectedProfessional.experience === 1 ? 'year' : 'years' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Description:</span>
            <p class="detail-value description">{{ selectedProfessional.description || 'No description provided.' }}</p>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">
              <span class="status-badge" :class="selectedProfessional.blocked ? 'blocked' : 'active'">
                {{ selectedProfessional.blocked ? 'Blocked' : 'Active' }}
              </span>
              <span class="status-badge" :class="selectedProfessional.approved ? 'approved' : 'pending'" style="margin-left: 10px;">
                {{ selectedProfessional.approved ? 'Approved' : 'Pending Approval' }}
              </span>
            </span>
          </div>
        </div>
        <div class="modal-actions">
          <button 
            @click="toggleApproval(selectedProfessional)" 
            class="btn" 
            :class="selectedProfessional.approved ? 'btn-reject' : 'btn-approve'"
          >
            {{ selectedProfessional.approved ? 'Revoke Approval' : 'Approve Professional' }}
          </button>
          <button 
            @click="toggleBlock(selectedProfessional)" 
            class="btn" 
            :class="selectedProfessional.blocked ? 'btn-unblock' : 'btn-block'"
          >
            {{ selectedProfessional.blocked ? 'Unblock Professional' : 'Block Professional' }}
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
  name: 'AdminProfessionals',
  data() {
    return {
      professionals: [],
      filteredProfessionals: [],
      loading: true,
      error: null,
      processingId: null,
      actionType: null,
      searchTerm: '',
      sortKey: 'id',
      sortDirection: 'asc',
      selectedProfessional: null,
      notification: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      }
    };
  },
  computed: {
    sortedProfessionals() {
      return [...this.filteredProfessionals].sort((a, b) => {
        let modifier = this.sortDirection === 'asc' ? 1 : -1;
        if (a[this.sortKey] < b[this.sortKey]) return -1 * modifier;
        if (a[this.sortKey] > b[this.sortKey]) return 1 * modifier;
        return 0;
      });
    }
  },
  created() {
    this.fetchProfessionals();
  },
  methods: {
    async fetchProfessionals() {
      this.loading = true;
      this.error = null;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('No authorization token found');
        }
        
        const response = await axios.get('http://127.0.0.1:5000/admin/professionals', {
          headers: {
            'Authorization': token
          }
        });
        
        this.professionals = response.data;
        this.filteredProfessionals = [...this.professionals];
      } catch (error) {
        console.error('Error fetching professionals:', error);
        this.error = error.response?.data?.error || error.message || 'Failed to load professional data';
      } finally {
        this.loading = false;
      }
    },
    
    async toggleApproval(professional) {
      this.processingId = professional.id;
      this.actionType = 'approval';
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('No authorization token found');
        }
        
        const response = await axios.put(
          `http://127.0.0.1:5000/admin/professionals/${professional.id}`, 
          { approved: !professional.approved },
          {
            headers: {
              'Authorization': token
            }
          }
        );
        
        // Update local data
        professional.approved = !professional.approved;
        
        // Update selected professional if modal is open
        if (this.selectedProfessional && this.selectedProfessional.id === professional.id) {
          this.selectedProfessional.approved = professional.approved;
        }
        
        // Show success notification
        this.showNotification({
          message: `Professional ${professional.name} has been ${professional.approved ? 'approved' : 'unapproved'}`,
          type: 'success'
        });
      } catch (error) {
        console.error('Error toggling professional approval:', error);
        this.showNotification({
          message: error.response?.data?.error || error.message || 'Failed to update professional approval status',
          type: 'error'
        });
      } finally {
        this.processingId = null;
        this.actionType = null;
      }
    },
    
    async toggleBlock(professional) {
      this.processingId = professional.id;
      this.actionType = 'block';
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('No authorization token found');
        }
        
        const response = await axios.put(
          `http://127.0.0.1:5000/admin/professionals/${professional.id}`,
          { blocked: !professional.blocked },
          {
            headers: {
              'Authorization': token
            }
          }
        );
        
        // Update local data
        professional.blocked = !professional.blocked;
        
        // Update selected professional if modal is open
        if (this.selectedProfessional && this.selectedProfessional.id === professional.id) {
          this.selectedProfessional.blocked = professional.blocked;
        }
        
        // Show success notification
        this.showNotification({
          message: `Professional ${professional.name} has been ${professional.blocked ? 'blocked' : 'unblocked'}`,
          type: 'success'
        });
      } catch (error) {
        console.error('Error toggling professional block status:', error);
        this.showNotification({
          message: error.response?.data?.error || error.message || 'Failed to update professional block status',
          type: 'error'
        });
      } finally {
        this.processingId = null;
        this.actionType = null;
      }
    },
    
    filterProfessionals() {
      if (!this.searchTerm.trim()) {
        this.filteredProfessionals = [...this.professionals];
        return;
      }
      
      const term = this.searchTerm.toLowerCase().trim();
      this.filteredProfessionals = this.professionals.filter(professional => 
        professional.name.toLowerCase().includes(term) || 
        professional.email.toLowerCase().includes(term) ||
        professional.id.toString().includes(term) ||
        professional.service_type.toLowerCase().includes(term)
      );
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

    formatServiceType(type) {
      if (!type) return 'Unknown';
      return type.toLowerCase().replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    },

    viewDetails(professional) {
      this.selectedProfessional = { ...professional };
    },

    closeModal() {
      this.selectedProfessional = null;
    },

    showNotification(options) {
      // Clear any existing timeout
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
    }
  }
};
</script>

<style scoped>
.admin-professionals {
  color: var(--light-color);
}

h2 {
  margin-bottom: 25px;
  color: var(--light-color);
}

.search-bar {
  margin-bottom: 20px;
}

.input-group {
  display: flex;
  width: 100%;
  max-width: 400px;
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
}

.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--dark-color);
  border-radius: 5px;
  overflow: hidden;
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

.data-table tr.blocked {
  opacity: 0.7;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.active {
  background-color: var(--success-bg);
  color: var(--success-color);
}

.status-badge.blocked {
  background-color: var(--danger-bg);
  color: var(--danger-color);
}

.status-badge.approved {
  background-color: var(--success-bg);
  color: var(--success-color);
}

.status-badge.pending {
  background-color: var(--warning-bg);
  color: var(--warning-color);
}

.actions {
  display: flex;
  gap: 5px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-approve {
  background-color: var(--success-color);
  color: white;
}

.btn-approve:hover {
  background-color: #218838;
}

.btn-reject {
  background-color: #6c757d;
  color: white;
}

.btn-reject:hover {
  background-color: #5a6268;
}

.btn-block {
  background-color: var(--danger-color);
  color: white;
}

.btn-block:hover {
  background-color: #c82333;
}

.btn-unblock {
  background-color: #17a2b8;
  color: white;
}

.btn-unblock:hover {
  background-color: #138496;
}

.btn-details {
  background-color: var(--primary-color);
  color: white;
}

.btn-details:hover {
  background-color: #4d3a49;
}

button:disabled {
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
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 24px;
  background: none;
  border: none;
  color: var(--light-color);
  cursor: pointer;
}

.modal-content h3 {
  color: var(--light-color);
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.professional-details {
  margin-bottom: 20px;
}

.detail-row {
  margin-bottom: 10px;
  display: flex;
}

.detail-label {
  width: 120px;
  font-weight: bold;
  color: var(--light-color);
}

.detail-value {
  flex: 1;
  color: var(--muted-color);
}

.detail-value.description {
  margin-top: 0;
  white-space: pre-line;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid var(--border-color);
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

@media (max-width: 768px) {
  .data-table {
    font-size: 0.9rem;
  }
  
  .data-table th, .data-table td {
    padding: 10px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .btn {
    padding: 5px 10px;
    font-size: 0.85rem;
    width: 100%;
  }
  
  .toast {
    left: 20px;
    right: 20px;
    min-width: auto;
  }
  
  .detail-row {
    flex-direction: column;
  }
  
  .detail-label {
    width: 100%;
  }
}
</style>
