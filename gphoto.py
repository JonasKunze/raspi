import re
import time

from PIL import Image
from PIL import ImageStat

class Wrapper(object):

    def __init__(self, subprocess):
        self._subprocess = subprocess

    def call(self, cmd):
        p = self._subprocess.Popen(cmd, shell=True, stdout=self._subprocess.PIPE,
            stderr=self._subprocess.PIPE)
        out, err = p.communicate()
        return p.returncode, out.rstrip(), err.rstrip()

class ImageAnalyzer():

    @staticmethod
    def mean_brightness(filepath):
        im = Image.open(filepath)
        stat = ImageStat.Stat(im)
        rms = stat.rms[0]
        im.close()
        return rms

class GPhoto(Wrapper):
    """ A class which wraps calls to the external gphoto2 process. """

    def __init__(self, subprocess):
        Wrapper.__init__(self, subprocess)
        self._CMD = 'gphoto2'
        self._shutter_choices = None
        self._iso_choices = None

    def get_camera_date_time(self):
        code, out, err = self.call(self._CMD + " --get-config /main/settings/datetime")
        if code != 0:
            raise Exception(err)
        timestr = None
        for line in out.split('\n'):
            if line.startswith('Current:'):
                timestr = line[line.find(':'):]
        if not timestr:
            raise Exception('No time parsed from ' + out)
        stime = time.strptime(timestr, ": %Y-%m-%d %H:%M:%S")
        return stime

    def capture_image_and_download(self):
        code, out, err = self.call(self._CMD + " --capture-image-and-download --force-overwrite")
        if code != 0:
            raise Exception(err)
        filename = None
        for line in out.split('\n'):
            if line.startswith('Saving file as '):
                filename = line.split('Saving file as ')[1]
        return filename

    def get_shutter_speeds(self):
        code, out, err = self.call([self._CMD + " --get-config /main/capturesettings/shutterspeed"])
        if code != 0:
            raise Exception(err)
        choices = [] 
        current = None
        for line in out.split('\n'):
            if line.startswith('Choice:'):
                index = line.split(' ')[1]
                name = line.split(' ')[2]
                value = line.split(' ')[2]
                if "." not in value:
                    value = value+"."
                entry = {
                'value' : eval(value),
                'index' : index,
                'name' : name
                }
                choices.append(entry) 
            if line.startswith('Current:'):
                current = line.split(' ')[1]
        self._shutter_choices = choices
        return current, choices

    def set_shutter_speed(self, secs):
        code, out, err = None, None, None
        if self._shutter_choices == None:
            self.get_shutter_speeds()
        code, out, err = self.call([self._CMD + " --set-config /main/capturesettings/shutterspeed=" + str(secs)])

    def get_isos(self):
        code, out, err = self.call([self._CMD + " --get-config /main/imgsettings/iso"])
        if code != 0:
            raise Exception(err)
        choices = {}
        current = None
        for line in out.split('\n'):
            if line.startswith('Choice:'):
                choices[line.split(' ')[2]] = line.split(' ')[1]
            if line.startswith('Current:'):
                current = line.split(' ')[1]
        self._iso_choices = choices
        return current, choices

    def set_iso(self, iso=None, index=None):
        code, out, err = None, None, None
        if iso:
            if self._iso_choices == None:
                self.get_isos()
            code, out, err = self.call([self._CMD + " --set-config /main/imgsettings/iso=" + str(self._iso_choices[iso])])
        if index:
            code, out, err = self.call([self._CMD + " --set-config /main/imgsettings/iso=" + str(index)])
