<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h2>Admin Dashboard</h2>
      <button @click="manualRefresh" class="refresh-btn" :disabled="isRefreshing">
        <i class="fas" :class="isRefreshing ? 'fa-spinner fa-spin' : 'fa-sync-alt'"></i>
        {{ isRefreshing ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <div class="dashboard-stats">
      <div class="stat-card">
        <h3>Total Customers</h3>
        <p class="stat-value">{{ stats.customers || 0 }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Professionals</h3>
        <p class="stat-value">{{ stats.professionals || 0 }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Services</h3>
        <p class="stat-value">{{ stats.services || 0 }}</p>
      </div>
      <div class="stat-card">
        <h3>Pending Approvals</h3>
        <p class="stat-value">{{ stats.pendingApprovals || 0 }}</p>
      </div>
    </div>
    
    <div class="dashboard-actions">
      <h3>Quick Actions</h3>
      <div class="action-buttons">
        <router-link to="/admin/home/service" class="action-btn">
          Manage Services
        </router-link>
        <router-link to="/admin/home/professionals" class="action-btn">
          Approve Professionals
        </router-link>
        <router-link to="/admin/home/customers" class="action-btn">
          View Customers
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {
        customers: 0,
        professionals: 0,
        services: 0,
        pendingApprovals: 0
      },
      isRefreshing: false,
      isInitialLoad: true
    };
  },
  mounted() {
    // Check if this is the initial page load or a refresh
    const hasRefreshed = sessionStorage.getItem('dashboard_refreshed');
    
    if (!hasRefreshed && this.isInitialLoad) {
      // Set the flag to prevent infinite refresh loop
      sessionStorage.setItem('dashboard_refreshed', 'true');
      // Reload the entire page to remount App.vue
      window.location.reload();
    } else {
      // Clear the flag for next visit
      sessionStorage.removeItem('dashboard_refreshed');
      // Fetch dashboard data
      this.fetchDashboardData();
    }
  },
  methods: {
    manualRefresh() {
      // Reload the entire page
      window.location.reload();
    },
    
    async fetchDashboardData() {
      this.isRefreshing = true;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) throw new Error('Not authenticated');
        
        const response = await axios.get('http://127.0.0.1:5000/admin/dashboard', {
          headers: {
            'Authorization': token
          }
        });
        
        if (response.data) {
          this.stats = response.data;
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        this.isRefreshing = false;
      }
    }
  }
};
</script>

<style scoped>
.admin-dashboard {
  color: #BFC3BA;
}

.admin-dashboard h2 {
  margin-bottom: 25px;
  color: #BFC3BA;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: #2F2235;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  font-size: 1rem;
  margin-bottom: 10px;
  color: #A9ACA9;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #60495A;
  margin: 0;
}

.dashboard-actions {
  background-color: #2F2235;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.dashboard-actions h3 {
  margin-bottom: 15px;
  color: #A9ACA9;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.action-btn {
  display: inline-block;
  background-color: #60495A;
  color: white;
  padding: 10px 15px;
  border-radius: 5px;
  text-decoration: none;
  transition: all 0.3s;
}

.action-btn:hover {
  background-color: #4d3a49;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .dashboard-stats {
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  }
  
  .stat-value {
    font-size: 2rem;
  }
  
  .action-btn {
    width: 100%;
    text-align: center;
  }
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.refresh-btn {
  background-color: #60495A;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 8px 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #4d3a49;
}

.refresh-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
