# -*- coding: UTF-8 -*-
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask_login import login_user, logout_user, login_required, \
    current_user
from werkzeug.exceptions import abort
import json
from datetime import datetime, timedelta 
import time
from .. import db
from ..models import InstrumentModel
from ..email import send_email
from . import instrument

def refreshInstrmentState():
    
    # 获取今天的时间
    now_time = datetime.now()
    utc_time = now_time - timedelta(hours=8)
    utc_time = utc_time.strftime("%Y%m%d")   

    # 获取所有设备id号
    instrmentIdList = db.session.execute(
        '''SELECT id FROM instrument'''
    ).fetchall()
    print(instrmentIdList)
    borrowList = []
    # 获取借用人列表
    for i in instrmentIdList:
        print(i[0]) 
        borrowList += db.session.execute(
               ''' SELECT instrument_id, borrowMan_id, borrowState
                    FROM borrow
                    where instrument_id = {instrument_id} and 
                    borrowStartTime <= {Time} and
                    borrowEndTime >= {Time}'''.format(instrument_id=i[0],Time=utc_time) 
            ).fetchall()
    # 重置所有设备状态
    db.session.execute(
                ''' UPDATE instrument SET 
                    useState = 'free', borrowMan_id = null''')
    db.session.commit()
    # 更新设备状态
    for i in borrowList:
        if i[0]:
            db.session.execute(
                    ''' UPDATE instrument SET 
                        borrowMan_id = {borrowMan_id}, useState = '{State}'
                        WHERE id = {id};'''.format(borrowMan_id = i[1], State = i[2], id = i[0])
            )
    db.session.commit()



# 主界面
@instrument.route('/')
def index():
    # 判断借用人是否为空
    refreshInstrmentState()

    posts = db.session.execute(
    '''SELECT i.id, i.name, i.brand, i.model, useState, username
        FROM instrument i
        JOIN users u
        ON i.borrowMan_id = u.id;'''
    ).fetchall()

    posts += db.session.execute(
    '''SELECT id, name, brand, model, useState
        FROM instrument 
        WHERE borrowMan_id is null
        ;'''
    ).fetchall()
    # 排序
    posts.sort()
    
    print(posts)

    return render_template('instrument/index.html', posts = posts)

# 获取设备信息
def get_post(id):
    post = db.session.execute(
            '''SELECT id, name,  brand, model, SN, assetNumber, useState, maintenanceState, 
               describe, placeNumber, calibrationDate, laboratory, RFID
               FROM instrument
               WHERE id = {id}'''.format(id=id)
            ).fetchone()

    if post is None:
        abort(404, "Post id {id} doesn't exist.".format(id=id))
    '''
    if check_author and post["id"] != g.user["id"]:
        abort(403)
    '''
    return post

# 创建新设备
@instrument.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        name = request.form["name"]
        brand = request.form["brand"]
        model = request.form["model"]
        SN = request.form["SN"]
        assetNumber = request.form["assetNumber"]
        useState = request.form["useState"]
        maintenanceState = request.form["maintenanceState"]
        describe = request.form["describe"]
        placeNumber = request.form["placeNumber"]
        calibrationDate = request.form["calibrationDate"]
        laboratory = request.form["laboratory"]
        RFID = request.form["RFID"]

        error = None

        if not name:
            error = "Title is required."
        print("error")
        if error is not None:
            flash(error)
        else:
            instrumentModel = InstrumentModel(name=name,
                        brand = brand,
                        model = model,
                        SN = SN,
                        assetNumber = assetNumber,
                        useState = useState,
                        maintenanceState = maintenanceState,
                        describe = describe,
                        placeNumber = placeNumber,
                        calibrationDate = calibrationDate,
                        laboratory = laboratory,
                        RFID = RFID)
            db.session.add(instrumentModel)
            db.session.commit()

            return redirect(url_for("instrument.index"))

    return render_template("instrument/create.html")

# 更新设备信息
@instrument.route("/update/<int:id>", methods=("GET", "POST"))
@login_required
def update(id):
    
    if request.method == "POST":
        name = request.form["name"]
        brand = request.form["brand"]
        model = request.form["model"]
        SN = request.form["SN"]
        assetNumber = request.form["assetNumber"]
        useState = request.form["useState"]
        maintenanceState = request.form["maintenanceState"]
        describe = request.form["describe"]
        placeNumber = request.form["placeNumber"]
        calibrationDate = request.form["calibrationDate"]
        laboratory = request.form["laboratory"]
        RFID = request.form["RFID"]

        db.session.execute(
                '''UPDATE instrument SET name = {name},  brand = {brand}, model = {model}, SN = {SN}, assetNumber = {assetNumber}, useState = {useState}, 
                maintenanceState = {maintenanceState},describe = {describe}, placeNumber = {placeNumber}, calibrationDate = {calibrationDate}, laboratory = {laboratory}, RFID = {RFID} 
                WHERE id = {id}'''.
                format(name=name, brand=brand, model=model, SN=SN, assetNumber=assetNumber, useState=useState, maintenanceState=maintenanceState, 
                describe=describe, placeNumber=placeNumber, calibrationDate=calibrationDate, laboratory=laboratory, RFID=RFID, id=id),
        )
        db.session.commit()
        return redirect(url_for("instrument.index"))
    else :
        post = get_post(id)
        print(post)
    return render_template("instrument/update.html", post=post)

# 删除仪器
@instrument.route("/delete/<int:id>", methods=("POST","GET"))
@login_required
def delete(id):
    db.session.execute("DELETE FROM instrument WHERE id = ?", (id,))
    db.session.commit()
    return redirect(url_for("instrument.index"))

# 请求借用界面
@instrument.route("/borrow/<int:id>", methods=("GET", "POST"))
def borrow(id):
    post = get_post(id)
    print(post)
    return render_template("instrument/borrow.html", post=post, isborrow=True)

# 请求借用界面
@instrument.route("/lookBorrow/<int:id>", methods=("GET", "POST"))
def lookBorrow(id):
    post = get_post(id)
    print(post)
    return render_template("instrument/borrow.html", post=post, isborrow=False)

# 功能函数，将借用时间的元组转为列表
def borrowTimeTupleToList(Tuple):
    returnlist = [[] for i in range(len(Tuple))]
    temp = 0
    # 元组转列表
    for s in Tuple: 
        returnlist[temp].append(s[0])
        returnlist[temp].append(s[1])
        temp += 1
    return returnlist

# 获取仪器借用时间
@instrument.route("/getBorrowTime/<int:id>", methods=("GET", "POST"))
def getBorrowTime(id):
    continueList = []
    intermittentList = []
    resultJS = {}
    continueList = borrowTimeTupleToList(
        db.session.execute(
        ''' SELECT borrowStartTime, borrowEndTime
            FROM borrow
            WHERE instrument_id = {id}
            AND borrowState='continue'; '''.format(id=id)
        ).fetchall()
    )
    
    intermittentList = borrowTimeTupleToList(
        db.session.execute(
        ''' SELECT borrowStartTime, borrowEndTime
            FROM borrow
            WHERE instrument_id = {id}
            AND borrowState='intermittent'; '''.format(id=id)
        ).fetchall()
    )

    resultJS['continue'] = list(continueList)
    resultJS['intermittent'] = list(intermittentList)
    print(resultJS)
    return json.dumps(resultJS)
    #return render_template("instrument/borrow.html", post=posts)

# 提交借用时间
@instrument.route("/putBorrowTime/<int:id>", methods=("GET", "POST"))
def putBorrowTime(id):
    data = json.loads(request.form.get('timeData'))
    if len(data['intermittentTime']) != 2 and len(data['continueTime']) != 2 :
        return 'None'

    if len(data['intermittentTime']) == 2 :
        db.session.execute(
            '''INSERT INTO borrow (instrument_id  , borrowState,  borrowStartTime, borrowEndTime, borrowMan_id
            ) VALUES ({id}, 'intermittent', {startTime}, {endTime}, {userId})'''.\
            format(id=id, startTime = data['intermittentTime'][0], endTime=data['intermittentTime'][1], userId=current_user.id),
        )
    elif len(data['continueTime']) == 2 :
        db.session.execute(
            '''INSERT INTO borrow (instrument_id  , borrowState,  borrowStartTime, borrowEndTime, borrowMan_id
            ) VALUES ({id}, 'continue', {startTime}, {endTime}, {userId})'''.
            format(id=id, startTime = data['continueTime'][0], endTime=data['continueTime'][1], userId=current_user.id),
        )
    db.session.commit()

    return 'success'

# 删除仪器借用信息
@instrument.route("/deleteBorrowTime/<int:id>", methods=("GET", "POST"))
def deleteBorrowTime(id):
    db.session.seexecute(
        '''DELETE FROM borrow 
        WHERE instrument_id = {id} and borrowMan_id = {userId}'''.
        format(id=id, userId=current_user.id),
    )
    db.session.session.commit()
    return 'success'
