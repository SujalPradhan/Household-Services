<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Customer Registration</h1>
        <p>Sign up to access household services</p>
      </div>

      <form @submit.prevent="register" class="auth-form">
        <!-- Personal Information Section -->
        <div class="form-section">
          <h3>Personal Information</h3>
          
          <div class="form-group">
            <label for="name">Full Name</label>
            <div class="input-group">
              <span class="input-group-text"><i class="fas fa-user"></i></span>
              <input 
                type="text" 
                id="name" 
                v-model="formData.name" 
                class="form-control" 
                placeholder="Your full name"
                required
              >
            </div>
          </div>

          <div class="form-group">
            <label for="email">Email Address</label>
            <div class="input-group">
              <span class="input-group-text"><i class="fas fa-envelope"></i></span>
              <input 
                type="email" 
                id="email" 
                v-model="formData.email" 
                class="form-control" 
                placeholder="Your email address"
                required
              >
            </div>
          </div>

          <div class="form-group">
            <label for="pincode">Pincode</label>
            <div class="input-group">
              <span class="input-group-text"><i class="fas fa-map-marker-alt"></i></span>
              <input 
                type="text" 
                id="pincode" 
                v-model="formData.pincode" 
                class="form-control" 
                placeholder="Your area pincode"
                maxlength="6"
                pattern="[0-9]{6}"
              >
            </div>
            <small class="form-text text-muted">Enter a valid 6-digit pincode</small>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="password">Password</label>
              <div class="input-group">
                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  id="password" 
                  v-model="formData.password" 
                  class="form-control" 
                  placeholder="Create a password"
                  required
                  minlength="6"
                >
                <button 
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="showPassword = !showPassword"
                >
                  <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
            </div>

            <div class="form-group">
              <label for="confirmPassword">Confirm Password</label>
              <div class="input-group">
                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                <input 
                  :type="showConfirmPassword ? 'text' : 'password'" 
                  id="confirmPassword" 
                  v-model="formData.confirmPassword" 
                  class="form-control" 
                  placeholder="Confirm your password"
                  required
                >
                <button 
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <div v-if="passwordMismatch" class="error-message">
                Passwords do not match
              </div>
            </div>
          </div>
        </div>

        <div class="form-group form-check">
          <input type="checkbox" id="terms" class="form-check-input" v-model="formData.termsAccepted" required>
          <label for="terms" class="form-check-label">
            I agree to the <a href="#" @click.prevent="showTerms">Terms and Conditions</a>
          </label>
        </div>

        <div class="form-error" v-if="errorMessage">
          {{ errorMessage }}
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="loading || passwordMismatch">
          <span v-if="loading">
            <i class="fas fa-spinner fa-spin"></i> Registering...
          </span>
          <span v-else>Register as Customer</span>
        </button>

        <div class="register-option">
          <p>Are you a service professional? <router-link to="/register-professional">Register as Professional</router-link></p>
        </div>
      </form>

      <div class="auth-footer">
        <p>Already have an account? <router-link to="/login">Login</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RegisterView',
  data() {
    return {
      formData: {
        name: '',
        email: '',
        pincode: '',
        password: '',
        confirmPassword: '',
        termsAccepted: false
      },
      showPassword: false,
      showConfirmPassword: false,
      loading: false,
      errorMessage: ''
    };
  },
  computed: {
    passwordMismatch() {
      return this.formData.password && 
             this.formData.confirmPassword && 
             this.formData.password !== this.formData.confirmPassword;
    }
  },
  methods: {
    showTerms() {
      alert('Terms and Conditions for customers...');
    },
    async register() {
      if (this.passwordMismatch) {
        this.errorMessage = 'Passwords do not match';
        return;
      }

      this.loading = true;
      this.errorMessage = '';

      try {
        // Register the user
        const registerResponse = await axios.post('http://127.0.0.1:5000/signup', {
          email: this.formData.email,
          password: this.formData.password,
          role: 'customer', // Explicitly set role as customer
          name: this.formData.name,
          pincode: this.formData.pincode
        });

        console.log('Registration successful:', registerResponse.data);
        
        // After successful registration, automatically log in the user
        const loginResponse = await axios.post('http://127.0.0.1:5000/signin', {
          email: this.formData.email,
          password: this.formData.password
        });
        
        // Store the authentication token
        if (loginResponse.data.user && loginResponse.data.user.authentication_token) {
          sessionStorage.setItem('Authorization', loginResponse.data.user.authentication_token);
          
          // Set refresh flag before redirecting
          sessionStorage.setItem('dashboard_refreshed', 'false');
          
          // Navigate directly to the customer dashboard
          this.$router.push('/customer');
        } else {
          throw new Error('Authentication token not received');
        }
      } catch (error) {
        console.error('Registration Error:', error);
        this.errorMessage = error.response?.data?.error || error.message || 'Registration failed';
        
        // If auto-login fails, redirect to login page
        if (error.message === 'Authentication token not received') {
          this.$router.push({
            path: '/login',
            query: { registrationSuccess: true, userType: 'customer' }
          });
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Similar styling as RegisterProfessional.vue */
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 250px);
  padding: 20px;
}

.auth-card {
  background-color: #3F3244;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 600px;
  overflow: hidden;
  margin: 0 auto;
}

.auth-header {
  background-color: #2F2235;
  padding: 30px;
  text-align: center;
}

.auth-header h1 {
  color: #BFC3BA;
  margin-bottom: 10px;
  font-size: 2.2rem;
}

.auth-header p {
  color: #A9ACA9;
  margin-bottom: 0;
}

.auth-form {
  padding: 30px;
}

.form-section {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(191, 195, 186, 0.1);
}

.form-section h3 {
  color: #BFC3BA;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #BFC3BA;
  font-weight: 500;
}

.input-group {
  position: relative;
  display: flex;
  border-radius: 6px;
  overflow: hidden;
}

.input-group-text {
  background-color: #60495A;
  border: none;
  color: #BFC3BA;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 15px;
}

.form-control {
  flex: 1;
  padding: 12px 15px;
  border: none;
  background-color: #2F2235;
  color: #BFC3BA;
}

.form-control::placeholder {
  color: #A9ACA9;
  opacity: 0.7;
}

.form-control:focus {
  outline: none;
  box-shadow: 0 0 0 2px #60495A;
  background-color: #2F2235;
  color: #BFC3BA;
}

.btn-outline-secondary {
  background-color: #2F2235;
  border: none;
  color: #BFC3BA;
}

.btn-outline-secondary:hover {
  background-color: #60495A;
}

.form-check {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.form-check-input {
  margin-right: 8px;
  accent-color: #60495A;
}

.form-check-label {
  color: #BFC3BA;
  margin-bottom: 0;
}

.form-check-label a {
  color: #60495A;
  text-decoration: none;
  font-weight: 600;
}

.form-check-label a:hover {
  text-decoration: underline;
}

.form-text {
  font-size: 0.85rem;
  color: #A9ACA9;
  margin-top: 5px;
}

.form-error {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 20px;
  text-align: center;
}

.error-message {
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 5px;
}

.btn-primary {
  background-color: #60495A;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4d3a49;
}

.btn-block {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.register-option {
  text-align: center;
  margin-bottom: 20px;
  color: #BFC3BA;
}

.register-option a {
  color: #60495A;
  font-weight: 600;
  text-decoration: none;
}

.register-option a:hover {
  text-decoration: underline;
}

.auth-footer {
  padding: 20px 30px;
  text-align: center;
  border-top: 1px solid rgba(191, 195, 186, 0.1);
}

.auth-footer p {
  color: #BFC3BA;
  margin: 0;
}

.auth-footer a {
  color: #60495A;
  font-weight: 600;
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .auth-card {
    max-width: 100%;
  }
}
</style>
