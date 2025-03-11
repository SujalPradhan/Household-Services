<template>
  <div class="navigation-bar" :class="{ 'vertical': vertical }">
    <div v-if="showBrand" class="nav-brand">
      <i :class="brandIcon" class="brand-icon"></i>
      <h2>{{ brandName }}</h2>
    </div>
    
    <div class="nav-items">
      <router-link 
        v-for="item in items" 
        :key="item.path" 
        :to="item.path" 
        class="nav-item"
        :class="{ 'has-icon': !!item.icon }"
      >
        <i v-if="item.icon" :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </router-link>
    </div>
    
    <div v-if="showActions && actionItems.length > 0" class="nav-actions">
      <button 
        v-for="action in actionItems" 
        :key="action.label" 
        @click="action.handler" 
        class="nav-action-btn"
        :class="action.class || ''"
      >
        <i v-if="action.icon" :class="action.icon"></i>
        <span v-if="action.label">{{ action.label }}</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NavigationBar',
  props: {
    brandName: {
      type: String,
      default: 'App'
    },
    brandIcon: {
      type: String,
      default: 'fas fa-home'
    },
    showBrand: {
      type: Boolean,
      default: true
    },
    items: {
      type: Array,
      required: true
    },
    actionItems: {
      type: Array,
      default: () => []
    },
    showActions: {
      type: Boolean,
      default: true
    },
    vertical: {
      type: Boolean,
      default: false
    }
  }
};
</script>

<style scoped>
.navigation-bar {
  display: flex;
  align-items: center;
  background: linear-gradient(to right, #2F2235 0%, #3F3244 100%);
  padding: 0 20px;
  color: #BFC3BA;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border-bottom: 3px solid #60495A;
  z-index: 100;
  position: sticky;
  top: 0;
  transition: all 0.3s ease;
}

.vertical {
  flex-direction: column;
  height: 100%;
  border-bottom: none;
  border-right: 3px solid #60495A;
  padding: 20px 0;
  width: 250px;
  align-items: stretch;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 0;
}

.vertical .nav-brand {
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  justify-content: center;
}

.brand-icon {
  font-size: 1.8rem;
  color: #60495A;
  background-color: rgba(255, 255, 255, 0.1);
  padding: 8px;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(96, 73, 90, 0.5);
}

.nav-brand h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #BFC3BA;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.nav-items {
  display: flex;
  align-items: center;
  height: 100%;
  flex: 1;
}

.vertical .nav-items {
  flex-direction: column;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0 18px;
  height: 70px;
  color: #BFC3BA;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
  position: relative;
  letter-spacing: 0.3px;
}

.vertical .nav-item {
  height: auto;
  padding: 15px 20px;
  width: 100%;
}

.nav-item i {
  margin-right: 10px;
  font-size: 1.1rem;
  transition: transform 0.3s;
}

.nav-item:hover {
  background-color: rgba(96, 73, 90, 0.3);
  color: white;
}

.nav-item:hover i {
  transform: translateY(-2px);
}

.vertical .nav-item:hover i {
  transform: translateX(2px);
}

.nav-item.router-link-active {
  color: white;
  background-color: rgba(96, 73, 90, 0.2);
}

.nav-item.router-link-active i {
  color: #60495A;
}

.nav-item.router-link-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to right, #60495A, #7e57c2);
}

.vertical .nav-item.router-link-active::after {
  top: 0;
  bottom: 0;
  left: 0;
  right: auto;
  width: 3px;
  height: auto;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vertical .nav-actions {
  flex-direction: column;
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-action-btn {
  background: linear-gradient(135deg, #60495A, #7e57c2);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.vertical .nav-action-btn {
  width: 100%;
  justify-content: center;
}

.nav-action-btn:hover {
  background: linear-gradient(135deg, #70596A, #8e67d2);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.nav-action-btn:active {
  transform: translateY(0);
}

.nav-action-btn.danger {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.nav-action-btn.danger:hover {
  background: linear-gradient(135deg, #f55a4e, #d44637);
}

@media (max-width: 768px) {
  .navigation-bar {
    padding: 10px;
    flex-wrap: wrap;
  }
  
  .nav-brand {
    width: 100%;
    justify-content: center;
    padding: 10px 0;
  }
  
  .nav-items {
    width: 100%;
    overflow-x: auto;
    justify-content: space-between;
    padding: 5px 0;
  }
  
  .nav-item {
    height: 40px;
    padding: 0 12px;
    font-size: 0.85rem;
  }
  
  .nav-actions {
    width: 100%;
    justify-content: center;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .vertical {
    width: 100%;
    height: auto;
  }
}
</style>
