from tensorflow.keras.models import load_model  # TensorFlow is required for Keras to work
from tensorflow.keras.layers import DepthwiseConv2D
from tensorflow.keras.utils import get_custom_objects
import cv2  # Install opencv-python
import numpy as np
import time
from collections import Counter

# Custom class to handle DepthwiseConv2D layer
class CustomDepthwiseConv2D(DepthwiseConv2D):
    @classmethod
    def from_config(cls, config):
        if 'groups' in config:
            del config['groups']
        return cls(**config)

class TM_model:
    def __init__(self):
        # Register the custom object
        get_custom_objects().update({'DepthwiseConv2D': CustomDepthwiseConv2D})

        # Disable scientific notation for clarity
        np.set_printoptions(suppress=True)

        # Load the model
        self.model = load_model("keras_Model.h5", compile=False)

        # Load the labels
        self.class_names = open("labels.txt", "r").readlines()

    def get_prediction_from_webcam(self, duration=7):
        # CAMERA can be 0 or 1 based on default camera of your computer
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            print("Error: Could not open webcam.")
            return None, None

        predictions = []
        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                # Grab the webcamera's image
                ret, image = camera.read()
                if not ret:
                    print("Error: Could not read image from webcam.")
                    continue

                # Resize the raw image into (224-height, 224-width) pixels
                image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

                # Show the image in a window (optional, can be commented out)
                cv2.imshow("Webcam Image", image)
                cv2.waitKey(1)  # Add this to update the window

                # Make the image a numpy array and reshape it to the model's input shape
                image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

                # Normalize the image array
                image = (image / 127.5) - 1

                # Predict using the model
                prediction = self.model.predict(image)
                index = np.argmax(prediction)
                class_name = self.class_names[index].strip()
                confidence_score = prediction[0][index]

                # Append prediction and confidence score
                predictions.append((class_name, confidence_score))

            # Find the most common prediction
            if predictions:
                most_common_class = Counter([pred[0] for pred in predictions]).most_common(1)[0][0]
                avg_confidence_score = np.mean([pred[1] for pred in predictions if pred[0] == most_common_class])
                print(most_common_class)
                return most_common_class, avg_confidence_score
            else:
                return None, None

        finally:
            camera.release()
            cv2.destroyAllWindows()

if __name__ == '__main__':
    class_name, confidence_score = TM_model.get_prediction_from_webcam(duration=5)
    if class_name and confidence_score:
        print("Class:", class_name, "Average Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
    else:
        print("Failed to get prediction.")
