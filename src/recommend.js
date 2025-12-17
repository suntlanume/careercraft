import React, { useState } from 'react';
import axios from 'axios';

function CareerRecommendations({ user }) {
  const [recommendations, setRecommendations] = useState([]);
  
  const fetchRecommendations = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/recommendations', { skills: user.skills });
      setRecommendations(response.data);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  return (
    <div>
      <h2>Career Recommendations for {user.name}</h2>
      <button onClick={fetchRecommendations}>Get Recommendations</button>
      {recommendations.length > 0 && (
        <ul>
          {recommendations.map((rec, index) => (
            <li key={index}>
              <strong>{rec.role}</strong><br />
              <p>Matched Skills: {rec.matched_skills.join(', ')}</p>
              <p>Next Step: {rec.next_step}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default CareerRecommendations;