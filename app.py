from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import jsonify
import requests
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1234@localhost:5432/test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

    
class db_st_analysis(db.Model):
    __tablename__ = 'db_st_analysis'
    
    Frame_id = db.Column(db.Integer, primary_key=True)
    Obj_id = db.Column(db.Integer)
    Class_Type = db.Column(db.String(30), nullable=False)
    Obj_direction = db.Column(db.String(30), nullable=False)
    cam_position = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<Obj %r>' % self.Frame_id
    


db.create_all()

def send_to_database():
    data = []
    data.append({
        'Obj_id': random.randrange(1, 50, 3),
        'Class_Type': random.choice(['car', 'truck']),
        'Obj_direction': random.choice(['In', 'Out']),
        'cam_position': random.choice(['cam_1', 'cam_2'])
    })
    # http request to the backend server
    res = requests.post("http://127.0.0.1:5000/json_example", json={
        'data': data
        })

def send_random_to_db():
    # I made it in a dict format in case I have to work with dict later, then it is very similar
    # creating random data
    data = {
        'Obj_id': random.randrange(1, 50, 3),
        'Class_Type': random.choice(['car', 'truck']),
        'Obj_direction': random.choice(['In', 'Out']),
        'cam_position': random.choice(['cam_1', 'cam_2'])
    }
    Obj_id = data['Obj_id']
    Class_Type = data['Class_Type']
    Obj_direction = data['Obj_direction']
    cam_position = data['cam_position']
    new_record = db_st_analysis(Obj_id=Obj_id, 
                                Class_Type=Class_Type, 
                                Obj_direction=Obj_direction, 
                                cam_position=cam_position)
    # returns a response for the insertion
    # or no return if we don't want instant reload to the page
    try:
        db.session.add(new_record)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue adding your record'


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        new_record = db_st_analysis(Obj_id=request.form['Obj_id'],
                                    Class_Type=request.form['Class_Type'], 
                                    Obj_direction=request.form['Obj_direction'], 
                                    cam_position=request.form['cam_position'])

        try:
            db.session.add(new_record)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        data = db_st_analysis.query.order_by(db_st_analysis.Frame_id).all()
        print(type(data))
        print(data)
        return render_template('index.html', data=data)
    


@app.route('/delete/<int:id>')
def delete(id):
    row_to_delete = db_st_analysis.query.get_or_404(id)

    try:
        db.session.delete(row_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    item = db_st_analysis.query.get_or_404(id)

    if request.method == 'POST':
        # return "hellop"
        print("reached here")
        item.Class_Type = request.form['Class_Type']
        # row.Obj_direction = request.form['Obj_direction']
        # row.cam_position = request.form['cam_position']
        # item = db_st_analysis(Frame_id=id, Obj_id=row.Obj_id, Class_Type=request.form['Class_Type'], Obj_direction=request.form['Obj_direction'], cam_position=request.form['cam_position'])
        # item.update()

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', item=item)
    
@app.route('/json_example', methods=['POST'])
def json_example():
    requested_data = request.get_json()
    request_data = requested_data['data'][0]
    
    print(type(request_data))
    print(request_data)

    Obj_id = request_data['Obj_id']
    Class_Type = request_data['Class_Type']
    Obj_direction = request_data['Obj_direction']
    cam_position = request_data['cam_position']
    
    # print(Obj_id)
    # print(Class_Type)
    # print(Obj_direction)
    # print(cam_position)
    
    new_record = db_st_analysis(Obj_id=Obj_id, 
                                Class_Type=Class_Type, 
                                Obj_direction=Obj_direction, 
                                cam_position=cam_position)
    # returns a response for the insertion
    # or no return if we don't want instant reload to the page
    try:
        db.session.add(new_record)
        db.session.commit()
        # return redirect('/')
    except:
        return 'There was an issue adding your record'
    
    return '...'

##############################################################
#                            camera
##############################################################
import cv2
from flask import Response

    
camera = cv2.VideoCapture(0)
def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    
@app.route('/get_cam')
def get_cam():
    return render_template('index_cam.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
