import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Import CSS
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import './assets/variables.css'; // Import our color variables first
import './assets/global.css';

const app = createApp(App);
app.use(router);
app.mount('#app');

// Make showRegisterModal accessible globally through the root instance
app.config.globalProperties.showRegisterModal = false;
