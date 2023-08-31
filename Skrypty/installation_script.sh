#Wybór dystrybucji oprogramowania ROS2
distribution=humble
#Ustawianie odpowiednich ustawień językowych
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
#Dodanie repozytorium ROS2 do Systemu
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
#Instalacja ROS2
sudo apt update
sudo apt upgrade
sudo apt install ros-$distribution-desktop
sudo apt install ros-$distribution-ros-base
sudo apt install ros-dev-tools
#instalacja Gazebo 
sudo apt install gazebo
sudo apt install ros-$distribution-gazebo-ros-pkgs
#instalacja Nav2
sudo apt install ros-$distribution-navigation2
sudo apt install ros-$distribution-nav2-bringup
sudo apt install ros-$distribution-turtlebot3-gazebo
#zależności potrzebne do działania Open-RMF
sudo apt update && sudo apt install \
python3-pip \
curl \
python3-colcon-mixin \
ros-dev-tools \
-y
sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'
wget https://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -
python3 -m pip install flask-socketio fastapi uvicorn
sudo rosdep init # run if first time using rosdep.
rosdep update
colcon mixin add default https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml
colcon mixin update default
#instalacja OPEN RMF
sudo apt update && sudo apt install ros-$distribution-rmf-dev