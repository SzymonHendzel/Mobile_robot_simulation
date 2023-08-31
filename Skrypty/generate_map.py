import sys
import os
import pathlib

try:
    map_path=pathlib.Path(sys.argv[1])
    output_model_dir=pathlib.Path(sys.argv[2])
    map_path=pathlib.Path(*map_path.parts[2:])
    output_model_dir=pathlib.Path(*output_model_dir.parts[2:])
    f=os.path.basename(map_path)
    filename = f.split('.')[0]
    filename = filename +'.world'
    output_world_path = os.path.join(output_model_dir,filename)
    os.system(f'ros2 run rmf_building_map_tools building_map_generator gazebo ~/{map_path} ~/{output_world_path} ~/{output_model_dir}')
    os.system(f'ros2 run rmf_building_map_tools building_map_model_downloader ~/{map_path} -f -e ~/.gazebo/models')
    os.system(f'ros2 run rmf_building_map_tools building_map_model_downloader ~/{map_path} -f -e ~/{output_model_dir}')
    os.system(f'ros2 run rmf_building_map_tools building_map_generator nav ~/{map_path} ~/{output_model_dir}')
except:
    print('Sciezki nie zostały podane')

