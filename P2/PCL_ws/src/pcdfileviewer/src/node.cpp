#include <ros/ros.h>
#include <pcl_ros/point_cloud.h>
#include <pcl/point_types.h>
#include <boost/foreach.hpp>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/visualization/cloud_viewer.h>
#include <pcl/filters/voxel_grid.h>

#include <pcl/io/pcd_io.h>
#include <iostream>
#include <pcl/keypoints/sift_keypoint.h>

#include <pcl/kdtree/kdtree_flann.h>


const float min_scale = 0.01f;
const int n_octaves = 3;
const int n_scales_per_octave = 4;
const float min_contrast = 0.001f;



void visualize_keypoints (const pcl::PointCloud<pcl::PointXYZRGB>::Ptr points,
                          const pcl::PointCloud<pcl::PointWithScale>::Ptr keypoints)
{
  // Add the points to the vizualizer
  pcl::visualization::PCLVisualizer viz;
  viz.addPointCloud (points, "points");

  // Draw each keypoint as a sphere
  for (size_t i = 0; i < keypoints->size (); ++i)
  {
    // Get the point data
    const pcl::PointWithScale & p = keypoints->points[i];

    // Pick the radius of the sphere *
    float r = 2 * p.scale;
    // * Note: the scale is given as the standard deviation of a Gaussian blur, so a
    //   radius of 2*p.scale is a good illustration of the extent of the keypoint

    // Generate a unique string for each sphere
    std::stringstream ss ("keypoint");
    ss << i;

    // Add a sphere at the keypoint
    viz.addSphere (p, 2*p.scale, 1.0, 0.0, 0.0, ss.str ());
  }

  // Give control over to the visualizer
  viz.spin ();
}


void simpleVis ()
{
	 pcl::PointCloud<pcl::PointWithScale>::Ptr keypoints (new pcl::PointCloud<pcl::PointWithScale>);
	 pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZRGB>); 
	 if (pcl::io::loadPCDFile<pcl::PointXYZRGB> ("./PointCloudCaptures/capture_3.pcd", *cloud) == -1){  //* load the file 
    		PCL_ERROR ("Couldn't read the pcd file  \n"); 
  		} 
	// Crea el visualizador
  	pcl::visualization::CloudViewer viewer ("Cloud Viewer");
  	pcl::SIFTKeypoint<pcl::PointXYZRGB, pcl::PointWithScale> sift;

  	//pcl::PointCloud<pcl::PointWithScale> result;
	//sift.setSearchMethod (pcl::KdTreeFLANN<pcl::PointXYZRGB>::Ptr (new pcl::KdTreeFLANN<pcl::PointXYZRGB>));
	pcl::search::KdTree<pcl::PointXYZRGB>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZRGB>()); 
	sift.setSearchMethod (tree);
  	sift.setScales(min_scale, n_octaves, n_scales_per_octave);
 	sift.setMinimumContrast(min_contrast);
  	sift.setInputCloud(cloud);
	sift.compute(keypoints);
  	//visualizo 
	while(!viewer.wasStopped())
	{
	//mientras no se cierre muestre la nube de puntos 
	  viewer.showCloud (cloud);
	  
	  visualize_keypoints(cloud,keypoints);
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