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
listemp = ['https://www.linkedin.com/in/mohamed-issaoui-b4b9a81b2/',
                'https://www.linkedin.com/in/mariem-el-mechry/',
                'https://www.linkedin.com/in/ines-besrour-697574216/',
                'https://www.linkedin.com/in/jihed-selmi-503/',
                'https://www.linkedin.com/in/maissa-abdelwahed-862357177/']
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

#Authorized employees liste
listempauth = ['https://www.linkedin.com/in/mohamed-issaoui-b4b9a81b2/',
                'https://www.linkedin.com/in/mariem-el-mechry/',
                'https://www.linkedin.com/in/maissa-abdelwahed-862357177/']


def check_auth(img) :

  resize_image(img, img, 400,400)
  img = cv2.imread(img)
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
     print(mydata)
     if mydata in listempauth:
        response = [1,mydata]
     else:
        response = [0,""]
     return response
  else:
    #cv2.imshow("",img)
    return ["Please provide a valid QR code image !",0]

# call the function with different images
img1 = "backend/qrcodes/emp1.png"
#img2 = cv2.imread("/content/qrcodes/emp1.png")
#img3 = cv2.imread("/content/qrcodes/emp7.png")

data = check_auth(img1)
print(data[0])
#check_auth(img2)
#check_auth(img3)

#---------------------------------------------API FLASK---------------------------------------------------------

# API Flask
from flask import Flask, request,jsonify,Response
from flask_cors import CORS
import logging
import os
import numpy as np
from PIL import Image
import base64
import cv2
from pyzbar.pyzbar import decode

#run_with_ngrok(app)

app = Flask(__name__)


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
    print(res)
    #print("path to new image to upload", "backend/qrcodes/"+filename)

    #to save image with the same text color (green or red)
    #rgb_image = cv2.cvtColor(res[1], cv2.COLOR_BGR2RGB)
    #image = Image.fromarray(rgb_image)
    #image.save("backend/res-auth/auth-result.png",format="PNG")
    response = res
    return response
  except Exception as e:
    logging.error(f"Error occurred: {str(e)}")
    return jsonify({"error": "something went wrong !!"}), 500

#------------------------------------end part 1--------------------------------------------------------






#----------------------Décoder un code QR à partir de webcam + tester l'autorisation d'un employé----------------------
from flask_socketio import SocketIO, emit
import socketio

sio = socketio.Server(cors_allowed_origins="http://localhost:3000")
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # 3 is id  for width
cap.set(4, 480)  # 4 is id  for height

@sio.on('connect')
def connect():
    generate_frames()


def generate_frames():
   while True:
    success, img = cap.read()
    ret,buffer = cv2.imencode('.png',img)
    img_bytes = buffer.tobytes()
  
    for barcode in decode(img):
        mydata = barcode.data.decode('utf-8')
        pts = np.array([barcode.polygon], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(img, pts, True, (255, 0, 255), 10)
        pts2 = barcode.rect
        #check if the employee is authorized and display output
        if mydata in listempauth:
            cv2.putText(img, "Authorized", (pts2[0], pts2[1]), cv2.FONT_HERSHEY_PLAIN, 0.9, (0, 255, 0), 2)
        else:
            cv2.putText(img, "Un-Authorized", (pts2[0], pts2[1]), cv2.FONT_HERSHEY_PLAIN, 0.9, (0, 0, 255), 2)
        print(mydata)
    #img_base64 = cv2.imencode('.jpg', img)[1].tobytes()
    print(img_bytes)
    sio.emit('frame', {'image': base64.b64encode(img_bytes).decode('utf-8')})
    #yield (b'--frame\r\n'
              # b'Content-Type: image/jpeg\r\n\r\n' + img_bytes + b'\r\n')

    #cv2.imshow('Result :', img)
    #cv2.waitKey(1)

@sio.on('disconnect')
def handle_disconnect():
    cap.release()


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app, log_output=False)
    #app.run(debug=True)
