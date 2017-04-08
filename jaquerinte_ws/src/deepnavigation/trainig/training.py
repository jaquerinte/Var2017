from __future__ import print_function
from resnet50 import ResNet50
import numpy as np
from keras.models import load_model
import keras.backend as K
from PIL import Image, ImageOps

#imgHeight=320
#imgWith=240

imgHeight=224
imgWith=224
nb_epoch=25

def load_Data():
	listImagenes=[]
	listVelLinear=[]
	listVelAngular=[]
	contador=0
	file=open("./manifest2.txt","r")
	for line in file:
		partes=line.split()
		img=Image.open(partes[0]).resize((imgHeight,imgWith)).convert("RGB")
		listImagenes.append(np.asarray(img).astype("float16")/255)
		listVelLinear.append(partes[1])
		listVelAngular.append(partes[2])
		#print('\b'+str(contador))
		#contador=contador+1

	listVelLinear = np.asarray(listVelLinear).astype("float32")/0.5
	
	n=len(listImagenes)

	if K.image_dim_ordering() == 'th':
		X = np.asarray(listImagenes).reshape(n,3,imgHeight,imgWith)
	else:
		X = np.asarray(listImagenes).reshape(n,imgHeight,imgWith,3)
	Y = np.column_stack((listVelLinear,listVelAngular))
	#Y=[]
	#matrix 
	#Y.append(listVelLinear)
	#Y.append(listVelAngular)

	return X,Y,n 

def trainEvaluate(modelo,imput,output,imputTest,outputTest):
	modelo.fit(imput,output,256,verbose=1,nb_epoch=nb_epoch,validation_data=(imputTest,outputTest))
	score = modelo.evaluate(imputTest, outputTest, verbose=0)
	print('Test score:', score[0])
	print('Test accuracy:', score[1])
	return score[1]





X,Y,n=load_Data()
modelo=ResNet50(True,"imagenet",None,imgHeight,imgWith)
randomize = np.arange(len(Y))
np.random.shuffle(randomize)
#X, Y = X[randomize], Y[randomize]
n_partition = int(n*0.9)	# Train 90% and Test 10%
X_train = X[:n_partition]
Y_train = Y[:n_partition]

X_test  = X[n_partition:]
Y_test  = Y[n_partition:]

#print(X_train.shape, 'train samples')
#print(X_test.shape, 'test samples')
#print(input_shape,'input_shape')
print(nb_epoch,'epochs')

trainEvaluate(modelo,X_train,Y_train,X_test,Y_test)

filename="turteblot.h5"
modelo.save(filename)


