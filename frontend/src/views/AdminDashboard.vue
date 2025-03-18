<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">

      <div v-if="admin" class="admin-welcome">
        <h1>Admin Dashboard</h1>
        <!-- Add download button -->

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

      <!-- NEW: Service Type Analytics Section -->
      <div class="section analytics-section">
        <h2><i class="fas fa-chart-bar"></i> Service Request Distribution</h2>
        <div class="chart-container">
          <div v-if="loadingCharts" class="loading-spinner">
            <div class="spinner"></div>
            <p>Generating chart...</p>
          </div>
          <div v-else-if="!serviceTypeChartData.labels.length" class="empty-chart">
            <p>Not enough data to generate charts</p>
          </div>
          <div v-else class="chart-wrapper">
            <canvas ref="serviceTypeChart"></canvas>
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
import Chart from 'chart.js/auto';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      admin: null,
      loading: true,
      loadingCharts: true,
      downloadInProgress: false,
      dashboardData: {
        totalCustomers: 0,
        totalProfessionals: 0,
        totalServices: 0,
        totalRequests: 0,
        pendingApprovals: [],
        recentRequests: []
      },
      serviceTypeChart: null,
      serviceTypeChartData: {
        labels: [],
        datasets: [{
          label: 'Service Requests',
          data: [],
          backgroundColor: [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(199, 199, 199, 0.7)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(199, 199, 199, 1)'
          ],
          borderWidth: 1
        }]
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
        
        // After loading the existing data
        await this.prepareServiceTypeChart();
      } catch (error) {
        console.error("Error fetching admin dashboard data:", error);
        // Show an error notification (if you have one)
      } finally {
        this.loading = false;
        this.loadingCharts = false;
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
    },
    
    // Updated method to prepare service type chart data
    async prepareServiceTypeChart() {
      try {
        this.loadingCharts = true;
        const token = sessionStorage.getItem('Authorization');
        
        // Get all service requests with detailed debugging
        console.log("Fetching service requests for chart data...");
        const requestsResponse = await axios.get('http://127.0.0.1:5000/admin/service-requests', {
          headers: {
            Authorization: token
          }
        });
        
        // Log the raw data we receive
        console.log("Raw service requests data:", requestsResponse);
        
        const requests = requestsResponse.data || [];
        if (!requests.length) {
          console.log("No service request data available for chart");
          this.loadingCharts = false;
          return;
        }
        
        // Get all services to map service types
        console.log("Fetching services for mapping...");
        const servicesResponse = await axios.get('http://127.0.0.1:5000/admin/service', {
          headers: {
            Authorization: token
          }
        });
        
        console.log("Services data:", servicesResponse.data);
        
        // Build a map of service_id to service_type for reference
        const serviceMap = {};
        (servicesResponse.data || []).forEach(service => {
          serviceMap[service.id] = {
            name: service.name,
            type: service.service_type
          };
        });
        
        console.log("Service map created:", serviceMap);
        
        // Count requests by service type
        const requestsByType = {};
        
        requests.forEach(request => {
          // First try to use service_name from the request
          let serviceType = request.service_name;
          
          // If that fails, try to look up the service type using the service_id
          if (!serviceType && request.service_id && serviceMap[request.service_id]) {
            serviceType = serviceMap[request.service_id].name;
          }
          
          // Default to "Unknown" if we can't determine the service type
          serviceType = serviceType || "Unknown";
          
          if (requestsByType[serviceType]) {
            requestsByType[serviceType]++;
          } else {
            requestsByType[serviceType] = 1;
          }
        });
        
        console.log("Processed request counts by type:", requestsByType);
        
        if (Object.keys(requestsByType).length === 0) {
          console.log("No service types found for chart");
          this.loadingCharts = false;
          return;
        }
        
        // Use a fixed set of colors that can be repeated for many service types
        const backgroundColors = [
          'rgba(255, 99, 132, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 206, 86, 0.7)',
          'rgba(75, 192, 192, 0.7)',
          'rgba(153, 102, 255, 0.7)',
          'rgba(255, 159, 64, 0.7)',
          'rgba(199, 199, 199, 0.7)'
        ];
        
        const borderColors = [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(199, 199, 199, 1)'
        ];
        
        // Get the service types and counts
        const serviceTypes = Object.keys(requestsByType);
        const serviceCounts = Object.values(requestsByType);
        
        // Create colors arrays with the right length (repeating if necessary)
        const backgroundColorsArray = serviceTypes.map((_, i) => 
          backgroundColors[i % backgroundColors.length]);
        const borderColorsArray = serviceTypes.map((_, i) => 
          borderColors[i % borderColors.length]);
        
        // Prepare chart data
        this.serviceTypeChartData = {
          labels: serviceTypes,
          datasets: [{
            label: 'Number of Requests',
            data: serviceCounts,
            backgroundColor: backgroundColorsArray,
            borderColor: borderColorsArray,
            borderWidth: 1
          }]
        };
        
        console.log("Chart data prepared:", this.serviceTypeChartData);
        
        // Render after a short delay to ensure the DOM has updated
        setTimeout(() => {
          this.renderServiceTypeChart();
        }, 100);
      } catch (error) {
        console.error("Error preparing chart data:", error);
      } finally {
        this.loadingCharts = false;
      }
    },
    
    renderServiceTypeChart() {
      try {
        const ctx = this.$refs.serviceTypeChart;
        console.log("Canvas element:", ctx);
        
        if (!ctx) {
          console.error("Chart canvas element not found");
          return;
        }
        
        // Destroy existing chart if it exists
        if (this.serviceTypeChart) {
          this.serviceTypeChart.destroy();
        }
        
        // Create new chart with improved error handling
        this.serviceTypeChart = new Chart(ctx, {
          type: 'bar',
          data: this.serviceTypeChartData,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                displayColors: false
              },
              title: {
                display: true,
                text: 'Number of Requests per Service',
                color: '#fff',
                font: {
                  size: 16
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  color: 'rgba(255, 255, 255, 0.7)',
                  precision: 0
                },
                grid: {
                  color: 'rgba(255, 255, 255, 0.1)'
                }
              },
              x: {
                ticks: {
                  color: 'rgba(255, 255, 255, 0.7)',
                  autoSkip: false,
                  maxRotation: 45,
                  minRotation: 45
                },
                grid: {
                  display: false
                }
              }
            }
          }
        });
        console.log("Chart created successfully");
      } catch (error) {
        console.error("Error creating chart:", error);
      }
    },
    
    // Add the download method from cc.js
    
  },
  async mounted() {
    console.log("AdminDashboard component mounted");
    await this.fetchDashboardData();
  },
  beforeUnmount() {
    // Clean up chart when component is unmounted
    if (this.serviceTypeChart) {
      this.serviceTypeChart.destroy();
    }
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
  color: var (--muted-color);
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

/* Chart Styles */
.analytics-section {
  margin-top: 30px;
  margin-bottom: 30px;
}

.chart-container {
  background-color: var(--dark-color);
  border-radius: 8px;
  padding: 20px;
  position: relative;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  min-height: 350px;
}

.chart-wrapper {
  height: 350px;
  position: relative;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.empty-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--muted-color);
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 5px;
}

/* Download button styles */
.download-section {
  margin-top: 15px;
}

.download-btn {
  background: linear-gradient(135deg, #60495A, #3F3244);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #7d5e74, #524258);
}

.download-btn i {
  font-size: 1rem;
}
</style>
