import mysql.connector

class User:

    def connect(self):
        self.mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="attendance_db"
    )
        self.mycursor = self.mydb.cursor()

    def close(self):
        if (self.mydb is not None):
            self.mycursor.close()
            self.mydb.close()

    def addUser(self, name, password, face_features, audio_profile):
        self.connect()
        noErr = True
        name = name.strip()
        sql = "INSERT INTO user_tbl (name, password, face_features, audio_profile) VALUES (%s, %s, %s, %s)"
        # check later if password is uniuqe
        try:
            self.mycursor.execute(sql, (name, password, face_features, audio_profile))
        except Exception as e:
            print(e)
            noErr = False
        finally:
            self.mydb.commit()
            self.close()
            return noErr

    def updateUser(self, id, name = None, password = None, face_features = None, audio_profile = None, isActive = None):
        self.connect()
        self.mycursor.execute(f"SELECT * FROM user_tbl WHERE user_id = {id}")
        result = self.mycursor.fetchone()
        if (result is None):
            print("no User with this id is found")
            self.close()
            return False

        tmp_id, tmp_name, tmp_password, tmp_face_features, tmp_audio_profile, tmp_isActive = result

        if (name is None):
            name = tmp_name
        if (password is None):
            password = tmp_password
        if (face_features is None):
            face_features = tmp_face_features
        if (audio_profile is None):
            audio_profile = tmp_audio_profile
        if (isActive is None):
            isActive = tmp_isActive
        #check later if password is uniuqe
        sql = "UPDATE user_tbl SET name = %s, password = %s, face_features = %s, audio_profile = %s, isActive = %s WHERE user_id = %s"
        val = (name, password, face_features, audio_profile, isActive, id)
        self.mycursor.execute(sql, val)
        self.mydb.commit()



        self.close()

    def deleteUser(self, id):
        self.connect()
        self.mycursor.execute(f"SELECT * FROM user_tbl WHERE user_id = {id} AND isActive = True")
        result = self.mycursor.fetchone()
        if (result is None):
            print("no User with this id is found")
            self.close()
            return False

        sql = f"DELETE FROM user_tbl WHERE user_id = {id}"
        self.mycursor.execute(sql)
        self.mydb.commit()
        returnVal = True
        # if (self.mycursor.rowcount == 0):
        #     returnVal = False
        self.close()
        return returnVal

    def getOneUser(self, id):
        self.connect()
        self.mycursor.execute(f"SELECT * FROM user_tbl WHERE user_id = {id} AND isActive = True")
        result = self.mycursor.fetchone()
        self.close()
        return result #if empty it will return None

    def getAllUsers(self):
        self.connect()
        self.mycursor.execute("SELECT * FROM user_tbl WHERE isActive = True")
        result = self.mycursor.fetchall()
        self.close()
        return result #if empty it will return None

    def markAttended(self, id = None, credit = (None, None)):
        self.connect()
        noErr = True
        if (id is not None):
            sql = f"INSERT INTO attendance_tbl VALUES (null, {id}, null)"
            try:
                self.mycursor.execute(sql)
            except Exception as e:
                if (e.args[2] == "23000"):
                    print("no user with this user id")
                    noErr = False
                elif (e.args[2] == "45000"):
                    print("user attendance already recorded")
                    noErr = False
                # raise Exception("")
            finally:
                self.mydb.commit()
                self.close()

        if (credit != (None, None)):
            name, password = credit
            sql = f"SELECT user_id FROM user_tbl WHERE name = '{name}' AND password = '{password}';" #AND isActive = 'True'
            self.mycursor.execute(sql)
            result = self.mycursor.fetchone()
            if (result):
                id = result[0]
                noErr = self.markAttended(id = id)
            else:
                print("no user found with provided credential")
                noErr = False
        return noErr


