#
#   Copyright (c)     
#
#   The Verifiable & Control-Theoretic Robotics (VECTR) Lab
#   University of California, Los Angeles
#
#   Authors: Kenny J. Chen, Ryan Nemiroff, Brett T. Lopez
#   Contact: {kennyjchen, ryguyn, btlopez}@ucla.edu
#

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition   
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    current_pkg = FindPackageShare('direct_lidar_inertial_odometry')

    # Set default arguments
    rviz = LaunchConfiguration('rviz', default='false')
    pointcloud_topic = LaunchConfiguration('pointcloud_topic', default='/ouster/points')
    imu_topic = LaunchConfiguration('imu_topic', default='/ouster/imu')
    use_sim_time = LaunchConfiguration('use_sim_time')
    odom_frame = LaunchConfiguration('odom_frame', default='odom')
    base_frame = LaunchConfiguration('base_frame', default='base_link')
    lidar_frame = LaunchConfiguration('lidar_frame', default='os_lidar')
    imu_frame = LaunchConfiguration('imu_frame', default='os_imu')
    enable_status_output = LaunchConfiguration('enable_status_output', default='false')

    # Define arguments
    declare_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )
    declare_rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value=rviz,
        description='Launch RViz'
    )
    declare_odom_frame_arg = DeclareLaunchArgument(
        'odom_frame',
        default_value=odom_frame,
        description='Odometry frame name'
    )
    declare_base_frame_arg = DeclareLaunchArgument(
        'base_frame',
        default_value=base_frame,
        description='Base frame name'
    )
    declar_lidar_frame_arg = DeclareLaunchArgument(
        'lidar_frame',
        default_value=lidar_frame,
        description='LiDAR frame name'
    )
    declare_imu_frame_arg = DeclareLaunchArgument(
        'imu_frame',
        default_value=imu_frame,
        description='IMU frame name'
    )
    declare_pointcloud_topic_arg = DeclareLaunchArgument(
        'pointcloud_topic',
        default_value=pointcloud_topic,
        description='Pointcloud topic name'
    )
    declare_imu_topic_arg = DeclareLaunchArgument(
        'imu_topic',
        default_value=imu_topic,
        description='IMU topic name'
    )
    declare_enable_status_output_arg = DeclareLaunchArgument(
        'enable_status_output',
        default_value=enable_status_output,
        description='Enable status output to terminal (true/false)'
    )

    # Load parameters
    dlio_yaml_path = PathJoinSubstitution([current_pkg, 'cfg', 'dlio.yaml'])
    dlio_params_yaml_path = PathJoinSubstitution([current_pkg, 'cfg', 'params.yaml'])

    # DLIO Odometry Node
    dlio_odom_node = Node(
        package='direct_lidar_inertial_odometry',
        executable='dlio_odom_node',
        output='screen',
        parameters=[dlio_yaml_path, dlio_params_yaml_path, 
        {
            'use_sim_time': use_sim_time,
            'odom_frame': odom_frame, 
            'base_frame': base_frame, 
            'lidar_frame': lidar_frame, 
            'imu_frame': imu_frame,
            'odom/enable_status_output': enable_status_output
        }],
        remappings=[
            ('pointcloud', pointcloud_topic),
            ('imu', imu_topic),
            ('odom', 'dlio/odom_node/odom'),
            ('pose', 'dlio/odom_node/pose'),
            ('path', 'dlio/odom_node/path'),
            ('kf_pose', 'dlio/odom_node/keyframes'),
            ('kf_cloud', 'dlio/odom_node/pointcloud/keyframe'),
            ('deskewed', 'dlio/odom_node/pointcloud/deskewed'),
        ],
    )

    # DLIO Mapping Node
    dlio_map_node = Node(
        package='direct_lidar_inertial_odometry',
        executable='dlio_map_node',
        output='screen',
        parameters=[dlio_yaml_path, dlio_params_yaml_path, 
        {
            'use_sim_time': use_sim_time,
            'lidar_frame': lidar_frame,
            'imu_frame': imu_frame,
            'odom_frame': odom_frame, 
            'base_frame': base_frame
        }],
        remappings=[
            ('keyframes', 'dlio/odom_node/pointcloud/keyframe'),
        ],
    )

    # RViz node
    rviz_config_path = PathJoinSubstitution([current_pkg, 'launch', 'dlio.rviz'])
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='dlio_rviz',
        arguments=['-d', rviz_config_path],
        output='screen',
        condition=IfCondition(LaunchConfiguration('rviz'))
    )

    return LaunchDescription([
        declare_rviz_arg,
        declare_pointcloud_topic_arg,
        declare_imu_topic_arg,
        declare_enable_status_output_arg,
        dlio_odom_node,
        dlio_map_node,
        rviz_node
    ])
