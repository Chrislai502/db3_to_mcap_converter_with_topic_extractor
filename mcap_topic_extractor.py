"""script that reads ROS2 messages from an MCAP bag using the rosbag2_py API."""
import argparse

import os
import shutil
import rosbag2_py

# ---------------------------------------------------------------------------- #
#                                  PARAMETERS                                  #
# ---------------------------------------------------------------------------- #

# ----------------------------- Timestamp Filter ----------------------------- #
# (For ART rosbags, you can use camera timestamps to filter the bag (NPC synced likely))
# These are the start and end timestamps to filter the bag, all TOPICS_TO_EXTRACT
# will be included in the output bag if they have a message within this time range.

# Example timestamps:
# sec: 1673037998
# nanosec: 455526000
# FROM_TIMESTAMP = 1673037998455526000
# FROM_TIMESTAMP = 1673037998455526000
FILTER_BY_TIMESTAMP = False

FROM_TIMESTAMP = 1673037588612982487
FROM_TIMESTAMP_TOPIC = "/vimba_front_right_center/image" # topic to check timestamp from

# sec: 1673038010
# nanosec: 792381600
# TO_TIMESTAMP = 1673038010792381600
TO_TIMESTAMP = 1673037592257594379
TO_TIMESTAMP_TOPIC = FROM_TIMESTAMP_TOPIC

# ------------------------ Output path for the new bag ----------------------- #
INPUT_PATH = "/media/Public/ROSBAG_BACKUPS/VEGAS_CES_2022/Jan6th_PTP_synced_cam_Lidar/rosbag2_2023_01_06-15_39_44/"
INPUT_PATH = "/home/zhihao/rosbags/merged_rosbag/"

OUTPUT_PATH = "/media/roar/2a177b93-e672-418b-8c28-b075e87fcbc7/Chris_short_bags/Rosbags/radar_only/timestamp_test/"
OUTPUT_PATH = "/home/zhihao/rosbags/filtered_merged_rosbag/"
# ---------------------- Topics to extract from the bag ---------------------- #
TOPICS_TO_EXTRACT = [

# Lidar Topics
"/luminar_front_points", \
"/luminar_left_points", \
"/luminar_right_points", \

# Radar Topics
"/radar_front/radar_visz_static",\
"/radar_front/radar_visz_static_array",\
"/radar_front/radar_visz_moving", "/radar_front/radar_visz_moving_array",\
"/perception/lvms_inside_vis", "/perception/lvms_outside_vis", \
'/radar_right/marker', '/radar_front/from_can_bus',  \
'/radar_front/to_can_bus'
,'/radar_front/esr_status1'\
,'/radar_front/esr_status2'\
,'/radar_front/esr_status3'\
,'/radar_front/esr_status4'\
,'/radar_front/esr_status5'\
,'/radar_front/esr_status6'\
,'/radar_front/esr_status7'\
,'/radar_front/esr_status8'\
,'/radar_front/esr_status9'\
,'/radar_front/esr_track'\
,'/radar_front/esr_valid1'\
,'/radar_front/esr_valid2'\
,'/radar_front/esr_vehicle1'\
,'/radar_front/esr_vehicle2'\
,'/radar_front/esr_vehicle3'\
,'/radar_front/esr_vehicle4'\
,'/radar_front/esr_vehicle5'\
,'/radar_left/detection'\
,'/radar_left/header_information_detections'\
,'/radar_left/marker'\
,'/radar_left/vehicle_state'\
,'/radar_right/detection'\
,'/radar_right/header_information_detections'\
,'/radar_right/marker'\
,'/radar_right/marker_array'\
,'/radar_right/vehicle_state'\

# Track Polygon
,'/path'\
,'/perception/lvms_inside'\
,'/perception/lvms_inside_vis'\
,'/perception/lvms_outside'\
,'/perception/lvms_outside_vis'\


# Novatel
,'/novatel_bottom/bestgnsspos'\
,'/novatel_bottom/bestgnssvel'\
,'/novatel_bottom/bestpos'\
,'/novatel_bottom/bestutm'\
,'/novatel_bottom/bestvel'\
,'/novatel_bottom/corrimu'\
,'/novatel_bottom/fix'\
,'/novatel_bottom/gps'\
,'/novatel_bottom/heading2'\
,'/novatel_bottom/imu/data'\
,'/novatel_bottom/insconfig'\
,'/novatel_bottom/inspva'\
,'/novatel_bottom/inspvax'\
,'/novatel_bottom/insstdev'\
,'/novatel_bottom/odom'\
,'/novatel_bottom/oem7raw'\
,'/novatel_bottom/rawimu'\
,'/novatel_bottom/rxstatus'\
,'/novatel_bottom/time'\
,'/novatel_top/bestgnsspos'\
,'/novatel_top/bestgnssvel'\
,'/novatel_top/bestpos'\
,'/novatel_top/bestutm'\
,'/novatel_top/bestvel'\
,'/novatel_top/corrimu'\
,'/novatel_top/fix'\
,'/novatel_top/gps'\
,'/novatel_top/heading2'\
,'/novatel_top/imu/data'\
,'/novatel_top/insconfig'\
,'/novatel_top/inspva'\
,'/novatel_top/inspvax'\
,'/novatel_top/insstdev'\
,'/novatel_top/odom'\
,'/novatel_top/oem7raw'\
,'/novatel_top/rawimu'\
,'/novatel_top/rxstatus'\
,'/novatel_top/time']
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                                MESSAGE_FILTER                                #
# ---------------------------------------------------------------------------- #
def message_filter(input_bag: str, topics_to_extract: list = None):
    
    global TOPIC_TYPES
    global TYPE_MAP
    global TOPICS_TO_EXTRACT
    global FROM_TIMESTAMP
    global TO_TIMESTAMP
    global OUTPUT_PATH
    global FROM_TIMESTAMP_TOPIC
    global TO_TIMESTAMP_TOPIC
    global FILTER_BY_TIMESTAMP

    reader = rosbag2_py.SequentialReader()
    writer = rosbag2_py.SequentialWriter()

    # If the output folder already exists, ask the user if they want to delete it
    if os.path.exists(OUTPUT_PATH):
        print ("OUTPUT_PATH: ", OUTPUT_PATH, "\n")
        answer = input("The OUTPUT_PATH already exists. Do you want to delete it? (y/n) ")
        if answer.lower() == "y":
            shutil.rmtree(OUTPUT_PATH)
            print("Folder deleted.")
        else:
            print("Deletion cancelled.")
            return

    # Opens the bag files and sets the converter options
    try:
        reader.open(
            rosbag2_py.StorageOptions(uri=input_bag, storage_id="mcap"),
            rosbag2_py.ConverterOptions(
                input_serialization_format="cdr", output_serialization_format="cdr"
            ),
        )

        writer.open(
            rosbag2_py.StorageOptions(uri=OUTPUT_PATH, storage_id="mcap"),
            rosbag2_py.ConverterOptions(
                input_serialization_format="cdr", output_serialization_format="cdr"
            ),
        )

    except Exception as e:
        print(e)
        return
    

    # Get all topics and types
    '''
    Reader has 4 functions:
    - get_all_topics_and_types
    - has_next
    - read_next
    - reset_filter
    - set_filter
    # Set filter for topic of string type
    source: https://github.com/ros2/rosbag2/blob/c7c7954d4d9944c160d7b3d716d1cb95d34e37e4/rosbag2_py/test/test_sequential_reader.py
    storage_filter = rosbag2_py.StorageFilter(topics=['/topic'])
    reader.set_filter(storage_filter)
    '''

    TOPIC_TYPES = reader.get_all_topics_and_types()
    TYPE_MAP = {TOPIC_TYPES[i].name: TOPIC_TYPES[i].type for i in range(len(TOPIC_TYPES))}
    
    print ("\n\n All topics and types in the input bag: \n")
    for i in TYPE_MAP:
        print(i, "  |  ",  TYPE_MAP[i])

    # Check if FILTER_BY_TIMESTAMP is True, Else Run through the whole bag
    if FILTER_BY_TIMESTAMP:

        '''
        This while loop does the following:
        1. Read the next message
        2. Check if the topic is in the set of topics to extract
        '''
        
        # Check if FROM_TIMESTAMP_TOPIC and TO_TIMESTAMP_TOPIC are in the input bag
        if FROM_TIMESTAMP_TOPIC not in TYPE_MAP or TO_TIMESTAMP_TOPIC not in TYPE_MAP:
            print("ERROR: The topics for the timestamp range are not in the input bag.")
            return
        
        counter = 0
        timestamp_buffer = 0
        print ("\n***MODE: Filtering by Timestamp***")
        print ("\nIterating through the input bag...")
        while reader.has_next():
            
            # Read the next message
            topic_name, data, timestamp = reader.read_next()

            if topic_name == FROM_TIMESTAMP_TOPIC and \
                FROM_TIMESTAMP <= timestamp <= TO_TIMESTAMP:

                print("Found the first timestamp range!")
                print("Timestamp: ", timestamp)

                # Keep a map of the topics that are in the output bag
                out_bag_topics = set()

                curr_timestamp = timestamp
                while (curr_timestamp <= TO_TIMESTAMP):
                    # Read the next message
                    topic_name, data, timestamp = reader.read_next()

                    # Check if the topic is in the set of topics to extract.
                    if topic_name in set(topics_to_extract):
                    
                        # Create the topic if it doesn't exist
                        if topic_name not in out_bag_topics:
                            topic = rosbag2_py.TopicMetadata(name=topic_name, type=TYPE_MAP[topic_name], \
                                    serialization_format='cdr')
                            writer.create_topic(topic)
                            out_bag_topics.add(topic_name)

                        # Write the message to the output bag
                        writer.write(topic_name, data, timestamp)

                    # Update the current timestamp
                    if topic_name == TO_TIMESTAMP_TOPIC:
                        curr_timestamp = timestamp

                    # Print the current timestamp
                    if counter % 50000 == 0:
                        print("Currently: ", curr_timestamp, " | Target: ", \
                            TO_TIMESTAMP, " | Diff: ", (TO_TIMESTAMP - curr_timestamp)/1e9, " secs")

                    counter += 1

                print("Found the last timestamp range!")

                # Break after the range is reached
                break
            
            # Print the current timestamp
            if (topic_name == FROM_TIMESTAMP_TOPIC):
                timestamp_buffer = timestamp
            if counter % 50000 == 0:
                print("Currently: ", timestamp_buffer, " | Target: ", \
                        FROM_TIMESTAMP, " | Diff: ", (FROM_TIMESTAMP - timestamp_buffer)/1e9, " secs")
            counter += 1
            
    else:
        
        '''
        This while loop does the following:
        1. Read the next message
        2. Check if the topic is in the set of topics to extract
        '''
        counter = 0
        timestamp_buffer = 0
        print ("\n***MODE: Filtering the whole bag***")
        print ("\nIterating through the input bag...")
        while reader.has_next():
            
            # Read the next message
            topic_name, data, timestamp = reader.read_next()

            # Keep a map of the topics that are in the output bag
            out_bag_topics = set()

            # Check if the topic is in the set of topics to extract.
            if topic_name in set(topics_to_extract):
            
                # Create the topic if it doesn't exist
                if topic_name not in out_bag_topics:
                    topic = rosbag2_py.TopicMetadata(name=topic_name, type=TYPE_MAP[topic_name], \
                            serialization_format='cdr')
                    writer.create_topic(topic)
                    out_bag_topics.add(topic_name)

                # Write the message to the output bag
                writer.write(topic_name, data, timestamp)

            # Print the current timestamp
            if counter % 50000 == 0:
                print("Currently: ", timestamp, " | Target: NO TIMESTAMP", " | Diff: ", (TO_TIMESTAMP - timestamp)/1e9, " secs")

            counter += 1

    # Close the bag file
    del reader
    del writer

# ---------------------------------------------------------------------------- #
#                                     MAIN                                     #
# ---------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", help="input bag path (folder or filepath) to read from", default=None
    )

    args = parser.parse_args()
    input_path = None

    # Check if Parameters are given.
    global TOPICS_TO_EXTRACT
    if TOPICS_TO_EXTRACT == []:
        TOPICS_TO_EXTRACT = None

    if args.input is None:
        if INPUT_PATH is None:
            print("No input path given. Exiting...")
            return
        else:
            input_path = INPUT_PATH

    print("Reading from Rosbag: ", input_path, "\n")
    print("Reading messages from bag...\n")

    # Filter and write the messages to a new bag
    message_filter(input_path, TOPICS_TO_EXTRACT)
    
    print("Done! Output bag in :", OUTPUT_PATH)
    print("Enjoy your new bag file! :)")

if __name__ == "__main__":
    main()
