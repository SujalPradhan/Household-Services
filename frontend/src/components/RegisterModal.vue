<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <button class="close-btn" @click="closeModal">×</button>
      <h2>Choose Registration Type</h2>
      <div class="options-container">
        <div class="option-card">
          <i class="fas fa-user"></i>
          <h3>Customer</h3>
          <p>Need household services? Register as a customer to book services.</p>
          <router-link to="/register" class="btn btn-primary" @click="closeModal">Register as Customer</router-link>
        </div>
        <div class="option-card">
          <i class="fas fa-tools"></i>
          <h3>Professional</h3>
          <p>Offer your expertise! Register as a service professional to provide services.</p>
          <router-link to="/register-professional" class="btn btn-primary" @click="closeModal">Register as Professional</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterModal',
  props: {
    show: {
      type: Boolean,
      required: true
    }
  },
  created() {
    // Close modal if user is logged in
    this.checkAuth();
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    checkAuth() {
      const token = sessionStorage.getItem('Authorization');
      if (token && this.show) {
        // If user is authenticated but modal is showing, close it
        this.closeModal();
      }
    }
  },
  watch: {
    // Monitor show prop to check authentication
    show(newVal) {
      if (newVal) {
        this.checkAuth();
      }
    }
  }
};
</script>

<style scoped>
/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background-color: #3F3244;
  border-radius: 10px;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.5);
  width: 90%;
  max-width: 800px;
  padding: 30px;
  position: relative;
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 28px;
  color: #BFC3BA;
  background: none;
  border: none;
  cursor: pointer;
}

.close-btn:hover {
  color: #60495A;
}

.modal-content h2 {
  color: #BFC3BA;
  text-align: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(191, 195, 186, 0.2);
}

.options-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 30px;
}

.option-card {
  background-color: #2F2235;
  border-radius: 10px;
  padding: 30px;
  width: 45%;
  min-width: 250px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.option-card i {
  font-size: 3rem;
  color: #60495A;
  margin-bottom: 15px;
}

.option-card h3 {
  margin-bottom: 15px;
  color: #BFC3BA;
}

.option-card p {
  color: #A9ACA9;
  margin-bottom: 20px;
}

.btn-primary {
  display: inline-block;
  background-color: #60495A;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #4d3a49;
}

/* Media Queries */
@media (max-width: 768px) {
  .options-container {
    flex-direction: column;
    align-items: center;
  }
  
  .option-card {
    width: 100%;
  }
  
  .modal-content {
    padding: 20px;
  }
}
</style>
