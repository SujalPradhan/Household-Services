<template>
  <div class="professional-layout">
    <header class="professional-header">
      <div class="header-content">
        <h1><i class="fas fa-tools"></i> UrbanAid</h1>
        <nav class="professional-nav">
          <router-link to="/professional/requests" class="nav-link">
            <i class="fas fa-clipboard-list"></i> 
            My Requests
            <span v-if="newRequestsCount > 0" class="badge">{{ newRequestsCount }}</span>
          </router-link>
          <router-link to="/professional/profile" class="nav-link">
            <i class="fas fa-user"></i> 
            Profile
          </router-link>
          <button @click="logout" class="logout-btn">
            <i class="fas fa-sign-out-alt"></i> Logout
          </button>
        </nav>
      </div>
    </header>
    
    <main class="professional-content">
      <router-view @new-requests-count="updateNewRequestsCount"/>
    </main>
    
    <footer class="professional-footer">
      <p>&copy; 2023 UrbanAid Professional Services Platform</p>
    </footer>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ProfessionalHome',
  data() {
    return {
      newRequestsCount: 0,
      user: null,
      loading: true,
      error: null
    };
  },
  methods: {
    logout() {
      // Clear authentication token
      sessionStorage.removeItem('Authorization');
      
      // Call logout endpoint
      axios.post('http://127.0.0.1:5000/signout')
        .catch(err => console.error("Logout error:", err));
      
      // Redirect to landing page
      this.$router.push('/');
    },
    updateNewRequestsCount(count) {
      this.newRequestsCount = count;
    },
    async checkProfessionalStatus() {
      try {
        this.loading = true;
        // Get the user data from sessionStorage if available
        const userData = sessionStorage.getItem('userData');
        
        if (userData) {
          this.user = JSON.parse(userData);
          
          // If blocked or inactive, redirect to blocked page
          if (this.user.blocked || this.user.active === false) {
            this.$router.push('/blocked');
            return;
          }
        } else {
          // If no user data, fetch it from the server
          const token = sessionStorage.getItem('Authorization');
          if (!token) {
            throw new Error('No authorization token found');
          }
          
          const response = await axios.get('http://127.0.0.1:5000/professional/profile', {
            headers: { 'Authorization': token }
          });
          
          this.user = response.data;
          
          // Store the user data
          sessionStorage.setItem('userData', JSON.stringify(this.user));
          
          // If blocked or inactive, redirect to blocked page
          if (this.user.blocked || this.user.active === false) {
            this.$router.push('/blocked');
          }
        }
      } catch (error) {
        console.error('Error checking professional status:', error);
        this.error = error.message || 'Failed to load professional profile';
      } finally {
        this.loading = false;
      }
    }
  },
  created() {
    // Check if the professional is blocked or inactive
    this.checkProfessionalStatus();
    
    // Redirect to requests page by default if directly accessing /professional
    if (this.$route.path === '/professional') {
      this.$router.push('/professional/requests');
    }
  }
};
</script>

<style scoped>
.professional-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  margin: 0;
  padding: 0;
}

.professional-header {
  background-color: #221728;
  padding: 0;
  color: #BFC3BA;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-bottom: 3px solid #60495A;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.professional-header h1 {
  margin: 0;
  color: #BFC3BA;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
}

.professional-header h1 i {
  margin-right: 10px;
  color: var(--primary-color);
}

.professional-nav {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-link {
  position: relative;
  padding: 8px 12px;
  color: #BFC3BA;
  text-decoration: none;
  font-weight: 600;
  border-radius: 6px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.nav-link i {
  font-size: 1rem;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-link.router-link-active {
  background-color: var(--primary-color);
  color: white;
}

.badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: #ff4757;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.logout-btn {
  background-color: transparent;
  color: #BFC3BA;
  border: 1px solid #60495A;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.logout-btn:hover {
  background-color: #60495A;
  color: white;
}

.professional-content {
  flex: 1;
  background-color: #3F3244;
  padding: 30px 20px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.professional-footer {
  background-color: #221728;
  color: var(--muted-color);
  text-align: center;
  padding: 15px;
  font-size: 0.9rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    padding: 15px;
    gap: 15px;
  }
  
  .professional-nav {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .nav-link, .logout-btn {
    padding: 10px;
  }
  
  .professional-content {
    padding: 20px 15px;
  }
}
</style>
