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
import TestPage from '../views/TestPage.vue';

const routes = [
  { path: '/', name: 'HomeView', component: HomeView },
  { path: '/login', name: 'LoginView', component: LoginView },
  { path: '/register', name: 'RegisterView', component: RegisterView },
  { path: '/register-professional', name: 'RegisterProfessional', component: RegisterProfessional },
  { path: '/customer', name: 'CustomerHome', component: CustomerHome },
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
    ]
  },
  { path: '/test', name: 'TestPage', component: TestPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard to protect admin routes
router.beforeEach((to, from, next) => {
  const token = sessionStorage.getItem('Authorization');
  
  if (to.path.startsWith('/admin') && !token) {
    console.log('Authentication required for admin routes - redirecting to login');
    next('/login');
  } else {
    next();
  }
});

export default router;
