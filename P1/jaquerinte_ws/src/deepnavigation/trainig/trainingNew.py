from __future__ import print_function
from resnet50 import ResNet50
import numpy as np
import tensorflow as tf
from keras.models import load_model
import keras.backend as K
from PIL import Image, ImageOps
import random
from tqdm import tqdm


#imgHeight=320
#imgWith=240

imgHeight=224
imgWith=224
nb_epoch=25

numberPerFit=27

listImagenes=[]
listVelLinear=[]
listVelAngular=[]

listLines=[] 

filename="turteblot2.hdf5"
optimizer = 'adam'

def load_DataIncial():

	file=open("./manifest.txt","r")
	for line in file:
			
			listLines.append(line)

		#	partes=line.split()
		#	listImagenes.append(partes[0])
		#		listVelLinear.append(partes[1])
		#	listVelAngular.append(partes[2])

	n=len(listLines)
	suffleValues()

	return n 
def suffleValues():
	random.shuffle(listLines)
	for line in listLines:
		#	print(line)
			partes=line.split()
			listImagenes.append(partes[0])
			listVelLinear.append(partes[1])
			listVelAngular.append(partes[2])

def load_DataPartial(number,position):
	listImagenesAux=[]
	listVelLinearAux=[]
	listVelAngularAux=[]
	total = number+position
	for i in range(position,total):

		img=Image.open(listImagenes[i]).resize((imgHeight,imgWith)).convert("RGB")
		listImagenesAux.append(np.asarray(img).astype("float16")/255)
		listVelLinearAux.append(listVelLinear[i])
		listVelAngularAux.append(listVelAngular[i])
		

	#listVelLinearAux = np.asarray(listVelLinearAux).astype("float32")/0.5
	
	n=len(listImagenesAux)

	if K.image_dim_ordering() == 'th':
		X = np.asarray(listImagenesAux).reshape(n,3,imgHeight,imgWith)
	else:
		X = np.asarray(listImagenesAux).reshape(n,imgHeight,imgWith,3)
	Y = np.column_stack((listVelLinearAux,listVelAngularAux))

	return X,Y




def trainEvaluate(modelo,total,epoca):
	X_test_acumulated=[] 
	Y_test_acumulated=[] 
	lossTotal=0; 

	newTotal = total / numberPerFit

	for i in tqdm(range(0,int(newTotal))):
		X,Y = load_DataPartial(numberPerFit,i)
		n_partition = int(numberPerFit*0.9)	# Train 90% and Test 10%
		X_train = X[:n_partition]
		Y_train = Y[:n_partition]
		X_test  = X[n_partition:]
		Y_test  = Y[n_partition:]
		
		if i % 2 == 0:
			with tf.device('/gpu:0'):
				value=modelo.fit(X_train,Y_train,256,verbose=0,nb_epoch=1)
		else:
			with tf.device('/gpu:1'):
				value=modelo.fit(X_train,Y_train,256,verbose=0,nb_epoch=1)
		#with tf.device('/gpu:1'):
		#	value=modelo.fit(X_train,Y_train,256,verbose=0,nb_epoch=1,)
		#print("Epoca actual: "+str(epoca))
		#print("Position:"+str(i)+" of: "+str(int(newTotal)))
		lossTotal=lossTotal+value.history['loss'][0]
		if i == 0:
			X_test_acumulated=X_test
			Y_test_acumulated=Y_test
		else:
			X_test_acumulated = np.concatenate((X_test_acumulated, X_test), axis=0)
			Y_test_acumulated = np.concatenate((Y_test_acumulated, Y_test), axis=0)

	score = modelo.evaluate(X_test_acumulated, Y_test_acumulated, verbose=0)
	#print('Test score:', score[0] , end='')
	#print('Test accuracy:', score[1] ,end='')
	#print('Traing loos',lossTotal/newTotal ,end='')
	return score[1]



#n=load_DataIncial()
modelo=ResNet50(True,"imagenet",None,imgHeight,imgWith)
modelo.compile(lr=0.001,loss='mean_squared_error',optimizer=optimizer)
#modelo.compile(loss='mse',optimizer=optimizer,metrics=['accuracy'])
#randomize = np.arange(n)
#np.random.shuffle(randomize)
# listImagenes, listVelLinear,listVelAngular = listImagenes[randomize], listVelLinear[randomize],listVelAngular[randomize]

print(nb_epoch,'epochs')

for i in tqdm(range(0,nb_epoch)):
	#suffles every epoch
	n=load_DataIncial()
	trainEvaluate(modelo,n,i)
	#cada epoca guarda el modelo
	modelo.save(filename)




