#!/usr/bin/env python3

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import cv2
import numpy
import string
import random
import argparse

#import tensorflow.keras as keras
import numpy as np

    
import tflite_runtime.interpreter as tflite



def decode(characters, y):
    y = numpy.argmax(numpy.array(y), axis=1)
    print (" The value of y is:" ,y)
    z=""

    for x in y:
        if x != 36:
            z = z + str(characters[x])
    print("Value of z is:", z)
    return (z)
    
    #return ''.join([characters[x] for x in y])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-name', help='Model name to use for classification', type=str)
    parser.add_argument('--captcha-dir', help='Where to read the captchas to break', type=str)
    parser.add_argument('--output', help='File where the classifications should be saved', type=str)
    parser.add_argument('--symbols', help='File with the symbols to use in captchas', type=str)
    args = parser.parse_args()

    if args.model_name is None:
        print("Please specify the CNN model to use")
        exit(1)

    if args.captcha_dir is None:
        print("Please specify the directory with captchas to break")
        exit(1)

    if args.output is None:
        print("Please specify the path to the output file")
        exit(1)

    if args.symbols is None:
        print("Please specify the captcha symbols file")
        exit(1)

    symbols_file = open(args.symbols, 'r')
    captcha_symbols = symbols_file.readline()
    symbols_file.close()

    print("Classifying captchas with symbol set {" + captcha_symbols + "}")

    #with tflite.device('/cpu:0'):

         
    interpreter = tflite.Interpreter(model_path=args.model_name) 
    interpreter.allocate_tensors()  
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()




    with open(args.output, 'w') as output_file:

        for x in os.listdir(args.captcha_dir):
                # load image and preprocess it
                raw_data = cv2.imread(os.path.join(args.captcha_dir, x))
                rgb_data = cv2.cvtColor(raw_data, cv2.COLOR_BGR2RGB)
                gray_data = cv2.cvtColor(raw_data, cv2.COLOR_BGR2GRAY)
            
                #print("The shape of gray data is: ", gray_data.shape)
           
            
                #grayscaled = tf.image.rgb_to_grayscale(rgb_data, name=None)


           
                ret,thresh_img = cv2.threshold(gray_data,200,255,cv2.THRESH_BINARY_INV)
           
            
                kernel = np.ones((2,2), np.uint8)
                erode_thresh_img = cv2.erode(thresh_img, kernel)
                blur = cv2.GaussianBlur(erode_thresh_img,(5,5),0)
                
                
            
                image = numpy.array(blur, dtype=numpy.float32) / 255.0
                (h, w) = image.shape
                image = image.reshape([ -1, h, w])
         #      prediction = model.predict(image)
                input_index = interpreter.get_input_details()[0]["index"] 
                interpreter.set_tensor(input_index, image)
                interpreter.invoke()
                
                prediction = []

                for result in output_details:
                    output_data = interpreter.get_tensor(result['index'])
                    prediction.append(output_data)

                prediction = numpy.reshape(prediction, (len(output_details), -1))                
                
                output_file.write(x + ", " + decode(captcha_symbols, prediction) + "\n")

                print('Classified ' + x)

if __name__ == '__main__':
    main()
