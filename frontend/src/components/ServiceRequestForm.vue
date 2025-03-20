<template>
  <div class="service-request-form-container">
    <h3>Request {{ service.name }}</h3>
    
    <form @submit.prevent="submitRequest" class="service-request-form">
      <div class="form-group">
        <label for="price">Price (₹)</label>
        <div class="price-display">{{ displayPrice }}</div>
        <div class="price-adjustment">
          <label for="priceAdjustment">Adjust the Price (optional)</label>
          <div class="slider-container">
            <input 
              type="range" 
              id="priceAdjustment" 
              v-model="priceAdjustment" 
              min="0" 
              max="20000" 
              step="50" 
              class="form-range"
            >
            <span class="slider-value">+₹{{ priceAdjustment }}</span>
          </div>
          <div class="price-breakdown">
            <span>Base Price: ₹{{ basePrice.toFixed(2) }}</span>
            <span>Adjustment: +₹{{ priceAdjustment }}</span>
            <span class="total-price">Total Price: ₹{{ formData.price.toFixed(2) }}</span>
          </div>
        </div>
        <input type="hidden" v-model="formData.price">
      </div>
      
      <div class="form-group">
        <label for="preferredDate">Preferred Service Date*</label>
        <input
          type="datetime-local"
          id="preferredDate"
          v-model="formData.preferred_date"
          class="form-control"
          :min="minDateTime"
          required
          @change="validatePreferredDate"
        >
        <div v-if="dateError" class="date-error">
          {{ dateError }}
        </div>
      </div>
      
      <div class="form-group">
        <label for="professional">Select Professional*</label>
        <div v-if="loading" class="loading-spinner">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="professionals.length === 0" class="no-professionals">
          <p>No professionals available for this service type.</p>
        </div>
        <div v-else>
          <select
            id="professional"
            v-model="formData.professional_id"
            class="form-control"
            required
          >
            <option value="" disabled>Select a professional</option>
            <option v-for="pro in professionals" :key="pro.id" :value="pro.id">
              {{ pro.name }} ({{ pro.experience }} years exp.)
            </option>
          </select>
          
          <div v-if="selectedProfessional" class="professional-info">
            <div class="professional-header">
              <h4>{{ selectedProfessional.name }}</h4>
              <span class="badge bg-primary">{{ selectedProfessional.service_type }}</span>
            </div>
            <p v-if="selectedProfessional.description">
              {{ selectedProfessional.description }}
            </p>
            <div class="professional-experience">
              <span class="experience-label">Experience:</span>
              <span class="experience-value">{{ selectedProfessional.experience }} years</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <label for="remarks">Additional Remarks</label>
        <textarea
          id="remarks"
          v-model="formData.remarks"
          class="form-control"
          rows="3"
          placeholder="Any special requirements or instructions..."
        ></textarea>
      </div>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div class="form-actions">
        <button type="button" @click="cancel" class="btn btn-secondary">Cancel</button>
        <button 
          type="submit" 
          class="btn btn-primary" 
          :disabled="submitting || professionals.length === 0 || !formData.professional_id">
          <span v-if="submitting">
            <i class="fas fa-spinner fa-spin"></i> Processing...
          </span>
          <span v-else>
            <i class="fas fa-check"></i> Submit Request
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ServiceRequestForm',
  props: {
    service: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      dateError: null,
      minDateTime: this.getTodayFormatted(),
      formData: {
        service_id: null,
        professional_id: '',
        preferred_date: this.getTomorrowFormatted(),
        remarks: '',
        price: 0
      },
      professionals: [],
      loading: false,
      error: null,
      submitting: false,
      basePrice: 0,
      priceAdjustment: 0
    };
  },
  computed: {
    displayPrice() {
      const totalPrice = parseFloat(this.formData.price);
      return `₹${totalPrice.toFixed(2)}`;
    },
    selectedProfessional() {
      if (!this.formData.professional_id) return null;
      return this.professionals.find(p => p.id === this.formData.professional_id);
    }
  },
  watch: {
    service: {
      immediate: true,
      handler(newService) {
        if (newService && newService.id) {
          this.formData.service_id = newService.id;
          
          // Use confirmedPrice or price property from parent component
          const servicePrice = newService.confirmedPrice || newService.price;
          console.log('Received service price:', servicePrice);
          this.basePrice = parseFloat(servicePrice);
          this.formData.price = parseFloat(servicePrice);
          
          // Reset price adjustment to avoid double counting
          this.priceAdjustment = 0;
          
          this.fetchProfessionals(newService.id);
        }
      }
    },
    priceAdjustment: {
      handler(newValue) {
        // Ensure values are treated as numbers
        const adjustmentValue = parseFloat(newValue) || 0;
        const newTotalPrice = this.basePrice + adjustmentValue;
        
        // Update the form data with the new total price
        this.formData.price = parseFloat(newTotalPrice.toFixed(2));
        console.log('Updated total price:', this.formData.price, 'Base:', this.basePrice, 'Adjustment:', adjustmentValue);
      }
    },
    // Add explicit watch for price changes to ensure it's updated
    'formData.price': {
      handler(newPrice) {
        console.log('Price in formData updated to:', newPrice);
      }
    }
  },
  methods: {
    validatePreferredDate() {
    const selectedDate = new Date(this.formData.preferred_date);
    const today = new Date();
    
    if (selectedDate < today) {
      this.dateError = "Service date cannot be in the past";
      // Reset to tomorrow as default
      this.formData.preferred_date = this.getTomorrowFormatted();
    } else {
      this.dateError = null;
    }
  },
  
  getTodayFormatted() {
    const today = new Date();
    // Format as YYYY-MM-DDThh:mm
    return today.toISOString().slice(0, 16);
  },
    async fetchProfessionals(serviceId) {
      this.loading = true;
      this.error = null;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Not authenticated');
        }
        
        const response = await axios.get(
          `http://127.0.0.1:5000/service/${serviceId}/professionals`, 
          {
            headers: {
              'Authorization': token
            }
          }
        );
        
        this.professionals = response.data.professionals || [];
      } catch (err) {
        console.error('Error fetching professionals:', err);
        this.error = 'Failed to load available professionals. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async submitRequest() {
      this.submitting = true;
      this.error = null;
      
      try {
        const token = sessionStorage.getItem('Authorization');
        if (!token) {
          throw new Error('Not authenticated');
        }
        
        // Ensure price calculation is correct (base + adjustment)
        const calculatedPrice = this.basePrice + parseFloat(this.priceAdjustment || 0);
        const finalPrice = parseFloat(calculatedPrice.toFixed(2));
        
        // Double-check the price is correct before submission
        if (finalPrice !== this.formData.price) {
          console.warn('Price mismatch detected, correcting...');
          this.formData.price = finalPrice;
        }
        
        // Format the preferred date to ISO string
        const formattedData = {
          ...this.formData,
          price: finalPrice, // Explicitly set price to the calculated value
          preferred_date: new Date(this.formData.preferred_date).toISOString()
        };
        
        console.log('Submitting service request with final price:', finalPrice);
        console.log('Price breakdown - Base:', this.basePrice, 'Adjustment:', this.priceAdjustment);
        console.log('Full request data:', formattedData);
        
        // Convert to JSON explicitly to ensure correct data format
        const response = await axios.post(
          'http://127.0.0.1:5000/customer/services',
          formattedData,
          {
            headers: {
              'Authorization': token,
              'Content-Type': 'application/json'
            }
          }
        );
        
        this.$emit('success', {
          message: 'Service request created successfully!',
          requestId: response.data.request_id,
          price: finalPrice // Pass price back to parent component
        });
        
        this.resetForm();
      } catch (err) {
        console.error('Error submitting service request:', err);
        this.error = err.response?.data?.error || 'Failed to submit service request. Please try again.';
        this.$emit('error', this.error);
      } finally {
        this.submitting = false;
      }
    },
    
    resetForm() {
      // Calculate the current total price correctly
      const currentTotal = this.basePrice + parseFloat(this.priceAdjustment || 0);
      
      this.formData = {
        service_id: this.service.id,
        professional_id: '',
        preferred_date: this.getTomorrowFormatted(),
        remarks: '',
        price: parseFloat(currentTotal.toFixed(2)) // Set price to the total
      };
      this.priceAdjustment = 0;
    },
    
    cancel() {
      this.$emit('cancel');
    },
    
    getTomorrowFormatted() {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(9, 0, 0, 0);
      
      // Format as YYYY-MM-DDThh:mm
      return tomorrow.toISOString().slice(0, 16);
    }
  }
};
</script>

<style scoped>
.service-request-form-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
}

.service-request-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 600;
  color: var(--light-color);
}

.form-control {
  padding: 10px;
  border-radius: 5px;
  border: 1px solid var(--border-color, #333);
  background-color: var(--dark-color, #222);
  color: var(--light-color, #eee);
}

.price-display {
  font-size: 1.5rem;
  font-weight: bold;
  color: #f8f9fa;
  padding: 10px;
  border-radius: 5px;
  background-color: #221728;
  border: 2px solid var(--primary-color, #60495A);
  display: inline-block;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.professional-info {
  margin-top: 10px;
  padding: 10px;
  border-radius: 5px;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color, #333);
}

.professional-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.professional-header h4 {
  margin: 0;
  color: var(--light-color, #eee);
}

.professional-experience {
  margin-top: 8px;
  font-size: 0.9rem;
}

.experience-label {
  font-weight: 600;
  margin-right: 5px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-primary {
  background-color: var(--primary-color, #60495A);
  color: white;
}

.btn-primary:disabled {
  background-color: var(--primary-color, #60495A);
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.error-message {
  padding: 10px;
  border-radius: 5px;
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.no-professionals {
  padding: 15px;
  text-align: center;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 5px;
  color: var(--muted-color, #999);
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.bg-primary {
  background-color: var(--primary-color, #60495A);
  color: white;
}

.price-adjustment {
  margin-top: 10px;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.form-range {
  flex: 1;
  height: 8px;
  background: var(--border-color, #333);
  outline: none;
  opacity: 0.7;
  transition: opacity .2s;
  border-radius: 4px;
}

.form-range:hover {
  opacity: 1;
}

.form-range::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #8e67d2;
  cursor: pointer;
  border: 2px solid #f8f9fa;
}

.form-range::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #8e67d2;
  cursor: pointer;
  border: 2px solid #f8f9fa;
}

.slider-value {
  min-width: 60px;
  font-weight: 600;
  color: #f8f9fa;
  background-color: var(--primary-color, #60495A);
  padding: 3px 10px;
  border-radius: 15px;
  text-align: center;
}

.price-breakdown {
  margin-top: 15px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 5px;
  padding: 10px 15px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 0.9rem;
}

.total-price {
  margin-top: 5px;
  font-weight: bold;
  color: var(--primary-color, #60495A);
  font-size: 1.1rem;
}
</style>
