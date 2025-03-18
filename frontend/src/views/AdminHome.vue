<template>
  <div class="admin-layout">
    <!-- Top Navigation Bar -->
    <div class="admin-navbar">
      <div class="navbar-brand">
        <h2>Admin Panel</h2>
      </div>
      <div class="navbar-menu">
        <router-link to="/admin/home/dashboard" class="menu-item">
          <i class="fas fa-tachometer-alt"></i> Dashboard
        </router-link>
        <router-link to="/admin/home/service" class="menu-item">
          <i class="fas fa-tools"></i> Services
        </router-link>
        <router-link to="/admin/home/requests" class="menu-item">
          <i class="fas fa-clipboard-list"></i> Service Requests
        </router-link>
        <router-link to="/admin/home/customers" class="menu-item">
          <i class="fas fa-users"></i> Customers
        </router-link>
        <router-link to="/admin/home/professionals" class="menu-item">
          <i class="fas fa-user-tie"></i> Professionals
        </router-link>
      </div>
      <div class="navbar-actions"> 
        <button @click="downloadServiceClosedRequests" class="btn-download">
          <i class="fas fa-file-download"></i> Download Reports
        </button>
        <button @click="logout" class="btn-logout">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>
    
    <div class="admin-content">
      <div class="content-main">
        <router-view />
      </div>
    </div>
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
    },
    
    async downloadServiceClosedRequests() {
      try {
        // Show a simple alert instead of toast
        alert('Preparing download, please wait...');
        
        // Use axios instead of fetch
        const response = await axios.get('http://127.0.0.1:5000/downloadcsv');
        const data = response.data;
        
        if (response.status === 200) {
          const taskId = data['task_id'];
          
          const intv = setInterval(async () => {
            try {
              // Check if the CSV file is ready
              const csvResponse = await axios.get(`http://127.0.0.1:5000/getcsv/${taskId}`, {
                responseType: 'blob' // Important for downloading files
              });
              
              if (csvResponse.status === 200) {
                clearInterval(intv);
                
                // Create a download link for the file
                const url = window.URL.createObjectURL(new Blob([csvResponse.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', `service-requests-${Date.now()}.csv`);
                document.body.appendChild(link);
                link.click();
                link.remove();
                
                setTimeout(() => {
                  alert('Download completed!');
                }, 500);
              }
            } catch (err) {
              if (err.response && err.response.status !== 400) {
                clearInterval(intv);
                console.error('Error checking CSV status:', err);
              }
              // If status is 400, task is still pending, continue waiting
            }
          }, 1000); // Check every second
        }
      } catch (error) {
        console.error('Error downloading service requests:', error);
        alert('Failed to download service requests');
      }
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
  margin: 0;
  padding: 0;
}

/* Top Navigation Bar */
.admin-navbar {
  background-color: #2F2235;
  color: #BFC3BA;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  border-bottom: 3px solid #60495A;
  z-index: 100;
  position: sticky;
  top: 0;
}

.navbar-brand h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #BFC3BA;
}

.navbar-menu {
  display: flex;
  align-items: center;
  height: 100%;
}

.menu-item {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 15px;
  color: #BFC3BA;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
  position: relative;
}

.menu-item i {
  margin-right: 8px;
}

.menu-item:hover {
  background-color: rgba(96, 73, 90, 0.3);
  color: white;
}

.menu-item.router-link-active {
  color: white;
}

.menu-item.router-link-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: #60495A;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-name {
  font-weight: 600;
  color: #BFC3BA;
}

.btn-logout {
  background-color: #60495A;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-logout:hover {
  background-color: #7d5e74;
}

/* New download button style */
.btn-download {
  background-color: #3F3244;
  color: white;
  border: 1px solid #60495A;
  padding: 6px 12px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-download:hover {
  background-color: #60495A;
  transform: translateY(-2px);
}

.btn-download i {
  font-size: 0.9rem;
}

/* Content area */
.admin-content {
  flex: 1;
  background-color: #3F3244;
  min-height: calc(100vh - 60px); /* Account for navbar height */
}

.content-main {
  padding: 20px;
  padding-top: 15px;
  overflow-y: auto;
}

/* Responsive styles */
@media (max-width: 768px) {
  .admin-navbar {
    flex-direction: column;
    height: auto;
    padding: 10px;
  }
  
  .navbar-brand {
    margin-bottom: 10px;
  }
  
  .navbar-menu {
    width: 100%;
    overflow-x: auto;
    justify-content: space-between;
    padding-bottom: 5px;
  }
  
  .menu-item {
    height: 40px;
    padding: 0 10px;
    font-size: 0.9rem;
  }
  
  .menu-item i {
    margin-right: 5px;
  }
  
  .navbar-actions {
    width: 100%;
    justify-content: space-between;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
}
</style>
