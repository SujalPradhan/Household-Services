<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">

      <div v-if="admin" class="admin-welcome">
        <h1>Admin Dashboard</h1>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading dashboard data...</p>
    </div>

    <div v-else class="dashboard-content">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-users"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ dashboardData.totalCustomers || 0 }}</div>
            <div class="stat-label">Total Customers</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-user-tie"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ dashboardData.totalProfessionals || 0 }}</div>
            <div class="stat-label">Total Professionals</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-briefcase"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ dashboardData.totalServices || 0 }}</div>
            <div class="stat-label">Services Offered</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-clipboard-check"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ dashboardData.totalRequests || 0 }}</div>
            <div class="stat-label">Service Requests</div>
          </div>
        </div>
      </div>

      <div class="dashboard-sections">
        <div class="section">
          <h2><i class="fas fa-user-check"></i> Pending Professional Approvals</h2>
          <div v-if="dashboardData.pendingApprovals?.length === 0" class="empty-state">
            <p>No pending professional approvals</p>
          </div>
          <div v-else class="pending-approvals">
            <div v-for="professional in dashboardData.pendingApprovals" :key="professional.id" class="professional-card">
              <div class="professional-info">
                <h3>{{ professional.name }}</h3>
                <p><i class="fas fa-envelope"></i> {{ professional.email }}</p>
                <p><i class="fas fa-tools"></i> {{ professional.service_type }}</p>
                <p><i class="fas fa-star"></i> Experience: {{ professional.experience }} years</p>
                <p v-if="professional.description"><i class="fas fa-info-circle"></i> {{ professional.description }}</p>
              </div>
              <div class="approval-actions">
                <button @click="approveProfessional(professional.id)" class="btn btn-success">
                  <i class="fas fa-check"></i> Approve
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="section">
          <h2><i class="fas fa-chart-line"></i> Recent Service Requests</h2>
          <div v-if="dashboardData.recentRequests?.length === 0" class="empty-state">
            <p>No recent service requests</p>
          </div>
          <div v-else class="recent-requests">
            <table>
              <thead>
                <tr>
                  <th>Service</th>
                  <th>Customer</th>
                  <th>Professional</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="request in dashboardData.recentRequests" :key="request.id">
                  <td>{{ request.service_name }}</td>
                  <td>{{ request.customer_name }}</td>
                  <td>{{ request.professional_name || 'Unassigned' }}</td>
                  <td><span class="status-badge" :class="request.status.toLowerCase()">{{ request.status }}</span></td>
                  <td>{{ formatDate(request.date) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
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
      admin: null,
      loading: true,
      dashboardData: {
        totalCustomers: 0,
        totalProfessionals: 0,
        totalServices: 0,
        totalRequests: 0,
        pendingApprovals: [],
        recentRequests: []
      }
    };
  },
  methods: {
    async fetchDashboardData() {
      try {
        this.loading = true;
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Authorization token not found');
        }
        
        // Fetch admin info
        const adminResponse = await axios.get('http://127.0.0.1:5000/admin/dashboard', {
          headers: {
            Authorization: token
          }
        });
        
        this.admin = adminResponse.data;
        
        // Fetch customers count
        const customersResponse = await axios.get('http://127.0.0.1:5000/admin/customers', {
          headers: {
            Authorization: token
          }
        });
        this.dashboardData.totalCustomers = customersResponse.data.length || 0;
        
        // Fetch professionals data
        const professionalsResponse = await axios.get('http://127.0.0.1:5000/admin/professionals', {
          headers: {
            Authorization: token
          }
        });
        
        const professionals = professionalsResponse.data || [];
        this.dashboardData.totalProfessionals = professionals.length;
        
        // Filter for pending approvals
        this.dashboardData.pendingApprovals = professionals.filter(p => !p.approved && !p.blocked).slice(0, 5);
        
        // Fetch services
        const servicesResponse = await axios.get('http://127.0.0.1:5000/admin/service', {
          headers: {
            Authorization: token
          }
        });
        this.dashboardData.totalServices = servicesResponse.data.length || 0;
        
        // Fetch all service requests
        const requestsResponse = await axios.get('http://127.0.0.1:5000/admin/service-requests', {
          headers: {
            Authorization: token
          }
        });
        
        const requests = requestsResponse.data || [];
        this.dashboardData.totalRequests = requests.length;
        
        // Get recent requests (most recent 5)
        this.dashboardData.recentRequests = requests
          .sort((a, b) => new Date(b.date_of_request) - new Date(a.date_of_request))
          .slice(0, 5)
          .map(req => ({
            id: req.id,
            service_name: req.service_name,
            customer_name: req.customer_name,
            professional_name: req.professional_name,
            status: req.status,
            date: req.date_of_request
          }));
        
      } catch (error) {
        console.error("Error fetching admin dashboard data:", error);
        // Show an error notification (if you have one)
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: '2-digit' 
      });
    },
    
    async approveProfessional(professionalId) {
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Authorization token not found');
        }
        
        await axios.put(`http://127.0.0.1:5000/admin/professionals/${professionalId}`, {
          approved: true
        }, {
          headers: {
            Authorization: token
          }
        });
        
        // Remove from pending approvals and refresh data
        this.dashboardData.pendingApprovals = this.dashboardData.pendingApprovals.filter(p => p.id !== professionalId);
        
        // Show success notification (if you have one)
        
      } catch (error) {
        console.error("Error approving professional:", error);
        // Show an error notification (if you have one)
      }
    },
    
    logout() {
      // Clear authentication token
      sessionStorage.removeItem('Authorization');
      
      // Call logout endpoint
      axios.post('http://127.0.0.1:5000/signout')
        .catch(err => console.error("Logout error:", err));
      
      // Redirect to landing page
      this.$router.push('/');
    }
  },
  async mounted() {
    await this.fetchDashboardData();
  }
};
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
  color: var(--light-color);
}

.dashboard-header {
  margin-bottom: 30px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.logout-btn {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.logout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #f55a4e, #e33e3e);
}

.admin-welcome {
  background-color: var(--secondary-color);
  padding: 15px;
  border-radius: 5px;
  border-left: 4px solid var(--primary-color);
}

.dashboard-content {
  margin-top: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: var(--dark-color);
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3);
}

.stat-icon {
  font-size: 2.5rem;
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-color);
  color: white;
  border-radius: 50%;
  margin-right: 20px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 5px;
}

.stat-label {
  color: var(--muted-color);
  font-size: 0.9rem;
}

.section {
  background-color: var(--secondary-color);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.section h2 {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 15px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.section h2 i {
  margin-right: 10px;
  color: var(--primary-color);
}

.empty-state {
  background-color: var(--dark-color);
  padding: 20px;
  text-align: center;
  color: var(--muted-color);
  border-radius: 5px;
}

.professional-card {
  background-color: var(--dark-color);
  border-radius: 5px;
  padding: 15px;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.professional-info h3 {
  margin-top: 0;
  margin-bottom: 10px;
}

.professional-info p {
  margin: 5px 0;
  color: var(--muted-color);
}

.professional-info i {
  width: 20px;
  color: var(--primary-color);
}

.approval-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 15px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #218838;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  text-align: left;
  padding: 12px 15px;
}

th {
  background-color: rgba(0, 0, 0, 0.2);
  color: var(--light-color);
  font-weight: 600;
}

tbody tr {
  background-color: var(--dark-color);
}

tbody tr:nth-child(odd) {
  background-color: rgba(0, 0, 0, 0.1);
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: lowercase;
}

.status-badge.requested {
  background-color: #17a2b8;
  color: white;
}

.status-badge.accepted {
  background-color: #ffc107;
  color: #212529;
}

.status-badge.completed {
  background-color: #28a745;
  color: white;
}

.status-badge.closed {
  background-color: #6c757d;
  color: white;
}

.status-badge.cancelled {
  background-color: #dc3545;
  color: white;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
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

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .professional-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .approval-actions {
    margin-top: 15px;
    width: 100%;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  table, thead, tbody, th, td, tr {
    display: block;
  }
  
  thead tr {
    position: absolute;
    top: -9999px;
    left: -9999px;
  }
  
  tr {
    margin-bottom: 15px;
  }
  
  td {
    border: none;
    position: relative;
    padding-left: 50%;
  }
  
  td:before {
    position: absolute;
    top: 12px;
    left: 15px;
    width: 45%;
    padding-right: 10px;
    white-space: nowrap;
    font-weight: bold;
  }
  
  td:nth-of-type(1):before { content: "Service"; }
  td:nth-of-type(2):before { content: "Customer"; }
  td:nth-of-type(3):before { content: "Professional"; }
  td:nth-of-type(4):before { content: "Status"; }
  td:nth-of-type(5):before { content: "Date"; }
}
</style>
