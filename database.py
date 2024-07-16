import argparse
import psycopg2
import cv2
import PySpin
import datetime
import os
import sys
import subprocess

def get_valid_input(prompt, min_value, max_value, type_converter=int):
    while True:
        try:
            value = type_converter(input(prompt))
            if min_value <= value <= max_value:
                return value
            else:
                raise ValueError(f"Value must be between {min_value} and {max_value}")
        except ValueError as e:
            print(f"Invalid input: {e}")

def main(args=None):
    if args is None:
        parser = argparse.ArgumentParser(description='Capture and save video using FLIR camera.')
        parser.add_argument('-ti', '--duration', type=int, help='Duration for video capture (seconds)')
        parser.add_argument('-fps', '--fps', type=int, help='Frame rate (frames per second)')
        parser.add_argument('-ex', '--auto_exposure', action='store_true', help='Use automatic exposure')
        parser.add_argument('-et', '--exposure_time', type=int, help='Exposure time (milliseconds)')
        parser.add_argument('-wi', '--width', type=int, help='Resolution width (pixels)')
        parser.add_argument('-he', '--height', type=int, help='Resolution height (pixels)')
        parser.add_argument('-lens', '--lens', type=str, help='Lens type')
        args = parser.parse_args()

    conn = None
    cur = None
    video_file_avi = None
    video_file_mp4 = None

    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname="FLIR_Database_OteizaLab",
            user="postgres",
            password="n1-323",
            host="localhost",
            port="5432"
        )
        print("Successfully connected to PostgreSQL server!")

        cur = conn.cursor()

        # Initialize camera
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        camera = cam_list.GetByIndex(0)
        camera.Init()

        # Fetch camera capabilities
        sensor_width_max = camera.Width.GetMax()
        sensor_width_min = camera.Width.GetMin()
        sensor_height_max = camera.Height.GetMax()
        sensor_height_min = camera.Height.GetMin()
        exposure_time_max = camera.ExposureTime.GetMax()
        exposure_time_min = camera.ExposureTime.GetMin()
        frame_rate_max = camera.AcquisitionFrameRate.GetMax()
        frame_rate_min = camera.AcquisitionFrameRate.GetMin()

        print("-----------------------------------------------------")
        print("CAMERA CAPABILITIES:")
        print(f"Max Resolution Width: {sensor_width_max}, Min Resolution Width: {sensor_width_min}")
        print(f"Max Resolution Height: {sensor_height_max}, Min Resolution Height: {sensor_height_min}")
        print(f"Max Exposure Time: {exposure_time_max}, Min Exposure Time: {exposure_time_min}")
        print(f"Max Frame Rate: {frame_rate_max}, Min Frame Rate: {frame_rate_min}")
        print("-----------------------------------------------------")

        # User specifications
        if args.duration is None:
            capture_duration = get_valid_input(f"Enter the duration for video capture (sec) between 0 and 100000: ", 0, 100000)
        else:
            capture_duration = args.duration

        # Validate duration against maximum allowed value
        if capture_duration > 100000:
            raise ValueError("Duration exceeds maximum allowed value of 100000 seconds")

        if args.fps is None:
            frame_rate = get_valid_input(f"Enter the frame rate (fps) between {frame_rate_min} and {frame_rate_max}: ", frame_rate_min, frame_rate_max)
        else:
            frame_rate = args.fps

        exposure_auto = args.auto_exposure
        if not exposure_auto:
            if args.exposure_time is None:
                exposure_time = get_valid_input(f"Enter the exposure time (ms) between {exposure_time_min} and {exposure_time_max}: ", exposure_time_min, exposure_time_max)
            else:
                exposure_time = args.exposure_time

        if args.width is None:
            resolution_width = get_valid_input(f"Enter the resolution width (px) between {sensor_width_min} and {sensor_width_max}: ", sensor_width_min, sensor_width_max)
        else:
            resolution_width = args.width

        if args.height is None:
            resolution_height = get_valid_input(f"Enter the resolution height (px) between {sensor_height_min} and {sensor_height_max}: ", sensor_height_min, sensor_height_max)
        else:
            resolution_height = args.height

        if args.lens is None:
            lens_type = input("Enter the lens type: ")
        else:
            lens_type = args.lens
        
        print("\n-----------------------------------------------------")
        print("USER SPECIFICATIONS:")
        print(f"Duration: {capture_duration} seconds")
        print(f"Frame Rate: {frame_rate} fps")
        print(f"Automatic Exposure: {'Yes' if exposure_auto else 'No'}")
        if not exposure_auto:
            print(f"Exposure Time: {exposure_time} ms")
        print(f"Resolution: {resolution_width}x{resolution_height} pixels")
        print(f"Lens Type: {lens_type}")
        print("-----------------------------------------------------\n")

        # Validate resolution against camera capabilities
        if resolution_width > sensor_width_max or resolution_height > sensor_height_max:
            raise ValueError(f"Resolution exceeds camera capabilities. Max resolution: {sensor_width_max}x{sensor_height_max}")

        # Set camera settings and start acquisition
        if exposure_auto:
            camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
        else:
            camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            camera.ExposureTime.SetValue(exposure_time)

        camera.AcquisitionFrameRateEnable.SetValue(True)
        camera.AcquisitionFrameRate.SetValue(frame_rate)

        camera.Width.SetValue(resolution_width)
        camera.Height.SetValue(resolution_height)

        camera.BeginAcquisition()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        avi_file_path = f'output_{timestamp}.avi'
        mp4_file_path = f'output_{timestamp}.mp4'
        fourcc_avi = cv2.VideoWriter_fourcc(*'XVID')
        fourcc_mp4 = cv2.VideoWriter_fourcc(*'mp4v')
        video_file_avi = cv2.VideoWriter(avi_file_path, fourcc_avi, frame_rate, (resolution_width, resolution_height))
        video_file_mp4 = cv2.VideoWriter(mp4_file_path, fourcc_mp4, frame_rate, (resolution_width, resolution_height))

        # Capture and save video frames
        try:
            start_time = datetime.datetime.now()
            end_time = start_time + datetime.timedelta(seconds=capture_duration)
            frame_count = 0

            while datetime.datetime.now() < end_time:
                image_result = camera.GetNextImage()

                if image_result.IsIncomplete():
                    print(f'Image incomplete with image status {image_result.GetImageStatus()} ...')
                else:
                    image_data = image_result.GetNDArray()

                    if image_data.shape[1] != resolution_width or image_data.shape[0] != resolution_height:
                        image_data = cv2.resize(image_data, (resolution_width, resolution_height))

                    if len(image_data.shape) == 2:
                        image_data = cv2.cvtColor(image_data, cv2.COLOR_GRAY2BGR)

                    video_file_avi.write(image_data)
                    video_file_mp4.write(image_data)

                    frame_count += 1
                    print(f"Frame {frame_count} captured")

                    image_result.Release()

            print(f"Total frames captured: {frame_count}")

            # Save video information to database
            exposure_settings = camera.ExposureTime.GetValue() if not exposure_auto else 'Auto'
            resolution = f"{resolution_width}x{resolution_height}"
            timestamp = start_time

            cur.execute(
                """
                INSERT INTO videos (exposure_settings, resolution, frame_rate, lens_type, timestamp, video_path)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (str(exposure_settings), resolution, frame_rate, lens_type, timestamp, mp4_file_path)
            )
            conn.commit()

        finally:
            # Cleanup resources
            if video_file_avi:
                video_file_avi.release()
            if video_file_mp4:
                video_file_mp4.release()
            camera.EndAcquisition()
            camera.DeInit()
            del camera
            cam_list.Clear()
            system.ReleaseInstance()

            if os.path.exists(avi_file_path):
                os.remove(avi_file_path)

            if cur:
                cur.close()

            # Play video option
            play_video = input("Do you want to play the video now? (yes/no): ").lower() == 'yes'

            if play_video:
                if sys.platform.startswith('win'):
                    os.startfile(mp4_file_path)
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', mp4_file_path])
                elif sys.platform.startswith('linux'):
                    subprocess.run(['xdg-open', mp4_file_path])

    except PySpin.SpinnakerException as e:
        print(f"Error: {e}")
        camera.DeInit()
        del camera
        cam_list.Clear()
        system.ReleaseInstance()
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"PostgreSQL error: {e}")
    except ValueError as e:
        print(f"ValueError: {e}")
        camera.DeInit()
        del camera
        cam_list.Clear()
        system.ReleaseInstance()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
