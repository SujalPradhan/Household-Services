import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import RegisterProfessional from '../views/RegisterProfessional.vue';
import HomeView from '../views/HomeView.vue';
import CustomerHome from '../views/CustomerHome.vue';
import AdminHome from '../views/AdminHome.vue';
import AdminDashboard from '../views/AdminDashboard.vue';
import AdminService from '../views/AdminService.vue';
import AdminCustomers from '../views/AdminCustomers.vue';
import AdminProfessional from '../views/AdminProfessional.vue';
import ProfessionalHome from '../views/ProfessionalHome.vue';
import ServiceRequests from '../views/ServiceRequests.vue';
import ProfessionalProfile from '../views/ProfessionalProfile.vue';
import TestPage from '../views/TestPage.vue';
import BlockedUserView from '../views/BlockedUserView.vue';
import AdminServiceRequests from '../views/AdminServiceRequests.vue';
import CustomerDashboard from '../views/CustomerDashboard.vue';
import CustomerServices from '../views/CustomerServices.vue';
import CustomerProfessionals from '../views/CustomerProfessionals.vue';
import CustomerRequests from '../views/CustomerRequests.vue';

const routes = [
  { path: '/', name: 'HomeView', component: HomeView },
  { path: '/login', name: 'LoginView', component: LoginView },
  { path: '/register', name: 'RegisterView', component: RegisterView },
  { path: '/register-professional', name: 'RegisterProfessional', component: RegisterProfessional },
  { 
    path: '/customer',
    name: 'CustomerHome', 
    component: CustomerHome,
    children: [
      { path: '', redirect: { name: 'CustomerDashboard' } },
      { path: 'dashboard', name: 'CustomerDashboard', component: CustomerDashboard },
      { path: 'services', name: 'CustomerServices', component: CustomerServices },
      { path: 'professionals', name: 'CustomerProfessionals', component: CustomerProfessionals },
      { path: 'requests', name: 'CustomerRequests', component: CustomerRequests }
    ]
  },
  { 
    path: '/admin/home', 
    name: 'AdminHome', 
    component: AdminHome,
    children: [
      { path: '', redirect: { name: 'AdminDashboard' } },
      { path: 'dashboard', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'service', name: 'AdminService', component: AdminService },
      { path: 'customers', name: 'AdminCustomers', component: AdminCustomers },
      { path: 'professionals', name: 'AdminProfessional', component: AdminProfessional },
      { path: 'requests', name: 'AdminServiceRequests', component: AdminServiceRequests },
    ]
  },
  {
    path: '/professional',
    name: 'ProfessionalHome',
    component: ProfessionalHome,
    children: [
      { path: '', redirect: { name: 'ServiceRequests' } },
      { path: 'requests', name: 'ServiceRequests', component: ServiceRequests },
      { path: 'profile', name: 'ProfessionalProfile', component: ProfessionalProfile },
    ]
  },
  { path: '/blocked', name: 'blocked', component: BlockedUserView },
  { path: '/test', name: 'TestPage', component: TestPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard to protect routes
router.beforeEach((to, from, next) => {
  const token = sessionStorage.getItem('Authorization');
  
  // Protected routes that need authentication
  if ((to.path.startsWith('/admin') || 
      to.path.startsWith('/professional') || 
      to.path.startsWith('/customer')) && !token) {
    console.log('Authentication required - redirecting to login');
    next('/login');
  } 
  // Redirect logged-in users away from login/register pages
  else if ((to.path === '/login' || to.path === '/register' || 
           to.path === '/register-professional') && token) {
    console.log('Already logged in - redirecting to dashboard');
    // Redirect based on user role (would need to check role from API or storage)
    next('/');
  }
  else {
    next();
  }
});

export default router;
