<template>
  <div>
    <!-- Navigation Bar - Only show when user is not logged in -->
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
          <a href="#" class="nav-btn btn-register" @click.prevent="showRegisterModal">Register</a>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1>Welcome to UrbanAid</h1>
        <p>Your one-stop solution for all household services</p>
        <div class="hero-actions">
          <router-link to="/login" class="btn btn-primary">Login</router-link>
          <button @click="$root.showRegisterModal = true" class="btn btn-outline">Register</button>
        </div>
      </div>
    </section>

    <!-- Services Section -->
    <section class="services">
      <div class="container">
        <h2>Our Services</h2>
        <div class="services-grid">
          <div class="service-card">
            <div class="card-icon">🧹</div>
            <h3>Cleaning</h3>
            <p>Professional home cleaning services</p>
          </div>
          <div class="service-card">
            <div class="card-icon">🔧</div>
            <h3>Repairs</h3>
            <p>Quick and reliable repair services</p>
          </div>
          <div class="service-card">
            <div class="card-icon">🪴</div>
            <h3>Gardening</h3>
            <p>Expert gardening and landscaping</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Registration Modal -->
    <div v-if="showRegisterModal" class="modal-overlay" @click.self="showRegisterModal = false">
      <div class="modal-content">
        <button class="close-btn" @click="showRegisterModal = false">×</button>
        <h2>Choose Registration Type</h2>
        <div class="options-container">
          <div class="option-card">
            <i class="fas fa-user"></i>
            <h3>Customer</h3>
            <p>Need household services? Register as a customer to book services.</p>
            <router-link to="/register" class="btn btn-primary" @click="showRegisterModal = false">Register as Customer</router-link>
          </div>
          <div class="option-card">
            <i class="fas fa-tools"></i>
            <h3>Professional</h3>
            <p>Offer your expertise! Register as a service professional to provide services.</p>
            <router-link to="/register-professional" class="btn btn-primary" @click="showRegisterModal = false">Register as Professional</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Section -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section about">
            <h3>UrbanAid</h3>
            <p>Your trusted partner for all household maintenance and repair needs.</p>
            <div class="contact">
              <span><i class="fas fa-phone"></i> &nbsp; 123-456-7890</span>
              <span><i class="fas fa-envelope"></i> &nbsp; info@householdservices.com</span>
            </div>
            <div class="socials">
              <a href="#"><i class="fab fa-facebook"></i></a>
              <a href="#"><i class="fab fa-twitter"></i></a>
              <a href="#"><i class="fab fa-instagram"></i></a>
              <a href="#"><i class="fab fa-linkedin"></i></a>
            </div>
          </div>
          <div class="footer-section links">
            <h3>Quick Links</h3>
            <ul>
              <li><router-link to="/">Home</router-link></li>
              <li><router-link to="/about">About</router-link></li>
              <li><router-link to="/services">Services</router-link></li>
              <li><router-link to="/contact">Contact</router-link></li>
            </ul>
          </div>
          <div class="footer-section services-links">
            <h3>Services</h3>
            <ul>
              <li><a href="#">Cleaning</a></li>
              <li><a href="#">Repairs</a></li>
              <li><a href="#">Gardening</a></li>
              <li><a href="#">Plumbing</a></li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; {{ new Date().getFullYear() }} Household Services | All Rights Reserved</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
// Import the CSS file
import '@/../../css/styles.css';

export default {
  name: 'HomeView',
  data() {
    return {
      isAuthenticated: false,
      showRegisterModal: false
    };
  },
  created() {
    this.checkAuth();
    // Add event listener for auth changes
    window.addEventListener('storage', this.handleStorageChange);
  },
  beforeDestroy() {
    // Clean up event listeners
    window.removeEventListener('storage', this.handleStorageChange);
  },
  methods: {
    checkAuth() {
      // Check for authentication token in session storage
      const token = sessionStorage.getItem('Authorization');
      this.isAuthenticated = !!token;
    },
    handleStorageChange(event) {
      // Handle changes to session storage
      if (event.key === 'Authorization') {
        this.checkAuth();
      }
    },
    showRegisterModal() {
      // Call the parent's method to show the register modal
      this.$parent.openRegisterModal();
    }
  }
};
</script>

<style scoped>
/* Navigation bar styles */
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
  color: var(--primary-color);
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

.hero {
  text-align: center;
  padding: 100px 0;
  background-color: #60495A;
  background-image: linear-gradient(135deg, #60495A 0%, #3F3244 100%);
  color: #BFC3BA;
}

.hero h1 {
  font-size: 2.8rem;
  font-weight: 700;
  margin-bottom: 20px;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

.hero-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.action-item {
  display: flex;
  justify-content: center;
}

.btn {
  display: inline-block;
  margin: 10px;
  padding: 12px 30px;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #60495A;
  color: white;
  border: 2px solid #60495A;
}

.btn-primary:hover {
  background-color: #3F3244;
  border-color: #3F3244;
}

.btn-outline {
  background-color: transparent;
  color: #3F3244;
  border: 2px solid #3F3244;
}

.btn-outline:hover {
  background-color: #3F3244;
  color: white;
}

.services {
  padding: 80px 0;
  background-color: #60495A;
  text-align: center;
}

.services h2 {
  color: #BFC3BA;
  font-size: 2.2rem;
  margin-bottom: 50px;
  position: relative;
  display: inline-block;
}

.services h2:after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background-color: #60495A;
}

.services-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 30px;
}

.service-card {
  background-color: #3F3244;
  border-radius: 10px;
  padding: 30px;
  width: 300px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  transition: transform 0.3s ease;
}

.service-card:hover {
  transform: translateY(-10px);
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.service-card h3 {
  color: #BFC3BA;
  margin-bottom: 15px;
}

.service-card p {
  color: #BFC3BA;
}

/* Registration Options Styles */
.registration-options {
  text-align: center;
  padding: 40px 0;
  background-color: #2F2235;
  color: #BFC3BA;
}

.options-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 30px;
  margin-top: 30px;
}

.option-card {
  background-color: #3F3244;
  border-radius: 10px;
  padding: 30px;
  width: 300px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.option-card:hover {
  transform: translateY(-5px);
}

.option-card i {
  font-size: 3rem;
  color: #60495A;
  margin-bottom: 15px;
}

.option-card h3 {
  margin-bottom: 15px;
  color: #BFC3BA;
}

.option-card p {
  color: #A9ACA9;
  margin-bottom: 20px;
}

.btn-primary {
  display: inline-block;
  background-color: #60495A;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #4d3a49;
}

/* Footer Styles */
.footer {
  background-color: #2F2235;
  color: #BFC3BA;
  padding: 40px 0 20px;
  margin-top: 60px;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 30px;
}

.footer-section {
  flex: 1;
  min-width: 250px;
}

.footer-section h3 {
  font-size: 1.4rem;
  margin-bottom: 20px;
  position: relative;
  padding-bottom: 10px;
}

.footer-section h3::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 50px;
  height: 2px;
  background-color: #60495A;
}

.footer-section p {
  margin-bottom: 20px;
}

.contact span {
  display: block;
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.socials {
  margin-top: 20px;
}

.socials a {
  display: inline-block;
  width: 35px;
  height: 35px;
  background-color: #60495A;
  color: #BFC3BA;
  border-radius: 50%;
  text-align: center;
  line-height: 35px;
  margin-right: 10px;
  transition: all 0.3s ease;
}

socials a:hover {
  background-color: #3F3244;
  transform: scale(1.1);
}

.footer-section ul {
  list-style-type: none;
  padding: 0;
}

.footer-section ul li {
  margin-bottom: 10px;
}

.footer-section ul li a {
  color: #BFC3BA;
  text-decoration: none;
  transition: all 0.3s ease;
}

.footer-section ul li a:hover {
  color: #A9ACA9;
  padding-left: 5px;
}

.footer-bottom {
  text-align: center;
  padding-top: 30px;
  margin-top: 30px;
  border-top: 1px solid rgba(191, 195, 186, 0.2);
}

.footer-bottom p {
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .services-grid {
    flex-direction: column;
    align-items: center;
  }
  
  .service-card {
    width: 100%;
    max-width: 350px;
  }
  
  .hero h1 {
    font-size: 2.2rem;
  }
  
  .footer-content {
    flex-direction: column;
  }
  
  .footer-section {
    margin-bottom: 30px;
  }
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
  background-color: #3F3244;
  border-radius: 10px;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.5);
  width: 90%;
  max-width: 800px;
  padding: 30px;
  position: relative;
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 28px;
  color: #BFC3BA;
  background: none;
  border: none;
  cursor: pointer;
}

.close-btn:hover {
  color: #60495A;
}

.modal-content h2 {
  color: #BFC3BA;
  text-align: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(191, 195, 186, 0.2);
}

.options-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 30px;
}

.option-card {
  background-color: #2F2235;
  border-radius: 10px;
  padding: 30px;
  width: 45%;
  min-width: 250px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.option-card i {
  font-size: 3rem;
  color: #60495A;
  margin-bottom: 15px;
}

.option-card h3 {
  margin-bottom: 15px;
  color: #BFC3BA;
}

.option-card p {
  color: #A9ACA9;
  margin-bottom: 20px;
}

.btn-primary {
  display: inline-block;
  background-color: #60495A;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #4d3a49;
}

/* Media Queries */
@media (max-width: 768px) {
  .options-container {
    flex-direction: column;
    align-items: center;
  }
  
  .option-card {
    width: 100%;
  }
  
  .modal-content {
    padding: 20px;
  }
}
</style>
