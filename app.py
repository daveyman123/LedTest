'''
	Raspberry Pi GPIO Status and Control
'''
from importlib import import_module
import os
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, Response

from camera import Camera

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera


app = Flask(__name__)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


ledYlw = 11

   
GPIO.setup(ledYlw, GPIO.OUT) 



duty = 0
# set up PWM
pwm_led_yellow = GPIO.PWM( ledYlw,100) 

	
@app.route("/")
def index():
	# Read GPIO Status
	duty = float(40)
	try:
		duty = float(request.values.get('brightness'))
	except:
		pass
	
	pwm_led_yellow.start(duty)
	ledYlwSts = duty

	
	templateData = {

      'ledYlw'  : ledYlwSts,

      }
	  
	return render_template('index.html', **templateData)

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
	
# The function below is executed when someone requests a URL with the actuator name and action in it:


@app.route("/<deviceName>/<action>")
def action(deviceName, action):
	

	duty = 0
	
	
	if deviceName == 'ledYlw':
		actuator = pwm_led_yellow
	
   
	if action == "on":
		duty = float(100)
		actuator.start(duty)
	if action == "off":
		duty = 0
		actuator.stop()
		     
	
	ledYlwSts = duty

    
	templateData = {
	 
      'ledYlw'  : ledYlwSts,
   
	}
	return render_template('index.html', **templateData)

if __name__ == "__main__":
   app.run(host='0.0.0.0', threaded=True, port=8080, debug=True)
