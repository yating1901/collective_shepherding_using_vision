import os, json

def load_robot_state(robot_file):
    with open(robot_file) as f:
        robot_data = json.load(f)
    return robot_data

path = os.getcwd()
robot_file = path + "/agent_list.json"
robot_data = load_robot_state(robot_file)
print(robot_data[0], "\n", robot_data[0]["ID"], robot_data[0]["x0"], robot_data[0]["x1"])