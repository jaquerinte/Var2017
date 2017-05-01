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
#include <string> 

pcl::PointCloud<pcl::PointXYZRGB>::Ptr visu_pc (new pcl::PointCloud<pcl::PointXYZRGB>);

void simpleVis ()
{
	// Crea el visualizador
  	pcl::visualization::CloudViewer viewer ("Simple Cloud Viewer");
	while(!viewer.wasStopped())
	{
	//mientras no se cierre muestre la nube de puntos 
	  viewer.showCloud (visu_pc);
	//Para el hilo 1000 milisegundos 
	  boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
	}

}

void callback(const pcl::PointCloud<pcl::PointXYZRGB>::ConstPtr& msg)
{
	pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZRGB>(*msg));
	pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud_filtered (new pcl::PointCloud<pcl::PointXYZRGB>);


	cout << "Puntos capturados: " << cloud->size() << endl;

	pcl::VoxelGrid<pcl::PointXYZRGB > vGrid;
	vGrid.setInputCloud (cloud);
	vGrid.setLeafSize (0.005f, 0.005f, 0.005f);
	vGrid.filter (*cloud_filtered);

	cout << "Puntos tras VG: " << cloud_filtered->size() << endl;

	visu_pc = cloud_filtered;
	
}

int main(int argc, char** argv)
{
  ros::init(argc, argv, "sub_pcl");
  ros::NodeHandle nh;
  // se llama al callback para procesar la nube de puntos
  ros::Subscriber sub = nh.subscribe<pcl::PointCloud<pcl::PointXYZRGB> >("/camera/depth/points", 1, callback);

  boost::thread t(simpleVis);
  int n = 0;
  while(ros::ok())
  {
	ros::spinOnce();
	try {
	//std::string value = std::stoi(n);
	std::stringstream sstm;
	sstm << "./PointCloudCaptures/capture_" << n << ".pcd";
	std::string result = sstm.str();

	pcl::io::savePCDFile(result,*visu_pc,false);
	boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
	++n;
	} catch(const std::exception& ex){

	}
  }

}
