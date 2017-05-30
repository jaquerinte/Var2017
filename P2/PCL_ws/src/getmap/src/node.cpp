#include <ros/ros.h>
#include <pcl_ros/point_cloud.h>
#include <pcl/point_types.h>
#include <boost/foreach.hpp>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/visualization/cloud_viewer.h>
#include <pcl/filters/voxel_grid.h>

#include <vector>
#include <string>
#include <sstream>
#include <pcl/io/pcd_io.h>
#include <pcl/registration/transforms.h>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/keypoints/sift_keypoint.h>

#include <pcl/pcl_config.h>
#if PCL_MAJOR_VERSION >= 1 && PCL_MINOR_VERSION >= 7
#  include <pcl/keypoints/harris_3d.h>
#else
#  include <pcl/keypoints/harris_3d.h>
#endif

#include <pcl/ModelCoefficients.h>
#include <pcl/sample_consensus/method_types.h>
#include <pcl/sample_consensus/model_types.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <pcl/search/kdtree.h>
#include <pcl/segmentation/extract_clusters.h>
#include <pcl/features/fpfh_omp.h>
#include <pcl/features/pfh.h>
#include <pcl/features/pfhrgb.h>
#include <pcl/features/3dsc.h>
#include <pcl/features/shot_omp.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl/kdtree/impl/kdtree_flann.hpp>
#include <pcl/registration/transformation_estimation_svd.h>
#include <pcl/registration/icp.h>
#include <pcl/registration/correspondence_rejection_sample_consensus.h>
#include <pcl/common/transforms.h>
#include <pcl/surface/grid_projection.h>
#include <pcl/surface/gp3.h>
#include <pcl/surface/marching_cubes_hoppe.h>
#include <pcl/io/pcd_io.h>
#include <iostream>

#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <pcl/registration/icp.h>




pcl::PointCloud<pcl::PointXYZRGB>::Ptr acumulated (new pcl::PointCloud<pcl::PointXYZRGB>);
pcl::PointCloud<pcl::PointXYZRGB>::Ptr Last (new pcl::PointCloud<pcl::PointXYZRGB>);
bool first = true;

template<typename FeatureType>
class ICCVTutorial
{
  public:
    ICCVTutorial (boost::shared_ptr<pcl::Keypoint<pcl::PointXYZRGB, pcl::PointXYZI> > keypoint_detector,
                  typename pcl::Feature<pcl::PointXYZRGB, FeatureType>::Ptr feature_extractor,
                  typename pcl::PointCloud<pcl::PointXYZRGB>::Ptr sourceAnte,
                  typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr source,
                  typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr target);
    
    /**
     * @brief starts the event loop for the visualizer
     */
    void run ();
  protected:
    /**
     * @brief remove plane and select largest cluster as input object
     * @param input the input point cloud
     * @param segmented the resulting segmented point cloud containing only points of the largest cluster
     */
    void segmentation (typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr input, typename pcl::PointCloud<pcl::PointXYZRGB>::Ptr segmented) const;
    
    /**
     * @brief Detects key points in the input point cloud
     * @param input the input point cloud
     * @param keypoints the resulting key points. Note that they are not necessarily a subset of the input cloud
     */
    void detectKeypoints (typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr input, pcl::PointCloud<pcl::PointXYZI>::Ptr keypoints) const;
    
    /**
     * @brief extract descriptors for given key points
     * @param input point cloud to be used for descriptor extraction
     * @param keypoints locations where descriptors are to be extracted
     * @param features resulting descriptors
     */
    void extractDescriptors (typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr input, typename pcl::PointCloud<pcl::PointXYZI>::Ptr keypoints, typename pcl::PointCloud<FeatureType>::Ptr features);
    
    /**
     * @brief find corresponding features based on some metric
     * @param source source feature descriptors
     * @param target target feature descriptors 
     * @param correspondences indices out of the target descriptors that correspond (nearest neighbor) to the source descriptors
     */    
    void findCorrespondences (typename pcl::PointCloud<FeatureType>::Ptr source, typename pcl::PointCloud<FeatureType>::Ptr target, std::vector<int>& correspondences) const;
    
    /**
     * @brief  remove non-consistent correspondences
     */
    void filterCorrespondences ();
    
    /**
     * @brief calculate the initial rigid transformation from filtered corresponding keypoints
     */
    void determineInitialTransformation ();
    
    /**
     * @brief calculate the final rigid transformation using ICP over all points
     */
    void determineFinalTransformation ();

    /**
     * @brief reconstructs the surface from merged point clouds
     */
    void reconstructSurface ();

    /**
     * @brief callback to handle keyboard events
     * @param event object containing information about the event. e.g. type (press, release) etc.
     * @param cookie user defined data passed during registration of the callback
     */
    void keyboard_callback (const pcl::visualization::KeyboardEvent& event, void* cookie);
    
  private:
    //pcl::visualization::PCLVisualizer visualizer_;
    pcl::PointCloud<pcl::PointXYZI>::Ptr source_keypoints_;
    pcl::PointCloud<pcl::PointXYZI>::Ptr target_keypoints_;
    boost::shared_ptr<pcl::Keypoint<pcl::PointXYZRGB, pcl::PointXYZI> > keypoint_detector_;
    typename pcl::Feature<pcl::PointXYZRGB, FeatureType>::Ptr feature_extractor_;
    boost::shared_ptr<pcl::PCLSurfaceBase<pcl::PointXYZRGBNormal> > surface_reconstructor_;
    typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr source_;
    typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr target_;
    typename pcl::PointCloud<pcl::PointXYZRGB>::Ptr source_segmented_;
    typename pcl::PointCloud<pcl::PointXYZRGB>::Ptr target_segmented_;
    typename pcl::PointCloud<pcl::PointXYZRGB>::Ptr source_transformed_;
    typename pcl::PointCloud<pcl::PointXYZRGB>::Ptr source_registered_;
    typename pcl::PolygonMesh surface_;
    typename pcl::PointCloud<FeatureType>::Ptr source_features_;
    typename pcl::PointCloud<FeatureType>::Ptr target_features_;
    std::vector<int> source2target_;
    std::vector<int> target2source_;
    pcl::CorrespondencesPtr correspondences_;
    Eigen::Matrix4f initial_transformation_matrix_;
    Eigen::Matrix4f transformation_matrix_;
    bool show_source2target_;
    bool show_target2source_;
    bool show_correspondences;
};

template<typename FeatureType>
ICCVTutorial<FeatureType>::ICCVTutorial(boost::shared_ptr<pcl::Keypoint<pcl::PointXYZRGB, pcl::PointXYZI> >keypoint_detector,
                                        typename pcl::Feature<pcl::PointXYZRGB, FeatureType>::Ptr feature_extractor,
                                        typename pcl::PointCloud<pcl::PointXYZRGB>::Ptr sourceAnte,
                                        typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr source,
                                        typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr target)
: source_keypoints_ (new pcl::PointCloud<pcl::PointXYZI> ())
, target_keypoints_ (new pcl::PointCloud<pcl::PointXYZI> ())
, keypoint_detector_ (keypoint_detector)
, feature_extractor_ (feature_extractor)
, source_ (source)
, target_ (target)
, source_segmented_ (new pcl::PointCloud<pcl::PointXYZRGB>)
, target_segmented_ (new pcl::PointCloud<pcl::PointXYZRGB>)
, source_transformed_ (new pcl::PointCloud<pcl::PointXYZRGB>)
, source_registered_ (new pcl::PointCloud<pcl::PointXYZRGB>)
, source_features_ (new pcl::PointCloud<FeatureType>)
, target_features_ (new pcl::PointCloud<FeatureType>)
, correspondences_ (new pcl::Correspondences)
, show_source2target_ (false)
, show_target2source_ (false)
, show_correspondences (false)
{
  //visualizer_.registerKeyboardCallback(&ICCVTutorial::keyboard_callback, *this, 0); 

  pcl::PointCloud<pcl::PointXYZRGB>::Ptr source_dst (new pcl::PointCloud<pcl::PointXYZRGB>);
  //compiamos las nubes para quitar los punteros constantes
  *source_segmented_ = *source_;
  *target_segmented_ = *target_;
  //Sacamos los Keypoints del source y del target 
  detectKeypoints (source_segmented_, source_keypoints_);
  detectKeypoints (target_segmented_, target_keypoints_);
  //Extraemos los descriptores del source y del target 
  extractDescriptors (source_segmented_, source_keypoints_, source_features_);
  extractDescriptors (target_segmented_, target_keypoints_, target_features_);
  //Sacamos las correspondecias entre ambas 
  findCorrespondences (source_features_, target_features_, source2target_);
  findCorrespondences (target_features_, source_features_, target2source_);
  // teniendo las correspondencias de ambos descartamos las que no son posibles 
  filterCorrespondences ();
  //determinamos la trasformacion inicial 
  determineInitialTransformation ();
  //aplicamos ICP a las nuebes
  determineFinalTransformation ();
  
  if(first){
  //*acumulated = *source_transformed_;
  //si es la primea la imagen la mete en el mapa gobal
  	*acumulated = *source_registered_;
  first = false;
  }else{
  //*acumulated += *source_transformed_;
  //Last = source_transformed_;
  //añadimos al mapa la imagen 
  *acumulated += *source_registered_;
  //guaramos la anterior transformada asi aguardamos la matriz de trasformacion global 
  Last = source_registered_;
  
}
  
  
}

template<typename FeatureType>
void ICCVTutorial<FeatureType>::segmentation (typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr source, typename pcl::PointCloud<pcl::PointXYZRGB>::Ptr segmented) const
{
  cout << "segmentation..." << std::flush;
  // fit plane and keep points above that plane
  pcl::ModelCoefficients::Ptr coefficients (new pcl::ModelCoefficients);
  pcl::PointIndices::Ptr inliers (new pcl::PointIndices);
  // Create the segmentation object
  pcl::SACSegmentation<pcl::PointXYZRGB> seg;
  // Optional
  seg.setOptimizeCoefficients (true);
  // Mandatory
  seg.setModelType (pcl::SACMODEL_PLANE);
  seg.setMethodType (pcl::SAC_RANSAC);
  seg.setDistanceThreshold (0.02);

  seg.setInputCloud (source);
  seg.segment (*inliers, *coefficients);
  
  pcl::ExtractIndices<pcl::PointXYZRGB> extract;
  extract.setInputCloud (source);
  extract.setIndices (inliers);
  extract.setNegative (true);

  extract.filter (*segmented);
  std::vector<int> indices;
  pcl::removeNaNFromPointCloud(*segmented, *segmented, indices);
  cout << "OK" << endl;
  
  cout << "clustering..." << std::flush;
  // euclidean clustering
  typename pcl::search::KdTree<pcl::PointXYZRGB>::Ptr tree (new pcl::search::KdTree<pcl::PointXYZRGB>);
  tree->setInputCloud (segmented);

  std::vector<pcl::PointIndices> cluster_indices;
  pcl::EuclideanClusterExtraction<pcl::PointXYZRGB> clustering;
  clustering.setClusterTolerance (0.02); // 2cm
  clustering.setMinClusterSize (1000);
  clustering.setMaxClusterSize (250000);
  clustering.setSearchMethod (tree);
  clustering.setInputCloud(segmented);
  clustering.extract (cluster_indices);
  
  if (cluster_indices.size() > 0)//use largest cluster
  {
    cout << cluster_indices.size() << " clusters found";
    if (cluster_indices.size() > 1)
      cout <<" Using largest one...";
    cout << endl;
    typename pcl::IndicesPtr indices (new std::vector<int>);
    *indices = cluster_indices[0].indices;
    extract.setInputCloud (segmented);
    extract.setIndices (indices);
    extract.setNegative (false);

    extract.filter (*segmented);
  }
}

template<typename FeatureType>
void ICCVTutorial<FeatureType>::detectKeypoints (typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr input, pcl::PointCloud<pcl::PointXYZI>::Ptr keypoints) const
{
  cout << "keypoint detection..." << std::flush;
  keypoint_detector_->setInputCloud(input);
  keypoint_detector_->setSearchSurface(input);
  keypoint_detector_->compute(*keypoints);
  cout << "OK. keypoints found: " << keypoints->points.size() << endl;
}

template<typename FeatureType>
void ICCVTutorial<FeatureType>::extractDescriptors (typename pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr input, typename pcl::PointCloud<pcl::PointXYZI>::Ptr keypoints, typename pcl::PointCloud<FeatureType>::Ptr features)
{
  typename pcl::PointCloud<pcl::PointXYZRGB>::Ptr kpts(new pcl::PointCloud<pcl::PointXYZRGB>);
  kpts->points.resize(keypoints->points.size());
  
  pcl::copyPointCloud(*keypoints, *kpts);
          
  typename pcl::FeatureFromNormals<pcl::PointXYZRGB, pcl::Normal, FeatureType>::Ptr feature_from_normals = boost::dynamic_pointer_cast<pcl::FeatureFromNormals<pcl::PointXYZRGB, pcl::Normal, FeatureType> > (feature_extractor_);
  
  feature_extractor_->setSearchSurface(input);
  feature_extractor_->setInputCloud(kpts);
  
  if (feature_from_normals)
  //if (boost::dynamic_pointer_cast<typename pcl::FeatureFromNormals<pcl::PointXYZRGB, pcl::Normal, FeatureType> > (feature_extractor_))
  {
   // cout << "normal estimation..." << std::flush;
    typename pcl::PointCloud<pcl::Normal>::Ptr normals (new  pcl::PointCloud<pcl::Normal>);
    pcl::NormalEstimation<pcl::PointXYZRGB, pcl::Normal> normal_estimation;
    normal_estimation.setSearchMethod (pcl::search::Search<pcl::PointXYZRGB>::Ptr (new pcl::search::KdTree<pcl::PointXYZRGB>));
    normal_estimation.setRadiusSearch (0.01);
    normal_estimation.setInputCloud (input);
    normal_estimation.compute (*normals);
    feature_from_normals->setInputNormals(normals);
  //  cout << "OK" << endl;
  }

  //cout << "descriptor extraction..." << std::flush;
  feature_extractor_->compute (*features);
 // cout << "OK" << endl;
}

template<typename FeatureType>
void ICCVTutorial<FeatureType>::findCorrespondences (typename pcl::PointCloud<FeatureType>::Ptr source, typename pcl::PointCloud<FeatureType>::Ptr target, std::vector<int>& correspondences) const
{
  //cout << "correspondence assignment..." << std::flush;
  correspondences.resize (source->size());

  // Use a KdTree to search for the nearest matches in feature space
  pcl::KdTreeFLANN<FeatureType> descriptor_kdtree;
  descriptor_kdtree.setInputCloud (target);

  // Find the index of the best match for each keypoint, and store it in "correspondences_out"
  const int k = 1;
  std::vector<int> k_indices (k);
  std::vector<float> k_squared_distances (k);
  for (size_t i = 0; i < source->size (); ++i)
  {
    descriptor_kdtree.nearestKSearch (*source, i, k, k_indices, k_squared_distances);
    correspondences[i] = k_indices[0];
  }
  //cout << "OK" << endl;
}

template<typename FeatureType>
void ICCVTutorial<FeatureType>::filterCorrespondences ()
{
  //cout << "correspondence rejection..." << std::flush;
  std::vector<std::pair<unsigned, unsigned> > correspondences;
  for (unsigned cIdx = 0; cIdx < source2target_.size (); ++cIdx)
    if (target2source_[source2target_[cIdx]] == cIdx)
      correspondences.push_back(std::make_pair(cIdx, source2target_[cIdx]));
  
  correspondences_->resize (correspondences.size());
  for (unsigned cIdx = 0; cIdx < correspondences.size(); ++cIdx)
  {
    (*correspondences_)[cIdx].index_query = correspondences[cIdx].first;
    (*correspondences_)[cIdx].index_match = correspondences[cIdx].second;
  }
  
  pcl::registration::CorrespondenceRejectorSampleConsensus<pcl::PointXYZI> rejector;
  rejector.setInputCloud(source_keypoints_);
  rejector.setTargetCloud(target_keypoints_);
  rejector.setInputCorrespondences(correspondences_);
  rejector.getCorrespondences(*correspondences_);
  //cout << "OK" << endl;
}

template<typename FeatureType>
void ICCVTutorial<FeatureType>::determineInitialTransformation ()
{
 // cout << "initial alignment..." << std::flush;
  pcl::registration::TransformationEstimation<pcl::PointXYZI, pcl::PointXYZI>::Ptr transformation_estimation (new pcl::registration::TransformationEstimationSVD<pcl::PointXYZI, pcl::PointXYZI>);
  
  transformation_estimation->estimateRigidTransformation (*source_keypoints_, *target_keypoints_, *correspondences_, initial_transformation_matrix_);
  
  pcl::transformPointCloud(*source_segmented_, *source_transformed_, initial_transformation_matrix_);
  //cout << "OK" << endl;
}

template<typename FeatureType>
void ICCVTutorial<FeatureType>::determineFinalTransformation ()
{
  //cout << "final registration..." << std::flush;
  pcl::Registration<pcl::PointXYZRGB, pcl::PointXYZRGB>::Ptr registration (new pcl::IterativeClosestPoint<pcl::PointXYZRGB, pcl::PointXYZRGB>);
  registration->setInputCloud(source_transformed_);
  //registration->setInputCloud(source_segmented_);
  registration->setInputTarget (target_segmented_);
  registration->setMaxCorrespondenceDistance(0.05);
  registration->setRANSACOutlierRejectionThreshold (0.05);
  registration->setTransformationEpsilon (0.000001);
  registration->setMaximumIterations (1000);
  registration->align(*source_registered_);
  transformation_matrix_ = registration->getFinalTransformation();
  //cout << "OK" << endl;
}

template<typename FeatureType>
void ICCVTutorial<FeatureType>::reconstructSurface ()
{
 // cout << "surface reconstruction..." << std::flush;
  // merge the transformed and the target point cloud
  pcl::PointCloud<pcl::PointXYZRGB>::Ptr merged (new pcl::PointCloud<pcl::PointXYZRGB>);
  *merged = *source_transformed_;
  *merged += *target_segmented_;
  
  // apply grid filtering to reduce amount of points as well as to make them uniform distributed
  pcl::VoxelGrid<pcl::PointXYZRGB> voxel_grid;
  voxel_grid.setInputCloud(merged);
  voxel_grid.setLeafSize(0.002, 0.002, 0.002);
  voxel_grid.setDownsampleAllData(true);
  voxel_grid.filter(*merged);

  pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr vertices (new pcl::PointCloud<pcl::PointXYZRGBNormal>);
  pcl::copyPointCloud(*merged, *vertices);

  pcl::NormalEstimation<pcl::PointXYZRGB, pcl::PointXYZRGBNormal> normal_estimation;
  normal_estimation.setSearchMethod (pcl::search::Search<pcl::PointXYZRGB>::Ptr (new pcl::search::KdTree<pcl::PointXYZRGB>));
  normal_estimation.setRadiusSearch (0.01);
  normal_estimation.setInputCloud (merged);
  normal_estimation.compute (*vertices);
  
  pcl::search::KdTree<pcl::PointXYZRGBNormal>::Ptr tree (new pcl::search::KdTree<pcl::PointXYZRGBNormal>);
  tree->setInputCloud (vertices);

  surface_reconstructor_->setSearchMethod(tree);
  surface_reconstructor_->setInputCloud(vertices);
  surface_reconstructor_->reconstruct(surface_);
 // cout << "OK" << endl;
}

template<typename FeatureType>
void ICCVTutorial<FeatureType>::run()
{
  //visualizer_.spin ();
}
void simpleVis ()
{
	// Crea el visualizador
  	pcl::visualization::CloudViewer viewer ("Simple Cloud Viewer");
	while(!viewer.wasStopped())
	{
		
	//mientras no se cierre muestre la nube de puntos 
	  viewer.showCloud (acumulated);
	
	//Para el hilo 1000 milisegundos 
	  boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
	}

}


void callback(const pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr& msg)
{
	//nube original 
	pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZRGB>(*msg));
	//nube filtrada
	pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud_filtered (new pcl::PointCloud<pcl::PointXYZRGB>);


	//cout << "Puntos capturados: " << cloud->size() << endl;
	//Pasamos la nube por el voxelGrid
	pcl::VoxelGrid<pcl::PointXYZRGB > vGrid;
	vGrid.setInputCloud (cloud);
	//establecemos el tamño del voxel
	vGrid.setLeafSize (0.05f, 0.05f, 0.05f);
	vGrid.filter (*cloud_filtered);
	//si es la primera vuelta cargamos Last en la memoria
	if(Last->size() == 0){
	//	cout << "last empy"<<endl;
		Last = cloud_filtered;
		//acumulated = cloud_filtered;
	}
	else{
	pcl::PointCloud<pcl::PointXYZRGB>::Ptr sourceAnte (new pcl::PointCloud<pcl::PointXYZRGB>);
  
  	//creamos el keypoint detector
  	boost::shared_ptr<pcl::Keypoint<pcl::PointXYZRGB, pcl::PointXYZI> > keypoint_detector;
  
 	//Seleccionamos Sift para la extracción de Keypoints 
    /*pcl::SIFTKeypoint<pcl::PointXYZRGB, pcl::PointXYZI>* sift3D = new pcl::SIFTKeypoint<pcl::PointXYZRGB, pcl::PointXYZI>;
    sift3D->setScales(0.01, 3, 4);
    sift3D->setMinimumContrast(0.0);
    keypoint_detector.reset(sift3D);*/

    pcl::HarrisKeypoint3D<pcl::PointXYZRGB,pcl::PointXYZI>* harris3D = new pcl::HarrisKeypoint3D<pcl::PointXYZRGB,pcl::PointXYZI> (pcl::HarrisKeypoint3D<pcl::PointXYZRGB,pcl::PointXYZI>::HARRIS);
    harris3D->setNonMaxSupression(true);
    harris3D->setRadius (0.01);
    harris3D->setRadiusSearch (0.01);
    keypoint_detector.reset(harris3D);

    //harris3D->setMethod(pcl::HarrisKeypoint3D<pcl::PointXYZRGB,pcl::PointXYZI>::TOMASI);
    harris3D->setMethod(pcl::HarrisKeypoint3D<pcl::PointXYZRGB,pcl::PointXYZI>::NOBLE);


  	//seleccionamos el descriptor en nustro caso PFHRGBSignature
    pcl::Feature<pcl::PointXYZRGB, pcl::PFHRGBSignature250>::Ptr feature_extractor (new pcl::PFHRGBEstimation<pcl::PointXYZRGB, pcl::Normal, pcl::PFHRGBSignature250>);
    feature_extractor->setKSearch(50);
    //llamada a la funcion de calculo de las nubes
    ICCVTutorial<pcl::PFHRGBSignature250> tutorial (keypoint_detector, feature_extractor, sourceAnte,cloud_filtered,Last);

      
	}

	
	//cout << "end callback"<<endl;
	
	
}


int 
main (int argc, char ** argv)
{
  
// inicializadores de ros
  ros::init(argc, argv, "sub_pcl");
  ros::NodeHandle nh;
 // se llama al callback para procesar la nube de puntos
  ros::Subscriber sub = nh.subscribe<pcl::PointCloud<pcl::PointXYZRGB> >("/camera/depth/points", 1, callback);
//hilo que procesa la vista
  boost::thread t(simpleVis);
//bucle sin fin para el funcionamiento de ros
 while(ros::ok())
  {
	ros::spinOnce();
  }



	
  
  
  return (0);
}
