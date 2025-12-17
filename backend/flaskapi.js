@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    user_skills = request.json.get('skills', [])
    recommendations = []
    
    for career in CareerRecommendation.query.all():
        matched_skills = set(user_skills).intersection(set(career.skills_required.split(',')))
        if matched_skills:
            recommendations.append({
                "role": career.role,
                "skills_required": career.skills_required.split(','),
                "next_step": career.next_step,
                "matched_skills": list(matched_skills)
            })
    
    return jsonify(recommendations)

