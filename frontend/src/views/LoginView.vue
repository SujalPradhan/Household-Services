<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Welcome Back</h1>
        <p>Login to your account to access all services</p>
      </div>

      <form @submit.prevent="login" class="auth-form">
        <div class="form-group">
          <label for="email">Email Address</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-envelope"></i></span>
            <input 
              type="email" 
              id="email" 
              v-model="email" 
              class="form-control" 
              placeholder="Enter your email"
              required
            >
          </div>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-lock"></i></span>
            <input 
              :type="showPassword ? 'text' : 'password'" 
              id="password" 
              v-model="password" 
              class="form-control" 
              placeholder="Enter your password"
              required
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

        <!-- <div class="form-extras">
          <div class="form-check">
            <input type="checkbox" id="remember" class="form-check-input" v-model="rememberMe">
            <label for="remember" class="form-check-label">Remember me</label> -->
          <!-- </div>
          <a href="#" class="forgot-password">Forgot password?</a>
        </div> -->

        <div v-if="errorMessage" class="error-message-box">
          <i class="fas fa-exclamation-circle"></i>
          {{ errorMessage }}
        </div>

        <button type="submit" class="btn btn-primary btn-block">
          <span v-if="loading">
            <i class="fas fa-spinner fa-spin"></i> Logging in...
          </span>
          <span v-else>Login</span>
        </button>

        <!-- <div class="auth-divider">
          <span>OR</span>
        </div> -->

        <!-- <div class="social-login">
          <button type="button" class="btn btn-social btn-google">
            <i class="fab fa-google"></i> Login with Google
          </button>
          <button type="button" class="btn btn-social btn-facebook">
            <i class="fab fa-facebook-f"></i> Login with Facebook
          </button>
        </div> -->
      </form>

      <div class="auth-footer">
        <p>Don't have an account? <router-link to="/register">Register</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginView',
  data() {
    return {
      email: '',
      password: '',
      rememberMe: false,
      showPassword: false,
      loading: false,
      errorMessage: ''
    };
  },
  created() {
    // Redirect if user is already logged in
    const token = sessionStorage.getItem('Authorization');
    if (token) {
      this.redirectBasedOnRole();
    }
  },
  methods: {
    async login() {
      this.loading = true;
      this.errorMessage = '';
      try {
        const response = await axios.post('http://127.0.0.1:5000/signin', {
          email: this.email,
          password: this.password
        });

        console.log("Full Response:", response.data);

        if (!response.data || !response.data.user) {
          throw new Error("Invalid response from server");
        }

        let user = response.data.user;
        
        // Store token properly
        sessionStorage.setItem("Authorization", user.authentication_token);
        
        // Store the user data for checking blocked status later
        sessionStorage.setItem("userData", JSON.stringify(user));
        
        console.log("User role:", user.role);
        
        // Check if user is active before redirecting
        if (user.active === false) {
          this.$router.push('/blocked');
          return;
        }
        
        // Check if professional is blocked before redirecting
        if (user.role === 'professional' && user.blocked === true) {
          this.$router.push('/blocked');
          return;
        }
        
        // Navigate based on role
        this.redirectBasedOnRole(user);
      } catch (error) {
        console.error("Login Error:", error);
        this.errorMessage = error.response?.data?.error || error.message || "Login failed";
      } finally {
        this.loading = false;
      }
    },
    redirectBasedOnRole(user) {
      // If user object is provided, use that role, otherwise check from storage
      if (user) {
        if (user.role === "customer") {
          this.$router.push('/customer');
        } else if (user.role === "professional") {
          this.$router.push('/professional');
        } else if (user.role === "admin") {
          this.$router.push('/admin/home');
        } else {
          this.$router.push('/');
        }
      } else {
        // Default redirect if no user data is available
        this.$router.push('/');
      }
    }
  }
};
</script>

<style scoped>
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
  max-width: 500px;
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

.form-group {
  margin-bottom: 25px;
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

.form-extras {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.form-check {
  display: flex;
  align-items: center;
}

.form-check-input {
  margin-right: 8px;
  accent-color: #60495A;
}

.form-check-label {
  color: #BFC3BA;
  margin-bottom: 0;
}

.forgot-password {
  color: #60495A;
  text-decoration: none;
  font-size: 14px;
}

.forgot-password:hover {
  text-decoration: underline;
}

.btn-block {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
}

.auth-divider {
  text-align: center;
  position: relative;
  margin: 25px 0;
}

.auth-divider:before {
  content: "";
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #60495A;
}

.auth-divider span {
  position: relative;
  background-color: #3F3244;
  padding: 0 15px;
  color: #A9ACA9;
  font-size: 14px;
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-social {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.btn-social i {
  margin-right: 10px;
}

.btn-google {
  background-color: #DB4437;
  color: white;
  border: none;
}

.btn-google:hover {
  background-color: #C53929;
  color: white;
}

.btn-facebook {
  background-color: #4267B2;
  color: white;
  border: none;
}

.btn-facebook:hover {
  background-color: #365899;
  color: white;
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

/* Form validation styles */
input.invalid {
  border: 1px solid #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 5px;
}

.error-message-box {
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.3);
  color: #dc3545;
  padding: 12px;
  border-radius: 5px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-message-box i {
  font-size: 18px;
  color: #dc3545;
}

@media (max-width: 576px) {
  .auth-container {
    padding: 10px;
  }
  
  .auth-card {
    border-radius: 8px;
  }
  
  .auth-header {
    padding: 20px;
  }
  
  .auth-header h1 {
    font-size: 1.8rem;
  }
  
  .auth-form {
    padding: 20px;
  }
  
  .form-extras {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .forgot-password {
    align-self: flex-end;
  }
}
</style>
