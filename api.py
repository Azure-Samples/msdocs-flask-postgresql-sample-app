from flask import request,jsonify
from flask_restful  import Resource,fields,marshal_with,marshal
from flask_security import auth_required,auth_token_required,hash_password,login_user,verify_password,current_user,logout_user
from models import db, Users,Device,Appliance, user_datastore
from datetime import datetime

#------------output fields-----------------
device_fields={
    "id":fields.Integer,
    "device_name":fields.String(attribute='name'),
    "location":fields.String,
    "appliances":fields.String(attribute=lambda x:[(i.id,i.name) for i in x.device_appliance])
}
appliance_fields={
    "appliance_id":fields.Integer(attribute="id"),
    "name":fields.String,
    "type":fields.String,
    "value":fields.Float,
    "mode":fields.Integer
}
user_fields={
    "user_id":fields.String(attribute='id'),
    "username":fields.String,
    "email":fields.String
}
print( )
#------------validation functions----------
def username_valid(name):
    b=(" " not in name)and(name not in [i[0] for i in db.session.query(Users.username).all()])
    return b
def password_valid(p):
    b=(" " not in p)
    return b
def email_valid(email):
    b=(email not in [x.email for x in Users.query.all()])
    print(b)
    return b
#----caching workaround--------------

# def get_tracker(tracker_id):
#     try:
#         trk=tracker.query.get(int(tracker_id))
#         if trk==None:
#             return "Tracker id not found",404
#         if trk.user_id!=current_user.id:
#             return "not authorized to access this tracker",400
#         return {**marshal(trk,tracker_fields),"log_objects":marshal(trk.logs,log_fields)}
#     except:
#         return "Internal Server Error",500

# @cache.memoize(60)
# def get_logs(log_id):
#     try:
#         logobj=log.query.get(int(log_id))
#         if logobj.parent.user_id!=current_user.id:
#             return "Not authorized to access this log",400
#         if logobj:
#             return marshal(logobj,log_fields)
#         else:
#             return "NOT FOUND",404
#     except:
#         return "INTERNAL SERVER ERROR",500

#---------API-----------
class UserApi(Resource):
    @auth_required('token')
    def get(self,username):
        print(current_user)
        try:
            if username=="*":
                user=Users.query.all()
            elif " " not in username:
                user=Users.query.filter(Users.username==username).first()
            else:
                return "invalid user",400
            #print(user) #debug print
            if user != None:
                # print({*user,user.get_auth_token()})
                return marshal(user,user_fields),200
            else:
                return "User not found",404
        except:
            return "Internal Server Error",500

    @auth_required("token")
    def put(self,username):
        try:
            newdata=request.json
            q=Users.query.filter(Users.username==username)
            pdata=q.one()
            if pdata==None:
                return "User not found",404
            modified_username=newdata.get("modified_username")
            password=newdata.get("old_password")
            modified_email=newdata.get("modified_email")
            uname_valid=modified_username.isalnum()
            if verify_password(password,pdata.password):
                if uname_valid:
                    if newdata.get("new_password"):
                        modified_password=newdata.get("new_password")
                        if not password_valid(modified_password):
                            return "modified password not valid",400
                        else:
                            q.update({"username":str(modified_username),
                            "password":hash_password(modified_password),
                            "email":str(modified_email)})
                            db.session.commit()
                    else:
                        q.update({"username":str(modified_username),
                        "email":str(modified_email)})
                        db.session.commit()
                elif not uname_valid:
                    return "Modified Username is invalid",400
            else:
                return "wrong password",400
            return {**marshal(pdata,user_fields),
            "auth_token":pdata.get_auth_token()},200
        except Exception as e:
            return e,500

    @auth_required("token")
    def delete(self,username):
        try:
            loginuser=request.json
            pwd=loginuser["password"]
            if (username,) in db.session.query(Users.username).all():
                dbuser=Users.query.filter(Users.username==username).first()
                if verify_password(pwd,dbuser.password):
                    db.session.delete(dbuser)
                    db.session.commit()
                else:
                    return "invalid password",400
            return "Deleted",200
        except:
            return "Internal Server Error",500

    def post(self):
        try:
            data=request.json
            if data:
                if username_valid(data['username']) and password_valid(data['password']) and email_valid(data["email"]):
                    # db.session.add(new_user)
                    user_datastore.create_user(username=str(data['username']),
                    email=str(data['email']),password=hash_password(data['password']))
                    dbuser=user_datastore.find_user(username=str(data['username']))
                    db.session.commit()
                elif not username_valid(data['username']):
                    return "Username is invalid",400
                elif not password_valid(data['password']):
                    return "Password is invalid",400
            return {**marshal(dbuser,user_fields),"auth_token":dbuser.get_auth_token()},200
        except Exception as e:
            return "Internal Server Error",500

class LoginApi(Resource):
    def get(self):
        pass
    def post(self):
        try:
            loginuser=request.json
            username=loginuser["username"]
            pwd=loginuser["password"]
            user_valid=username and username.isalnum()
            pass_valid=pwd and password_valid(pwd)
            if user_valid and pass_valid:
                if (username,) in db.session.query(Users.username).all():
                    dbuser=Users.query.filter(Users.username==username).first()
                    if verify_password(pwd,dbuser.password):
                        print(login_user(dbuser,remember=True,authn_via=["password"]))
                        return {**marshal(dbuser,user_fields),
                        "auth_token":dbuser.get_auth_token()},200
                    else:
                        print("invalid_password")
                        return "wrong password",400
                else:
                    print("user not found")
                    return "user not found",400
        except Exception as e:
            print(e)
            return e,415

class DeviceApi(Resource):
    @auth_required("token")
    def get(self,id):
        try:
            if id=="*":
                devices=current_user.user_devices
            elif type(id)==int:
                devices=Device.query.filter(id==id).first()
                if devices and devices.user_id==current_user.id:
                    return marshal(devices,device_fields),200
            else:
                return "invalid user",400
            #print(user) #debug print
            if devices != None:
                # print({*user,user.get_auth_token()})
                if len(devices)>1:
                    return marshal(devices,device_fields),200
                else:
                    result=[]
                    for i in devices:
                        result.append(marshal(i,device_fields))
                    return result,200
            else:
                return "User not found",404
        except:
            return "Internal Server Error",500

    @auth_required("token")
    def post(self):
        try:
            data=request.json
            if data:
                if len(data["secret"])==8 :
                    return "Invalid SECRET",402
                if len(data["name"])==0 :
                    return "Invalid NAME",402
                secret=str(data['secret']),
                name=data['name']
                location= data['location']
                user_id= current_user.id
                device=Device(secret=secret,name=name,location=location,user_id=user_id)
                db.session.add(device)
                db.session.commit()
                app1=Appliance(name="light1",type="digital",device_id=device.id)
                app2=Appliance(name="light2",type="digital",device_id=device.id)
                app3=Appliance(name="socket",type="digital",device_id=device.id)
                app4=Appliance(name="fan",type="analog",device_id=device.id)
                db.session.add(app1)
                db.session.add(app2)
                db.session.add(app3)
                db.session.add(app4)
                db.session.commit()
            return marshal(device,device_fields),200
        except Exception as e:
            return f"Internal Server Error due to {e}",500

    @auth_required("token")
    def put(self,id):
        try:
            newdata=request.json
            q=Device.query.filter(Device.id==id)
            pdata=q.one()
            if pdata==None:
                return "Device not found",404
            modified_name=newdata.get("modified_name")
            modified_location=newdata.get("modified_location")
            if modified_name==None|"":
                return "Invalid name",402
            if verify_password(password,pdata.password):
                if uname_valid:
                    if newdata.get("new_password"):
                        modified_password=newdata.get("new_password")
                        if not password_valid(modified_password):
                            return "modified password not valid",400
                        else:
                            q.update({"username":str(modified_username),
                            "password":hash_password(modified_password),
                            "email":str(modified_email)})
                            db.session.commit()
                    else:
                        q.update({"username":str(modified_username),
                        "email":str(modified_email)})
                        db.session.commit()
                elif not uname_valid:
                    return "Modified Username is invalid",400
            else:
                return "wrong password",400
            return {**marshal(pdata,user_fields),
            "auth_token":pdata.get_auth_token()},200
        except Exception as e:
            return e,500

        return 200

    @auth_required("token")
    def delete(self,tracker_id):
        return "OK",200
    
class ApplianceApi(Resource):

    @auth_required("token")
    def get(self,tracker_id):
        return 200

    @auth_required("token")
    def post(self):
        return 200

    @auth_required("token")
    def put(self,tracker_id):
        return 200

    @auth_required("token")
    def delete(self,tracker_id):
        return "OK",200
#===========Api===========
