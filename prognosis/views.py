# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pyrebase
from requests.exceptions import HTTPError
from rest_framework.decorators import api_view
from rest_framework.response import Response
import firebase_admin
from firebase_admin import credentials, firestore
from tensorflow.keras.models import load_model
import numpy as np
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import cv2

config = {
  "apiKey": "AIzaSyBX3EO4NDaPmIjErsK7O5CpwpcbJJBvApM",
  "authDomain": "retinamed-prognosis.firebaseapp.com",
  "projectId": "retinamed-prognosis",
  "storageBucket": "retinamed-prognosis.appspot.com",
  "messagingSenderId": "648132583252",
  "appId": "1:648132583252:web:f2e1ee0a618eb112bf32c1",
  "measurementId": "G-7QHLLFW7Q9",
  "databaseURL": ""
} 


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
cred = credentials.Certificate("serviceAccountKey.json") 
firebase_admin.initialize_app(cred)
db = firestore.client()


@csrf_exempt
@api_view(['POST', 'OPTIONS'])
def sign_in(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        try:
            # Authenticate user using Firebase
            user = auth.sign_in_with_email_and_password(email, password)
            return Response({'message': 'Authentication successful', 'user': user})
        except HTTPError as e:
            error_message = "Invalid email or password. Please try again."
            return Response({'error': error_message}, status=400)
        except Exception as e:
            error_message = "Error: {}".format(str(e))
            return Response({'error': error_message}, status=500)
    
    return Response({'error': 'Method Not Allowed'}, status=405)

@csrf_exempt
@api_view(['POST', 'OPTIONS'])
def sign_up(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        age = data.get('age')
        try:
            # Create user using Firebase
            user = auth.create_user_with_email_and_password(email, password)
            user_data = {
                'name': name,
                'age': age,
                'email': email
            }
            db.collection('users').document(user['localId']).set(user_data)
            return Response({'message': 'User created successfully', 'user': user})
        except HTTPError as e:
            error_message = "Username already exists."
            return Response({'error': error_message}, status=400)
        except Exception as e:
            error_message = "Error: {}".format(str(e))
            return Response({'error': error_message}, status=500)
    
    return Response({'error': 'Method Not Allowed'}, status=405)

@csrf_exempt
@api_view(['POST', 'OPTIONS'])
def reset(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')  
        try:
            auth.send_password_reset_email(email)
            return Response({'message': 'Check Your Email'})
        except Exception as e:
            error_message = "Error: {}".format(str(e))
            return Response({'error': error_message}, status=500)
    
    return Response({'error': 'Method Not Allowed'}, status=405)

def loadheartattack():
    model_path = "prognosis/models/final_model.h5"
    model = load_model(model_path)
    return model


@csrf_exempt
@api_view(['POST'])
def heartattack(request):
    if request.method == 'POST':
        data = request.data
        input_data = [float(data.get('age')), float(data.get('sex')), float(data.get('cp')), 
                          float(data.get('trtbps')), float(data.get('chol')), float(data.get('fbs')), 
                          float(data.get('restecg')), float(data.get('thalachh')), float(data.get('exng')), 
                          float(data.get('oldpeak')), float(data.get('slp')), float(data.get('caa')), 
                          float(data.get('thall'))]
        # Load the model
        heart_attck_model = loadheartattack()
        input_array = np.array(input_data).reshape(1, -1) 
        prediction = heart_attck_model.predict(input_array)
        if prediction >= 0.5:
            result = "Heart Attack"
        else:
            result = "No Heart Attack"
        return Response({'prediction': result})
    return Response({'error': 'Method Not Allowed'}, status=405)

def loadeyedisease():
    model_path = "prognosis/models/final.h5"
    model = load_model(model_path)
    return model

@csrf_exempt
@api_view(['POST'])
def eyedisease(request):
    CLASSES = {0: 'Cataract', 1: 'Diabetes', 2:'Glaucoma', 3: 'Normal', 4: 'Other'}
    
    if request.method == 'POST':
        # Get the image file from the request
        image_file = request.FILES.get('image')
        
        # Save the image temporarily
        filename = default_storage.save('temp_image.jpg', ContentFile(image_file.read()))
        temp_file_path = os.path.join(default_storage.location, filename)

        # Load the image using PIL
        image = Image.open(temp_file_path)

        # Preprocess the image
        img = cv2.imread(temp_file_path)
        img = cv2.resize(img, (150, 150))
        img = img / 255.0 
        img_batch = np.expand_dims(img, axis=0)

        # Load the eye disease model
        eye_disease_model = loadeyedisease()

        # Make prediction
        prediction = eye_disease_model.predict(img_batch)
        predicted_class_index = np.argmax(prediction[0])
        predicted_class_name = CLASSES[predicted_class_index]

        # Close the image file
        image.close()

        # Cleanup: Remove the temporary image file
        default_storage.delete(filename)

        return Response({'prediction': predicted_class_name})
    return Response({'error': 'Method Not Allowed'}, status=405)




