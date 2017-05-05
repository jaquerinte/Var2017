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




void simpleVis ()
{
	 pcl::visualization::PCLVisualizer viz; 
	 pcl::PointCloud<pcl::PointWithScale>::Ptr keypoints (new pcl::PointCloud<pcl::PointWithScale>);
	 pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZRGB>); 
	 if (pcl::io::loadPCDFile<pcl::PointXYZRGB> ("./PointCloudCaptures/capture_8.pcd", *cloud) == -1){  //* load the file 
    		PCL_ERROR ("Couldn't read the pcd file  \n"); 
  		} 
	// Crea el visualizador
  	//pcl::visualization::CloudViewer viewer ("Cloud Viewer");
  	
  	pcl::SIFTKeypoint<pcl::PointXYZRGB, pcl::PointWithScale> sift;
  	// Use  KdTree to perform neighborhood searches
	sift.setSearchMethod(pcl::search::KdTree<pcl::PointXYZRGB>::Ptr(new pcl::search::KdTree<pcl::PointXYZRGB>)); 
	sift.setScales (min_scale, n_octaves, n_scales_per_octave);
	sift.setMinimumContrast (min_contrast);
	sift.setInputCloud (cloud);

	pcl::PointCloud<pcl::PointWithScale>::Ptr keypoints_out_target(new pcl::PointCloud<pcl::PointWithScale>); 
    sift.compute(*keypoints_out_target); 
	pcl::PointCloud<pcl::PointXYZ>::Ptr keypoints_target(new pcl::PointCloud<pcl::PointXYZ>); 
    pcl::copyPointCloud(*keypoints_out_target, *keypoints_target); 

        //Visualize point cloud and keypoints 
        
	viz.addPointCloud(cloud, "target"); 
    viz.addPointCloud(keypoints_target, "keypoint"); 
    viz.setPointCloudRenderingProperties(pcl::visualization::PCL_VISUALIZER_COLOR, 255, 0, 0, "keypoint"); 


  	//visualizo 
	while(!viz.wasStopped())
	{
	//mientras no se cierre muestre la nube de puntos 
	  //viewer.showCloud (cloud);

        
        viz.spinOnce (100);
	  //viewerNormal.showCloud(cloud_normals)
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