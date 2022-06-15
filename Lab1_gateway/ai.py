from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import cv2
import time

cam=cv2.VideoCapture(0)
# Load the model
model = load_model('keras_model.h5')


def capture_img():
    ret,frame=cam.read()
    cv2.imwrite("captured.png",frame)
def ai_detection():
    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    # Replace this with the path to your image
    image = Image.open('captured.png')
    #resize the image to a 224x224 with the same strategy as in TM2:
    #resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    #turn the image into a numpy array
    image_array = np.asarray(image)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(data)

    # max_value = max(prediction)
    # max_i=prediction.index(max_value)
    # print("Result: ", rs_class[max_i])

    print(len(prediction[0]))
    name = ["White Mask", "Grey Mask", "UnMask"]
    index = -1
    max_value = -1
    for i in range(0 , len( prediction [0]) ) :
        if max_value < prediction[0][ i ]:
            max_value = prediction[0][ i ]
            index = i
    print ("Ket Qua: ", name[index])
    print ("Chinh Xac: ", max_value )
while True:
    capture_img()
    ai_detection()
    time.sleep(5)

    #print(prediction)
