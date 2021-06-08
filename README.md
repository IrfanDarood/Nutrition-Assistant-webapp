
<h1 align="center">
  <a href="https://nutribaba.herokuapp.com">
  <img src="https://raw.githubusercontent.com/IrfanDarood/Nutrition-Assistant-webapp/main/static/nutribabalogonew.png" width="224px"/><br/>
  </a>
  YOUR NUTRITION ASSISTANT WEB APP
</h1>
<p align="center">Know what you eat. Click a picture📸 of the food and upload⬆️ it to the `Assistant` and<br> know the <b>detailed nutritional contents</b> in your food.<br><br>
Find your <b>Body Mass Index(BMI)</b> using NutriBABA within a few clicks.</p>

<p align="center"><a href="https://nutribaba.herokuapp.com"> <img src="https://img.shields.io/badge/version-v1.0.0-blue?style=for-the-badge&logo=none" alt="cli version" /></a>&nbsp;&nbsp;<img src="https://img.shields.io/badge/Type-Web App-success?style=for-the-badge&logo=none" alt="webapp" />&nbsp;&nbsp;<img src="https://img.shields.io/badge/Category-health-success?style=for-the-badge&logo=none" alt="health" />&nbsp;&nbsp;<img src="https://img.shields.io/badge/Hosting-Heroku-red?style=for-the-badge&logo=none" alt="heroku" /></p>

## 📝 ABOUT THE PROJECT

### NutriBABA is a nutrition assistant web application which,

* Takes a picture of the food as input and provides all the nutrient contents of that food item.(requires user login, to give them a better experience)
* Gives a **graphical representation** of the food nutrient contents which a human brain can easily perceive rather than just **textual representation** which must be read throughout.
* Can also calculate the `Body Mass Index (BMI)` of a person instantly by taking the `height` (in Feets and Inches) and `weight` (in Kilograms) of a person.
* Spreads awareness about **Nutrition** and why it is important and also gives an overview on BMI i.e, What is BMI ? and why maintaining a normal BMI value is crucial.

## 🏗️ BUILT WITH

* Python Flask
* Jinja2 template
* HTML AND CSS
* Bootstrap 
* JavaScript
* MySql Database
* Docker
* APIs
* IBM Watson Visualization API
* USDA Food Central API

## ⚡️ QUICK START

Below are the instructions to set up this project on your local machine.

Nutribaba is a **containerized web application** which can run on any desktop with [Docker](https://www.docker.com/) installed. To know more about what containers are? And why do we containerize applications? [Click here](https://www.docker.com/resources/what-container)

To get started, you must install Docker  on their desktop to run the containerised NutriBABA web application.

## Prerequisites:

**Docker 🐳** 

## Installation:
 
[🔔 How to install Docker on my device?](https://docs.docker.com/engine/install/)


**Create an account on Docker Hub to push or pull your containers(Docker Images) to or from the hosted repository service, which is provided by Docker for finding and sharing container images with your team.**

You need this to access the **NutriBABA Docker image**.

Sign into your [`Docker-hub`](https://hub.docker.com/) account in Docker Desktop, which you installed previously.

## 🚀 DEPLOYMENT:
### METHOD 1

Run the following command in the cmd/shell to pull my docker image.

* Check whether **Docker** is installed properly:
	~~~
	docker version
	~~~
* Pull NutriBABA Docker image from my Docker hub [repo](https://hub.docker.com/r/irfandarood/nutribaba):
	~~~
	docker pull irfandarood/nutribaba
	~~~
	Now, Docker will pull the containerized web app image onto your system.
	
* Run the Docker image on your **local machine**:
	~~~
	docker run -p 5000:5000 irfandarood/nutribaba
	~~~
	In the above command **5000** is the port number on which NutriBABA will run.

* Check if the image is running successfully:
	~~~
	docker ps 
	~~~

* To view the **web app** in action 
	* Open a browser 
	* Search “localhost:\<portnumber\>” 
		~~~
		https://loaclhost:5000
		~~~ 
* To `stop` the Docker image, image id is required. Run this command to get the image Id:
	~~~
	docker ps
	~~~
* Copy the id of our image **irfandarood/nutribaba** and replace it with **image_id** in the below command:
	~~~
	docker stop image_id
	~~~

### METHOD 2

You can also build your own **Docker image** instead of using my Docker image as shown above. 
* Download the code from the repository.
* Open **Command Prompt**
* Navigate into the downloaded folder where `nutribaba.py` file is present.
* Run the following commands:

	* Build an image using DOCKER.
		~~~
		docker build -t appname .
		~~~
	* Run the Docker image on your local machine:
		~~~
		docker run -p 5000:5000 irfandarood/nutribaba
		~~~

## 💡 IMPLEMENTATION (`nutribaba.py`)


When a user uploads a picture of food on [trackfood](https://nutribaba.herokuapp.com/trackfood) page the web app.
That picture is saved with the users name 
~~~ python
 # Checking whether data came from the trackfood form using method POST.
    if request.method == 'POST':

        # saving the uploaded image into a variable img.
        img = request.files['foodimg']

        # this is the path where i want to store the image.
        pathname = './static/'+session['email']+'.jpg'

        # saving the image at the above path/location.
        img.save(pathname)
~~~~

This web application uses an api provided by IBM Watson [`IBM Watson™ Visual Recognition`](https://cloud.ibm.com/apidocs/visual-recognition/visual-recognition-v3) to recognize food items. 

~~~ python
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
~~~

It uses another api by the U.S. DEPARTMENT OF AGRICULTURE named [`FoodData Central`](https://fdc.nal.usda.gov/index.html) to fetch the nutritional contents of the recognized food item.

~~~ python
# using USDA API to get the nutrients of the food item
# Requesting the api through the url, specifing fooditem name, no of pages required(one page = set of nutrients present in the same food at one region)
# and the API key for authentication

nutrients = requests.get('https://api.nal.usda.gov/fdc/v1/foods/search?query={}&pageSize={}&api_key={}'.format(
    fooditem, '1', 'wNxP2RfBXrx3amU5HypuuEWUtSSgeRErZMcU5LFA'))
# loading the json file into a variable data.
data = json.loads(nutrients.text)

# Now the variable "data" contains all the nutritional data of the food item is json format.
# Only thing left is to display the data to the user.
~~~

In this WEB APP, the fetched details are displayed on the screen in both graphical and textual representations.


<img src="https://raw.githubusercontent.com/IrfanDarood/Nutrition-Assistant-webapp/main/static/piechart%20(2).png" width="auto"/><br/>
<br>
<img src="https://raw.githubusercontent.com/IrfanDarood/Nutrition-Assistant-webapp/main/static/nutrientlist%20(2).png" width="auto"/><br/>

<br>

## PIE CHART

The above pie chart was created using [`PLOTLY GO`](https://plotly.com/python/)

~~~ python 
# cretion of the piechart using plotly go
data = [
    go.Pie(
        labels=label,
        values=value
    )
]
graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

# labels and values are the names of the nutrients and their volume per 100grs of servings of the specific food
~~~

## BMI CALCULATION

This feature is completely implemented in `JAVASCRIPT`, for better performance and fast results.

~~~ javascript
<!-- JavaScript to calculate BMI --> 
    <script>
        function calculate(){
        var f,i,w;
        f=Number(document.getElementById("feet").value);
        i=Number(document.getElementById("inch").value);
        w=Number(document.getElementById("weight").value);
        f=f/3.281; //converting feets and inches to meters.
        i=i/39.37;
        f=f+i;
        w=w/(f**2);  //BMI Formula : weight(kg)/[height(M)]^2
        document.getElementById("bmi").value= w.toFixed(2);
        return true;
        }
        </script>
~~~

When ever a user enters height and weight the above javascript function `calculate()` is called.
This **function** calculates **Body Mass Index(BMI)** and displays the value in a read only text field of the form.

## LINKS

Here is the Demo video of the Web Application.

https://drive.google.com/file/d/1cfhaeK2PiFyWQVdQFCe3XuWNGZYIw_wV/view?usp=sharing

Visit NutriBABA :

https://nutribaba.herokuapp.com


## DOCUMENTATION
The complete documentation is provided in the [NutriBABA Documentation](https://github.com/IrfanDarood/Nutrition-Assistant-webapp/blob/main/NutriBABA%20Documentation.pdf). 

## LICENCE
NutriBABA is a free and open source software licenced under the [MIT Licence](https://github.com/IrfanDarood/Nutrition-Assistant-webapp/blob/main/LICENSE).

~~~
MIT License 
Copyright (c) 2021 Irfan Darood

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
~~~

## CONTRIBUTORS ✨
<a href="https://github.com/IrfanDarood/Nutrition-Assistant-webapp/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=IrfanDarood/Nutrition-Assistant-webapp" />
</a>

Made with [contributors-img](https://contrib.rocks).

## CONTACT
You can find me on Twitter at 

[`@MohdIrfanHuss19`](https://twitter.com/MohdIrfanHuss19?s=09)
