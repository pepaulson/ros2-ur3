#!/usr/bin/env python3

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class JointMover(Node):
    def __init__(self):
        super().__init__('joint_mover')
        self._client = ActionClient(
            self,
            FollowJointTrajectory,
            '/scaled_joint_trajectory_controller/follow_joint_trajectory'
        )

    def send_goal(self):
        traj = JointTrajectory()
        traj.joint_names = ['shoulder_lift_joint']
        pt = JointTrajectoryPoint()
        pt.positions = [0.5]
        pt.time_from_start.sec = 2
        traj.points = [pt]

        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = traj
        goal_msg.goal_time_tolerance.sec = 1

        self._client.wait_for_server()
        return self._client.send_goal_async(goal_msg)

def main(args=None):
    rclpy.init(args=args)
    node = JointMover()

    # 1) send the goal
    goal_handle_future = node.send_goal()

    # 2) wait for the goal to be accepted/rejected
    rclpy.spin_until_future_complete(node, goal_handle_future)
    goal_handle = goal_handle_future.result()
    if not goal_handle.accepted:
        node.get_logger().error('Goal rejected :(')
        node.destroy_node()
        rclpy.shutdown()
        return

    # 3) request the result
    result_future = goal_handle.get_result_async()

    # 4) wait for the result to come back
    rclpy.spin_until_future_complete(node, result_future)
    result = result_future.result().result
    node.get_logger().info(f'Motion completed with error code: {result.error_code}')

    # clean up
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
