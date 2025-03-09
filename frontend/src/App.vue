<template>
  <div id="app">
    <!-- Show navbar only when user is not logged in -->
    <nav class="main-nav" v-if="!isAuthenticated">
      <div class="nav-container">
        <router-link to="/" class="nav-logo">UrbanAid</router-link>
        <div class="nav-links">
          <router-link to="/">Home</router-link>
          <router-link to="/services">Services</router-link>
          <router-link to="/about">About</router-link>
          <router-link to="/contact">Contact</router-link>
        </div>
        <div class="nav-actions">
          <router-link to="/login" class="nav-btn btn-login">Login</router-link>
          <a href="#" class="nav-btn btn-register" @click.prevent="showRegisterModal = true">Register</a>
        </div>
      </div>
    </nav>
    
    <router-view />
    
    <register-modal :show="showRegisterModal" @close="showRegisterModal = false" />
  </div>
</template>

<script>
import RegisterModal from './components/RegisterModal.vue';

export default {
  name: 'App',
  components: {
    RegisterModal
  },
  data() {
    return {
      showRegisterModal: false,
      isAuthenticated: false
    };
  },
  created() {
    // Check authentication status when component is created
    this.checkAuth();
    
    // Listen for auth changes (login/logout)
    window.addEventListener('storage', this.handleStorageChange);
    
    // Custom event for auth changes within the same window
    window.addEventListener('auth-change', this.checkAuth);
  },
  beforeDestroy() {
    // Clean up event listeners
    window.removeEventListener('storage', this.handleStorageChange);
    window.removeEventListener('auth-change', this.checkAuth);
  },
  methods: {
    checkAuth() {
      // Check for authentication token in session storage
      const token = sessionStorage.getItem('Authorization');
      this.isAuthenticated = !!token;
    },
    handleStorageChange(event) {
      // Handle changes to session storage (for multi-tab support)
      if (event.key === 'Authorization') {
        this.checkAuth();
      }
    }
  }
};
</script>

<style>
:root {
  --primary-color: #60495A;
  --secondary-color: #3F3244;
  --dark-color: #2F2235;
  --light-color: #BFC3BA;
  --muted-color: #A9ACA9;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f4f4f4;
}

.main-nav {
  background-color: var(--dark-color);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 3px solid var(--primary-color);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
}

.nav-logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--light-color);
  text-decoration: none;
  transition: color 0.3s ease;
}

.nav-logo:hover {
  color: var(--primary-color);
}

.nav-links {
  display: flex;
}

.nav-links a {
  margin: 0 15px;
  color: var(--light-color);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
  padding: 8px 5px;
  border-bottom: 2px solid transparent;
}

.nav-links a:hover, .nav-links a.router-link-active {
  color: var (--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

.nav-actions {
  display: flex;
  gap: 10px;
}

.nav-btn {
  padding: 8px 15px;
  border-radius: 5px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-login {
  color: var(--light-color);
  background-color: transparent;
  border: 1px solid var(--primary-color);
}

.btn-login:hover {
  background-color: var(--primary-color);
  color: white;
}

.btn-register {
  background-color: var(--primary-color);
  color: white;
  border: 1px solid var(--primary-color);
}

.btn-register:hover {
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    padding: 10px;
  }
  
  .nav-logo {
    margin-bottom: 10px;
  }
  
  .nav-links {
    margin-bottom: 10px;
  }
  
  .nav-links a {
    margin: 0 10px;
    font-size: 0.9rem;
  }
  
  .nav-btn {
    padding: 6px 12px;
    font-size: 0.9rem;
  }
}
</style>
