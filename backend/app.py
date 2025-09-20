from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql.cursors
import os
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing

# --- Flask App Initialization ---
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend')
app.secret_key = 'e685fccd7ba3abba2fb269cf1cf82c4799257080a2a2da80' # REPLACE THIS

# Google reCAPTCHA Keys (from reCAPTCHA Admin Console)
app.config['6LepopMrAAAAAAKoGFh225kzQj1GmSgO2wQVjtiX'] = 'YOUR_RECAPTCHA_SITE_KEY_HERE' # REPLACE THIS
app.config['6LepopMrAAAAAFkQU5F4T-w4n-ltSGjDfoQM6H3r'] = 'YOUR_RECAPTCHA_SECRET_KEY_HERE' # REPLACE THIS

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', # Your MySQL username
    'password': '@Jbobby1', # IMPORTANT: Your actual MySQL root password!
    'db': 'online_voting_system', # The database name you created in Day 2
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor # This makes query results return as dictionaries
}

# Function to get a database connection
def get_db_connection():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to database: {e}")
        flash('Database connection error. Please try again later.')
        return None

# --- Routes Start Here ---

# Home Page Route (Now includes Admin Login link)
@app.route('/')
def index():
    return render_template('index.html')
# Voter Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        aadhar = request.form['aadhar']
        place_name = request.form['place_name']
        password = request.form['password']

        # Basic input validation
        if not (name and aadhar and place_name and password):
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))

        if not aadhar.isdigit() or len(aadhar) != 12:
            flash('Aadhar number must be 12 digits.', 'error')
            return redirect(url_for('register'))

        # CAPTCHA Verification
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            flash('Please complete the CAPTCHA verification.', 'error')
            return redirect(url_for('register'))

        recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
        recaptcha_data = {
            'secret': app.config['RECAPTCHA_SECRET_KEY'],
            'response': recaptcha_response
        }

        import requests  # Ensure 'requests' is installed
        try:
            r = requests.post(recaptcha_verify_url, data=recaptcha_data)
            recaptcha_result = r.json()
            if not recaptcha_result.get('success'):
                flash('CAPTCHA verification failed. Please try again.', 'error')
                return redirect(url_for('register'))
        except requests.exceptions.RequestException as e:
            flash('CAPTCHA service unavailable. Please try again later.', 'error')
            print(f"reCAPTCHA Request Error: {e}")
            return redirect(url_for('register'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # DB operations
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql_check_aadhar = "SELECT voter_id FROM Voters WHERE aadhar_number = %s"
                    cursor.execute(sql_check_aadhar, (aadhar,))
                    existing_voter = cursor.fetchone()

                    if existing_voter:
                        flash('Aadhar number already registered. Please login or use a different Aadhar.', 'error')
                        return redirect(url_for('register'))

                    sql_check_place = "SELECT place_id FROM Places WHERE place_name = %s"
                    cursor.execute(sql_check_place, (place_name,))
                    place = cursor.fetchone()

                    place_id = None
                    if place:
                        place_id = place['place_id']
                    else:
                        cursor.execute("INSERT INTO Places (place_name) VALUES (%s)", (place_name,))
                        connection.commit()
                        place_id = cursor.lastrowid

                    if not place_id:
                        flash('Could not determine or create place. Registration failed.', 'error')
                        return redirect(url_for('register'))

                    sql_insert_voter = """
                        INSERT INTO Voters (name, aadhar_number, password_hash, place_id)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert_voter, (name, aadhar, hashed_password, place_id))
                    connection.commit()

                    flash('Registration successful! Please login.', 'success')
                    return redirect(url_for('voter_login'))

            except pymysql.Error as e:
                connection.rollback()
                flash(f'An error occurred during registration: {e}', 'error')
                print(f"Registration Error: {e}")
            finally:
                connection.close()

    return render_template('register.html', config=app.config)


# Voter Login Route
@app.route('/voter_login', methods=['GET', 'POST'])
def voter_login():
    if request.method == 'POST':
        aadhar_or_name = request.form['aadhar_or_name']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Try to find voter by Aadhar number or Name
                    sql = "SELECT voter_id, name, password_hash, has_voted FROM Voters WHERE aadhar_number = %s OR name = %s"
                    cursor.execute(sql, (aadhar_or_name, aadhar_or_name))
                    voter = cursor.fetchone()

                    # Here's the core login check for voters:
                    # 1. Check if a voter was found.
                    # 2. Use check_password_hash to securely compare the entered password with the stored hash.
                    if voter and check_password_hash(voter['password_hash'], password):
                        # Set session variables for the logged-in voter
                        session['user_id'] = voter['voter_id']
                        session['username'] = voter['name']
                        session['is_admin'] = False # This user is not an admin
                        session['has_voted'] = bool(voter['has_voted']) # Store their voting status
                        flash(f'Welcome, {voter["name"]}! Logged in successfully.', 'success')
                        return redirect(url_for('voter_dashboard')) # Redirect to voter's dashboard
                    else:
                        flash('Invalid Aadhar/Name or password.', 'error')
            except pymysql.Error as e:
                flash(f'An error occurred during login: {e}', 'error')
                print(f"Voter Login Error: {e}")
            finally:
                if connection:
                    connection.close()
    # For GET requests (to display the form) or if POST fails
    return render_template('voter_login.html')

# Voter Dashboard Route (UPDATED for Day 4 - fetches candidates)
@app.route('/voter_dashboard')
def voter_dashboard():
    # Ensure only logged-in voters can access this page
    if 'user_id' not in session or session['is_admin']:
        flash('Please log in as a voter to access the dashboard.', 'error')
        return redirect(url_for('voter_login'))

    connection = get_db_connection() # Get a database connection
    candidates = [] # Initialize an empty list to hold candidate data
    if connection: # Check if connection was successful
        try:
            with connection.cursor() as cursor:
                # SQL query to fetch all candidates from the Candidates table
                sql = "SELECT candidate_id, name, party_name, symbol_url FROM Candidates ORDER BY party_name, name"
                cursor.execute(sql) # Execute the query
                candidates = cursor.fetchall() # Fetch all results as dictionaries
        except pymysql.Error as e:
            flash(f'Error loading candidates: {e}', 'error')
            print(f"Candidate Load Error: {e}")
        finally:
            if connection:
                connection.close() # Always close the connection

    # Render the voter_dashboard.html template, passing the fetched candidates
    # and the voter's has_voted status from the session (for showing/hiding form)
    return render_template('voter_dashboard.html', candidates=candidates, has_voted=session.get('has_voted', False))

# Vote Casting Route (NEW for Day 4 - handles vote submission)
@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    # Ensure only logged-in voters can cast a vote
    if 'user_id' not in session or session['is_admin']:
        flash('Please log in as a voter to cast a vote.', 'error')
        return redirect(url_for('voter_login'))

    # Quick check from session if voter has already voted (avoids DB query for already known state)
    if session.get('has_voted', False):
        flash('You have already cast your vote.', 'info')
        return redirect(url_for('voter_dashboard'))

    voter_id = session['user_id']
    candidate_id = request.form.get('candidate_id') # Get the selected candidate ID from the form

    if not candidate_id:
        flash('Please select a candidate to vote for.', 'error')
        return redirect(url_for('voter_dashboard'))

    connection = get_db_connection()
    if connection:
        try:
            # Start a transaction to ensure both INSERT and UPDATE operations succeed or fail together.
            connection.begin() # Start the transaction
            with connection.cursor() as cursor:
                # Double-check has_voted in DB (more reliable than session alone for race conditions)
                # FOR UPDATE clause locks the row to prevent concurrent updates from other sessions
                sql_check_voted_db = "SELECT has_voted FROM Voters WHERE voter_id = %s FOR UPDATE"
                cursor.execute(sql_check_voted_db, (voter_id,))
                voter_status_db = cursor.fetchone()

                if voter_status_db and voter_status_db['has_voted']:
                    flash('You have already cast your vote.', 'info')
                    connection.rollback() # Rollback the transaction as vote is already cast
                    return redirect(url_for('voter_dashboard'))

                # 1. Record the vote in the Votes table
                sql_insert_vote = "INSERT INTO Votes (voter_id, candidate_id) VALUES (%s, %s)"
                cursor.execute(sql_insert_vote, (voter_id, candidate_id))

                # 2. Update the voter's has_voted status in the Voters table to TRUE
                sql_update_voter_status = "UPDATE Voters SET has_voted = TRUE WHERE voter_id = %s"
                cursor.execute(sql_update_voter_status, (voter_id,))

                connection.commit() # Commit both operations together
                session['has_voted'] = True # Update session variable too, for immediate UI feedback
                flash('Your vote has been successfully cast. Thank you!', 'success')
                return render_template('thank_you.html') # Redirect to thank you page

        except pymysql.IntegrityError as e: # This handles UNIQUE constraint violations on voter_id in Votes table
            connection.rollback() # Rollback the transaction
            if "Duplicate entry" in str(e) and "voter_id" in str(e):
                flash('You have already cast your vote. Duplicate entry detected in database.', 'info')
            else:
                flash(f'An integrity error occurred: {e}', 'error')
                print(f"Vote Integrity Error: {e}")
        except pymysql.Error as e: # Catch any other database errors
            connection.rollback() # Rollback the transaction
            flash(f'An error occurred while casting your vote: {e}', 'error')
            print(f"Vote Casting Error: {e}")
        finally:
            if connection:
                connection.close() # Always close the database connection

    flash('An unexpected error occurred while processing your vote.', 'error')
    return redirect(url_for('voter_dashboard'))


# Logout Route (for both voters and admins)
@app.route('/logout')
def logout():
    # Clear all session variables
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    session.pop('has_voted', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index')) # Redirect to the home page

# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT admin_id, username, password_hash FROM Admins WHERE username = %s"
                    cursor.execute(sql, (username,))
                    admin = cursor.fetchone()

                    # Here's the core login check for admins:
                    # 1. Check if an admin was found.
                    # 2. Use check_password_hash to securely compare the entered password with the stored hash.
                    # This relies on you having updated admin password_hash values to actual hashes in DB.
                    if admin and check_password_hash(admin['password_hash'], password):
                        # Set session variables for the logged-in admin
                        session['user_id'] = admin['admin_id']
                        session['username'] = admin['username']
                        session['is_admin'] = True # This user IS an admin
                        flash(f'Welcome, {admin["username"]}! Admin logged in successfully.', 'success')
                        return redirect(url_for('admin_dashboard')) # Redirect to admin dashboard
                    else:
                        flash('Invalid username or password.', 'error')
            except pymysql.Error as e:
                flash(f'An error occurred during login: {e}', 'error')
                print(f"Admin Login Error: {e}")
            finally:
                if connection:
                    connection.close()
    # For GET requests (to display the form) or if POST fails
    return render_template('admin_login.html')
@app.route('/admin/reset_election', methods=['POST'])
def reset_election():
    # Ensure only logged-in admins can access this function
    if 'user_id' not in session or not session['is_admin']:
        flash('Access denied. Only administrators can reset the election.', 'error')
        return redirect(url_for('admin_login'))

    connection = get_db_connection()
    if connection:
        try:
            connection.begin() # Start a transaction for atomicity
            with connection.cursor() as cursor:
                # 1. Delete all records from the Votes table
                sql_delete_votes = "DELETE FROM Votes"
                cursor.execute(sql_delete_votes)

                # 2. Reset the has_voted flag for all voters to FALSE
                sql_reset_voters = "UPDATE Voters SET has_voted = FALSE"
                cursor.execute(sql_reset_voters)

                connection.commit() # Commit both operations
                flash('Election data successfully reset!', 'success')
        except pymysql.Error as e:
            connection.rollback() # Rollback on error
            flash(f'An error occurred during election reset: {e}', 'error')
            print(f"Election Reset Error: {e}")
        finally:
            if connection:
                connection.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    # Check if user is logged in AND is an admin
    if 'user_id' not in session or not session['is_admin']:
        flash('Please log in as an admin to access the dashboard.', 'error')
        return redirect(url_for('admin_login'))

    connection = get_db_connection()
    total_votes = 0
    party_results = [] # Overall party-wise results
    places = []        # List of all places for the filter dropdown
    place_results = [] # Party-wise results for a selected place
    selected_place_id = request.args.get('place_id', type=int) # Get 'place_id' from URL query parameter
    selected_place_name = "All Places" # Default display for selected place

    if connection:
        try:
            with connection.cursor() as cursor:
                # 1. Fetch total votes cast across the entire system
                sql_total_votes = "SELECT COUNT(*) AS total_count FROM Votes"
                cursor.execute(sql_total_votes)
                total_votes = cursor.fetchone()['total_count']

                # 2. Fetch party-wise results (overall, not per candidate)
                # This joins Votes with Candidates to group by party_name
                sql_party_results = """
                    SELECT C.party_name, COUNT(V.vote_id) AS vote_count
                    FROM Votes AS V
                    JOIN Candidates AS C ON V.candidate_id = C.candidate_id
                    GROUP BY C.party_name
                    ORDER BY vote_count DESC
                """
                cursor.execute(sql_party_results)
                party_results = cursor.fetchall() # Fetch all results

                # 3. Fetch all places for the filter dropdown
                sql_places = "SELECT place_id, place_name FROM Places ORDER BY place_name"
                cursor.execute(sql_places)
                places = cursor.fetchall()

                # 4. Fetch place-wise results if a specific place is selected in the filter
                if selected_place_id:
                    # Get the name of the selected place for display
                    sql_selected_place_name = "SELECT place_name FROM Places WHERE place_id = %s"
                    cursor.execute(sql_selected_place_name, (selected_place_id,))
                    name_row = cursor.fetchone()
                    if name_row:
                        selected_place_name = name_row['place_name']

                    # Query for party-wise results within the selected place
                    sql_place_results = """
                        SELECT C.party_name, COUNT(Vo.vote_id) AS vote_count
                        FROM Votes AS Vo
                        JOIN Candidates AS C ON Vo.candidate_id = C.candidate_id
                        JOIN Voters AS Vr ON Vo.voter_id = Vr.voter_id
                        WHERE Vr.place_id = %s
                        GROUP BY C.party_name
                        ORDER BY vote_count DESC
                    """
                    cursor.execute(sql_place_results, (selected_place_id,))
                    place_results = cursor.fetchall() # Fetch results for the specific place

        except pymysql.Error as e:
            flash(f'Error loading results: {e}', 'error')
            print(f"Admin Dashboard Error: {e}")
        finally:
            if connection:
                connection.close()

        # Render the admin dashboard template, passing all collected data
        return render_template(
            'admin_dashboard.html',
            total_votes=total_votes,
            party_results=party_results,
            places=places,
            selected_place_id=selected_place_id, # Pass back to pre-select dropdown
            selected_place_name=selected_place_name,
            place_results=place_results
        )

    # If not an admin or not logged in, redirect to admin login
    flash('Please log in as an admin to access the dashboard.', 'error')
    return redirect(url_for('admin_login'))

# --- Run the Flask Application ---
if __name__ == '__main__':
    app.run(debug=True) # THIS LINE IS LIKELY NOT INDENTED OR INDENTED INCORRECTLY