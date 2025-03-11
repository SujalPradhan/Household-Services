<template>
    <div class="customer-services">
      <div class="page-header">
        <h1>Available Services</h1>
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
            
            <div class="price-confirmation">
              <span class="price-info">Service will be requested at the price of <strong>₹{{ selectedService.price.toFixed(2) }}</strong></span>
            </div>
            
            <div class="modal-actions">
              <button 
                @click="closeServiceModal" 
                class="btn btn-secondary"
              >
                Close
              </button>
              <button 
                @click="requestServiceWithPrice(selectedService)" 
                class="btn btn-primary"
              >
                Confirm & Request
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
        searchQuery: '',
        availableServices: [],
        filteredServices: [],
        loading: true,
        selectedService: null,
        quickRequestService: null,
        notification: {
          show: false,
          message: '',
          type: 'success',
          timeout: null
        }
      };
    },
    methods: {
      async fetchServices() {
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
          
          // Process available services
          this.availableServices = response.data.available_services || [];
          this.filteredServices = [...this.availableServices];
          
        } catch (error) {
          console.error("Error fetching services:", error);
          this.showNotification({
            message: "Failed to load services. Please try again later.",
            type: "error"
          });
        } finally {
          this.loading = false;
        }
      },
      
      searchServices() {
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
      
      viewServiceDetails(service) {
        this.selectedService = { ...service };
      },
      
      closeServiceModal() {
        this.selectedService = null;
      },
      
      requestServiceDirectly(service) {
        this.quickRequestService = { 
          ...service,
          confirmedPrice: service.price // Ensure price is passed to the form
        };
        // Close the details modal if it's open
        this.selectedService = null;
      },
      
      requestServiceWithPrice(service) {
        // Explicitly pass the price to ensure backend connection
        this.quickRequestService = { 
          ...service,
          confirmedPrice: service.price 
        };
        this.closeServiceModal();
      },
      
      closeQuickRequestModal() {
        this.quickRequestService = null;
      },
      
      handleRequestSuccess(result) {
        this.showNotification({
          message: `Service request submitted successfully at price ₹${result.price?.toFixed(2) || this.quickRequestService?.price?.toFixed(2)}!`,
          type: "success"
        });
        
        // Close the modal
        this.closeQuickRequestModal();
      },
      
      handleRequestError(errorMessage) {
        this.showNotification({
          message: errorMessage,
          type: "error"
        });
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
      }
    },
    mounted() {
      this.fetchServices();
    }
  };
  </script>
  
  <style scoped>
  .customer-services {
    padding: 20px;
  }
  
  .page-header {
    margin-bottom: 30px;
  }
  
  .page-header h1 {
    margin-bottom: 15px;
    color: var(--light-color);
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
    color: var(--light-color);
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
    color: var(--light-color);
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
  
  .price-confirmation {
    margin-top: 20px;
    padding: 10px 15px;
    background-color: rgba(126, 87, 194, 0.1);
    border-radius: 5px;
    border-left: 4px solid var(--primary-color);
  }
  
  .price-info {
    color: var(--light-color);
    font-size: 0.95rem;
  }
  
  .modal-actions {
    margin-top: 25px;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
  
  /* Buttons */
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
  
  .btn-secondary {
    background: linear-gradient(135deg, #78909c, #546e7a);
    color: white;
  }
  
  .btn-secondary:hover {
    background: linear-gradient(135deg, #8ca0ac, #647c8a);
  }
  
  /* Loading States */
  .loading-container {
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
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  /* Empty States */
  .no-services {
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
  </style>
