import PySpin

def configure_camera_for_max_fps(camera):
    camera.Init()

    camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

    frame_rate_max = camera.AcquisitionFrameRate.GetMax()
    camera.AcquisitionFrameRateEnable.SetValue(True)
    camera.AcquisitionFrameRate.SetValue(frame_rate_max)

    width_max = camera.Width.GetMax()
    height_max = camera.Height.GetMax()
    camera.Width.SetValue(width_max)
    camera.Height.SetValue(height_max)

    camera.DeInit()

system = PySpin.System.GetInstance()
cam_list = system.GetCameras()
camera = cam_list.GetByIndex(0)

try:
    configure_camera_for_max_fps(camera)
    print("Camera configured for maximum frame rate.")
finally:
    del camera
    cam_list.Clear()
    system.ReleaseInstance()
