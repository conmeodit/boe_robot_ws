#include <algorithm>
#include <cmath>
#include <functional>
#include <memory>
#include <mutex>
#include <string>

#include <gazebo/common/Events.hh>
#include <gazebo/common/Plugin.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo_ros/node.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <ignition/math/Pose3.hh>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joint_state.hpp>

namespace boe_robot_gazebo
{

class CasterVisualPlugin : public gazebo::WorldPlugin
{
public:
  void Load(
    gazebo::physics::WorldPtr world,
    sdf::ElementPtr sdf) override
  {
    world_ = world;
    ros_node_ = gazebo_ros::Node::Get(sdf);

    cmd_vel_subscription_ =
      ros_node_->create_subscription<geometry_msgs::msg::Twist>(
      "cmd_vel",
      rclcpp::QoS(10),
      std::bind(
        &CasterVisualPlugin::CmdVelCallback,
        this,
        std::placeholders::_1));

    joint_state_publisher_ =
      ros_node_->create_publisher<sensor_msgs::msg::JointState>(
      "joint_states",
      rclcpp::QoS(10));

    update_connection_ =
      gazebo::event::Events::ConnectWorldUpdateBegin(
      std::bind(
        &CasterVisualPlugin::OnUpdate,
        this,
        std::placeholders::_1));

    last_sim_time_ = world_->SimTime();
    last_joint_state_time_ = last_sim_time_;
  }

private:
  static double WrapAngle(double angle)
  {
    return std::atan2(std::sin(angle), std::cos(angle));
  }

  void CmdVelCallback(
    const geometry_msgs::msg::Twist::SharedPtr message)
  {
    std::lock_guard<std::mutex> lock(command_mutex_);
    linear_x_ = message->linear.x;
    angular_z_ = message->angular.z;
  }

  bool FindModels()
  {
    if (!robot_model_) {
      robot_model_ = world_->ModelByName("boe_robot");
    }
    if (!rotation_visual_model_) {
      rotation_visual_model_ =
        world_->ModelByName("boe_caster_rotation_visual");
    }
    if (!wheel_visual_model_) {
      wheel_visual_model_ =
        world_->ModelByName("boe_caster_wheel_visual");
    }
    if (robot_model_ && !base_link_) {
      base_link_ = robot_model_->GetLink("base_link");
    }

    const bool ready =
      robot_model_ &&
      base_link_ &&
      rotation_visual_model_ &&
      wheel_visual_model_;

    if (ready && !models_found_) {
      models_found_ = true;
      RCLCPP_INFO(
        ros_node_->get_logger(),
        "Caster visuals are synchronized with base_link.");
    }

    return ready;
  }

  void OnUpdate(const gazebo::common::UpdateInfo & info)
  {
    const double dt = (info.simTime - last_sim_time_).Double();
    last_sim_time_ = info.simTime;

    if (dt <= 0.0 || dt > 0.1 || !FindModels()) {
      return;
    }

    double linear_x;
    double angular_z;
    {
      std::lock_guard<std::mutex> lock(command_mutex_);
      linear_x = linear_x_;
      angular_z = angular_z_;
    }

    const double velocity_x = linear_x;
    const double velocity_y = angular_z * caster_offset_x_;
    const double speed = std::hypot(velocity_x, velocity_y);

    if (speed > 1.0e-4) {
      const double target_angle =
        WrapAngle(std::atan2(velocity_y, velocity_x) + pi_);
      const double angle_error =
        WrapAngle(target_angle - swivel_angle_);
      const double max_step = swivel_rate_limit_ * dt;
      const double angle_step =
        std::clamp(angle_error, -max_step, max_step);

      swivel_velocity_ = angle_step / dt;
      swivel_angle_ =
        WrapAngle(swivel_angle_ + angle_step);

      const double rolling_speed =
        velocity_x * std::cos(swivel_angle_) +
        velocity_y * std::sin(swivel_angle_);

      wheel_velocity_ = rolling_speed / wheel_radius_;
      wheel_angle_ = WrapAngle(
        wheel_angle_ + wheel_velocity_ * dt);
    } else {
      swivel_velocity_ = 0.0;
      wheel_velocity_ = 0.0;
    }

    const ignition::math::Pose3d base_pose =
      base_link_->WorldPose();

    const ignition::math::Pose3d caster_pivot_pose(
      pivot_x_,
      pivot_y_,
      pivot_z_,
      0.0,
      0.0,
      swivel_angle_);

    const ignition::math::Pose3d wheel_offset_pose(
      wheel_offset_x_,
      wheel_offset_y_,
      wheel_offset_z_,
      0.0,
      wheel_angle_,
      0.0);

    rotation_visual_model_->SetWorldPose(
      base_pose * caster_pivot_pose);

    wheel_visual_model_->SetWorldPose(
      base_pose * caster_pivot_pose * wheel_offset_pose);

    PublishJointState(info.simTime);
  }

  void PublishJointState(const gazebo::common::Time & sim_time)
  {
    if ((sim_time - last_joint_state_time_).Double() < 0.02) {
      return;
    }
    last_joint_state_time_ = sim_time;

    sensor_msgs::msg::JointState message;
    message.header.stamp.sec = sim_time.sec;
    message.header.stamp.nanosec = sim_time.nsec;
    message.name = {
      "caster_rotation_joint",
      "caster_wheel_joint"
    };
    message.position = {
      swivel_angle_,
      wheel_angle_
    };
    message.velocity = {
      swivel_velocity_,
      wheel_velocity_
    };

    joint_state_publisher_->publish(message);
  }

  gazebo::physics::WorldPtr world_;
  gazebo::physics::ModelPtr robot_model_;
  gazebo::physics::ModelPtr rotation_visual_model_;
  gazebo::physics::ModelPtr wheel_visual_model_;
  gazebo::physics::LinkPtr base_link_;
  gazebo_ros::Node::SharedPtr ros_node_;

  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr
    cmd_vel_subscription_;
  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr
    joint_state_publisher_;
  gazebo::event::ConnectionPtr update_connection_;

  std::mutex command_mutex_;
  double linear_x_{0.0};
  double angular_z_{0.0};
  double swivel_angle_{0.0};
  double wheel_angle_{0.0};
  double swivel_velocity_{0.0};
  double wheel_velocity_{0.0};
  bool models_found_{false};

  gazebo::common::Time last_sim_time_;
  gazebo::common::Time last_joint_state_time_;

  const double caster_offset_x_{-0.055};
  const double wheel_radius_{0.01805};
  const double swivel_rate_limit_{4.0};
  const double pi_{3.14159265358979323846};

  const double pivot_x_{-0.0411668203};
  const double pivot_y_{-0.0042939669};
  const double pivot_z_{0.0079196660};

  const double wheel_offset_x_{0.0179800159};
  const double wheel_offset_y_{0.0039088610};
  const double wheel_offset_z_{-0.0220196660};
};

GZ_REGISTER_WORLD_PLUGIN(CasterVisualPlugin)

}  // namespace boe_robot_gazebo
