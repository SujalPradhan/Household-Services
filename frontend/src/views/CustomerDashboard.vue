<template>
  <div class="customer-dashboard-content">
    <!-- Welcome Message -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h1>Welcome to Your Dashboard</h1>
        <p>View your service request statistics and manage your household services.</p>
      </div>
    </div>
    
    <!-- Service Request Summary Section -->
    <div class="dashboard-section service-summary">
      <h3><i class="fas fa-clipboard-list"></i> Service Requests Summary</h3>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-clock"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ requestStats.pending }}</div>
            <div class="stat-label">Pending</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-spinner"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ requestStats.active }}</div>
            <div class="stat-label">In Progress</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ requestStats.completed }}</div>
            <div class="stat-label">Completed</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-clipboard-list"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ serviceRequests.length }}</div>
            <div class="stat-label">Total Requests</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Actions Section -->
    <div class="actions-row">
      <router-link to="/customer/services" class="action-btn service-btn">
        <i class="fas fa-tools"></i> Find Services
      </router-link>
      
      <router-link to="/customer/professionals" class="action-btn professional-btn">
        <i class="fas fa-user-tie"></i> Find Professionals
      </router-link>
      
      <router-link to="/customer/requests" class="action-btn request-btn">
        <i class="fas fa-clipboard-list"></i> View All Requests
      </router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CustomerDashboard',
  data() {
    return {
      customer: null,
      serviceRequests: [],
      loadingRequests: true,
      requestStats: {
        pending: 0,
        active: 0,
        completed: 0
      }
    };
  },
  methods: {
    async fetchDashboardData() {
      try {
        this.loadingRequests = true;
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Authorization token not found');
        }
        
        const response = await axios.get('http://127.0.0.1:5000/customer/dashboard', {
          headers: {
            Authorization: token
          }
        });
        
        // Get customer details
        this.customer = response.data.customer_details;
        
        // Process service history
        this.serviceRequests = response.data.service_history || [];
        
        // Calculate request stats
        this.calculateRequestStats();
        
      } catch (error) {
        console.error("Error fetching customer dashboard data:", error);
      } finally {
        this.loadingRequests = false;
      }
    },
    
    calculateRequestStats() {
      const stats = {
        pending: 0,
        active: 0,
        completed: 0
      };
      
      this.serviceRequests.forEach(request => {
        const status = request.status.toLowerCase();
        if (status === 'requested') {
          stats.pending++;
        } else if (status === 'accepted') {
          stats.active++;
        } else if (status === 'completed' || status === 'closed') {
          stats.completed++;
        }
      });
      
      this.requestStats = stats;
    }
  },
  mounted() {
    this.fetchDashboardData();
  }
};
</script>

<style scoped>
.customer-dashboard-content {
  padding: 20px;
}

.welcome-section {
  background-color: var(--secondary-color);
  padding: 30px;
  border-radius: 10px;
  margin-bottom: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  background-image: linear-gradient(135deg, rgba(96, 73, 90, 0.6) 0%, rgba(96, 73, 90, 0.2) 100%);
  border-left: 4px solid var(--primary-color);
}

.welcome-text h1 {
  margin: 0 0 10px 0;
  font-size: 1.8rem;
  color: var(--light-color);
}

.welcome-text p {
  margin: 0;
  color: var(--muted-color);
  font-size: 1.1rem;
}

.dashboard-section {
  background-color: var(--secondary-color);
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  margin-bottom: 25px;
}

.dashboard-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  color: var(--light-color);
  border-bottom: 1px solid rgba(191, 195, 186, 0.2);
  padding-bottom: 15px;
  font-size: 1.2rem;
}

.dashboard-section h3 i {
  margin-right: 10px;
  color: var(--primary-color);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background-color: var(--dark-color);
  border-radius: 10px;
  padding: 20px;
  display: flex;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--primary-color), #8e67d2);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 15px;
  font-size: 1.5rem;
  color: white;
  box-shadow: 0 3px 8px rgba(142, 103, 210, 0.3);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--light-color);
  line-height: 1;
}

.stat-label {
  color: var(--muted-color);
  font-size: 0.95rem;
  margin-top: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Action Buttons Row */
.actions-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.action-btn {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  background-color: var(--dark-color);
  color: var(--light-color);
  text-decoration: none;
  padding: 16px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  border: 1px solid rgba(255, 255, 255, 0.1);
  gap: 12px;
}

.action-btn i {
  font-size: 1.3rem;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.service-btn {
  background-image: linear-gradient(135deg, #60495A, #7e57c2);
}

.professional-btn {
  background-image: linear-gradient(135deg, #2F2235, #534269);
}

.request-btn {
  background-image: linear-gradient(135deg, #3F3244, #60495A);
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(96, 73, 90, 0.3);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .actions-row {
    grid-template-columns: 1fr;
  }
  
  .welcome-section {
    padding: 20px;
  }
  
  .welcome-text h1 {
    font-size: 1.5rem;
  }
  
  .welcome-text p {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
