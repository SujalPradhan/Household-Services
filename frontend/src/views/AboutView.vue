<template>
  <div class="about-page">
    <div class="container">
      <div class="about-content">
        <h1 class="about-title">About UrbanAid</h1>
        
        <div class="about-section">
          <div class="about-image">
            <img src="@/assets/images/about.jpg" alt="About UrbanAid" onerror="this.src='https://via.placeholder.com/500x300?text=UrbanAid'">
          </div>
          <div class="about-text">
            <h2>Our Mission</h2>
            <p>At UrbanAid, we're committed to connecting homeowners with skilled professionals to handle all their household service needs. Our platform makes it easy to find reliable, vetted service providers for cleaning, repairs, gardening, and more.</p>
            
            <h2>Our Story</h2>
            <p>Founded in 2023, UrbanAid began with a simple idea: make household services accessible, reliable, and stress-free. What started as a small network of local professionals has grown into a comprehensive platform serving thousands of customers.</p>
            
            <h2>Our Values</h2>
            <ul>
              <li><strong>Quality:</strong> We only partner with the best service providers who meet our high standards.</li>
              <li><strong>Reliability:</strong> Count on us to deliver services on time, every time.</li>
              <li><strong>Transparency:</strong> No hidden fees or surprises - just honest, upfront pricing.</li>
              <li><strong>Customer-First:</strong> Your satisfaction is our top priority.</li>
            </ul>
          </div>
        </div>
        
        <div class="team-section">
          <h2>Our Leadership Team</h2>
          <div class="team-grid">
            <div class="team-member">
              <div class="member-image">
                <img src="https://via.placeholder.com/150?text=CEO" alt="CEO">
              </div>
              <h3>John Doe</h3>
              <p class="position">Chief Executive Officer</p>
              <p>With over 15 years in the service industry, John leads our company vision and strategy.</p>
            </div>
            <div class="team-member">
              <div class="member-image">
                <img src="https://via.placeholder.com/150?text=COO" alt="COO">
              </div>
              <h3>Jane Smith</h3>
              <p class="position">Chief Operations Officer</p>
              <p>Jane ensures smooth service delivery and manages our network of service professionals.</p>
            </div>
            <div class="team-member">
              <div class="member-image">
                <img src="https://via.placeholder.com/150?text=CTO" alt="CTO">
              </div>
              <h3>David Wilson</h3>
              <p class="position">Chief Technology Officer</p>
              <p>David oversees our platform technology and continuous innovation.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AboutView'
};
</script>

<style scoped>
.about-page {
  padding: 40px 0;
}

.about-content {
  background-color: #3F3244;
  border-radius: 10px;
  padding: 30px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.about-title {
  font-size: 2.5rem;
  color: #BFC3BA;
  margin-bottom: 40px;
  text-align: center;
  position: relative;
}

.about-title::after {
  content: '';
  position: absolute;
  bottom: -15px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background-color: #60495A;
}

.about-section {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  margin-bottom: 50px;
}

.about-image {
  flex: 1 1 300px;
}

.about-image img {
  width: 100%;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.2);
}

.about-text {
  flex: 2 1 500px;
}

.about-text h2 {
  color: #BFC3BA;
  margin-top: 20px;
  margin-bottom: 15px;
  font-size: 1.8rem;
}

.about-text p {
  color: #BFC3BA;
  line-height: 1.7;
  margin-bottom: 20px;
}

.about-text ul {
  padding-left: 20px;
}

.about-text li {
  color: #BFC3BA;
  margin-bottom: 10px;
}

.team-section {
  margin-top: 60px;
}

.team-section h2 {
  color: #BFC3BA;
  font-size: 2rem;
  text-align: center;
  margin-bottom: 40px;
}

.team-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 30px;
}

.team-member {
  background-color: #2F2235;
  border-radius: 10px;
  padding: 25px;
  flex: 1 1 300px;
  max-width: 350px;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  transition: transform 0.3s ease;
}

.team-member:hover {
  transform: translateY(-10px);
}

.member-image {
  width: 150px;
  height: 150px;
  margin: 0 auto 20px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #60495A;
}

.member-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.team-member h3 {
  color: #BFC3BA;
  margin-bottom: 5px;
}

.position {
  color: #A9ACA9;
  font-style: italic;
  margin-bottom: 15px;
}

@media (max-width: 768px) {
  .about-section {
    flex-direction: column;
  }
  
  .about-image {
    order: -1;
  }
  
  .team-member {
    max-width: 100%;
  }
  
  .about-title {
    font-size: 2rem;
  }
}
</style>
