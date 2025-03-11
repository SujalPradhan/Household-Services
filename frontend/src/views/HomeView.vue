<template>
  <div>
    <!-- Navigation Bar - Only show when user is not logged in -->
    <nav class="main-nav" v-if="!isAuthenticated">
      <div class="nav-container">
        <router-link to="/" class="nav-logo">UrbanAid</router-link>
        <div class="nav-links">
          <router-link to="/">Home</router-link>
          <a href="#services" @click.prevent="scrollToSection('services')">Services</a>
          <a href="#about" @click.prevent="scrollToSection('about')">About</a>
          <a href="#contact" @click.prevent="scrollToSection('contact')">Contact</a>
        </div>
        <div class="nav-actions">
          <router-link to="/login" class="nav-btn btn-login">Login</router-link>
          <a href="#" class="nav-btn btn-register" @click.prevent="showRegisterModal = true">Register</a>
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
    <section id="services" class="services">
      <div class="container">
        <h2>Our Services</h2>
        <div class="services-grid">
          <div class="service-card">
            <div class="card-icon">🔧</div>
            <h3>Plumbing</h3>
            <p>Expert plumbing repair and installation services</p>
          </div>
          <div class="service-card">
            <div class="card-icon">🖌️</div>
            <h3>Painting</h3>
            <p>Professional painting for interior and exterior</p>
          </div>
          <div class="service-card">
            <div class="card-icon">⚡</div>
            <h3>Electrical</h3>
            <p>Safe and reliable electrical services</p>
          </div>
          <div class="service-card">
            <div class="card-icon">🪚</div>
            <h3>Carpentry</h3>
            <p>Custom woodworking and furniture repair</p>
          </div>
          <div class="service-card">
            <div class="card-icon">🧹</div>
            <h3>Cleaning</h3>
            <p>Professional home cleaning services</p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- About Section -->
    <section id="about" class="about">
      <div class="container">
        <h2>About UrbanAid</h2>
        <div class="about-content">
          <div class="about-text">
            <p>UrbanAid connects skilled professionals with homeowners and businesses needing household services. Our platform ensures quality, reliability, and convenience for all your maintenance needs.</p>
            <p>We carefully vet all service professionals to guarantee expertise and trustworthiness, while our streamlined booking system makes scheduling services quick and easy.</p>
            <p>Whether you need emergency repairs, regular maintenance, or home improvement projects, UrbanAid is your trusted partner for all household services.</p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Contact Section -->
    <section id="contact" class="contact">
      <div class="container">
        <h2>Contact Us</h2>
        <div class="contact-content">
          <div class="contact-info">
            <div class="contact-item">
              <i class="fas fa-envelope"></i>
              <h3>Email</h3>
              <p><a href="mailto:23f2004758@ds.study.iitm.ac.in">23f2004758@ds.study.iitm.ac.in</a></p>
            </div>
            <div class="contact-item">
              <i class="fas fa-phone"></i>
              <h3>Phone</h3>
              <p>+91 123-456-7890</p>
            </div>
            <div class="contact-item">
              <i class="fas fa-map-marker-alt"></i>
              <h3>Address</h3>
              <p>123 Urban Street, City Center<br>Chennai, Tamil Nadu</p>
            </div>
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
      <div class="footer-top">
        <div class="container">
          <div class="footer-content">
            <div class="footer-section about">
              <div class="footer-logo">
                <h3>UrbanAid</h3>
                <span class="tagline">Simplifying Home Services</span>
              </div>
              <p>Your trusted partner for all household maintenance and repair needs.</p>
              <div class="contact">
                <span><i class="fas fa-phone"></i> &nbsp; 123-456-7890</span>
                <span><i class="fas fa-envelope"></i> &nbsp; 23f2004758@ds.study.iitm.ac.in</span>
              </div>
              <div class="socials">
                <a href="#" title="Facebook"><i class="fab fa-facebook-f"></i></a>
                <a href="#" title="Twitter"><i class="fab fa-twitter"></i></a>
                <a href="#" title="Instagram"><i class="fab fa-instagram"></i></a>
                <a href="#" title="LinkedIn"><i class="fab fa-linkedin-in"></i></a>
              </div>
            </div>
            
            <div class="footer-section links">
              <h3>Quick Links</h3>
              <div class="footer-links">
                <ul>
                  <li><router-link to="/"><i class="fas fa-angle-right"></i> Home</router-link></li>
                  <li><a href="#services" @click.prevent="scrollToSection('services')"><i class="fas fa-angle-right"></i> Services</a></li>
                  <li><a href="#about" @click.prevent="scrollToSection('about')"><i class="fas fa-angle-right"></i> About</a></li>
                  <li><a href="#contact" @click.prevent="scrollToSection('contact')"><i class="fas fa-angle-right"></i> Contact</a></li>
                </ul>
              </div>
            </div>
            
            <div class="footer-section services-links">
              <h3>Services</h3>
              <div class="footer-links">
                <ul>
                  <li><a href="#services" @click.prevent="scrollToSection('services')"><i class="fas fa-angle-right"></i> Plumbing</a></li>
                  <li><a href="#services" @click.prevent="scrollToSection('services')"><i class="fas fa-angle-right"></i> Painting</a></li>
                  <li><a href="#services" @click.prevent="scrollToSection('services')"><i class="fas fa-angle-right"></i> Electrical</a></li>
                  <li><a href="#services" @click.prevent="scrollToSection('services')"><i class="fas fa-angle-right"></i> Carpentry</a></li>
                  <li><a href="#services" @click.prevent="scrollToSection('services')"><i class="fas fa-angle-right"></i> Cleaning</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <div class="container">
          <p>&copy; {{ new Date().getFullYear() }} UrbanAid | All Rights Reserved</p>
          <div class="footer-bottom-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">FAQ</a>
          </div>
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
    },
    scrollToSection(sectionId) {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }
    }
  }
};
</script>

<style scoped>
/* Navigation bar styles */
.main-nav {
  background-color: #3F3244;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
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
  background-color: #3F3244;
  background-image: linear-gradient(135deg, #3F3244 0%, #332A37 100%);
  color: #BFC3BA;
  border-bottom: 5px solid rgba(96, 73, 90, 0.3);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  position: relative;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3F3244, #60495A, #3F3244);
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
  background-color: #3F3244;
  text-align: center;
  border-top: 1px solid rgba(96, 73, 90, 0.5);
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
  position: relative;
}

.services::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 6px;
  background: linear-gradient(90deg, transparent, rgba(96, 73, 90, 0.3), transparent);
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
  background-color: #332A37;
  border-radius: 10px;
  padding: 30px;
  width: 300px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  transition: all 0.3s ease;
  border: 1px solid rgba(96, 73, 90, 0.3);
  position: relative;
  overflow: hidden;
}

.service-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #60495A, #A77E9B, #60495A);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.service-card:hover {
  transform: translateY(-10px);
  border-color: rgba(96, 73, 90, 0.7);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}

.service-card:hover::before {
  transform: scaleX(1);
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
  background-color: #332A37;
  border-radius: 10px;
  padding: 30px;
  width: 300px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
  border: 1px solid rgba(96, 73, 90, 0.3);
  position: relative;
  overflow: hidden;
}

.option-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, #60495A, transparent);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  border-color: rgba(96, 73, 90, 0.7);
}

.option-card:hover::after {
  transform: scaleX(1);
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

/* About Section Styles */
.about {
  padding: 80px 0;
  background-color: #3F3244;
  color: #BFC3BA;
  border-top: 1px solid rgba(96, 73, 90, 0.5);
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
  position: relative;
}

.about::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h20L0 20z' fill='%2360495A' fill-opacity='0.03' fill-rule='evenodd'/%3E%3C/svg%3E");
  opacity: 0.3;
  pointer-events: none;
}

.about h2 {
  color: #BFC3BA;
  font-size: 2.2rem;
  margin-bottom: 50px;
  text-align: center;
  position: relative;
  display: inline-block;
}

.about h2:after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background-color: #60495A;
}

.about-content {
  display: flex;
  justify-content: center;
  max-width: 900px;
  margin: 0 auto;
  background-color: rgba(47, 34, 53, 0.5);
  padding: 30px;
  border-radius: 15px;
  border: 1px solid rgba(96, 73, 90, 0.3);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 1;
}

.about-text {
  line-height: 1.8;
}

.about-text p {
  margin-bottom: 20px;
  font-size: 1.1rem;
}

/* Contact Section Styles */
.contact {
  padding: 80px 0;
  background-color: #3F3244;
  color: #BFC3BA;
  text-align: center;
  border-top: 1px solid rgba(96, 73, 90, 0.5);
  position: relative;
  overflow: hidden;
}

.contact::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 6px;
  background: linear-gradient(90deg, transparent, rgba(96, 73, 90, 0.5), transparent);
}

.contact h2 {
  color: #BFC3BA;
  font-size: 2.2rem;
  margin-bottom: 50px;
  position: relative;
  display: inline-block;
}

.contact h2:after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background-color: #60495A;
}

.contact-content {
  display: flex;
  justify-content: center;
}

.contact-info {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 40px;
  max-width: 1000px;
}

.contact-item {
  background-color: #332A37;
  padding: 30px;
  border-radius: 10px;
  width: 250px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  transition: all 0.3s ease;
  border: 1px solid rgba(96, 73, 90, 0.3);
  position: relative;
  overflow: hidden;
}

.contact-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, #60495A, transparent);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.contact-item:hover {
  transform: translateY(-10px);
  border-color: rgba(96, 73, 90, 0.7);
}

.contact-item:hover::after {
  transform: scaleX(1);
}

.contact-item i {
  font-size: 2.5rem;
  color: #60495A;
  margin-bottom: 15px;
}

.contact-item h3 {
  margin-bottom: 15px;
  color: #BFC3BA;
}

.contact-item p {
  color: #A9ACA9;
}

.contact-item a {
  color: #A9ACA9;
  text-decoration: none;
  transition: color 0.3s ease;
}

.contact-item a:hover {
  color: #60495A;
}

/* Footer Styles - Updated Design */
.footer {
  background-color: #3F3244;
  color: #BFC3BA;
  margin-top: 0;
  position: relative;
  overflow: hidden;
}

.footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #3F3244, #60495A, #3F3244);
}

.footer-top {
  padding: 70px 0 40px;
  border-bottom: 1px solid rgba(96, 73, 90, 0.3);
  position: relative;
}

.footer-top::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 40%;
  height: 100%;
  background: radial-gradient(circle at bottom right, rgba(96, 73, 90, 0.1), transparent 70%);
  pointer-events: none;
  z-index: 0;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 40px;
  position: relative;
  z-index: 1;
}

.footer-section {
  flex: 1;
  min-width: 250px; /* Increased min-width for better layout with 3 columns */
  position: relative;
}

.footer-logo {
  margin-bottom: 15px;
  display: inline-block;
}

.footer-logo h3 {
  font-size: 1.8rem;
  margin-bottom: 5px;
  color: #BFC3BA;
  position: relative;
}

.tagline {
  font-size: 0.85rem;
  color: var(--primary-color);
  font-style: italic;
  display: block;
  margin-top: -5px;
}

.footer-section p {
  margin-bottom: 20px;
  line-height: 1.7;
  color: rgba(191, 195, 186, 0.8);
}

.footer-section h3 {
  font-size: 1.4rem;
  margin-bottom: 25px;
  position: relative;
  padding-bottom: 15px;
  display: inline-block;
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

.contact span {
  display: block;
  margin-bottom: 12px;
  font-size: 0.95rem;
  color: rgba(191, 195, 186, 0.9);
}

.contact i {
  color: var(--primary-color);
  width: 20px;
  text-align: center;
  margin-right: 5px;
}

.socials {
  margin-top: 25px;
  display: flex;
  gap: 12px;
}

.socials a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: rgba(96, 73, 90, 0.2);
  color: #BFC3BA;
  border-radius: 50%;
  font-size: 1rem;
  transition: all 0.3s ease;
  border: 1px solid rgba(96, 73, 90, 0.5);
}

.socials a:hover {
  background-color: var(--primary-color);
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
}

.footer-links ul {
  list-style-type: none;
  padding: 0;
}

.footer-links ul li {
  margin-bottom: 14px;
  transition: transform 0.3s ease;
}

.footer-links ul li:hover {
  transform: translateX(5px);
}

.footer-links ul li a {
  color: rgba(191, 195, 186, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
}

.footer-links ul li a i {
  font-size: 0.8rem;
  margin-right: 8px;
  color: var(--primary-color);
  transition: transform 0.3s ease;
}

.footer-links ul li a:hover {
  color: #BFC3BA;
}

.footer-links ul li a:hover i {
  transform: translateX(3px);
}

.footer-bottom {
  padding: 25px 0;
  text-align: center;
  position: relative;
  z-index: 1;
  background-color: rgba(47, 34, 53, 0.3);
}

.footer-bottom .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-bottom p {
  font-size: 0.9rem;
  margin: 0;
  color: rgba(191, 195, 186, 0.7);
}

.footer-bottom-links {
  display: flex;
  gap: 20px;
}

.footer-bottom-links a {
  color: rgba(191, 195, 186, 0.7);
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.3s ease;
}

.footer-bottom-links a:hover {
  color: var(--primary-color);
}

@media (max-width: 992px) {
  .footer-content {
    gap: 30px;
  }
  
  .footer-section {
    min-width: calc(33% - 30px); /* Adjusted for 3 columns */
  }
}

@media (max-width: 768px) {
  .footer-top {
    padding: 50px 0 30px;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 40px;
  }
  
  .footer-section {
    min-width: 100%;
  }
  
  .footer-bottom .container {
    flex-direction: column;
    gap: 15px;
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
  border: 1px solid rgba(96, 73, 90, 0.3);
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
  background-color: #332A37;
  border-radius: 10px;
  padding: 30px;
  width: 45%;
  min-width: 250px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(96, 73, 90, 0.3);
  position: relative;
  overflow: hidden;
}

.option-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, #60495A, transparent);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  border-color: rgba(96, 73, 90, 0.7);
}

.option-card:hover::after {
  transform: scaleX(1);
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .contact-info {
    flex-direction: column;
    align-items: center;
  }
  
  .contact-item {
    width: 100%;
    max-width: 300px;
  }
}

div {
  background-color: #3F3244;
}

/* Override backgrounds for specific elements that need different styling */
.service-card {
  background-color: #332A37;
}

.about-content {
  background-color: rgba(47, 34, 53, 0.5);
}

.contact-item {
  background-color: #332A37;
}

.option-card {
  background-color: #332A37;
}

.modal-content {
  background-color: #3F3244;
}
</style>
