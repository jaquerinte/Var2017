#include <ros/ros.h>
#include <pcl_ros/point_cloud.h>
#include <pcl/point_types.h>
#include <boost/foreach.hpp>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/visualization/cloud_viewer.h>
#include <pcl/filters/voxel_grid.h>

#include <pcl/io/pcd_io.h>
#include <iostream>

#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <pcl/common/io.h>
#include <pcl/keypoints/sift_keypoint.h>
#include <pcl/features/normal_3d.h>
#include <pcl/features/pfh.h>

#include <pcl/registration/correspondence_estimation.h>
#include <pcl/registration/correspondence_rejection_sample_consensus.h>
#include <pcl/registration/transformation_estimation_svd.h>



const float min_scale = 0.01f;
const int n_octaves = 3;
const int n_scales_per_octave = 4;
const float min_contrast = 0.001f;
const float normal_radius = 0.03f;
const float feature_radius = 0.05f;

void featuresDetector(pcl::PointCloud<pcl::PointXYZRGB>::Ptr &cloud,pcl::PointCloud<pcl::Normal>::Ptr &normals_out){
	pcl::NormalEstimation<pcl::PointXYZRGB, pcl::Normal> norm_est;
	norm_est.setSearchMethod(pcl::search::KdTree<pcl::PointXYZRGB>::Ptr(new pcl::search::KdTree<pcl::PointXYZRGB>));
	norm_est.setRadiusSearch (normal_radius);
	norm_est.setInputCloud (cloud);
	norm_est.setSearchSurface (cloud);
	norm_est.compute (*normals_out);
}

void keypointsDetector(pcl::PointCloud<pcl::PointXYZRGB>::Ptr &cloud,pcl::PointCloud<pcl::PointWithScale>::Ptr &keypoints_out){
	pcl::SIFTKeypoint<pcl::PointXYZRGB, pcl::PointWithScale> sift;
  	// Use  KdTree to perform neighborhood searches
	sift.setSearchMethod(pcl::search::KdTree<pcl::PointXYZRGB>::Ptr(new pcl::search::KdTree<pcl::PointXYZRGB>)); 
	sift.setScales (min_scale, n_octaves, n_scales_per_octave);
	sift.setMinimumContrast (min_contrast);
	sift.setInputCloud (cloud);
    sift.compute(*keypoints_out); 
}

void compute_PFH_features_at_keypoints(pcl::PointCloud<pcl::PointXYZRGB>::Ptr &cloud,pcl::PointCloud<pcl::Normal>::Ptr &normals,
	pcl::PointCloud<pcl::PointWithScale>::Ptr &keypoints,pcl::PointCloud<pcl::PFHSignature125>::Ptr &descriptors_out){

	pcl::PFHEstimation<pcl::PointXYZRGB, pcl::Normal, pcl::PFHSignature125> pfh_est;
	pfh_est.setSearchMethod(pcl::search::KdTree<pcl::PointXYZRGB>::Ptr(new pcl::search::KdTree<pcl::PointXYZRGB>)); 
	pfh_est.setRadiusSearch (feature_radius);
	pcl::PointCloud<pcl::PointXYZRGB>::Ptr keypoints_xyzrgb(new pcl::PointCloud<pcl::PointXYZRGB>);
	pcl::copyPointCloud (*keypoints, *keypoints_xyzrgb);
	// Use all of the points for analyzing the local structure of the cloud
	pfh_est.setSearchSurface (cloud);
	pfh_est.setInputNormals (normals);
	// But only compute features at the keypoints
    pfh_est.setInputCloud (keypoints_xyzrgb);
    // Compute the features
	pfh_est.compute (*descriptors_out);

}

void getDescriptor(pcl::PointCloud<pcl::PointXYZRGB>::Ptr &cloud,pcl::PointCloud<pcl::PFHSignature125>::Ptr &descriptors_out,pcl::PointCloud<pcl::PointWithScale>::Ptr &keypoints_out){
	 pcl::PointCloud<pcl::Normal>::Ptr normals_out (new pcl::PointCloud<pcl::Normal>);
	 

	featuresDetector(cloud,normals_out);
  	//compute sift detector 
	keypointsDetector(cloud,keypoints_out);
	//keypoints and descriptor
	compute_PFH_features_at_keypoints(cloud,normals_out,keypoints_out,descriptors_out);
}

boost::shared_ptr<pcl::Correspondences>  correspondencesPFH(pcl::PointCloud<pcl::PFHSignature125>::Ptr &desc_pfh_1, pcl::PointCloud<pcl::PFHSignature125>::Ptr &desc_pfh_2,pcl::PointCloud<pcl::PointXYZ>::Ptr keypoint1,pcl::PointCloud<pcl::PointXYZ>::Ptr keypoint2){

	boost::shared_ptr<pcl::Correspondences> cor_all (new pcl::Correspondences);
	boost::shared_ptr<pcl::Correspondences> cor_inliers (new pcl::Correspondences);

	pcl::registration::CorrespondenceEstimation<pcl::PFHSignature125, pcl::PFHSignature125> corEst; 
	pcl::registration::CorrespondenceRejectorSampleConsensus<pcl::PointXYZ> sac; 

	corEst.setInputSource (desc_pfh_1); 
	corEst.setInputTarget (desc_pfh_2); 	
	corEst.determineReciprocalCorrespondences (*cor_all);

	sac.setInputSource (keypoint1); 
	sac.setInputTarget (keypoint2); 
	sac.setInlierThreshold (0.1); 
	sac.setMaximumIterations (1500); 
	sac.setInputCorrespondences (cor_all);	
	sac.getCorrespondences (*cor_inliers);

	return cor_inliers; 



}

Eigen::Matrix4f rigidTransformation(pcl::PointCloud<pcl::PointXYZ>::Ptr &keypoints1, pcl::PointCloud<pcl::PointXYZ>::Ptr &keypoints2, boost::shared_ptr<pcl::Correspondences> &cor_inliers){

 		Eigen::Matrix4f transform; 
        pcl::registration::TransformationEstimationSVD<pcl::PointXYZ, pcl::PointXYZ> transformSVD;

        transformSVD.estimateRigidTransformation (*keypoints1, *keypoints2, *cor_inliers, transform); 

        return transform;

}

void simpleVis ()
{	
	//visualicer
	 pcl::visualization::PCLVisualizer viz; 
	 pcl::visualization::PCLVisualizer viz2; 
	//cloud
	 pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZRGB>);
	 pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud2 (new pcl::PointCloud<pcl::PointXYZRGB>);
	 //Keypoints 
	 pcl::PointCloud<pcl::PointWithScale>::Ptr keypoints_out (new pcl::PointCloud<pcl::PointWithScale>);
	 pcl::PointCloud<pcl::PointWithScale>::Ptr keypoints_out2 (new pcl::PointCloud<pcl::PointWithScale>);
	 //Descriptors
	 pcl::PointCloud<pcl::PFHSignature125>::Ptr descriptors_out (new pcl::PointCloud<pcl::PFHSignature125>);
	 pcl::PointCloud<pcl::PFHSignature125>::Ptr descriptors_out2 (new pcl::PointCloud<pcl::PFHSignature125>);
	//* load the file 
	 if (pcl::io::loadPCDFile<pcl::PointXYZRGB> ("./PointCloudCaptures/capture_5.pcd", *cloud) == -1){  
    		PCL_ERROR ("Couldn't read the pcd file  \n"); 
  		} 
  	if (pcl::io::loadPCDFile<pcl::PointXYZRGB> ("./PointCloudCaptures/capture_6.pcd", *cloud2) == -1){  
    		PCL_ERROR ("Couldn't read the pcd file  \n"); 
  		} 
  	//cloud loaded 
  	//compute detector
  	getDescriptor(cloud,descriptors_out,keypoints_out);
  	getDescriptor(cloud2,descriptors_out2,keypoints_out2);
  	//trasform key points 
  	pcl::PointCloud<pcl::PointXYZ>::Ptr keypoints_target (new pcl::PointCloud<pcl::PointXYZ>);
  	pcl::PointCloud<pcl::PointXYZ>::Ptr keypoints_target2 (new pcl::PointCloud<pcl::PointXYZ>);
  	pcl::copyPointCloud(*keypoints_out,*keypoints_target);
  	pcl::copyPointCloud(*keypoints_out2,*keypoints_target2);



  	boost::shared_ptr<pcl::Correspondences> corresp = correspondencesPFH(descriptors_out,descriptors_out2,keypoints_target,keypoints_target2);
  	Eigen::Matrix4f transf_matrix = rigidTransformation(keypoints_target,keypoints_target2,corresp);

  	pcl::transformPointCloud (*cloud, *cloud2, transf_matrix); 
    //Visualize point cloud and keypoints 

    //pcl::visualization::PointCloudColorHandlerCustom<pcl::PointXYZ> cloud_1_color_handler (cloud, 0, 255, 0);
	//pcl::visualization::PointCloudColorHandlerCustom<pcl::PointXYZ> cloud_2_color_handler (cloud2, 255, 0, 0);

	//viz.addPointCloud (cloud, cloud_1_color_handler, "cloud_1");
	//viz.addPointCloud (cloud2, cloud_2_color_handler, "cloud_2");
	viz.addPointCloud(cloud, "target"); 
	viz2.addPointCloud(cloud2, "target2"); 
    //print points for features
    cout << "Puntos del detector: " << descriptors_out->size() << endl;
    cout << "Puntos del detector: " << descriptors_out2->size() << endl;
  	//visualizo 
	while(!viz.wasStopped())
	{
        viz.spinOnce ();
        viz2.spinOnce ();
	//Para el hilo 1000 milisegundos 
	  boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
	}
}


int main(int argc, char** argv)
{
  ros::init(argc, argv, "pcd_viewer");
  ros::NodeHandle nh;
  boost::thread t(simpleVis);

  while(ros::ok())
  {
	ros::spinOnce();
  }

}