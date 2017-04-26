from __future__ import print_function
from resnet50 import ResNet50
import numpy as np
import tensorflow as tf
from keras.models import load_model
import keras.backend as K
from PIL import Image, ImageOps
import random
from tqdm import tqdm
from keras.preprocessing import image
from imagenet_utils import preprocess_input, decode_predictions
import sys




#imgHeight=320
#imgWith=240

imgHeight=224
imgWith=224
nb_epoch=25

#numberPerFit=224
numberPerFit = 443

filename="newDatasedWeights.hdf5"
f = open('data.txt','w')

listImagenes=[]
listVelLinear=[]
listVelAngular=[]

listLines=[]

minBreak = 0.0001


optimizer = 'adam'


def load_DataIncial():
	#file=open("./manifest-old.txt","r")
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


	#for line in listLines:
	#	partes=line.split()
	#	listImgNew.append(partes[0])
	#	listVelNew.append(partes[1])
	#	listAngNew.append(partes[2])
	total = number+position
	for i in range(position,total):

		#img=Image.open(listImagenes[i]).resize((imgHeight,imgWith)).convert("RGB")
		#listImagenesAux.append(np.asarray(img).astype("float32"))
		img = image.load_img(listImagenes[i], target_size=(224, 224))
		x = image.img_to_array(img)
		x = x.reshape((1,)+x.shape)
		#x = np.expand_dims(x, axis=0)
		#x = preprocess_input(x)
		listImagenesAux.append(x)
		listVelLinearAux.append(listVelLinear[i])
		listVelAngularAux.append(listVelAngular[i])


	#listVelLinearAux = np.asarray(listVelLinearAux).astype("float32")/0.5

	n=len(listImagenesAux)

	#if K.image_dim_ordering() == 'th':
	#	X = np.asarray(listImagenesAux).reshape(n,3,imgHeight,imgWith)
	#else:
	#	X = np.asarray(listImagenesAux).reshape(n,imgHeight,imgWith,3)
		#X = np.asarray(listImagenesAux)
	#for list in lisImagenesAux
	X = np.vstack(listImagenesAux)
	Y = np.column_stack((listVelLinearAux,listVelAngularAux))
	#print (Y)
	return X,Y




def trainEvaluate(modelo,total,epoca,lastValue,traing):
	X_test_acumulated=[]
	Y_test_acumulated=[]
	lossTotal=0

	newTotal = total / numberPerFit

	for i in tqdm(range(0,int(newTotal))):
		X,Y = load_DataPartial(numberPerFit,i)
		n_partition = int(numberPerFit*0.9)	# Train 90% and Test 10%
		X_train = X[:n_partition]
		Y_train = Y[:n_partition]
		X_test  = X[n_partition:]
		Y_test  = Y[n_partition:]

		#if i % 2 == 0:
		#	with tf.device('/gpu:0'):
		#		value=modelo.fit(X_train,Y_train,256,verbose=0,nb_epoch=1)
		#else:
		#	with tf.device('/gpu:1'):
		#		value=modelo.fit(X_train,Y_train,256,verbose=0,nb_epoch=1)
		#with tf.device('/gpu:1'):
		#	value=modelo.fit(X_train,Y_train,256,verbose=0,nb_epoch=1,)
		#print("Epoca actual: "+str(epoca))
		#print("Position:"+str(i)+" of: "+str(int(newTotal)))

		value=modelo.fit(X_train,Y_train,batch_size=20,verbose=0,nb_epoch=1)
		lossTotal=lossTotal+value.history['loss'][0]
		if i == 0:
			X_test_acumulated=X_test
			Y_test_acumulated=Y_test
		else:
			X_test_acumulated = np.concatenate((X_test_acumulated, X_test), axis=0)
			Y_test_acumulated = np.concatenate((Y_test_acumulated, Y_test), axis=0)

	score = modelo.evaluate(X_test_acumulated, Y_test_acumulated,batch_size=20,verbose=0)
	#print(modelo.metrics_names)
	#score.history[]	
	print('Test loss:',score)
	actual = lossTotal/newTotal
	print('Traing loos:',actual)
	print('Diff:',abs(actual - lastValue))
	f.write("Test lose:"+str(score)+'\n')
	f.write("Traing lose:"+str(actual)+'\n')
	if traing < actual :
		sys.exit()
	elif abs(actual - lastValue) < minBreak :
		modelo.save(filename)
		sys.exit()
	else:
		value = actual
		traing = actual
	return value,traing


value = 0
traing = 999
n=load_DataIncial()
modelo=ResNet50(True,"imagenet",None,imgHeight,imgWith)
modelo.compile(lr=0.001,loss='mean_squared_error',optimizer=optimizer)
#modelo.compile(loss='mse',optimizer=optimizer,metrics=['accuracy'])
#randomize = np.arange(n)
#np.random.shuffle(randomize)
# listImagenes, listVelLinear,listVelAngular = listImagenes[randomize], listVelLinear[randomize],listVelAngular[randomize]
print(nb_epoch,'epochs')
#random.shuffle(listLines)
for i in tqdm(range(0,nb_epoch)):
	#suffles every epoch
	#n=load_DataIncial()
	
	value,traing = trainEvaluate(modelo,n,i,value,traing)
	#cada epoca guarda el modelo
	modelo.save(filename)




