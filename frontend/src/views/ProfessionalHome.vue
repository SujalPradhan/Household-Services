<template>
  <div class="professional-layout">
    <header class="professional-header">
      <h1>UrbanAid</h1>
      <div class="professional-nav">
        <router-link to="/professional/requests" class="nav-link">
          My Requests
          <span v-if="newRequestsCount > 0" class="badge">{{ newRequestsCount }}</span>
        </router-link> |
        <router-link to="/professional/profile">Profile</router-link> |
        <button @click="logout" class="logout-btn">Logout</button>
      </div>
    </header>
    <main class="professional-content">
      <router-view @new-requests-count="updateNewRequestsCount"/>
    </main>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ProfessionalHome',
  data() {
    return {
      newRequestsCount: 0
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
    }
  },
  created() {
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
}

.professional-header {
  background-color: #2F2235;
  padding: 20px;
  color: #BFC3BA;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  border-bottom: 3px solid #60495A;
}

.professional-header h1 {
  margin-bottom: 15px;
  color: #BFC3BA;
}

.professional-nav {
  padding: 10px 0;
}

.professional-nav a {
  margin-right: 15px;
  font-weight: 600;
  color: #BFC3BA;
  text-decoration: none;
  padding: 8px 10px;
  transition: all 0.3s;
  border-bottom: 2px solid transparent;
}

.professional-nav a:hover {
  color: #60495A;
  border-bottom: 2px solid #60495A;
}

.professional-nav a.router-link-active {
  color: #60495A;
  border-bottom: 2px solid #60495A;
}

.logout-btn {
  background-color: #60495A;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease;
}

.logout-btn:hover {
  background-color: #3F3244;
}

.professional-content {
  padding: 20px;
  flex: 1;
  background-color: #3F3244;
}

.nav-link {
  position: relative;
}

.badge {
  position: absolute;
  top: -8px;
  right: -12px;
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
}
</style>
