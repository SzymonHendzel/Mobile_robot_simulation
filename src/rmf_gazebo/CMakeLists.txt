cmake_minimum_required(VERSION 3.8)

project(rmf_gazebo)

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(gazebo_ros REQUIRED)

install(DIRECTORY
  rmf_config
  models
  launch
  DESTINATION share/${PROJECT_NAME}
)