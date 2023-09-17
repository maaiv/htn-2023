
import time

import scamp

import threading


import adhawkapi
import adhawkapi.frontend

import keyboard as k
from random import randint





import winsound    
import math


s = scamp.Session()



global blink
blink = False




def async_play(inst, pitch, volume, duration):

    def wrapper_play_chord(instrument,pitch,volume,duration):
        instrument.play_chord(pitch,volume,duration)
        time.sleep(duration)
        instrument.end_all_notes()

    def wrapper_play_note(instrument,pitch,volume,duration):
        instrument.play_note(pitch,volume,duration)
        time.sleep(duration)
        instrument.end_all_notes()

    if type(pitch) == list:
        threading.Thread(target=wrapper_play_chord, args=(inst,pitch,volume,duration), daemon=True).start()
    elif type(pitch) == int:
        threading.Thread(target=wrapper_play_note, args=(inst,pitch,volume,duration), daemon=True).start()

# notes = [(pitch,duration)...]

def async_queue_melody(instrument,notes,volume):

    def wrapper_queue_melody(inst,notes,volume):

        for note in notes:
            if type(note[0]) == list:
                inst.play_chord(note[0],volume,note[1])
            elif type(note[0]) == int:
                inst.play_note(note[0] + 12,volume,note[1])
            time.sleep(note[1])
            inst.end_all_notes()
                
    threading.Thread(target=wrapper_queue_melody, args=(instrument,notes,volume), daemon=True).start()

piano = s.new_part("clarinet")










class FrontendData:
    ''' BLE Frontend '''

    def __init__(self):
        # Instantiate an API object

        global blinks
        blinks = []

        self._api = adhawkapi.frontend.FrontendApi(ble_device_name='ADHAWK MINDLINK-281')
        
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
        ''' Handles the latest et data '''
        if et_data.gaze is not None:
            global xvec, yvec, zvec, vergence
            
            
            
            if type(et_data.gaze[0]) == float and type(et_data.gaze[1]) == float:
                xvec, yvec, zvec, vergence = et_data.gaze



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
                print((xvec - left), (right - left)/6)
                if (yvec - top) <= (bottom -top)/2:

                    if (xvec - left) <= (right - left)/4:
                        async_queue_melody(piano,[(56,0.8),(47,0.8),(57,1.6/3),(56,1.6/3),(54,1.6/3),
                            (52,0.8),(49,0.8),(57,1.6/3),(56,1.6/3),(54,1.6/3),
                            ],1)
                    elif (xvec - left) <= 2*(right - left)/4:
                                    
                        async_queue_melody(piano,[(51,0.8),(47,0.8),(54,1.6/3),(52,1.6/3),(51,1.6/3),
                            (52,1.6)
                            ],1)
                    elif (xvec - left) <= 3*(right - left)/4:
                        async_queue_melody(piano,[(56,0.8),(56,0.2),(54,0.2),(52,0.4),(54,0.4),(47,0.4),(51,0.4),(54,0.2),(56,0.2)],1)

                    else:
                        async_queue_melody(piano,[(57,0.4),(57,0.4),(57,0.2),(56,0.2),(54,0.2),(52,0.2),(54,0.4),(47,0.4),(51,0.2),(52,0.2),(54,0.4),
                          (52,1.6)
                          ],1)

                else:
                    if (xvec - left) <= (right - left)/4:
                        async_queue_melody(piano,[(56,0.8),(52,0.4),(47,0.4),(56,0.8),(52,0.4),(47,0.4),
                          (45,0.4),(47,0.4),(49,0.4),(56,0.4),(54,0.8),(51,0.4),(52,0.4)
                          ],1)
                    elif (xvec - left) <= 2*(right - left)/4:
                        async_queue_melody(piano,[(57,0.8),(52,0.4),(49,0.4),(57,0.8),(52,0.4),(49,0.4),
                          (51,0.4),(52,0.4),(54,0.4),(57,0.4),(56,0.8),(51,0.4),(52,0.4)
                          ],1)
                    elif (xvec - left) <= 3*(right - left)/4:
                        async_queue_melody(piano,[(52,0.1),(54,0.1),(57,0.1),(54,0.1),(61,0.4),(61,0.4),(59,0.8),
                          (52,0.1),(54,0.1),(57,0.1),(54,0.1),(59,0.4),(59,0.4),(57,0.2),(56,0.2),(54,0.4)
                          ],1)
                    else:    
                        async_queue_melody(piano,[(52,0.1),(54,0.1),(57,0.1),(54,0.1),(57,0.4),(59,0.4),(56,0.2),(54,0.2),(52,0.2),(52,0.2),
                          (59,0.4),(57,0.8)
                          ],1)
            except:
                print(xvec,yvec)

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
    
        global left, right, bottom, top

        async_queue_melody(piano,[([52,56,59],0.2),([64,56,59],0.2),([64,68,59],0.2),([64,68,71],0.8)],1)
        
        print("look at left")
        k.wait('space')
        left = xvec
        print("look at right")
        k.wait('space')
        right = xvec
        print("look at bottom ")
        k.wait('space')
        bottom = yvec
        print("look at top")
        k.wait('space')
        top = yvec

        
        xvecs = []
        for i in range(5):
            xvecs.append(xvec)


        while True:


            if k.is_pressed("p"):
                exit()
            if k.is_pressed("a"):
                print((xvec-left), (yvec-top))
            if k.is_pressed("left arrow"):
                left = xvec
            if k.is_pressed("right arrow"):
                right = xvec
            if k.is_pressed("up arrow"):
                top = yvec
            if k.is_pressed("down arrow"):
                bottom = yvec
            time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    main()
