# Importing the Flask Framework

from modules import *
from flask import *
import database
import configparser


page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
unikey = config['DATABASE']['user']
portchoice = config['FLASK']['port']

#####################################################
##  INDEX
#####################################################

# What happens when we go to our website
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['unikey'] = unikey
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

################################################################################
# Login Page
################################################################################

# This is for the login
# Look at the methods [post, get] that corresponds with form actions etc.
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'unikey' : unikey}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['sid'], request.form['password'])

        # If our database connection gave back an error
        if(val == None):
            flash("""Error with the database connection. Please check your terminal
            and make sure you updated your INI files.""")
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))
        # If it was successful, then we can log them in :)
        session['name'] = val[1]
        session['sid'] = request.form['sid']
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)


################################################################################
# Logout Endpoint
################################################################################

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))


################################################################################
# Transcript Page
################################################################################

@app.route('/transcript')
def transcript():
    transcripts = database.get_transcript(session['sid'])
    
    # What happens if textbooks are null?
    if (transcripts is None):
        # Set it to an empty list and show error message
        transcripts = []
        flash('Error, there are no transcript')
    
    page['title'] = 'Transcript'
    #print(session['sid'])
    return render_template('transcript.html', page=page, session=session, transcripts=transcripts)

################################################################################
# Textbook page
################################################################################

# List the textbook
@app.route('/textbooks')
def list_textbooks():
    # Go into the database file and get the list_textbooks() function
    textbooks = database.list_textbooks()

    # What happens if textbooks are null?
    if (textbooks is None):
        # Set it to an empty list and show error message
        textbooks = []
        flash('Error, there are no list of textbooks')

    page['title'] = 'Textbook'
    return render_template('textbook.html', page=page, session=session, textbooks=textbooks)

################################################################################
# Number of Unit offering page
################################################################################

# List the Number of unit offerings per textbook
@app.route('/num_uof')
def num_uof():
    # Go into the database file and get the list_textbooks() function
    groups = database.group_textbook()

    # What happens if units are null?
    if (groups is None):
        # Set it to an empty list and show error message
        groups = []
        flash('Error, there are no groups of textbook')

    page['title'] = 'UnitOff per Textbook'
    return render_template('group.html', page=page, session=session, groups=groups)

################################################################################
# Search Unit Offerings Based on Textbook
################################################################################

@app.route('/search', methods=['POST', 'GET'])
def search():
    
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        
        # put the textbook name into the result
        session['result'] = request.form['textbook']
        return redirect(url_for('result'))
    else:
        # Else, they're just looking at the page :)
        page['title'] = 'result'
        return render_template('search.html', page=page, session=session)
   
@app.route('/result')
def result():
    # return if there is no search happening yet
    if 'result' not in session:
        return redirect(url_for('search'))
    
    # Go into the database file and get the search_uof() function
    textbook = session['result']
    error, uof = database.search_uof(textbook)
    session.pop('result')
    
    page['title'] = 'result'
    
    # the database return data as normal
    if (error == 0):
        return render_template('result.html', page=page, session=session, uof=uof, textbook=textbook)

    # What happens if there are errors?
    
    # Set it to an empty list, show error message
    # and stay in the form page
    uof = []
    
    
    if (error == -1):
        flash('Error, the input is empty')
    elif (error == -2):
        flash('Error, the input length exceeded the allowed range of 50 characters')
    elif (error == -3):
        flash('Error, there is a problem when fetching the unit offerings from the database')
    elif (error == -4):
        flash('Error, there is a problem with the database connection')
    
    return redirect(url_for('search'))

################################################################################
# Change the textbook of a unit offering
################################################################################

@app.route('/change', methods=['POST', 'GET'])
def change():
    
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        
        # get the fields
        code = request.form['code']
        semester = request.form['semester']
        year = request.form['year']
        new = request.form['new']
        
        # invoke change_textbook method from database
        error = database.change_textbook(code, semester, year, new)
        
        if (error == 0):
            return redirect(url_for('list_textbooks'))
        
        # What happens if there are errors?
        
        # Show the error message and stay in the form page
        if (error == -1):
            flash("Error, there is at least an empty input")
        elif (error == -2):
            flash("Error, the UOS Code exceeded 8 characters")
        elif (error == -3):
            flash("Error, the Semester exceeded 2 characters")
        elif (error == -4):
            flash("Error, the Semester is not S1 or S2")
        elif (error == -5):
            flash("Error, the Year is not an integer")
        elif (error == -6):
            flash("Error, the Year is negative")
        elif (error == -7):
            flash("Error, the Textbook name exceeded 50 characters")
        elif (error == -8):
            flash("Error, there is a problem with database connection")
        elif (error == -9):
            flash("Error, there is a problem when updating the database")
            
        return redirect(url_for('change'))    
        
    else:
        # Else, they're just looking at the page :)
        page['title'] = 'change'
        return render_template('change.html', page=page, session=session)
    
################################################################################
# List the academic staf and their position
################################################################################

@app.route('/extension', methods=['POST', 'GET'])
def extension():
    
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        
        # get the fields
        staff_id = request.form['id']
        position = request.form['pos']
        
        # put the data in the session
        error = database.insert_staff(staff_id, position)
        
        if (error == -1):
            flash("Error, staff position cannot be more than 50 characters")
        elif (error == -2):
            flash("Error, there is a problem with the database connection")
        
        print("|id:{}|position:{}|".format(staff_id, position))
            
        return redirect(url_for('extension'))    
        
    else:
        # Else, they're just looking at the page :)
        
        staffs1 =  database.get_staffs1()
        
        if (staffs1) is None:
            staffs1 = []
        
        staffs2 = database.get_staffs2()
        
        if (staffs2 is None):
            staffs2=[]
            
        page['title'] = 'extension'
        return render_template('extension.html', page=page, session=session, staffs1=staffs1, staffs2=staffs2)


################################################################################
# List Units page
################################################################################

# List the units of study
@app.route('/list-units')
def list_units():
    # Go into the database file and get the list_units() function
    units = database.list_units()

    # What happens if units are null?
    if (units is None):
        # Set it to an empty list and show error message
        units = []
        flash('Error, there are no units of study')
    page['title'] = 'Units of Study'
    return render_template('units.html', page=page, session=session, units=units)


