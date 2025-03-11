<template>
  <div class="admin-services">
    <div class="header-actions">
      <h2>Service Management</h2>
      <button @click="openAddModal" class="btn btn-add">
        <i class="fas fa-plus"></i> Add New Service
      </button>
    </div>
    
    <div class="search-bar">
      <div class="input-group">
        <input 
          type="text" 
          v-model="searchTerm" 
          placeholder="Search services..." 
          class="form-control"
          @input="filterServices"
        >
        <button class="btn btn-search">
          <i class="fas fa-search"></i>
        </button>
      </div>
    </div>
    
    <!-- Loading state -->
    <div class="loading-container" v-if="loading">
      <div class="spinner"></div>
      <p>Loading service data...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button @click="fetchServices" class="btn btn-retry">Retry</button>
    </div>
    
    <!-- Empty state -->
    <div v-else-if="services.length === 0" class="no-data">
      <i class="fas fa-inbox fa-3x"></i>
      <p>No services found.</p>
      <button @click="openAddModal" class="btn btn-primary">Add First Service</button>
    </div>
    
    <!-- Service cards - the single UI design -->
    <div v-else class="service-cards">
      <div v-for="service in sortedServices" :key="service.id" class="service-card">
        <div class="service-card-header">
          <h3>{{ service.name }}</h3>
          <span class="service-price">₹{{ service.price.toFixed(2) }}</span>
        </div>
        <div class="service-card-body">
          <div class="service-meta">
            <div class="meta-item">
              <i class="fas fa-calendar-alt"></i> {{ formatDate(service.created_at, true) }}
            </div>
            <div class="meta-item">
              <i class="fas fa-tools"></i> {{ service.service_type }}
            </div>
          </div>
          <p class="service-description">{{ service.description || 'No description provided.' }}</p>
        </div>
        <div class="service-card-footer">
          <button @click="viewDetails(service)" class="btn btn-details" title="View details">
            <i class="fas fa-info-circle"></i>
          </button>
          <button @click="editService(service)" class="btn btn-edit" title="Edit service">
            <i class="fas fa-edit"></i>
          </button>
          <button 
            @click="confirmDelete(service)" 
            class="btn btn-delete" 
            title="Delete service"
            :disabled="processingId === service.id">
            <span v-if="processingId === service.id">
              <i class="fas fa-spinner fa-spin"></i>
            </span>
            <span v-else>
              <i class="fas fa-trash"></i>
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Service Form Modal (Add/Edit) -->
    <div v-if="showFormModal" class="modal-overlay" @click.self="cancelForm">
      <div class="modal-content">
        <h3>{{ isEditing ? 'Edit Service' : 'Add New Service' }}</h3>
        
        <form @submit.prevent="submitForm" class="service-form">
          <div class="form-group">
            <label for="serviceName">Service Name</label>
            <input 
              type="text" 
              id="serviceName" 
              v-model="formData.name" 
              class="form-control" 
              placeholder="Enter service name"
              required
            >
          </div>
          
          <div class="form-group">
            <label for="servicePrice">Price (₹)</label>
            <input 
              type="number" 
              id="servicePrice" 
              v-model="formData.price" 
              class="form-control" 
              placeholder="Service price"
              step="0.01"
              min="0"
              required
            >
          </div>
          
          <div class="form-group">
            <label for="serviceType">Service Type</label>
            <select 
              id="serviceType" 
              v-model="formData.service_type" 
              class="form-control"
              required
            >
              <option value="" disabled>Select a service type</option>
              <option v-for="type in serviceTypes" :key="type" :value="type">{{ type }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="serviceDescription">Description</label>
            <textarea 
              id="serviceDescription" 
              v-model="formData.description" 
              class="form-control" 
              placeholder="Describe the service"
              rows="4"
            ></textarea>
          </div>
          
          <div class="form-error" v-if="formError">
            {{ formError }}
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="cancelForm">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="formSubmitting">
              <span v-if="formSubmitting">
                <i class="fas fa-spinner fa-spin"></i> Saving...
              </span>
              <span v-else>
                {{ isEditing ? 'Update Service' : 'Add Service' }}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Service Details Modal -->
    <div v-if="selectedService" class="modal-overlay" @click.self="closeDetailsModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeDetailsModal">×</button>
        <h3>Service Details</h3>
        
        <div class="service-details">
          <div class="detail-row">
            <span class="detail-label">Name:</span>
            <span class="detail-value">{{ selectedService.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Price:</span>
            <span class="detail-value">₹{{ selectedService.price.toFixed(2) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Service Type:</span>
            <span class="detail-value">{{ selectedService.service_type }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Description:</span>
            <p class="detail-value description">{{ selectedService.description || 'No description provided.' }}</p>
          </div>
          <div class="detail-row">
            <span class="detail-label">Created:</span>
            <span class="detail-value">{{ formatDate(selectedService.created_at) }}</span>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="editService(selectedService)" class="btn btn-edit">
            <i class="fas fa-edit"></i> Edit Service
          </button>
          <button @click="confirmDelete(selectedService)" class="btn btn-delete">
            <i class="fas fa-trash"></i> Delete Service
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal-content delete-modal">
        <button class="close-btn" @click="cancelDelete">×</button>
        <h3>Confirm Deletion</h3>
        
        <div class="delete-warning">
          <i class="fas fa-exclamation-triangle"></i>
          <p>Are you sure you want to delete this service?</p>
          <p class="warning-service-name">{{ serviceToDelete?.name }}</p>
          <p class="warning-text">This action cannot be undone.</p>
        </div>
        
        <div class="modal-actions">
          <button @click="cancelDelete" class="btn btn-secondary">Cancel</button>
          <button @click="deleteService" class="btn btn-danger" :disabled="deleteProcessing">
            <span v-if="deleteProcessing">
              <i class="fas fa-spinner fa-spin"></i> Deleting...
            </span>
            <span v-else>
              Delete Service
            </span>
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
  name: 'AdminService',
  data() {
    return {
      services: [],
      filteredServices: [],
      loading: true,
      error: null,
      processingId: null,
      searchTerm: '',
      sortKey: 'id',
      sortDirection: 'asc',
      
      // Service types available
      serviceTypes: ['PLUMBING', 'ELECTRICAL', 'CLEANING', 'CARPENTRY', 'PAINTING'],
      
      // Service details
      selectedService: null,
      
      // Form handling
      showFormModal: false,
      isEditing: false,
      formData: {
        name: '',
        price: 0,
        description: '',
        service_type: ''
      },
      formError: null,
      formSubmitting: false,
      
      // Delete handling
      showDeleteModal: false,
      serviceToDelete: null,
      deleteProcessing: false,
      
      // Notification
      notification: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      },
      expandedServiceId: null,
      serviceRequests: [],
      loadingRequests: false,
    };
  },
  computed: {
    sortedServices() {
      return [...this.filteredServices].sort((a, b) => {
        let modifier = this.sortDirection === 'asc' ? 1 : -1;
        
        // Special handling for dates
        if (this.sortKey === 'created_at') {
          return new Date(a.created_at) > new Date(b.created_at) ? modifier : -modifier;
        }
        
        // Normal comparison for other fields
        if (a[this.sortKey] < b[this.sortKey]) return -1 * modifier;
        if (a[this.sortKey] > b[this.sortKey]) return 1 * modifier;
        return 0;
      });
    }
  },
  created() {
    this.fetchServices();
  },
  methods: {
    async fetchServices() {
      this.loading = true;
      this.error = null;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('No authorization token found');
        }
        
        const response = await axios.get('http://127.0.0.1:5000/admin/service', {
          headers: {
            'Authorization': token
          }
        });
        
        this.services = response.data;
        this.filteredServices = [...this.services];
      } catch (error) {
        console.error('Error fetching services:', error);
        this.error = error.response?.data?.error || error.message || 'Failed to load service data';
      } finally {
        this.loading = false;
      }
    },
    
    filterServices() {
      if (!this.searchTerm.trim()) {
        this.filteredServices = [...this.services];
        return;
      }
      
      const term = this.searchTerm.toLowerCase().trim();
      this.filteredServices = this.services.filter(service => 
        service.name.toLowerCase().includes(term) || 
        service.description?.toLowerCase().includes(term) ||
        service.id.toString().includes(term) ||
        service.price.toString().includes(term)
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
    
    formatDate(dateString, shortFormat = false) {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      if (shortFormat) {
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
    
    // Form handling methods
    openAddModal() {
      this.isEditing = false;
      this.formData = {
        name: '',
        price: 0,
        description: '',
        service_type: ''  // Ensure this is reset
      };
      this.formError = null;
      this.showFormModal = true;
    },
    
    editService(service) {
      this.isEditing = true;
      // Create a deep copy of the service to avoid directly modifying the original data
      this.formData = { 
        id: service.id,
        name: service.name,
        price: parseFloat(service.price),
        description: service.description || '',
        service_type: service.service_type || ''  // Ensure this is copied
      };
      console.log("Editing service:", this.formData);  // Debug log
      this.formError = null;
      this.showFormModal = true;
      
      // Close the details modal if open
      this.selectedService = null;
      
      // Ensure the modal is displayed by forcing a layout calculation
      setTimeout(() => {
        const modalElement = document.querySelector('.modal-overlay');
        if (modalElement) {
          modalElement.style.display = 'flex';
        }
      }, 10);
    },
    
    cancelForm() {
      this.showFormModal = false;
      this.formData = {
        name: '',
        price: 0,
        description: '',
        service_type: ''
      };
      this.formError = null;
    },
    
    async submitForm() {
      this.formError = null;
      this.formSubmitting = true;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('No authorization token found');
        }
        
        // Validate service type
        if (!this.formData.service_type) {
          this.formError = "Service type is required";
          this.formSubmitting = false;
          return;
        }
        
        // Ensure price is a number
        this.formData.price = parseFloat(this.formData.price);
        
        let response;
        
        if (this.isEditing) {
          // Update existing service
          response = await axios.put(
            `http://127.0.0.1:5000/admin/service/${this.formData.id}`,
            this.formData,
            {
              headers: {
                'Authorization': token
              }
            }
          );
          
          // Immediately refresh data from server instead of updating locally
          await this.fetchServices();
          
          this.showNotification({
            message: `Service "${this.formData.name}" has been updated successfully`,
            type: 'success'
          });
        } else {
          // Add new service
          response = await axios.post(
            'http://127.0.0.1:5000/admin/service',
            this.formData,
            {
              headers: {
                'Authorization': token
              }
            }
          );
          
          // Refresh the service list
          await this.fetchServices();
          
          this.showNotification({
            message: `Service "${this.formData.name}" has been added successfully`,
            type: 'success'
          });
        }
        
        // Close the form modal
        this.showFormModal = false;
      } catch (error) {
        console.error('Error submitting service form:', error);
        this.formError = error.response?.data?.error || error.message || 'Failed to save service';
      } finally {
        this.formSubmitting = false;
      }
    },
    
    // Service details methods
    viewDetails(service) {
      this.selectedService = { ...service };
    },
    
    closeDetailsModal() {
      this.selectedService = null;
    },
    
    // Delete handling methods
    confirmDelete(service) {
      this.serviceToDelete = service;
      this.showDeleteModal = true;
      
      // Close any other modals
      this.selectedService = null;
      this.showFormModal = false;
    },
    
    cancelDelete() {
      this.showDeleteModal = false;
      this.serviceToDelete = null;
    },
    
    async deleteService() {
      if (!this.serviceToDelete) return;
      
      this.deleteProcessing = true;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('No authorization token found');
        }
        
        await axios.delete(`http://127.0.0.1:5000/admin/service/${this.serviceToDelete.id}`, {
          headers: {
            'Authorization': token
          }
        });
        
        // Fetch fresh data from server instead of updating locally
        await this.fetchServices();
        
        this.showNotification({
          message: `Service "${this.serviceToDelete.name}" has been deleted successfully`,
          type: 'success'
        });
        
        // Close the delete modal
        this.showDeleteModal = false;
        this.serviceToDelete = null;
      } catch (error) {
        console.error('Error deleting service:', error);
        this.showNotification({
          message: error.response?.data?.error || error.message || 'Failed to delete service',
          type: 'error'
        });
      } finally {
        this.deleteProcessing = false;
      }
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
    async viewRequests(service) {
      if (this.expandedServiceId === service.id) {
        // If already expanded, collapse it
        this.expandedServiceId = null;
        return;
      }
      
      this.expandedServiceId = service.id;
      this.loadingRequests = true;
      this.serviceRequests = [];
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Not authenticated');
        }
        
        const response = await axios.get(`http://127.0.0.1:5000/admin/service/${service.id}/requests`, {
          headers: { 'Authorization': token }
        });
        
        this.serviceRequests = response.data;
      } catch (error) {
        console.error('Error fetching service requests:', error);
        this.showNotification({
          message: 'Failed to load service requests',
          type: 'error'
        });
      } finally {
        this.loadingRequests = false;
      }
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
      const statusLower = String(status).toLowerCase();
      if (statusLower === 'requested') return 'status-requested';
      if (statusLower === 'accepted') return 'status-accepted';
      if (statusLower === 'completed') return 'status-completed';
      if (statusLower === 'cancelled') return 'status-cancelled';
      if (statusLower === 'closed') return 'status-closed';
      return '';
    },
  }
};
</script>

<style scoped>
.admin-services {
  color: var(--light-color);
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

h2 {
  color: var(--light-color);
  margin: 0;
}

.btn-add {
  background-color: var(--success-color);
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.btn-add:hover {
  background-color: #218838;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.btn-search:hover {
  background-color: #4d3a49;
}

/* Loading and error states */
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

/* Card View Styles - The single UI design we're using */
.service-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.service-card {
  background-color: var(--dark-color);
  border-radius: 10px;
  color: var(--muted-color);
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.3);
}

.service-card-header {
  background-color: #221728;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--primary-color);
}

.service-card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--light-color);
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

.service-card-body {
  padding: 15px;
  flex: 1;
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
  color: var(--light-color);
  font-size: 0.95rem;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.service-card-footer {
  display: flex;
  justify-content: space-around;
  padding: 10px 15px;
  background-color: rgba(0, 0, 0, 0.1);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.service-card-footer .btn {
  padding: 8px 15px;
  flex: 1;
  margin: 0 5px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.btn-details {
  background-color: var(--primary-color);
  color: white;
}

.btn-details:hover {
  background-color: #4d3a49;
}

.btn-edit {
  background-color: var(--info-color);
  color: white;
}

.btn-edit:hover {
  background-color: #138496;
}

.btn-delete {
  background-color: var(--danger-color);
  color: white;
}

.btn-delete:hover:not(:disabled) {
  background-color: #c82333;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Empty state styling */
.no-data {
  text-align: center;
  padding: 40px 20px;
  background-color: var(--dark-color);
  border-radius: 10px;
  color: var(--muted-color);
}

.no-data i {
  margin-bottom: 15px;
  color: var(--primary-color);
}

.no-data p {
  margin-bottom: 20px;
  font-size: 1.1rem;
}

/* Button styles */
.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4d3a49;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .service-cards {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 576px) {
  .service-cards {
    grid-template-columns: 1fr;
  }
}

/* Improved modal styles to ensure visibility */
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
  opacity: 1;
  visibility: visible;
  transition: opacity 0.3s, visibility 0.3s;
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
  transform: translateY(0);
  transition: transform 0.3s;
  animation: modalAppear 0.3s ease;
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Additional form styles to improve usability */
.form-control {
  flex: 1;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  background-color: var(--dark-color);
  color: var(--light-color);
  width: 100%;
  box-sizing: border-box;
}

textarea.form-control {
  resize: vertical;
  min-height: 100px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--light-color);
  font-weight: 500;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

select.form-control {
  background-color: var(--dark-color);
  color: var(--light-color);
  border-radius: 5px;
  padding: 10px 15px;
  border: none;
  width: 100%;
  appearance: auto;
}

select.form-control:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--primary-color);
}

/* Style for service type tag in the card */
.service-meta .meta-item i.fa-tools {
  color: #3fb950;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

@media (max-width: 576px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

/* Service Requests Expansion Panel */
.requests-row {
  background-color: rgba(0, 0, 0, 0.1);
}

.service-requests-panel {
  padding: 20px;
  background-color: #2F2235;
  border-radius: 5px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.service-requests-panel h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: var(--light-color);
  border-bottom: 1px solid var(--primary-color);
  padding-bottom: 10px;
}

.requests-table-container {
  overflow-x: auto;
  margin-bottom: 15px;
}

.requests-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.requests-table th, .requests-table td {
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.requests-table th {
  background-color: rgba(0, 0, 0, 0.2);
  font-weight: 600;
  color: var(--light-color);
}

.panel-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}

.status-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
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

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
}

.spinner {
  border: 3px solid rgba(96, 73, 90, 0.3);
  border-radius: 50%;
  border-top: 3px solid var(--primary-color);
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

.no-requests {
  padding: 20px;
  text-align: center;
  color: var(--muted-color);
}

.expanded {
  background-color: rgba(96, 73, 90, 0.2);
  border-bottom: none !important;
}
</style>
