# Importamos los paquetes necesarios
import numpy as np
import imutils
import cv2

class Stitcher:
	def __init__(self):
		# Determinamos si utilizamos OpenCV v3.X
		self.isv3 = imutils.is_cv3()

	def stitch(self, images, ratio=0.75, reprojThresh=4.0,
		showMatches=False):
		# Desempaquetamos las imagenes, detectamos los keypointsy extraemos los descriptores invariantes de ellos
		(imageB, imageA) = images
		
		(kpsA, featuresA) = self.detectAndDescribe(imageA)	
		(kpsB, featuresB) = self.detectAndDescribe(imageB)
		
		# Obtenemos los matches entre las dos imagenes
		M = self.matchKeypoints(kpsA, kpsB,
			featuresA, featuresB, ratio, reprojThresh)

		# Si los matches es None, entonces no hay suficientes matches para crear la panoramica
		if M is None:
			return None

		# Sino, aplicamos aplicamos la deformacion para unir las imagenes en una misma panoramica
		(matches, H, status) = M
		result = cv2.warpPerspective(imageA, H,
			(imageA.shape[1] + imageB.shape[1], imageA.shape[0]))
		result[0:imageB.shape[0], 0:imageB.shape[1]] = imageB

		# Comprobamos si los matches deben ser mostrados o no
		if showMatches:
			vis = self.drawMatches(imageA, imageB, kpsA, kpsB, matches,
				status)

			# Devuelve una tupla con el resultado de la transformacion y la visualizacion de sus puntos comunes
			return (result, vis)

		# Devuelve la imagen transformada
		return result

	# Obtiene los keyPoints y caracteristicas de una imagen en cuestion
	def detectAndDescribe(self, image):
		# Convertimos la imagen a escala de grises por si utilizamos OpenCV 2.4.X
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		# Comprobamos si usamon OpenCV 3.X
		if self.isv3:
			# Detectamos y extraemos caracteristicas de la imagen

			#descriptor = cv2.xfeatures2d.SIFT_create() # Para SIFT_create() y SURF_create()
			descriptor = cv2.ORB_create() # Para ORB_create()
			(kps, features) = descriptor.detectAndCompute(image, None)

		# Sino, utilizamos OpenCV 2.4.X
		else:
			# Detectamos keypoints de la imagen
			detector = cv2.FeatureDetector_create("ORB")
			kps = detector.detect(gray)

			# Extraemos caracteristicas de la imagen
			extractor = cv2.DescriptorExtractor_create("ORB")
			(kps, features) = extractor.compute(gray, kps)
		# Convertimos los keypoints de objetos Keypoint a arrays de NumPy
		kps = np.float32([kp.pt for kp in kps])
		# Devuelve una tupla de keypoints y caracteristicas
		return (kps,features)

	# Realiza el calculo de la matriz de transformacion teniendo en cuenta los puntos obtenidos con detectAndDescribe
	def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB,
		ratio, reprojThresh):
		#computa los matches de cada imagen e inicializa la lista de  matches actual
		matcher = cv2.DescriptorMatcher_create("BruteForce")
		rawMatches = matcher.knnMatch(featuresA, featuresB, 2) #Calcula los matches de la derecha con la izquierda
		matches = []

		######################################
		# Bucle de matches
		for m in rawMatches:
			# Nos aseguramos que la distancia se encuentra a cierto ratio de cada una (p.e. Lowe's ratio test)
			if len(m) == 2 and m[0].distance < m[1].distance * ratio:
				matches.append((m[0].trainIdx, m[0].queryIdx))

		# Para calcular la homografia deben haber al menos 4 matches
		if len(matches) > 4:
			# Construimos 2 sets de puntos
			ptsA = np.float32([kpsA[i] for (_, i) in matches])
			ptsB = np.float32([kpsB[i] for (i, _) in matches])

			# Calculamos la homografia entre los dos conjuntos de puntos utilizando RANSAC
			(H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
				reprojThresh)

			# Devuelve los matches junto con la matriz de homografia y el estado de cada punto coincidente
			return (matches, H, status)

		# Sino, no se puede computar ninguna homografia
		return None

	# Muestra los matches creando lineas entre los matches encontrados
	def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
		# Inicializamos la imagen en la que mostraremos los matches
		(hA, wA) = imageA.shape[:2]
		(hB, wB) = imageB.shape[:2]
		vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
		vis[0:hA, 0:wA] = imageA
		vis[0:hB, wA:] = imageB

		# Bucle de matches
		for ((trainIdx, queryIdx), s) in zip(matches, status):
			#Solo procesa el match si el keypoint coincide correctamente
			if s == 1:
				# Dibuja el match
				ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
				ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
				cv2.line(vis, ptA, ptB, (0, 255, 0), 1)

		# Devuelve la visualizacion
		return vis