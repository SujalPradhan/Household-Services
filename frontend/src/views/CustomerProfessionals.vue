<template>
  <div class="customer-professionals">
    <div class="page-header">
      <h1>Find Professionals</h1>
      <div class="search-filters">
        <div class="search-container">
          <input 
            v-model="searchQuery" 
            placeholder="Search by name or skills" 
            class="search-input"
          />
          <button @click="searchProfessionals" class="search-button">
            <i class="fas fa-search"></i> Search
          </button>
        </div>
        <div class="filter-container">
          <label for="serviceTypeFilter">Filter by Service:</label>
          <select v-model="serviceTypeFilter" id="serviceTypeFilter" @change="applyFilters">
            <option value="">All Service Types</option>
            <option v-for="type in serviceTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Professionals Section -->
    <div class="professionals-section">
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>Looking for qualified professionals...</p>
      </div>
      
      <div v-else-if="filteredProfessionals.length === 0" class="no-professionals">
        <p>No professionals found matching your criteria.</p>
        <button @click="clearFilters" class="btn btn-secondary">Clear Filters</button>
      </div>
      
      <div v-else class="professionals-grid">
        <div 
          v-for="professional in filteredProfessionals" 
          :key="professional.id" 
          class="professional-card"
          @click="viewProfessionalDetails(professional)"
        >
          <div class="professional-avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="professional-info">
            <h3>{{ professional.name }}</h3>
            <div class="professional-meta">
              <div class="meta-item">
                <i class="fas fa-tools"></i> {{ professional.service_type }}
              </div>
              <div class="meta-item">
                <i class="fas fa-star"></i> {{ professional.experience }} {{ professional.experience === 1 ? 'year' : 'years' }} experience
              </div>
            </div>
            <p v-if="professional.description" class="professional-description">
              {{ truncateText(professional.description, 100) }}
            </p>
          </div>
          <div class="view-profile">
            <i class="fas fa-chevron-right"></i>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Professional Details Modal -->
    <div v-if="selectedProfessional" class="modal-overlay" @click.self="closeProfessionalModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeProfessionalModal">×</button>
        <div class="professional-details">
          <div class="professional-header">
            <div class="professional-avatar large">
              <i class="fas fa-user-circle"></i>
            </div>
            <div>
              <h2>{{ selectedProfessional.name }}</h2>
              <span class="service-type-badge">{{ selectedProfessional.service_type }}</span>
            </div>
          </div>
          
          <div class="detail-section">
            <h3><i class="fas fa-info-circle"></i> About</h3>
            <p class="professional-about">{{ selectedProfessional.description || 'No description provided.' }}</p>
          </div>
          
          <div class="detail-section">
            <h3><i class="fas fa-star"></i> Experience</h3>
            <p>{{ selectedProfessional.experience }} {{ selectedProfessional.experience === 1 ? 'year' : 'years' }} of professional experience</p>
          </div>
          
          <div class="detail-section">
            <h3><i class="fas fa-tools"></i> Services Offered</h3>
            <div class="services-offered">
              <div v-if="loadingServices" class="loading-services">
                <div class="spinner small"></div>
                <p>Loading available services...</p>
              </div>
              <div v-else-if="professionalServices.length === 0" class="no-services-message">
                <p>This professional doesn't have any available services right now.</p>
              </div>
              <ul v-else class="services-list">
                <li v-for="service in professionalServices" :key="service.id" class="service-item">
                  <div class="service-item-info">
                    <h4>{{ service.name }}</h4>
                    <span class="service-price">₹{{ service.price.toFixed(2) }}</span>
                  </div>
                  <button @click="requestServiceFromProfessional(service)" class="btn btn-request">
                    Request
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Request Service Modal -->
    <div v-if="requestService" class="modal-overlay" @click.self="closeRequestModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeRequestModal">×</button>
        <h2>Request Service</h2>
        <p><strong>Service:</strong> {{ requestService.name }}</p>
        <p><strong>Professional:</strong> {{ selectedProfessional ? selectedProfessional.name : 'Not selected' }}</p>
        
        <div class="form-group">
          <label for="preferredDate">Preferred Date:</label>
          <input type="datetime-local" id="preferredDate" v-model="requestForm.preferredDate" class="form-control" required>
        </div>
        
        <div class="form-group">
          <label for="remarks">Additional Notes:</label>
          <textarea id="remarks" v-model="requestForm.remarks" class="form-control" rows="4"></textarea>
        </div>
        
        <div class="modal-actions">
          <button @click="closeRequestModal" class="btn btn-secondary">Cancel</button>
          <button @click="submitServiceRequest" class="btn btn-primary" :disabled="isSubmitting">
            <span v-if="isSubmitting">
              <i class="fas fa-spinner fa-spin"></i> Processing...
            </span>
            <span v-else>
              Submit Request
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
  name: 'CustomerProfessionals',
  data() {
    return {
      professionals: [],
      filteredProfessionals: [],
      loading: true,
      searchQuery: '',
      serviceTypeFilter: '',
      serviceTypes: ['PLUMBING', 'ELECTRICAL', 'CLEANING', 'CARPENTRY', 'PAINTING'],
      selectedProfessional: null,
      professionalServices: [],
      loadingServices: false,
      requestService: null,
      requestForm: {
        preferredDate: this.getDefaultDate(),
        remarks: ''
      },
      isSubmitting: false,
      notification: {
        show: false,
        message: '',
        type: 'success',
        timeout: null
      }
    };
  },
  methods: {
    async fetchProfessionals() {
      try {
        this.loading = true;
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Authorization token not found');
        }
        
        const response = await axios.get('http://127.0.0.1:5000/admin/search-professionals', {
          headers: {
            Authorization: token
          }
        });
        
        // Filter only approved and not blocked professionals
        this.professionals = (response.data || []).filter(
          pro => pro.approved && !pro.blocked
        );
        
        this.filteredProfessionals = [...this.professionals];
      } catch (error) {
        console.error("Error fetching professionals:", error);
        this.showNotification({
          message: "Failed to load professionals. Please try again later.",
          type: "error"
        });
      } finally {
        this.loading = false;
      }
    },
    
    searchProfessionals() {
      this.applyFilters();
    },
    
    applyFilters() {
      let filtered = [...this.professionals];
      
      // Apply search query filter
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(pro => 
          (pro.name && pro.name.toLowerCase().includes(query)) || 
          (pro.description && pro.description.toLowerCase().includes(query))
        );
      }
      
      // Apply service type filter
      if (this.serviceTypeFilter) {
        filtered = filtered.filter(pro => pro.service_type === this.serviceTypeFilter);
      }
      
      this.filteredProfessionals = filtered;
    },
    
    clearFilters() {
      this.searchQuery = '';
      this.serviceTypeFilter = '';
      this.filteredProfessionals = [...this.professionals];
    },
    
    async viewProfessionalDetails(professional) {
      this.selectedProfessional = { ...professional };
      await this.fetchProfessionalServices(professional);
    },
    
    async fetchProfessionalServices(professional) {
      this.loadingServices = true;
      this.professionalServices = [];
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Authorization token not found');
        }
        
        // First get all available services
        const response = await axios.get('http://127.0.0.1:5000/customer/dashboard', {
          headers: {
            Authorization: token
          }
        });
        
        // Filter services that match this professional's service type
        const allServices = response.data.available_services || [];
        this.professionalServices = allServices.filter(
          service => service.service_type === professional.service_type
        );
      } catch (error) {
        console.error("Error fetching professional services:", error);
        this.showNotification({
          message: "Failed to load services for this professional.",
          type: "error"
        });
      } finally {
        this.loadingServices = false;
      }
    },
    
    closeProfessionalModal() {
      this.selectedProfessional = null;
      this.professionalServices = [];
    },
    
    requestServiceFromProfessional(service) {
      this.requestService = service;
      this.requestForm.preferredDate = this.getDefaultDate();
      this.requestForm.remarks = '';
    },
    
    closeRequestModal() {
      this.requestService = null;
    },
    
    getDefaultDate() {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(10, 0, 0, 0);
      
      // Format as YYYY-MM-DDThh:mm
      return tomorrow.toISOString().slice(0, 16);
    },
    
    async submitServiceRequest() {
      if (!this.requestService || !this.selectedProfessional) {
        this.showNotification({
          message: "Missing service or professional information.",
          type: "error"
        });
        return;
      }
      
      this.isSubmitting = true;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Authorization token not found');
        }
        
        await axios.post('http://127.0.0.1:5000/customer/services', {
          service_id: this.requestService.id,
          professional_id: this.selectedProfessional.id,
          remarks: this.requestForm.remarks,
          preferred_date: this.requestForm.preferredDate
        }, {
          headers: {
            Authorization: token
          }
        });
        
        this.showNotification({
          message: "Service request submitted successfully!",
          type: "success"
        });
        
        // Close the modal
        this.closeRequestModal();
      } catch (error) {
        console.error("Error submitting request:", error);
        this.showNotification({
          message: error.response?.data?.error || "Failed to submit service request.",
          type: "error"
        });
      } finally {
        this.isSubmitting = false;
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
        }, 3000)
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
  mounted() {
    this.fetchProfessionals();
  }
};
</script>

<style scoped>
.customer-professionals {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin-bottom: 15px;
  color: var(--light-color);
}

.search-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

.search-container {
  display: flex;
  flex: 1;
  max-width: 400px;
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

.filter-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-container label {
  color: var(--light-color);
  font-weight: 500;
}

.filter-container select {
  padding: 10px;
  border-radius: 5px;
  background-color: var(--dark-color);
  color: var(--light-color);
  border: 1px solid var(--border-color, #333);
}

/* Professionals Grid */
.professionals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.professional-card {
  background-color: var(--dark-color);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 15px;
}

.professional-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.3);
}

.professional-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.professional-avatar i {
  font-size: 2rem;
  color: white;
}

.professional-avatar.large {
  width: 80px;
  height: 80px;
}

.professional-avatar.large i {
  font-size: 3rem;
}

.professional-info {
  flex: 1;
}

.professional-info h3 {
  margin: 0 0 10px 0;
  color: var(--light-color);
  font-size: 1.2rem;
}

.professional-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
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

.professional-description {
  color: var(--muted-color);
  margin: 0;
  font-size: 0.9rem;
}

.view-profile {
  color: var(--primary-color);
  margin-left: 15px;
  transition: transform 0.3s;
}

.professional-card:hover .view-profile {
  transform: translateX(5px);
}

/* Professional Details Modal */
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

.professional-header {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.professional-header h2 {
  margin: 0 0 5px 0;
  color: var(--light-color);
  font-size: 1.5rem;
}

.service-type-badge {
  background-color: var(--primary-color);
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h3 {
  display: flex;
  align-items: center;
  color: var(--light-color);
  font-size: 1.1rem;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.detail-section h3 i {
  margin-right: 8px;
  color: var(--primary-color);
}

.professional-about {
  color: var(--muted-color);
  line-height: 1.6;
  white-space: pre-line;
}

/* Services List */
.services-offered {
  margin-top: 15px;
}

.services-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.service-item {
  background-color: var(--dark-color);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-item-info h4 {
  margin: 0 0 5px 0;
  color: var(--light-color);
  font-size: 1rem;
}

.service-price {
  color: var(--primary-color);
  font-weight: bold;
}

.btn-request {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 5px;
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-request:hover {
  background-color: #8e67d2;
  transform: translateY(-2px);
}

.loading-services {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.spinner.small {
  width: 30px;
  height: 30px;
  border-width: 3px;
}

.no-services-message {
  text-align: center;
  padding: 20px;
  color: var(--muted-color);
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
  border: 1px solid var(--border-color, #333);
}

.modal-actions {
  margin-top: 25px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Button Styles */
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
}

.btn-primary {
  background: linear-gradient(135deg, #7e57c2, #60495A);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #8e67d2, #70596A);
  transform: translateY(-2px);
}

.btn-secondary {
  background: linear-gradient(135deg, #78909c, #546e7a);
  color: white;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #8ca0ac, #647c8a);
  transform: translateY(-2px);
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}

/* Loading States */
.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 50px 0;
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

/* Empty State */
.no-professionals {
  color: var(--muted-color);
  border-radius: 8px;
  background-color: var(--dark-color);
  text-align: center;
  padding: 40px 20px;
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

/* Responsive Styles */
@media (max-width: 768px) {
  .professionals-grid {
    grid-template-columns: 1fr;
  }
  
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-container {
    max-width: none;
  }
  
  .professional-meta {
    flex-direction: column;
    gap: 5px;
  }
}
</style>
