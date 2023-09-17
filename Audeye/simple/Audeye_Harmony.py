''' Demonstrates how to subscribe to and handle data from gaze and event streams '''

import time

from scipy.interpolate import interp1d

from scipy.spatial.transform import Rotation as R
import numpy as np
import enum 

from pysinewave import SineWave
import threading

from Instrument import Instrument

from scamp import * 

piano = Instrument.Instrument(bit_rate = 44100)


# # piano.record_key(52, duration=0.3)  # C5
# piano.record_chord([(52, 56)], duration=1)  # C5 E5 A5

# piano.play()
# # piano.close()   # Terminates PyAudio

s = Session()
theinstrument = "clarinet"
piano = s.new_part(theinstrument)


def async_play(instrument, pitch, volume, duration):
    inst = instrument


    def wrapper_play_chord(instrument,pitch,volume,duration):
        chord = instrument.start_chord(pitch,volume)
        if theinstrument != "piano":
            time.sleep(duration*1.1)
            chord.end()


    def wrapper_play_note(instrument,pitch,volume,duration):
        note = instrument.start_note(pitch,volume)
        if theinstrument != "piano":
            time.sleep(duration*2)
            note.end()

    if type(pitch) == list:
        threading.Thread(target=wrapper_play_chord, args=(inst,pitch,volume,duration), daemon=True).start()
    elif type(pitch) == int:
        threading.Thread(target=wrapper_play_note, args=(inst,pitch,volume,duration), daemon=True).start()

# def async_play(pitch, duration):
#     note = Instrument.Instrument(bit_rate = 44000)
#     note.record_key(pitch, duration)

#     threading.Thread(target=note.play, daemon=True).start()

def block(keys, duration):
    async_play(piano, keys, 1, duration*10)

# block([49, 52, 56, 52], 0.2)


def arpeggiate(pitches, duration):
    for pitch in pitches:
        async_play(piano, pitch, 1, duration)
        time.sleep(duration)

#arpeggiate([49, 52, 56, 52], 0.2)

def waltz(pitches, duration):

    async_play(piano, pitches[0], 1, duration)
    time.sleep(duration)
    for i in range(2):
        async_play(piano, pitches[1:3], 1, duration)
        time.sleep(duration)

# waltz([49, 52, 56, 52], 0.2)

    # repeat = [(pitches[0][1], pitches[0][2])]

    # async_play(pitches[0][0], duration)
    # time.sleep(duration)
    # async_chord(repeat, duration)
    # time.sleep(duration)
    # async_chord(repeat, duration)
    # note = Instrument.Instrument(bit_rate = 44000)
    # note.record_key(pitches[0][0], duration)

    # threading.Thread(target=note.play, daemon=True).start()

    # repeat = [(pitches[0][1], pitches[0][2])]
    # print(repeat)

    # time.sleep(duration)

    # piano = Instrument.Instrument(bit_rate = 44100)
    # # piano.record_key(52, duration=0.3)  # C5
    # piano.record_chord([(pitches[0][1], pitches[0][2])], duration=duration)  # C5 E5 A5
    # threading.Thread(target=piano.play, daemon=True).start()

    # time.sleep(duration)

    # piano = Instrument.Instrument(bit_rate = 44100)
    # # piano.record_key(52, duration=0.3)  # C5
    # piano.record_chord([(pitches[0][1], pitches[0][2])], duration=duration)  # C5 E5 A5
    # threading.Thread(target=piano.play, daemon=True).start()
    # # for i in range(0,2):
    # #     print("hi")
    # #     async_chord(repeat)
    # #     time.sleep(duration)








class EulerRotationOrder(enum.IntEnum):
    '''Various Euler rotation orders. lowercase x,y, z stand for the axes of the world coordinate system, and
    uppercase X, Y, and Z stands for the local moving axes'''
    # pylint: disable=invalid-name
    XY = 0  # first rotate around local X, then rotate around local Y axis (this is also known as yx')
    YX = 1  # first rotate around local Y, then rotate around local X axis (this is also known as xy')


def vector_to_angles(xpos, ypos, zpos, rotation_order: EulerRotationOrder = EulerRotationOrder.XY):
    '''
    Converts a gaze vector to [azimuth (yaw), elevation (pitch)] angles based on a specific rotation order and
    a vector defined in our usual backend coordinate system (with X oriented in the positive direction to the right,
    Y oriented in the positive direction going up and Z oriented in the positive direction behind the user). Also note
    that we want the positive yaw to be rotation to the right.
    '''
    azimuth = elevation = np.nan
    if rotation_order == EulerRotationOrder.YX:
        azimuth = np.arctan2(xpos, -zpos)
        elevation = np.arctan2(ypos, np.sqrt(xpos ** 2 + zpos ** 2))
    elif rotation_order == EulerRotationOrder.XY:
        azimuth = np.arctan2(xpos, np.sqrt(ypos ** 2 + zpos ** 2))
        elevation = np.arctan2(ypos, -zpos)
    return azimuth, elevation





import adhawkapi
import adhawkapi.frontend

import keyboard as k
from random import randint
 
import pyautogui
screenWidth, screenHeight = pyautogui.size() # Get the size of the primary monitor.

import winsound    
import math

global blink
blink = False

global notes
notes = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
    "C2": 12,
}

global notesobj
notesobj = {}
for key, value in notes.items():
    notesobj[key] = SineWave(pitch = value, pitch_per_second = 100)

class FrontendData:
    ''' BLE Frontend '''

    def __init__(self):
        # Instantiate an API object

        global blinks
        blinks = []

        self._api = adhawkapi.frontend.FrontendApi(ble_device_name='ADHAWK MINDLINK-284')
        
        # Tell the api that we wish to receive eye tracking data stream
        # with self._handle_et_data as the handler
        self._api.register_stream_handler(adhawkapi.PacketType.EYETRACKING_STREAM, self._handle_et_data)

        # Tell the api that we wish to tap into the EVENTS stream
        # with self._handle_events as the handler
        self._api.register_stream_handler(adhawkapi.PacketType.EVENTS, self._handle_events)
        
        # Start the api and set its connection callback to self._handle_tracker_connect/disconnect.
        # When the api detects a connection to a MindLink, this function will be run.
        self._api.start(tracker_connect_cb=self._handle_tracker_connect,
                        tracker_disconnect_cb=self._handle_tracker_disconnect)

        


    def shutdown(self):
        '''Shutdown the api and terminate the bluetooth connection'''
        self._api.shutdown()

    @staticmethod
    def _handle_et_data(et_data: adhawkapi.EyeTrackingStreamData):
        ''' Handles the latest et     data '''
        if et_data.gaze is not None:
            global xvec, yvec, zvec, vergence
            
            
            if type(et_data.gaze[0]) == float:
                xvec, yvec, zvec, vergence = et_data.gaze

            xvec += 2.923
            yvec -= 1.78


            # print(f'Gaze={xvec:.2f},y={yvec:.2f},z={zvec:.2f},vergence={vergence:.2f}')
            

        if et_data.eye_center is not None:
            if et_data.eye_mask == adhawkapi.EyeMask.BINOCULAR:    
                rxvec, ryvec, rzvec, lxvec, lyvec, lzvec = et_data.eye_center
                # print(f'Eye center: Left=(x={lxvec:.2f},y={lyvec:.2f},z={lzvec:.2f}) '
                #       f'Right=(x={rxvec:.2f},y={ryvec:.2f},z={rzvec:.2f})')

        if et_data.pupil_diameter is not None:
            if et_data.eye_mask == adhawkapi.EyeMask.BINOCULAR:
                rdiameter, ldiameter = et_data.pupil_diameter
                #print(f'Pupil diameter: Left={ldiameter:.2f} Right={rdiameter:.2f}')

        if et_data.imu_quaternion is not None:
            if et_data.eye_mask == adhawkapi.EyeMask.BINOCULAR:
                x, y, z, w = et_data.imu_quaternion
                # (imu_rol, imu_az, imu_el) = R.from_quat(i    mu_quaternion).as_euler('zyx', degrees=True)
                # print(f'IMU: x={x:.2f},y={y:.2f},z={z:.2f},w={w:.2f}')

    @staticmethod
    def _handle_events(event_type, timestamp, *args):
        
        if event_type == adhawkapi.Events.BLINK:

            try:
                xvecave = sum(xvecs) / len(xvecs)
                inc = (right-left)/5
                # print(left, right)
                # print(xvecave)
                print((xvecave-left)/inc, int((xvecave-left)/inc))
                notes = []
                
                if int((xvecave-left)/inc) <= 0:
                    notes = [49, 52, 56, 52] # a minor
                    # print(0)
                    # arpeggiate(, 0.3) 
                    # c = SineWave(pitch = 10, pitch_per_second = 100)
                    # c.play()
                    # time.sleep(1)
                    # c.stop
                    # notesobj["C"].play()
                    # time.sleep(1)
                    # notesobj["C"].stop()
                    

                    # winsound.Beep(329,300)
                elif int((xvecave-left)/inc) == 1:
                    notes = [54, 59, 63, 59]# g major
                    # print(1)
                    # arpeggiate([54, 59, 63, 59], 0.3) # g major
                    # c = SineWave(pitch = 12, pitch_per_second = 100)
                    # c.play()
                    # time.sleep(1)
                    # c.stop
                    # notesobj["E"].play()
                    # time.sleep(1)
                    # notesobj["E"].stop()
                    # winsound.Beep(293,300)
                elif int((xvecave-left)/inc) == 2:
                    notes = [52, 56, 59, 56]# c major
                    # print(2)
                    # arpeggiate([52, 56, 59, 56], 0.3) # c major
                    # c = SineWave(pitch = 14, pitch_per_second = 100)
                    # c.play()
                    # time.sleep(1)
                    # c.stop
                    # notesobj["G"].play()
                    # time.sleep(1)
                    # notesobj["G"].stop()    
                    # winsound.Beep(261,300)
                elif int((xvecave-left)/inc) == 3:
                    notes = [56, 60, 63, 60]# e major
                    # print("3")
                    # arpeggiate([56, 60, 63, 60], 0.3) # e major
                else:
                    notes = [57, 61, 64, 61]# f major
                    # print("3")
                    # arpeggiate([57, 61, 64, 61], 0.3) 
                

                inc = (top-bottom)/2
                print(left, right)
                print(yvec)
                print((yvec-bottom)/inc, int((yvec-bottom)/inc))

                if int(yvec-bottom)/inc <= 0:
                    arpeggiate(notes, 0.3)
                else:
                    arpeggiate(notes, 0.3)

                

            except:
                pass

            duration = args[0]
            # print(f'Got blink: {timestamp} {duration}')    

        if event_type == adhawkapi.Events.EYE_CLOSED:
            eye_idx = args[0]
            # print(f'Eye Close: {t    imestamp} {eye_idx}')
        if event_type == adhawkapi.Events.EYE_OPENED:
            eye_idx = args[0]
            # print(f'Eye Open: {timestamp} {eye_idx}')

    def _handle_tracker_connect(self):
        print("Tracker connected")
        self._api.set_et_stream_rate(60, callback=lambda *args: None)

        self._api.set_et_stream_control([
            adhawkapi.EyeTrackingStreamTypes.GAZE,
            adhawkapi.EyeTrackingStreamTypes.EYE_CENTER,
            adhawkapi.EyeTrackingStreamTypes.PUPIL_DIAMETER,
            adhawkapi.EyeTrackingStreamTypes.IMU_QUATERNION,
        ], True, callback=lambda *args: None)

        self._api.set_event_control(adhawkapi.EventControlBit.BLINK, 1, callback=lambda *args: None)
        self._api.set_event_control(adhawkapi.EventControlBit.EYE_CLOSE_OPEN, 1, callback=lambda *args: None)

    def _handle_tracker_disconnect(self):
        print("Tracker disconnected")


def main():
    
    ''' App entrypoint '''
    frontend = FrontendData()    

    try:
        time.sleep(1)
        global left, right, bottom, top, xvecs
        print("look at left")
        k.wait('space')
        left = xvec
        print(left)
        print("look at right")
        k.wait('space')
        right = xvec
        print(right)
        print("look at bottom ")
        k.wait('space')
        bottom = yvec
        print(bottom)
        print("look at top")
        k.wait('space')
        top = yvec
        print(top)

        xvecs = []
        for i in range(10):
            xvecs.append(xvec)
        
        # print(xvecs)

        while True:            
            xvecs.pop(0)
            xvecs.append(xvec)
            # print(xvecs)
            if k.is_pressed("p"):
                exit()
            if k.is_pressed("a"):
                print((xvec-left), (yvec-top))
            if k.is_pressed("left arrow"):
                left = xvec
                print(left)
            if k.is_pressed("right arrow"):
                right = xvec
                print(right)
            if k.is_pressed("up arrow"):
                top = yvec
                print(top)
            if k.is_pressed("down arrow"):
                bottom = yvec
                print(bottom)
            time.sleep(0.1)
        # time.sleep(1)

        # print("look at top left")
        # k.wait('space')
        # topleft = (xvec,yvec)
        # print("look at top right")
        # k.wait('space')
        # topright = (xvec,yvec)
        # print("look at bottom right")
        # k.wait('space')
        # bottomright = (xvec,yvec)
        # print("look at bottom left")
        # k.wait('space')
        # bottomleft = (xvec,yvec)
        # print(topleft,topright,bottomleft,bottomright)
        # while True:        
        #     try:
        #         print(xvec,yvec) 
        #         xmap = interp1d([topleft[0], bottomright[0]],[0,screenWidth])    
        #         ymap = interp1d([bottomleft[1], topright[1]],[screenHeight,0])
        #         global xpos, ypos     

        #         xpos = xmap(xvec)
        #         ypos = ymap(yvec)
        #         print(xvec,yvec) 

        #         try:    
        #             pyautogui.moveTo(xpos,ypos)
        #         except:
        #             pass
        #     except:
        #         pass
        #     if k.is_pressed("a"):
        #         print(ypos, xpos)
        #         print(topleft,topright,bottomleft,bottomright)
        #     if k.is_pressed("p"):
        #         exit()    
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
