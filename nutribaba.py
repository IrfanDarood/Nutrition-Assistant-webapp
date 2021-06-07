# Hello Folks!
# this is the python file which contains all the app routes and web app functionalities

# these are the imports

from flask import Flask, render_template, request, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import json
import requests
from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import hashlib
import plotly
import plotly.graph_objs as go

# setting up Flask and database connection credentials.
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'kFODHuq1oX'
app.config['MYSQL_PASSWORD'] = 'dsc8nkk0S8'
app.config['MYSQL_DB'] = 'kFODHuq1oX'
mysql = MySQL(app)
app.secret_key = 'a'


# Below are the app routes, which are resposible to perform operations and render next html page with a message, when user clicks something in the web app to navigate to any other place.

# Home page route .
@app.route('/')
def home():
    return render_template('index.html')


# Registration page route

@app.route('/register')
def register():
    return render_template('register.html')


# when a user sign up by filling user details, this route is called in the html page using POST method and
# data is stored into the remote database

@app.route('/uploaddata', methods=['GET', 'POST'])
def uploaddata():
    msg = ''

    # checking whether the data came from the webapp registration  form with method POST

    if request.method == 'POST':
        name = request.form['username']
        email = request.form['emailaddress']
        pword = request.form['pword']
        cpword = request.form['confirmPassword']

        # Password and Confirm Password must be same before the get entered into the database

        if pword == cpword:

            # Before saving password into the database, it is hashed using MD5 hashing method for data security.
            pword = hashlib.md5(pword.encode())

            # we store the hexa decimal form of the hashed password into the database.
            pword = pword.hexdigest()

            # creating a connection with the database and checking whether the user is a new user or has already registered before.
            # if any entry with the entered mail address already exists in the database, a new entry for the same mail will not be done
            cursor = mysql.connection.cursor()
            cursor.execute(
                'SELECT * FROM userdetails WHERE email= % s', (email,))
            mysql.connection.commit()
            userexist = cursor.fetchone()
            if userexist != None:
                msg = 'User with this Email already exist. Please Login'
                return render_template('register.html', msg=msg)

            # if there is no matching entry in the database, only then a new entry is done into the database creating a new user.
            else:
                cursor = mysql.connection.cursor()
                cursor.execute(
                    'INSERT INTO userdetails VALUES (% s, % s, % s)', (name, email, pword))
                mysql.connection.commit()
                msg = 'You have successfully registered !'
                return render_template('login.html', msg=msg)

# Login page route


@app.route('/login')
def login():
    return render_template('login.html')

# Authentication for the login.


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():

    # checking whether the data came from the webapp login form with method POST
    if request.method == 'POST':
        email = request.form['emailaddress']
        pword = request.form['pword']

        # checking whether the user has registered before logging in or not.
        # if there is no entry with the entered mail in the database then the user did not register to the webapp.
        # Login will fail providing the appropriate message to the user.
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM userdetails WHERE email= % s', (email,))
        mysql.connection.commit()
        userexist = cursor.fetchone()
        if userexist == None:
            msg = 'User with this Email doesn\'t exist. Please Sign-up before Login'
            return render_template('login.html', msg=msg)

        # if the user already registered then his credentials will be checked further.
        # converting the password to the hashed hexa decimal form to compare with the password present in the database.
        pword = hashlib.md5(pword.encode())
        pword = pword.hexdigest()

        # if the user login details are correct then the below sql query will result in one row.
        cursor.execute(
            'SELECT * FROM userdetails WHERE email= % s and pword = % s', (email, pword))
        mysql.connection.commit()
        data = cursor.fetchone()

        # if there is no data in the database with this email "none" will be returned
        if data == None:
            data = 'INCORRECT DETAILS'
            return render_template('login.html', msg=data)

        # if a row of data is returned then user login credentials are correct, authentication is successfull.
        else:

            # session variable is created to check whether user is logged in or not when he tries to access other features of the webapp.
            session["email"] = email
        print("data", data)
    return render_template('index.html')

# app route to the track food page where user will check nutrients in their food.


@app.route('/trackfood')
def trackfood():
    return render_template('trackfood.html')

# route to the terms and conditions


@app.route('/termsconditions')
def termsconditions():
    return render_template('TermsConditions.html')

# route to logout. The session variable is deleted when the user logs out


@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')

# Now this is the main part of the webapp
# Here the user uploads the image and a list of nutrients is resulted.
# This webapp uses two APIs to get all the nutritional content of a food item. ('IBM Watson Visual-recognition API' and 'USDA Food Central API').


@app.route('/upload_img', methods=['GET', 'POST'])
def upload_img():

    # Checking whether data came from the trackfood form using method POST.
    if request.method == 'POST':

        # saving the uploaded image into a variable img.
        img = request.files['foodimg']

        # this is the path where i want to store the image.
        pathname = './static/'+session['email']+'.jpg'

        # saving the image at the above path/location.
        img.save(pathname)

        # Using ibm watson visualrecognition API to identify the fooditem (This API is going to depricate in dec 2021, I need to look for an alternative.)
        # authenticating to the API using the API key.
        authenticator = IAMAuthenticator(
            'P4KdTbcPJhm8pxf2_JQHclANOs-7Inhu8hMenVX88t_M')
        visual_recognition = VisualRecognitionV3(
            version='2018-03-19',
            authenticator=authenticator
        )
        try:
            # Setting up the API url
            visual_recognition.set_service_url(
                'https://api.us-south.visual-recognition.watson.cloud.ibm.com/instances/341d2fd2-3d4b-4a9f-a216-f413be52fc73')

            # sending the image uploaded by the user to the visual recognition api to recognize the food item.
            with open(pathname, 'rb') as images_file:
                classes = visual_recognition.classify(
                    images_file=images_file,
                    classifier_ids=["food"]).get_result()

            # Now if the uploaded image contains a valid food, then API will result a JSON file with the name of the food else it will return with the food name as 'NON FOOD'
            # Saving the food name in a variable fooditem using the resultant json file 'classes'.
            fooditem = classes['images'][0]['classifiers'][0]['classes'][0]['class']

        # If an error occurs in the API call then no data is sent to the html page to display.
        except:
            return render_template('trackfood.html', msg=0)

        # If the uploaded food image has no valid food item in it then the below condition becomes true.
        if fooditem.lower() == 'non-food':
            # I am using this below structure i.e, dictionaries in a dictionary to send data to the html page.
            # In the html page this sturcture is checked for the food item name and other details, this will also help in iterating nutrient list.
            # Now here as the food name in non food no nutrients are sent and the name of fooditem in the dictionary is set not NON FOOD.
            allnutrients = {'meta': {}, 'Essentials': {}, 'Minerals': {
            }, 'Vitamins': {}, 'Fattyacids': {}, 'Carotenoids': {}}

            # Initiallising the food item name in the dictionary with the fooditem name recognized , NON FOOD in this case.
            allnutrients['meta']['fooditem'] = fooditem.upper()
            allnutrients['meta']['nutrients'] = 0
            return render_template('trackfood.html', msg=allnutrients)
        else:

            # using USDA API to get the nutrients of the food item
            # Requesting the api through the url, specifing fooditem name, no of pages required(one page = set of nutrients present in the same food at one region)
            # and the API key for authentication

            nutrients = requests.get('https://api.nal.usda.gov/fdc/v1/foods/search?query={}&pageSize={}&api_key={}'.format(
                fooditem, '1', 'wNxP2RfBXrx3amU5HypuuEWUtSSgeRErZMcU5LFA'))
            # loading the json file into a variable data.
            data = json.loads(nutrients.text)
            # Creating a dictionary which has multiple dictionaries within to structure the data before sending to the html page to get displayed
            allnutrients = {'meta': {}, 'Essentials': {}, 'Minerals': {
            }, 'Vitamins': {}, 'Fattyacids': {}, 'Carotenoids': {}}

            # the below lists are used to create a pie chart
            # the reason why i am creating these two lists while i still have the same data saved in the above dictionary is :
            # creating a pie chart requires labels and their integer values but the above dictionary saves values in string format just to concatinate value with units resulted in the json file.
            # i could have used the dictioanary values by type casting them to integers, but iterating into the dictionary and typecasting values everytime
            # takes a lot of computation. so i decided to create two lists which will be used to create the piechart
            # i should have gone for a better structure and still didn't do that yet.
            # I'm a terrible person!
            # if you find a better way, don't forget to share ;)

            label = []
            value = []
            n = len(data['foods'][0]['foodNutrients'])
            allnutrients['meta']['fooditem'] = fooditem.upper()
            allnutrients['meta']['nutrients'] = n
            fattyacids = ['SFA', 'MUFA', 'PUFA']
            allnutrients['Minerals']['total'] = 0
            allnutrients['Vitamins']['total'] = 0
            allnutrients['Fattyacids']['total'] = 0
            allnutrients['Carotenoids']['total'] = 0
            for i in range(0, n):
                # the below code will group all the fatty acids together.
                if(any([substring in (data['foods'][0]['foodNutrients'][i]['nutrientName']) for substring in fattyacids])):
                    allnutrients['meta']['nutrients'] -= 1
                    continue
                # in the json file, I noticed that the nutrients were indexed using an integer variable 'nutrientNumber', and also all the nutrients were categorized
                # into ranges of numbers i.e, nutrients between 300 to 317 were all minerals.
                # saving that index into a variable 'no'
                no = int(data['foods'][0]['foodNutrients']
                         [i]['nutrientNumber'])
                # i still needed to hard code some essential nutrients first. used the below code todo so
                if(no < 292 or no == 421 or no == 601):
                    allnutrients['Essentials'][(data['foods'][0]['foodNutrients'][i]['nutrientName'])] = str(
                        (data['foods'][0]['foodNutrients'][i]['value']))+" "+(data['foods'][0]['foodNutrients'][i]['unitName'])

                    # below code is for the pie chart. lets call this "Units Normalizer"
                    # In the json file not all nutrient values had same unit, some had grams, some milligrams and some micrograms(ug)
                    # these values must be normalized for an accuate pie chart.
                    if (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'g':
                        label.append(data['foods'][0]
                                     ['foodNutrients'][i]['nutrientName'])
                        value.append(data['foods'][0]
                                     ['foodNutrients'][i]['value'])
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'mg':
                        label.append(data['foods'][0]
                                     ['foodNutrients'][i]['nutrientName'])
                        value.append(
                            (data['foods'][0]['foodNutrients'][i]['value'])*0.001)
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'ug':
                        label.append(data['foods'][0]
                                     ['foodNutrients'][i]['nutrientName'])
                        value.append(
                            (data['foods'][0]['foodNutrients'][i]['value'])*0.000001)

                # nutrients with nutrientNumber between 300 to 317 were all minerals
                elif(no > 300 and no < 317):
                    allnutrients['Minerals'][(data['foods'][0]['foodNutrients'][i]['nutrientName'])] = str(
                        (data['foods'][0]['foodNutrients'][i]['value']))+" "+(data['foods'][0]['foodNutrients'][i]['unitName'])

                    # Units Normalizer. (reference line 269)
                    if (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'g':
                        allnutrients['Minerals']['total'] = (
                            allnutrients['Minerals']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'mg':
                        allnutrients['Minerals']['total'] = (
                            allnutrients['Minerals']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])*0.001
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'ug':
                        allnutrients['Minerals']['total'] = (
                            allnutrients['Minerals']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])*0.000001

                # nutrientNumber ranging from 318 to 578 were all vitamins
                # i want to seperate carotenoid from vitamins and display them seperately
                # i found some carotenoid on nutrientNumber 321, 322, 334, 337, 338
                elif(no >= 318 and no < 578 and no not in [321, 322, 334, 337, 338]):
                    allnutrients['Vitamins'][(data['foods'][0]['foodNutrients'][i]['nutrientName'])] = str(
                        (data['foods'][0]['foodNutrients'][i]['value']))+" "+(data['foods'][0]['foodNutrients'][i]['unitName'])

                    # Units Normalizer. (reference line 269)
                    if (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'g':
                        allnutrients['Vitamins']['total'] = (
                            allnutrients['Vitamins']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'mg':
                        allnutrients['Vitamins']['total'] = (
                            allnutrients['Vitamins']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])*0.001
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'ug':
                        allnutrients['Vitamins']['total'] = (
                            allnutrients['Vitamins']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])*0.000001

                # categorizing Carotenoids
                elif(no in [321, 322, 334, 337, 338]):
                    allnutrients['Carotenoids'][(data['foods'][0]['foodNutrients'][i]['nutrientName'])] = str(
                        (data['foods'][0]['foodNutrients'][i]['value']))+" "+(data['foods'][0]['foodNutrients'][i]['unitName'])

                    # Units Normalizer. (reference line 269)
                    if (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'g':
                        allnutrients['Carotenoids']['total'] = (
                            allnutrients['Carotenoids']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'mg':
                        allnutrients['Carotenoids']['total'] = (
                            allnutrients['Carotenoids']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])*0.001
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'ug':
                        allnutrients['Carotenoids']['total'] = (
                            allnutrients['Carotenoids']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])*0.000001
                # categorizing fatty acids
                elif(no >= 602):
                    allnutrients['Fattyacids'][(data['foods'][0]['foodNutrients'][i]['nutrientName'])] = str(
                        (data['foods'][0]['foodNutrients'][i]['value']))+" "+(data['foods'][0]['foodNutrients'][i]['unitName'])

                    # Units Normaizer. (reference line 269)
                    if (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'g':
                        allnutrients['Fattyacids']['total'] = (
                            allnutrients['Fattyacids']['total'])+(data['foods'][0]['foodNutrients'][i]['value'])
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'mg':
                        allnutrients['Fattyacids']['total'] = (
                            allnutrients['Fattyacids']['total'])+((data['foods'][0]['foodNutrients'][i]['value'])*0.001)
                    elif (data['foods'][0]['foodNutrients'][i]['unitName']).lower() == 'ug':
                        allnutrients['Fattyacids']['total'] = (allnutrients['Fattyacids']['total'])+(
                            (data['foods'][0]['foodNutrients'][i]['value'])*0.000001)

# the below code is to enter the sub groups of nutrients created above, into the pie chart label and values
# and also into the allnutrients dictionary

            label.append('Minerals')
            label.append('Vitamins')
            label.append('Carotenoids')
            label.append('Fattyacids')
            value.append(allnutrients['Minerals']['total'])
            value.append(allnutrients['Vitamins']['total'])
            value.append(allnutrients['Carotenoids']['total'])
            value.append(allnutrients['Fattyacids']['total'])
            allnutrients['Minerals']['total'] = str(
                round(((allnutrients['Minerals']['total'])*1000), 1))+" "+"MG"
            allnutrients['Vitamins']['total'] = str(
                round(((allnutrients['Vitamins']['total'])*1000), 1))+" "+"MG"
            allnutrients['Carotenoids']['total'] = str(
                round(((allnutrients['Carotenoids']['total'])*1000), 1))+" "+"MG"
            allnutrients['Fattyacids']['total'] = str(
                round(((allnutrients['Fattyacids']['total'])*1000), 1))+" "+"MG"

# cretion of the piechart using plotly go
            data = [
                go.Pie(
                    labels=label,
                    values=value
                )
            ]
            graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('trackfood.html', msg=allnutrients, plot=graphJSON)

# route to myBMI page


@app.route('/mybmi')
def mybmi():
    return render_template('mybmi.html')

# route to Nutrition page where user will find info of daily nutrition.``


@app.route('/nutrition')
def nutrition():
    return render_template('nutrition.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
