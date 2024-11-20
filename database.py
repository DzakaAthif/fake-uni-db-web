#!/usr/bin/env python3

from modules import pg8000
import configparser


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        '''
        This is doing a couple of things in the back
        what it is doing is:

        connect(database='y12i2120_unikey',
            host='soit-db-pro-2.ucc.usyd.edu.au,
            password='password_from_config',
            user='y19i2120_unikey')
        '''
        connection = pg8000.connect(database=config['DATABASE']['db'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    # Return the connection to use
    return connection


################################################################################
# Login Function
#   - This function performs a "SELECT" from the database to check for the
#       student with the same unikey and password as given.
#   - Note: This is only an exercise, there's much better ways to do this
################################################################################

def check_login(sid, pwd):
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                 FROM unidb.student
                 WHERE studid=%s AND password=%s"""
        cur.execute(sql, (sid, pwd))
        r = cur.fetchone()              # Fetch the first row
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error Invalid Login")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


################################################################################
# List Units
#   - This function performs a "SELECT" from the database to get the unit
#       of study information.
#   - This is useful for your part when we have to make the page.
################################################################################

def list_units():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uosCode, uosName, credits, year, semester
                        FROM UniDB.UoSOffering JOIN UniDB.UnitOfStudy USING (uosCode)
                        ORDER BY uosCode, year, semester""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


################################################################################
# Get transcript function
#   - Your turn now!
#   - What do you have to do?
#       1. Connect to the database and set up the cursor.
#       2. You're given an SID - get the transcript for the SID.
#       3. Close the cursor and the connection.
#       4. Return the information we need.
################################################################################

def get_transcript(sid):
    
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        sql = """SELECT uosCode, uosName, credits, year, semester, grade
                        FROM UniDB.Transcript JOIN UniDB.UnitOfStudy USING (uosCode)
                        WHERE studid=%s
                        ORDER BY uosCode, year, semester"""
        params = (sid,)
        cur.execute(sql, params)
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching transcript from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# List Textbooks
################################################################################

def list_textbooks():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT uosCode, semester, year, uosName, textbook
                        FROM UniDB.UoSOffering JOIN UniDB.UnitOfStudy USING (uosCode)
                        ORDER BY uosCode, year, semester""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# Group Textbooks
################################################################################

def group_textbook():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT textbook, COUNT(*)
                        FROM UniDB.UoSOffering
                        GROUP BY textbook
                        ORDER BY textbook""")
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching group textbook from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

################################################################################
# Search Unit Offering Based on a Textbook
################################################################################

def search_uof(textbook):
    
    # check if the input is empy
    # Actually the website form itself would not allow a user to submit
    # and empy textbook name since the form is a required form.
    # however, we just checked again just in case.
    if (textbook is None):
        return (-1, None);
    
    # check if textbook length is at most 50 (sql restriction)
    if (len(textbook) > 50):
        return (-2, None)
    
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return (-4, None)
    
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        sql = """SELECT uosCode, semester, year, uosName
                    FROM UniDB.UoSOffering JOIN UniDB.UnitOfStudy USING (uosCode)
                    WHERE textbook=%s
                    ORDER BY uosCode, year, semester"""
        cur.execute(sql, (textbook,))
        val = cur.fetchall()
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching unit offerings from database")
        return (-3, Val)

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return (0, val)

################################################################################
# Change the textbook of a unit offering
################################################################################

def change_textbook(code, semester, year, new):
    
    # check if the input is empty
    if (code is None or semester is None or year is None or new is None):
        return -1
    
    # check if code is at most 8 char length
    if (len(code) > 8):
        return -2
    
    # check if semester is at most 2 char length
    if (len(semester) > 2):
        return -3
    
    # check if the format of semester is correct
    if (semester[0] != 'S' or int(semester[1]) > 2):
        return -4
    
    
    try:
        # check if the year is negative
        if (int(year) < 0):
            return -6
    except:
        # if it fails its not an integer
        return -5
    
    # check if the new textbook name is at most 50 char length
    if (len(new) > 50):
        return -7
    
    
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return -8
    
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        sql = """UPDATE UniDB.UoSOffering 
                    SET textbook = %s
                    WHERE uosCode = %s
                    AND semester = %s
                    AND year = %s"""
        cur.execute(sql, (new, code, semester, int(year)))
        conn.commit()
        
    except:
        print("Error updating the textbook in database")
        return -9

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return 0

################################################################################
# Get the list of staffs
################################################################################

def insert_staff(staff_id, pos):
    
    # sanitizing here
    if len(pos) > 50:
        return -1
    
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return -2
    
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        sql = """INSERT INTO UniDb.DepPosition(staffId, pos)
                    VALUES (%s, %s)"""
        
        cur.execute(sql, (staff_id, pos))
        conn.commit()
        
    except:
        print("Error inserting the staf position in database")
        return -2

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return 0

def get_staffs1():
    
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        sql = """SELECT id, name
                    FROM UniDB.AcademicStaff
                    WHERE id NOT IN (SELECT staffId FROM UniDB.DepPosition)
                    ORDER BY Id, name"""
        
        cur.execute(sql)  
        val = cur.fetchall()
        
    except:
        print("Error fetching the staffs1 from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

def get_staffs2():
    
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        sql = """SELECT staffId, name, pos
                    FROM UniDB.AcademicStaff INNER JOIN UniDB.DepPosition ON (id=staffId)
                    ORDER BY staffId, name"""

        cur.execute(sql)
        val = cur.fetchall()
        
    except:
        print("Error fetching the staffs2 from database")

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val

#####################################################
#  Python code if you run it on it's own as 2tier
#####################################################


if (__name__ == '__main__'):
    print("{}\n{}\n{}".format("=" * 50, "Welcome to the 2-Tier Python Database", "=" * 50))
    print("""
This file is to interact directly with the database.
We're using the unidb (make sure it's in your database)

Try to execute some functions:
check_login('3070799133', 'random_password')
check_login('3070088592', 'Green')
list_units()""")

