from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


VALID_ROBOT_MODELS = {"scout", "ranger"}


def launch_setup(context, *args, **kwargs):
    current_pkg = FindPackageShare("direct_lidar_inertial_odometry")

    robot_model = LaunchConfiguration("robot_model").perform(context).strip()

    if robot_model not in VALID_ROBOT_MODELS:
        raise RuntimeError(
            f"[dlio.launch.py] invalid robot_model='{robot_model}'. "
            f"Allowed values: {sorted(VALID_ROBOT_MODELS)}"
        )

    rviz = LaunchConfiguration("rviz")
    pointcloud_topic = LaunchConfiguration("pointcloud_topic")
    imu_topic = LaunchConfiguration("imu_topic")
    use_sim_time = LaunchConfiguration("use_sim_time")
    odom_frame = LaunchConfiguration("odom_frame")
    base_frame = LaunchConfiguration("base_frame")
    lidar_frame = LaunchConfiguration("lidar_frame")
    imu_frame = LaunchConfiguration("imu_frame")
    enable_status_output = LaunchConfiguration("enable_status_output")

    dlio_yaml_path = PathJoinSubstitution([
        current_pkg,
        "cfg",
        f"{robot_model}.yaml"
    ])
    dlio_params_yaml_path = PathJoinSubstitution([
        current_pkg,
        "cfg",
        "params.yaml"
    ])

    dlio_odom_node = Node(
        package="direct_lidar_inertial_odometry",
        executable="dlio_odom_node",
        output="screen",
        parameters=[
            dlio_yaml_path,
            dlio_params_yaml_path,
            {
                "use_sim_time": use_sim_time,
                "odom_frame": odom_frame,
                "base_frame": base_frame,
                "lidar_frame": lidar_frame,
                "imu_frame": imu_frame,
                "odom/enable_status_output": enable_status_output,
            }
        ],
        remappings=[
            ("pointcloud", pointcloud_topic),
            ("imu", imu_topic),
            ("odom", "dlio/odom_node/odom"),
            ("pose", "dlio/odom_node/pose"),
            ("path", "dlio/odom_node/path"),
            ("kf_pose", "dlio/odom_node/keyframes"),
            ("kf_cloud", "dlio/odom_node/pointcloud/keyframe"),
            ("deskewed", "dlio/odom_node/pointcloud/deskewed"),
        ],
    )

    dlio_map_node = Node(
        package="direct_lidar_inertial_odometry",
        executable="dlio_map_node",
        output="screen",
        parameters=[
            dlio_yaml_path,
            dlio_params_yaml_path,
            {
                "use_sim_time": use_sim_time,
                "lidar_frame": lidar_frame,
                "imu_frame": imu_frame,
                "odom_frame": odom_frame,
                "base_frame": base_frame,
            }
        ],
        remappings=[
            ("keyframes", "dlio/odom_node/pointcloud/keyframe"),
        ],
    )

    rviz_config_path = PathJoinSubstitution([
        current_pkg,
        "launch",
        "dlio.rviz"
    ])

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="dlio_rviz",
        arguments=["-d", rviz_config_path],
        output="screen",
        condition=IfCondition(rviz),
    )

    return [
        dlio_odom_node,
        dlio_map_node,
        rviz_node,
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "robot_model",
            default_value="scout",
            description="Robot model: scout | ranger",
        ),
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="Use simulation time",
        ),
        DeclareLaunchArgument(
            "rviz",
            default_value="false",
            description="Launch RViz",
        ),
        DeclareLaunchArgument(
            "odom_frame",
            default_value="odom",
            description="Odometry frame name",
        ),
        DeclareLaunchArgument(
            "base_frame",
            default_value="base_link",
            description="Base frame name",
        ),
        DeclareLaunchArgument(
            "lidar_frame",
            default_value="os_lidar",
            description="LiDAR frame name",
        ),
        DeclareLaunchArgument(
            "imu_frame",
            default_value="os_imu",
            description="IMU frame name",
        ),
        DeclareLaunchArgument(
            "pointcloud_topic",
            default_value="/ouster/points",
            description="Pointcloud topic name",
        ),
        DeclareLaunchArgument(
            "imu_topic",
            default_value="/ouster/imu",
            description="IMU topic name",
        ),
        DeclareLaunchArgument(
            "enable_status_output",
            default_value="false",
            description="Enable status output to terminal (true/false)",
        ),
        OpaqueFunction(function=launch_setup),
    ])