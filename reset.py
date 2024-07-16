import PySpin

def reset_flir_camera():
    try:
        # Initialize Spinnaker SDK
        system = PySpin.System.GetInstance()
        print('Initializing FLIR camera system...')

        # Retrieve list of cameras
        cam_list = system.GetCameras()

        if cam_list.GetSize() == 0:
            raise Exception("No FLIR cameras found.")

        # Select and initialize the first camera
        camera = cam_list.GetByIndex(0)
        camera.Init()

        # Reset camera to factory defaults
        print('Resetting FLIR camera to factory defaults...')
        camera.UserSetDefault()

        # Apply default settings (example: set acquisition mode)
        camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

        # Deinitialize camera and release resources
        camera.DeInit()
        del camera
        cam_list.Clear()
        system.ReleaseInstance()

        print('FLIR camera reset completed successfully.')

    except PySpin.SpinnakerException as e:
        print(f"Error: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    reset_flir_camera()
