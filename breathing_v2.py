# Copyright (c) Acconeer AB, 2022-2023
# All rights reserved

from __future__ import annotations
import npyfile
import numpy as np
import time
import csv
import acconeer.exptool as et
from acconeer.exptool import a121
from acconeer.exptool.a121 import Profile
from acconeer.exptool.a121.algo.breathing import RefApp
from acconeer.exptool.a121.algo.breathing._ref_app import (
    BreathingProcessorConfig,
    RefAppConfig,
    get_sensor_config,
)
from acconeer.exptool.a121.algo.presence import ProcessorConfig as PresenceProcessorConfig


def main():
    args = a121.ExampleArgumentParser().parse_args()
    et.utils.config_logging(args)

    # Setup the configurations
    # Detailed at https://docs.acconeer.com/en/latest/exploration_tool/algo/a121/ref_apps/breathing.html

    # Sensor selections
    sensor = 1

    #Default configuration
    breathing_processor_config = BreathingProcessorConfig(
        lowest_breathing_rate=6,
        highest_breathing_rate=60,
        time_series_length_s=20,
    )

    #Grace tuning breathing processor
    breathing_processor_config = BreathingProcessorConfig(
        lowest_breathing_rate= 4,
        highest_breathing_rate= 60,
        time_series_length_s=20
    )

    #Sam tuning 
    # breathing_processor_config = BreathingProcessorConfig(
    #     lowest_breathing_rate= 2.1,
    #     highest_breathing_rate= 13.7,
    #     time_series_length_s= 10
    # )


    # Presence Configurations
    #Sam Tuned
    #presence_config = PresenceProcessorConfig(
        #intra_detection_threshold=4,
        #intra_frame_time_const=0.15,
        #inter_frame_fast_cutoff=20,
        #inter_frame_slow_cutoff=0.05,
        #inter_frame_deviation_time_const=0.5,
        #intra_output_time_const=0.1,    
    #)

    #Grace Tuned + Default
    presence_config = PresenceProcessorConfig(
        intra_detection_threshold=4,
        intra_frame_time_const=0.15,
        inter_frame_fast_cutoff=20,
        inter_frame_slow_cutoff=0.2,
        inter_frame_deviation_time_const=0.5    
    )

    # Breathing Configurations
    
    #Sam Tuned
    # ref_app_config = RefAppConfig(
    #     use_presence_processor=False,
    #     start_m=0.4, #cannot be 0
    #     end_m=0.8,
    #     hwaas = 50,
    #     num_distances_to_analyze=3,
    #     distance_determination_duration=10,
    #     breathing_config=breathing_processor_config,
    #     presence_config=presence_config,
    #     profile = Profile.PROFILE_5
    # )

    #Grace Tuned
    # ref_app_config = RefAppConfig(
    #     use_presence_processor=True,
    #     #Adjust start and end of range as appropriate
    #     start_m=0.6, #cannot be 0
    #     end_m=1,
    #     num_distances_to_analyze=5,
    #     distance_determination_duration=5,
    #     breathing_config=breathing_processor_config,
    #     presence_config=presence_config,
    #     profile = Profile.PROFILE_5,
    #     sweeps_per_frame= 8
    # )

    #Default
    ref_app_config = RefAppConfig(
        use_presence_processor=True,
        num_distances_to_analyze=3,
        distance_determination_duration=5,
        breathing_config=breathing_processor_config,
        presence_config=presence_config,
    )

    # End setup configurations

    # Preparation for client
    sensor_config = get_sensor_config(ref_app_config=ref_app_config)
    client = a121.Client.open(serial_port="COM7", override_baudrate=115200)
    client.setup_session(sensor_config)

    ratio = 1
    
    with a121.H5Recorder("./raw_data-161.h5",client):
        # Preparation for reference application processor
        ref_app = RefApp(client=client, sensor_id=sensor, ref_app_config=ref_app_config)
        ref_app.start()

        interrupt_handler = et.utils.ExampleInterruptHandler()
        print("Press Ctrl-C to end session")

    
        startTime = time.time()
        with open('sensorData-final-default-regular.csv', 'w', newline = '') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Timestamp", "Breath Rate", 
                                "App State", "Distances Being Analyzed",
                                "Intra Presence Score", "Intra",
                                "Inter Presence Score", "Inter",
                                "Presence Distance", "Presence Detected", 
                                "Frame", "Abs Mean Sweep", 
                                "Fast LP Mean Sweep", "Slow LP Mean Sweep", "LP Noise",
                                "Presence Distance Index", "PSD", "Frequencies", "Breathing Motion", 
                                "Time Vector", "Breathing Rate History",
                                "All Breathing Rate History"])
            while not interrupt_handler.got_signal:
                #Gets the data from the sensor
                distressCounter = 0
                processed_data = ref_app.get_next()
                currentTime = time.time() - startTime
                try:
                    if (processed_data.breathing_result):
                        if (processed_data.breathing_result.breathing_rate):
                            calibratedBPM = processed_data.breathing_result.breathing_rate * ratio
                            
                            print(f"{currentTime}\t{calibratedBPM}")
                            tosend = [currentTime, calibratedBPM, 
                                      processed_data.app_state, processed_data.distances_being_analyzed, 
                                      processed_data.presence_result.intra_presence_score, processed_data.presence_result.intra, 
                                      processed_data.presence_result.inter_presence_score, processed_data.presence_result.inter,
                                      processed_data.presence_result.presence_distance, processed_data.presence_result.presence_detected,
                                      processed_data.presence_result.extra_result.frame, processed_data.presence_result.extra_result.abs_mean_sweep,
                                      processed_data.presence_result.extra_result.fast_lp_mean_sweep, processed_data.presence_result.extra_result.slow_lp_mean_sweep,
                                      processed_data.presence_result.extra_result.lp_noise, processed_data.presence_result.extra_result.presence_distance_index,
                                      processed_data.breathing_result.extra_result.psd, processed_data.breathing_result.extra_result.frequencies, 
                                      processed_data.breathing_result.extra_result.breathing_motion, processed_data.breathing_result.extra_result.time_vector,
                                      processed_data.breathing_result.extra_result.breathing_rate_history, processed_data.breathing_result.extra_result.all_breathing_rate_history]
                            #Sends an array of the time and respiration rate to csv file
                            csv_writer.writerow(tosend)
                        else:
                            #breathing result exists, but rate not determined
                            toSend = [currentTime, 'N/A', 
                                      processed_data.app_state, processed_data.distances_being_analyzed, 
                                      processed_data.presence_result.intra_presence_score, processed_data.presence_result.intra, 
                                      processed_data.presence_result.inter_presence_score, processed_data.presence_result.inter,
                                      processed_data.presence_result.presence_distance, processed_data.presence_result.presence_detected,
                                      processed_data.presence_result.extra_result.frame, processed_data.presence_result.extra_result.abs_mean_sweep,
                                      processed_data.presence_result.extra_result.fast_lp_mean_sweep, processed_data.presence_result.extra_result.slow_lp_mean_sweep,
                                      processed_data.presence_result.extra_result.lp_noise, processed_data.presence_result.extra_result.presence_distance_index,
                                      processed_data.breathing_result.extra_result.psd, processed_data.breathing_result.extra_result.frequencies, 
                                      processed_data.breathing_result.extra_result.breathing_motion, processed_data.breathing_result.extra_result.time_vector,
                                      processed_data.breathing_result.extra_result.breathing_rate_history, processed_data.breathing_result.extra_result.all_breathing_rate_history]
                            csv_writer.writerow(toSend)
                            print("Calculating respiration rate...")
                    else: 
                        if (processed_data.presence_result):
                            #No breathing results, but presence result
                            print("Presence detected")
                            toSend = [currentTime, 'N/A', 
                                      processed_data.app_state, processed_data.distances_being_analyzed, 
                                      processed_data.presence_result.intra_presence_score, processed_data.presence_result.intra, 
                                      processed_data.presence_result.inter_presence_score, processed_data.presence_result.inter,
                                      processed_data.presence_result.presence_distance, processed_data.presence_result.presence_detected,
                                      processed_data.presence_result.extra_result.frame, processed_data.presence_result.extra_result.abs_mean_sweep,
                                      processed_data.presence_result.extra_result.fast_lp_mean_sweep, processed_data.presence_result.extra_result.slow_lp_mean_sweep,
                                      processed_data.presence_result.extra_result.lp_noise, processed_data.presence_result.extra_result.presence_distance_index,
                                      'N/A', 'N/A', 
                                      'N/A', 'N/A',
                                      'N/A', 'N/A']
                            csv_writer.writerow(toSend)
                        else:
                            toSend = [currentTime, 'N/A', 
                                      processed_data.app_state, processed_data.distances_being_analyzed, 
                                      'N/A', 'N/A', 
                                      'N/A', 'N/A',
                                      'N/A', 'N/A',
                                      'N/A', 'N/A',
                                      'N/A', 'N/A',
                                      'N/A', 'N/A',
                                      'N/A', 'N/A', 
                                      'N/A', 'N/A',
                                      'N/A', 'N/A']
                            csv_writer.writerow(toSend)
                            print("Presence not detected")
                except et.PGProccessDiedException:
                    break

    

    ref_app.stop()
    print("Disconnecting...")
    client.close()


if __name__ == "__main__":
    main()