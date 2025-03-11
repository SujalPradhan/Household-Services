<template>
  <div class="blocked-container">
    <div class="blocked-card">
      <div class="blocked-header">
        <i class="fas fa-ban blocked-icon"></i>
        <h1>Account Suspended</h1>
      </div>
      <div class="blocked-body">
        <p>Your account has been temporarily suspended.</p>
        <p>This may be due to one of the following reasons:</p>
        <ul>
          <li>Violation of our terms of service</li>
          <li>Multiple service cancellations</li>
          <li>Reported inappropriate behavior</li>
          <li>Administrative review</li>
        </ul>
        <p>Please contact our support team for more information and to resolve this issue.</p>
      </div>
      <div class="blocked-footer">
        <a href="mailto:support@urbanaid.com" class="support-link">
          <i class="fas fa-envelope"></i> Contact Support
        </a>
        <button @click="logout" class="logout-btn">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'BlockedUserView',
  methods: {
    logout() {
      // Clear authentication token
      sessionStorage.removeItem('Authorization');
      
      // Call logout endpoint
      axios.post('http://127.0.0.1:5000/signout')
        .catch(err => console.error("Logout error:", err));
      
      // Redirect to landing page
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.blocked-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #3F3244;
  padding: 20px;
}

.blocked-card {
  background-color: #2F2235;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 600px;
  overflow: hidden;
}

.blocked-header {
  background-color: #d32f2f;
  padding: 30px;
  text-align: center;
  color: white;
}

.blocked-icon {
  font-size: 4rem;
  margin-bottom: 15px;
}

.blocked-header h1 {
  margin: 0;
  font-size: 2.2rem;
}

.blocked-body {
  padding: 30px;
  color: #BFC3BA;
}

.blocked-body p {
  margin-bottom: 15px;
  line-height: 1.6;
}

.blocked-body ul {
  margin-bottom: 20px;
  padding-left: 20px;
}

.blocked-body li {
  margin-bottom: 8px;
  color: #A9ACA9;
}

.blocked-footer {
  padding: 20px 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.support-link, .logout-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.support-link {
  background-color: #60495A;
  color: white;
}

.support-link:hover {
  background-color: #70596A;
}

.logout-btn {
  background-color: transparent;
  border: 1px solid #BFC3BA;
  color: #BFC3BA;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
</style>
