import time
import PySpin

def measure_data_transfer_rate_lower_resolution(camera, duration=10):
    camera.Init()

    # Set frame rate to maximum
    frame_rate_max = camera.AcquisitionFrameRate.GetMax()
    camera.AcquisitionFrameRateEnable.SetValue(True)
    camera.AcquisitionFrameRate.SetValue(frame_rate_max)

    # Set lower resolution
    camera.Width.SetValue(640)
    camera.Height.SetValue(480)

    # Start capturing images
    camera.BeginAcquisition()

    start_time = time.time()
    frame_count = 0
    total_data_transferred = 0

    try:
        while time.time() - start_time < duration:
            image_result = camera.GetNextImage(1000)  # 1000 ms timeout

            if image_result.IsIncomplete():
                print(f'Image incomplete with image status {image_result.GetImageStatus()} ...')
            else:
                image_data = image_result.GetNDArray()
                data_size = image_data.nbytes
                total_data_transferred += data_size
                frame_count += 1
                image_result.Release()

    finally:
        camera.EndAcquisition()
        camera.DeInit()

    elapsed_time = time.time() - start_time
    data_rate = total_data_transferred / elapsed_time / (1024 * 1024)  # MB/s

    return frame_count, data_rate, elapsed_time

# Initialize system and camera
system = PySpin.System.GetInstance()
cam_list = system.GetCameras()
camera = cam_list.GetByIndex(0)

try:
    frame_count, data_rate, elapsed_time = measure_data_transfer_rate_lower_resolution(camera)
    print(f"Captured {frame_count} frames in {elapsed_time:.2f} seconds at lower resolution.")
    print(f"Data transfer rate: {data_rate:.2f} MB/s")
finally:
    del camera
    cam_list.Clear()
    system.ReleaseInstance()
