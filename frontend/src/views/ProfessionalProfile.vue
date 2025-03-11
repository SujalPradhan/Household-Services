<template>
  <div class="professional-profile">
    <div class="page-header">
      <h1>My Profile</h1>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading your profile...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      <span>{{ error }}</span>
    </div>
    
    <div v-else class="profile-container">
      <div class="profile-card">
        <div class="profile-header">
          <div class="profile-info">
            <h2>{{ profile.name }}</h2>
            <div class="profile-service">{{ profile.service_type }}</div>
          </div>
          <div class="status-pills">
            <span class="status-pill" :class="{ 'approved': profile.approved }">
              {{ profile.approved ? 'Approved' : 'Pending Approval' }}
            </span>
            <span v-if="profile.blocked" class="status-pill blocked">
              Blocked
            </span>
          </div>
        </div>
        
        <div class="profile-body">
          <div class="profile-field">
            <span class="field-label"><i class="fas fa-envelope"></i> Email</span>
            <span class="field-value">{{ profile.email }}</span>
          </div>
          
          <div class="profile-field">
            <span class="field-label"><i class="fas fa-briefcase"></i> Experience</span>
            <span class="field-value">{{ profile.experience }} years</span>
          </div>
          
          <div class="profile-field">
            <span class="field-label"><i class="fas fa-file-alt"></i> Description</span>
            <p class="field-value description">{{ profile.description || 'No description provided.' }}</p>
          </div>
        </div>
      </div>
      
      <!-- Edit Profile button removed -->
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
  name: 'ProfessionalProfile',
  data() {
    return {
      profile: null,
      loading: true,
      error: null,
      notification: {
        show: false,
        message: '',
        type: 'info',
        timeout: null
      }
    };
  },
  created() {
    this.fetchProfile();
  },
  methods: {
    async fetchProfile() {
      this.loading = true;
      this.error = null;
      
      try {
        // Try different session storage keys that might contain the user data
        const userData = this.getUserDataFromSession();
        
        if (userData) {
          this.profile = userData;
          console.log('Profile data retrieved from session storage:', userData);
        } else {
          // If no data in session storage, fetch from API
          await this.fetchProfileFromAPI();
        }
      } catch (error) {
        console.error('Error loading profile:', error);
        this.error = 'Failed to load profile information. Please try again later.';
      } finally {
        this.loading = false;
      }
    },
    
    getUserDataFromSession() {
      // Try different possible keys for the user data
      const possibleKeys = ['user', 'userData', 'userInfo', 'profileData'];
      
      for (const key of possibleKeys) {
        const dataString = sessionStorage.getItem(key);
        if (dataString) {
          try {
            return JSON.parse(dataString);
          } catch (e) {
            console.warn(`Found data in ${key} but failed to parse:`, e);
          }
        }
      }
      
      // Check if the data is stored in the 'Authorization' header
      const token = sessionStorage.getItem('Authorization');
      if (token) {
        console.log('Found authorization token, will try API request');
      }
      
      return null;
    },
    
    async fetchProfileFromAPI() {
      const token = sessionStorage.getItem('Authorization');
      if (!token) {
        throw new Error('Authorization token not found');
      }
      
      const response = await axios.get('http://127.0.0.1:5000/professional/profile', {
        headers: {
          'Authorization': token
        }
      });
      
      if (response.data) {
        this.profile = response.data;
        // Save the data for future use
        sessionStorage.setItem('userData', JSON.stringify(response.data));
        console.log('Profile data fetched from API and saved to session storage');
      } else {
        throw new Error('No profile data received from API');
      }
    },
    
    // editProfile method removed
    
    // Notification methods
    showNotification(options) {
      if (this.notification.timeout) {
        clearTimeout(this.notification.timeout);
      }
      
      this.notification = {
        show: true,
        message: options.message,
        type: options.type || 'info',
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
.professional-profile {
  color: var(--light-color);
}

.page-header {
  margin-bottom: 25px;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  position: relative;
  color: var(--light-color);
}

.page-header h1:after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -8px;
  width: 60px;
  height: 3px;
  background: var(--primary-color);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(96, 73, 90, 0.2);
  border-top: 4px solid var(--primary-color, #60495A);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  padding: 20px;
  background-color: rgba(220, 53, 69, 0.1);
  border-left: 4px solid #dc3545;
  color: #dc3545;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.error-message i {
  font-size: 1.5rem;
}

.profile-container {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  background-color: var(--dark-color, #2F2235);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  margin-bottom: 25px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.profile-header {
  background-color: rgba(0,0,0,0.2);
  padding: 25px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-info h2 {
  margin: 0 0 5px 0;
  font-size: 1.8rem;
  color: var(--light-color);
}

.profile-service {
  display: inline-block;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 1.1rem;
}

.status-pills {
  display: flex;
  gap: 10px;
}

.status-pill {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: uppercase;
  background-color: #6c757d;
  color: white;
  letter-spacing: 0.5px;
}

.status-pill.approved {
  background-color: #28a745;
}

.status-pill.blocked {
  background-color: #dc3545;
}

.profile-body {
  padding: 25px;
}

.profile-field {
  margin-bottom: 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 20px;
}

.profile-field:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.field-label {
  display: block;
  font-weight: 600;
  color: var(--light-color);
  margin-bottom: 10px;
  font-size: 1.05rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-label i {
  color: var(--primary-color);
}

.field-value {
  color: var(--muted-color);
  font-size: 1.1rem;
}

.field-value.description {
  white-space: pre-line;
  line-height: 1.6;
  background-color: rgba(0, 0, 0, 0.2);
  padding: 15px;
  border-radius: 8px;
  margin-top: 10px;
}

/* Remove profile-actions style since button is gone */

/* Keep other button styles for potential future use */
.btn {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, #7e57c2, #60495A);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #8e67d2, #70596A);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Toast Notification */
.toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  min-width: 300px;
  max-width: 400px;
  background-color: white;
  color: #333;
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.25);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px;
  animation: slideIn 0.3s ease-in-out;
  z-index: 1001;
}

@keyframes slideIn {
  from { transform: translateY(100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.toast.success {
  border-left: 5px solid #28a745;
}

.toast.error {
  border-left: 5px solid #dc3545;
}

.toast.info {
  border-left: 5px solid #17a2b8;
}

.toast-content {
  display: flex;
  align-items: center;
}

.toast-content i {
  margin-right: 12px;
  font-size: 1.3rem;
}

.toast.success i {
  color: #28a745;
}

.toast.error i {
  color: #dc3545;
}

.toast.info i {
  color: #17a2b8;
}

.toast-close {
  cursor: pointer;
  padding: 5px;
  transition: opacity 0.3s;
}

.toast-close:hover {
  opacity: 0.7;
}

/* Responsive design */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .status-pills {
    align-self: flex-start;
  }
  
  /* Remove profile-actions media query */
}
</style>
