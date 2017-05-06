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
#include <pcl/kdtree/kdtree_flann.h>


const float min_scale = 0.01f;
const int n_octaves = 3;
const int n_scales_per_octave = 4;
const float min_contrast = 0.001f;
const float normal_radius = 0.03f;

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

void simpleVis ()
{	
	//visualicer
	 pcl::visualization::PCLVisualizer viz; 
	//features 
	 pcl::PointCloud<pcl::Normal>::Ptr normals_out (new pcl::PointCloud<pcl::Normal>);
	//keypoints 
	 pcl::PointCloud<pcl::PointWithScale>::Ptr keypoints_out (new pcl::PointCloud<pcl::PointWithScale>);
	//cloud
	 pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZRGB>); 
	//* load the file 
	 if (pcl::io::loadPCDFile<pcl::PointXYZRGB> ("./PointCloudCaptures/capture_4.pcd", *cloud) == -1){  
    		PCL_ERROR ("Couldn't read the pcd file  \n"); 
  		} 
  	//cloud loaded 
  	//compute normals detector
  	featuresDetector(cloud,normals_out);
  	//compute sift detector 
	keypointsDetector(cloud,keypoints_out);
	//create an axiliar cloud for visualization purpose
	pcl::PointCloud<pcl::PointXYZ>::Ptr keypoints_target(new pcl::PointCloud<pcl::PointXYZ>);
	//pcl::PointCloud<pcl::PointXYZ>::Ptr normals_target(new pcl::PointCloud<pcl::PointXYZ>);
	//copy the cloud
    pcl::copyPointCloud(*keypoints_out, *keypoints_target); 
    //pcl::copyPointCloud(*normals_out,*normals_target);

    //Visualize point cloud and keypoints 
	viz.addPointCloud(cloud, "target"); 
    viz.addPointCloud(keypoints_target, "keypoint"); 
    viz.addPointCloudNormals<pcl::PointXYZRGB, pcl::Normal>(cloud, normals_out, 10, 0.05, "normals");
    //viz.addPointCloud(normals_target,"normals");
    viz.setPointCloudRenderingProperties(pcl::visualization::PCL_VISUALIZER_COLOR, 255, 0, 0, "keypoint"); 
    //print points for features
    cout << "Puntos de normales: " << normals_out->size() << endl;
    //print points for detector
    cout << "Puntos de sift: " << keypoints_out->size() << endl;
  	//visualizo 
	while(!viz.wasStopped())
	{
        viz.spinOnce ();
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