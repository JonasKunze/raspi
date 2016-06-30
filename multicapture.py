import picamera
import picamera.array

theGodArray = None

# Inherit from PiRGBAnalysis
class MyAnalysisClass(picamera.array.PiRGBAnalysis):
    def analyse(self, array):
        print(array.shape)
        global theGodArray
        theGodArray = array

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBAnalysis(camera) as output:
        camera.resolution = (256, 256)
        camera.framerate = 30
        output = MyAnalysisClass(camera)
        output2 = MyAnalysisClass(camera)
        camera.start_recording(output, format='rgb')
        camera.start_recording(output2, format='rgb', splitter_port=2, resize=(128, 128))
        camera.wait_recording(5)
        camera.stop_recording()
