# Importing library
from pyzbar.pyzbar import decode
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
#from google.colab.patches import cv2_imshow
import numpy as np
from PIL import Image
import qrcode

# Data to encode : liste of employees id
listemp = ['id-emp1-1136363636','id-emp2-7373737337','id-emp3-0098773731',
         'id-emp4-2263663636','id-emp5-1100110011','id-emp6-2530987633','id-emp7-1212121212']
i = 0

# Create qrcode from data
for item in listemp:
  img = qrcode.make(item)
  i+=1
  imgname = 'emp'+str(i)+'.png'
  print('QR code pour Empolyé '+str(i))
  img.show()
  print(type(img))
  img.save('backend/qrcodes/'+str(imgname))

#Tester de décoder un code QR à partir d'une image + tester l'autorisation d'un enmployé



#Resize the image before checking the existance of QR code in it

def resize_image(input_image_path, output_image_path, new_width, new_height):
    # Open the input image
    img = Image.open(input_image_path)
    print(img)
    # Resize the image
    resized_img = img.resize((new_width, new_height))
    print(resized_img)
    # Save the resized image
    resized_img.save(output_image_path)

##Check authorization with QR code images function

def check_auth(img) :

  resize_image(img, img, 400,400)
  img = cv2.imread(img)

  #Authorized employees liste
  listempauth = ['id-emp4-2263663636','id-emp5-1100110011','id-emp2-7373737337','id-emp7-1212121212']

  code = decode(img)
  if code :
    for i in code:
     mydata = i.data.decode('utf-8')
     #bounding box
     pts = np.array([i.polygon], np.int32)
     pts = pts.reshape((-1, 1, 2))
     pts2 = i.rect
     #check for authorization
     response = []
     if mydata in listempauth:
        cv2.polylines(img, pts, True, (0, 255, 0), 15)
        cv2.putText(img, "Authorized", (pts2[0],pts2[1]), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2)
        cv2.imshow("",img)
        response = [1,img]
     else:
        cv2.polylines(img, pts, True, (0, 0, 255), 15)
        cv2.putText(img, "Un-Authorized", (pts2[0],pts2[1]), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 255), 2)
        cv2.imshow("",img)
        response = [0,img]
     return response

  else:
    cv2.imshow("",img)
    return ["Please provide a valid QR code image !",0]

# call the function with different images
img1 = "/Users/abdelwahed/PhpstormProjects/qrcode-project/backend/qrcodes/emp1.png"
#img2 = cv2.imread("/content/qrcodes/emp1.png")
#img3 = cv2.imread("/content/qrcodes/emp7.png")

data = check_auth(img1)
print(data[0])
#check_auth(img2)
#check_auth(img3)

#---------------------------------------------API FLASK---------------------------------------------------------

# API Flask
from flask import Flask, request,jsonify
from flask_cors import CORS
import logging
import os
import numpy as np
from PIL import Image
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#run_with_ngrok(app)

# Set the folder where uploaded images will be stored
UPLOAD_FOLDER = "backend/qrcodes/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/",methods=['POST'])
def index():
  try:
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    print("file",file)
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    print("---------------------------")
    #filename = str(uuid.uuid4()) + "-" + file.filename
    filename = file.filename
    print("filename well generated !")
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    print("file well saved !")
    res = check_auth("backend/qrcodes/"+filename)
    print(res[0])
    #print("path to new image to upload", "backend/qrcodes/"+filename)
    #Additional data to be sent in the response
    additional_data = {
        'auth': res[0],
    }
    if res[0] == 0 or res[0] == 1 :
      #to save image with the same text color (green or red)
      rgb_image = cv2.cvtColor(res[1], cv2.COLOR_BGR2RGB)
      image = Image.fromarray(rgb_image)
      image.save("backend/res-auth/auth-result.png",format="PNG")

      with open("backend/res-auth/auth-result.png", 'rb') as file:
        img_data = file.read()

      #convert the bytes object img_data to a base64-encoded string base64_file_data
      base64_file_data = base64.b64encode(img_data).decode('utf-8')

      print("hello there 123")
      # Combine the file data and additional data in the response
      response = {
        'file_data': base64_file_data,
        'additional_data': additional_data,
      }
      return response
    else :
      response = {
        'file_data': "",
        'additional_data': additional_data}
      return response

  except Exception as e:
    logging.error(f"Error occurred: {str(e)}")
    return jsonify({"error": "something went wrong !!"}), 500

if __name__ == "__main__":
    app.run()
