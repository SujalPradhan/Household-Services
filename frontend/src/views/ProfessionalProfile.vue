<template>
  <div class="professional-profile">
    <h2>My Profile</h2>
    
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading your profile...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-else class="profile-card">
      <div class="profile-header">
        <h3>{{ profile.name }}</h3>
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
          <span class="field-label">Email:</span>
          <span class="field-value">{{ profile.email }}</span>
        </div>
        
        <div class="profile-field">
          <span class="field-label">Service Type:</span>
          <span class="field-value">{{ profile.service_type }}</span>
        </div>
        
        <div class="profile-field">
          <span class="field-label">Experience:</span>
          <span class="field-value">{{ profile.experience }} years</span>
        </div>
        
        <div class="profile-field">
          <span class="field-label">Description:</span>
          <p class="field-value description">{{ profile.description || 'No description provided.' }}</p>
        </div>
      </div>
    </div>
    
    <div class="profile-actions">
      <button class="btn btn-primary" @click="editProfile" :disabled="!profile || loading">
        <i class="fas fa-edit"></i> Edit Profile
      </button>
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
        // Get profile from session storage
        const userString = sessionStorage.getItem('user');
        if (!userString) {
          throw new Error('User information not found');
        }
        
        const userData = JSON.parse(userString);
        this.profile = userData;
      } catch (error) {
        console.error('Error loading profile:', error);
        this.error = 'Failed to load profile information. Please try again later.';
      } finally {
        this.loading = false;
      }
    },
    
    editProfile() {
      // Show message - in a real app, this would open an edit form
      this.showNotification({
        message: 'Profile editing feature is coming soon!',
        type: 'info'
      });
    },
    
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
  max-width: 800px;
  margin: 0 auto;
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
  padding: 15px;
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.2);
  color: #dc3545;
  border-radius: 5px;
  margin-bottom: 20px;
}

.profile-card {
  background-color: #2F2235;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  margin-bottom: 20px;
}

.profile-header {
  background-color: #221728;
  padding: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--light-color);
}

.status-pills {
  display: flex;
  gap: 10px;
}

.status-pill {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  background-color: #6c757d;
  color: white;
}

.status-pill.approved {
  background-color: #28a745;
}

.status-pill.blocked {
  background-color: #dc3545;
}

.profile-body {
  padding: 20px;
}

.profile-field {
  margin-bottom: 20px;
}

.field-label {
  display: block;
  font-weight: bold;
  color: var(--light-color);
  margin-bottom: 5px;
}

.field-value {
  color: var(--muted-color);
}

.field-value.description {
  white-space: pre-line;
  line-height: 1.6;
}

.profile-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4d3a49;
}

.btn:disabled {
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

.toast.info {
  border-left: 4px solid #17a2b8;
}

.toast-content {
  display: flex;
  align-items: center;
}

.toast-content i {
  margin-right: 10px;
  font-size: 1.2rem;
}

.toast-close {
  cursor: pointer;
  padding: 5px;
}
</style>
