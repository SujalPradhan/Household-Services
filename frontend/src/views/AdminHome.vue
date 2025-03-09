<template>
  <div class="admin-layout">
    <header class="admin-header">
      <h1>UrbanAid</h1>
      <div class="admin-nav">
        <router-link to="/admin/home/dashboard">Dashboard</router-link> |
        <router-link to="/admin/home/service">Services</router-link> |
        <router-link to="/admin/home/customers">Customers</router-link> |
        <router-link to="/admin/home/professionals">Professionals</router-link> |
        <button @click="logout" class="logout-btn">Logout</button>
      </div>
    </header>
    <main class="admin-content">
      <router-view/>
    </main>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminHome',
  methods: {
    logout() {
      // Clear authentication token
      sessionStorage.removeItem('Authorization');
      
      // Call logout endpoint if needed
      axios.post('http://127.0.0.1:5000/signout')
        .catch(err => console.error("Logout error:", err));
      
      // Redirect to login
      this.$router.push('/login');
    }
  },
  created() {
    // Redirect to dashboard by default if directly accessing /admin/home
    if (this.$route.path === '/admin/home') {
      this.$router.push('/admin/home/dashboard');
    }
  }
};
</script>

<style scoped>
.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-header {
  background-color: #2F2235;
  padding: 20px;
  color: #BFC3BA;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  border-bottom: 3px solid #60495A;
}

.admin-header h1 {
  margin-bottom: 15px;
  color: #BFC3BA;
}

.admin-nav {
  padding: 10px 0;
}

.admin-nav a {
  margin-right: 15px;
  font-weight: 600;
  color: #BFC3BA;
  text-decoration: none;
  padding: 8px 10px;
  transition: all 0.3s;
  border-bottom: 2px solid transparent;
}

.admin-nav a:hover {
  color: #60495A;
  border-bottom: 2px solid #60495A;
}

.admin-nav a.router-link-active {
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

.admin-content {
  padding: 20px;
  flex: 1;
  background-color: #3F3244;
}
</style>
