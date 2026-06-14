import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from resume_parser import extract_text, extract_name, extract_contact_info
from skill_extractor import extract_skills, find_missing_skills
from matcher import calculate_match_score
import database
import simulation

app = Flask(__name__)
app.secret_key = 'smartscreen_secret_key' # For session management

# Configure Upload Folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'png', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/candidate', methods=['GET', 'POST'])
def candidate():
    if request.method == 'POST':
        # File handler
        if 'resume' not in request.files:
            return "No file part", 400
        file = request.files['resume']
        
        job_role_select = request.form.get('job_role_select', 'Not Specified')
        job_role_custom = request.form.get('job_role_custom', '').strip()
        job_role = job_role_custom if job_role_select == 'Other' and job_role_custom else job_role_select
        
        job_desc = request.form.get('job_desc', '')
        
        if file.filename == '':
            return "No selected file", 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Logic
            resume_text = extract_text(filepath)
            name = extract_name(resume_text)
            
            score = calculate_match_score(job_desc, resume_text)
            gap_analysis = find_missing_skills(job_desc, resume_text)
            
            skills_found = ", ".join(gap_analysis['res_has_all'])
            missing_skills = ", ".join(gap_analysis['technical'] + gap_analysis['soft'])
            
            # DB insert
            database.insert_candidate(name, score, skills_found, missing_skills, job_role)
            
            # Additional context for Candidate UI 
            extracted_skills = extract_skills(resume_text)['all']
            
            return render_template('result.html',
                                   role="Candidate",
                                   job_role=job_role,
                                   name=name,
                                   score=score,
                                   gap=gap_analysis,
                                   skills_found=skills_found,
                                   extracted_skills=extracted_skills)
                                   
    return render_template('candidate.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = database.verify_user(email, password)
        if user:
            session['user_id'] = user[0]
            session['email'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('recruiter'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/recruiter', methods=['GET', 'POST'])
def recruiter():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        if 'resumes' not in request.files:
            return "No file part", 400
            
        files = request.files.getlist('resumes')
        
        job_role_select = request.form.get('job_role_select', 'Not Specified')
        job_role_custom = request.form.get('job_role_custom', '').strip()
        job_role = job_role_custom if job_role_select == 'Other' and job_role_custom else job_role_select
        
        job_desc = request.form.get('job_desc', '')
        
        results = []
        for file in files:
            if file and allowed_file(file.filename) and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                resume_text = extract_text(filepath)
                name = extract_name(resume_text)
                score = calculate_match_score(job_desc, resume_text)
                gap_analysis = find_missing_skills(job_desc, resume_text)
                
                # Determine Status
                status = "Rejected"
                if score >= 75:
                    status = "Shortlisted"
                elif score >= 60:
                    status = "Consider"

                contact = extract_contact_info(resume_text)
                email = contact['email'] if contact['email'] != "Not Found" else "Email not found"
                phone = contact['phone'] if contact['phone'] != "Not Found" else "Phone not found"
                address = contact['address']
                
                extracted_all = extract_skills(resume_text)
                top_skills = extracted_all['technical'][:5] if extracted_all['technical'] else extracted_all['all'][:5]
                if not top_skills:
                    top_skills = ["Technical skills not identified"]

                results.append({
                    "name": name if name != "Unknown Candidate" else f"Candidate {file.filename[:10]}",
                    "score": round(score),
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "top_skills": top_skills,
                    "photo": f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=random&color=fff&size=128",
                    "matching": gap_analysis['res_has_all'],
                    "missing": gap_analysis['technical'],
                    "weak": gap_analysis['soft'],
                    "status": status,
                    "summary": f"Matches {len(gap_analysis['res_has_all'])} relevant skills from job description."
                })
                # DB insert
                database.insert_candidate(name, score, ", ".join(gap_analysis['res_has_all']), ", ".join(gap_analysis['technical']), job_role)
        
        # Get Job Requirements for Summary
        job_reqs = extract_skills(job_desc)['all']
        
        # Sort results descending
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        return render_template('result.html', 
                               role="Recruiter", 
                               job_role=job_role, 
                               candidates=results,
                               job_requirements=job_reqs)
        
    return render_template('recruiter.html')

@app.route('/dashboard')
def dashboard():
    candidates = database.get_all_candidates()
    return render_template('dashboard.html', candidates=candidates)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    prediction = None
    if request.method == 'POST':
        mass = float(request.form.get('mass', 0))
        height = float(request.form.get('height', 0))
        from ml_model import predict_required_force
        prediction = round(predict_required_force(mass, height), 4)
    return render_template('analyze.html', prediction=prediction)

@app.route('/theory')
def theory():
    return render_template('theory.html')

@app.route('/simulate', methods=['GET', 'POST'])
def simulate():
    if request.method == 'POST':
        mass = float(request.form.get('mass', 0))
        distance = float(request.form.get('distance', 0))
        opposing_force = float(request.form.get('opposing_force', 0))
        
        gravity_force = simulation.calculate_gravity(mass, distance)
        lifts = simulation.check_lift(gravity_force, opposing_force)
        
        result_text = "OBJECT LIFTS" if lifts else "GRAVITY WINS (OBJECT STAYS)"
        graph_path = simulation.generate_graph(mass, distance, opposing_force)
        
        return render_template('results.html',
                               mass=mass,
                               distance=distance,
                               gravity_force=round(gravity_force, 4),
                               opposing_force=opposing_force,
                               result=result_text,
                               graph_path=graph_path)
    return render_template('simulate.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
