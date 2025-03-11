<template>
  <div class="admin-customers">
    <h2>Customer Management</h2>
    
    <div class="search-bar">
      <div class="input-group">
        <input 
          type="text" 
          v-model="searchTerm" 
          placeholder="Search customers..." 
          class="form-control"
          @input="filterCustomers"
        >
        <button class="btn btn-search">
          <i class="fas fa-search"></i>
        </button>
      </div>
    </div>
    
    <div class="loading-container" v-if="loading">
      <div class="spinner"></div>
      <p>Loading customer data...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button @click="fetchCustomers" class="btn btn-retry">Retry</button>
    </div>
    
    <div v-else-if="customers.length === 0" class="no-data">
      <p>No customers found.</p>
    </div>
    
    <div v-else class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="sortBy('id')">
              ID <i :class="getSortIcon('id')"></i>
            </th>
            <th @click="sortBy('name')">
              Name <i :class="getSortIcon('name')"></i>
            </th>
            <th @click="sortBy('email')">
              Email <i :class="getSortIcon('email')"></i>
            </th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in sortedCustomers" :key="customer.id" :class="{ 'inactive': !customer.active }">
            <td>{{ customer.id }}</td>
            <td>{{ customer.name }}</td>
            <td>{{ customer.email }}</td>
            <td>
              <span class="status-badge" :class="customer.active ? 'active' : 'inactive'">
                {{ customer.active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <button 
                @click="toggleCustomerStatus(customer)" 
                class="btn" 
                :class="customer.active ? 'btn-deactivate' : 'btn-activate'"
                :disabled="processingId === customer.id"
              >
                <span v-if="processingId === customer.id">
                  <i class="fas fa-spinner fa-spin"></i>
                </span>
                <span v-else>
                  {{ customer.active ? 'Deactivate' : 'Activate' }}
                </span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
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
  name: 'AdminCustomers',
  data() {
    return {
      customers: [],
      filteredCustomers: [],
      loading: true,
      error: null,
      processingId: null,
      searchTerm: '',
      sortKey: 'id',
      sortDirection: 'asc',
      notification: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      }
    };
  },
  computed: {
    sortedCustomers() {
      return [...this.filteredCustomers].sort((a, b) => {
        let modifier = this.sortDirection === 'asc' ? 1 : -1;
        if (a[this.sortKey] < b[this.sortKey]) return -1 * modifier;
        if (a[this.sortKey] > b[this.sortKey]) return 1 * modifier;
        return 0;
      });
    }
  },
  created() {
    this.fetchCustomers();
  },
  methods: {
    async fetchCustomers() {
      this.loading = true;
      this.error = null;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('No authorization token found');
        }
        
        // Fix: Make sure to use the correct token format
        const response = await axios.get('http://127.0.0.1:5000/admin/customers', {
          headers: {
            'Authorization': token // Remove 'Bearer ' prefix, as it's already in the token
          }
        });
        
        this.customers = response.data;
        this.filteredCustomers = [...this.customers];
      } catch (error) {
        console.error('Error fetching customers:', error);
        this.error = error.response?.data?.error || error.message || 'Failed to load customer data';
      } finally {
        this.loading = false;
      }
    },
    
    async toggleCustomerStatus(customer) {
      this.processingId = customer.id;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('No authorization token found');
        }
        
        console.log(`Sending request to toggle customer ${customer.id} status from ${customer.active} to ${!customer.active}`);
        
        // Send the updated active status - toggle the current value
        const response = await axios.put(
          `http://127.0.0.1:5000/admin/customers/${customer.id}`, 
          {
            active: !customer.active
          },
          {
            headers: {
              'Authorization': token
            }
          }
        );
        
        console.log('API Response:', response.data);
        
        // Update local data only after successful API response
        customer.active = !customer.active;
        
        // Show success notification
        this.showNotification({
          message: `Customer ${customer.name} has been ${customer.active ? 'activated' : 'deactivated'}`,
          type: 'success'
        });
      } catch (error) {
        console.error('Error toggling customer status:', error);
        let errorMsg = 'Failed to update customer status';
        
        if (error.response) {
          console.log('Error response:', error.response.data);
          errorMsg = error.response.data.error || errorMsg;
        }
        
        this.showNotification({
          message: errorMsg,
          type: 'error'
        });
      } finally {
        this.processingId = null;
      }
    },
    
    filterCustomers() {
      if (!this.searchTerm.trim()) {
        this.filteredCustomers = [...this.customers];
        return;
      }
      
      const term = this.searchTerm.toLowerCase().trim();
      this.filteredCustomers = this.customers.filter(customer => 
        customer.name.toLowerCase().includes(term) || 
        customer.email.toLowerCase().includes(term) ||
        customer.id.toString().includes(term)
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
.admin-customers {
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

.data-table tr.inactive {
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

.status-badge.inactive {
  background-color: rgba(108, 117, 125, 0.2);
  color: #6c757d;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-activate {
  background-color: var(--success-color);
  color: white;
}

.btn-activate:hover {
  background-color: #218838;
}

.btn-deactivate {
  background-color: #6c757d;
  color: white;
}

.btn-deactivate:hover {
  background-color: #5a6268;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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
  
  .btn {
    padding: 5px 10px;
    font-size: 0.85rem;
  }
  
  .toast {
    left: 20px;
    right: 20px;
    min-width: auto;
  }
}
</style>
