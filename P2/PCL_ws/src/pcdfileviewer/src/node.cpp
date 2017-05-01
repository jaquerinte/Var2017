#include <ros/ros.h>
#include <pcl_ros/point_cloud.h>
#include <pcl/point_types.h>
#include <boost/foreach.hpp>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/visualization/cloud_viewer.h>
#include <pcl/filters/voxel_grid.h>

#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <iostream>

void simpleVis ()
{
	 pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZRGB>); 
	 if (pcl::io::loadPCDFile<pcl::PointXYZRGB> ("testFiLe.pcd", *cloud) == -1){  //* load the file 
    		PCL_ERROR ("Couldn't read the pcd file  \n"); 
  		} 
	// Crea el visualizador
  	pcl::visualization::CloudViewer viewer ("Cloud Viewer");
	while(!viewer.wasStopped())
	{
	//mientras no se cierre muestre la nube de puntos 
	  viewer.showCloud (cloud);
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