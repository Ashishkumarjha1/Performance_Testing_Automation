from configsession import configSession
import LicenseClass
import openpyxl
import json
import mysql.connector
from mysql.connector import Error
import threading
from time import sleep
from datetime import datetime
from insert_in_testrun_output import OutputDatabase
from comparison import AlarmSystemValidator


class ConfigureChannel:
    def __init__(self, file_path, config_file):
        self.file_path = file_path
        self.ip_address = None
        self.connection = None
        self.port = None
        self.username = None
        self.password = None
        self.cfsession = None
        self.config_file = config_file
        self.license = None
        self.site_id = None
        self.description = None
        self.test_run_name = None
        self.software_version = None
        self.tester_name = None
        self.test_suit_name = None
        self.test_suit_name_list_from_table = []
        self.testcase_channel_list_from_testrun = []
        self.testcase_channel_list_from_testsuit = []

    def read_login_details(self):
        with open('login_details.json', 'r') as file:
            data = json.load(file)
            self.ip_address = data['ip_address']
            self.port = data['port']
            self.username = data['username']
            self.password = data['password']
            print(self.password)
            self.description = data['description']
            print(data['description'])
            self.description = data['description']
            print(self.description)
            print(self.description)
            self.test_run_name = data['test_run_name']
            self.software_version = data['software_version']
            self.tester_name = data['tester_name']

            self.test_suit_name = data['test_suit_name']

        return data

    def load_config(self):
        with open('config.json', 'r') as file:
            config = json.load(file)
        return config

    def connect_to_database(self):
        config = self.load_config()
        try:
            self.connection = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                port=config['port']
            )

            if self.connection.is_connected():
                print(f"Connected to {config['database']} database")
        except Error as e:
            print(f"Error connecting to {config['database']} database:", e)

    def load_db_config(self):
        # Load the database configuration from a JSON file
        with open(self.config_file, 'r') as file:
            config = json.load(file)
        return config

    

    def login_to_config_service(self):
        base_url = f"http://{self.ip_address}:{self.port}"
        # print(base_url)
        self.cfsession = configSession(base_url, self.username, self.password)
        result = self.cfsession.login()
        # print(result)

    def read_testcase_table(self):
        config = self.load_db_config()
        try:
            connection = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                port=config['port']
            )
            cursor = connection.cursor()
            # SQL query to fetch data from the testcase table
            sql_query = "SELECT * FROM testcase where test_suit_name=%s"
            # Execute the query
            cursor.execute(sql_query, (self.test_suit_name,))
            # Fetch all the rows from the result of the query
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Exception as e:
            print(f"Error fetching data from the testcase table: {e}")

    def get_list_of_test_suit_name(self):
        try:
            cursor = self.connection.cursor()
            query = "SELECT test_suit_id FROM test_suit"
            cursor.execute(query)
            result = cursor.fetchall()
            self.test_suit_name_list_from_table = [row[0] for row in result]
            cursor.close()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.test_suit_name_list_from_table = []
            cursor.close()

    def insert_into_test_suit(self):
        if self.test_suit_name not in self.test_suit_name_list_from_table:
            try:
                cursor = self.connection.cursor()
                # Fetch all test_case_name from testrun table
                fetch_query = "SELECT test_case_name FROM testcase where test_suit_name=%s"
                cursor.execute(fetch_query, (self.test_suit_name,))
                test_case_names = cursor.fetchall()
                print(test_case_names)
                
                # Concatenate all test_case_names into a single string
                test_case_list_str = ','.join(
                    [test_case_name[0] for test_case_name in test_case_names])
                print(f"Concatenated test_case_list_str: {test_case_list_str}")

                # # Concatenate all test_case_names into a single string
                # test_case_list_str = ','.join(
                #     [test_case_name[0] for test_case_name in test_case_names])
                # Insert the test_suit record
                print(
                    f"Inserting with test_suit_id: {self.test_suit_name}, Description: {self.description}, testcaselist: {test_case_list_str}")

                insert_query = """
                    INSERT INTO test_suit (test_suit_id, Description, testcaselist) 
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (self.test_suit_name,
                                              self.description, test_case_list_str))

                # Commit the transaction
                self.connection.commit()
                cursor.close()
            except Exception as e:
                print(f"An error occurred: {e}")
                self.test_suit_name_list_from_table = []
                cursor.close()

    def list_of_channels_from_testrun_table(self):
        try:
            cursor = self.connection.cursor()
            # SQL query to retrieve channels from the testcase table
            query = "SELECT TestCaseList FROM test_run"
            cursor.execute(query)

            # Fetch all rows from the query
            results = cursor.fetchall()

            # Extract channels from the results and store them in self.testcase_channel_list_from_testrun
            self.testcase_channel_list_from_testrun = [
                row[0] for row in results]
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.testcase_channel_list_from_testrun = []

    def select_testcase_list_from_test_suit_table(self):
        try:
            cursor = self.connection.cursor()
            # SQL query to retrieve channels from the testcase table
            query = "SELECT testcaselist FROM test_suit"
            cursor.execute(query)

            # Fetch all rows from the query
            results = cursor.fetchall()

            # Extract channels from the results and store them in self.testcase_channel_list_from_testrun
            self.testcase_channel_list_from_testsuit = [
                row[0] for row in results]
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.testcase_channel_list_from_testsuit = []

    def insert_into_test_run(self):

        print(self.testcase_channel_list_from_testrun)

        try:
            data = []
            data.append(self.description)
            print(self.test_run_name)
            data.append(self.test_run_name)
            data.append(self.software_version)
            # get testcaselist and insert in test_run
            cursor = self.connection.cursor()
            print(cursor)
            query = "SELECT testcaselist FROM test_suit where test_suit_id=%s"
            cursor.execute(query, (self.test_suit_name,))
            result = cursor.fetchall()

            data.append(result[0][0])

            if (result[0][0] in self.testcase_channel_list_from_testsuit):
                # SQL query to delete the row
                delete_query = "DELETE FROM test_run WHERE TestCaseList = %s"

                # Execute the delete query
                cursor.execute(delete_query, (result[0][0],))

                # Commit the transaction
                self.connection.commit()

            
            
            # cursor.close()

            today = datetime.today()
            # formatted_date = today.strftime('%d-%m-%Y')
            data.append(today)
            data.append(self.tester_name)
            data.append("/home/allgovision/")
            print(data)
            insert_query = """
                    INSERT INTO test_run (
                        Description, TestRunName, software_version, 
                        TestCaseList, test_date, tester_name, TestRunBaseURL
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
            cursor.execute(insert_query, data)
            self.connection.commit()
            self.testcase_channel_list_from_testrun.append(data[3])
            # print(cursor.rowcount,
            #       "Record inserted successfully into test_run table")

            # Get the ID of the last inserted record
            return cursor.lastrowid
        except Error as e:
            print("Error inserting into test_run:", e)
            return None

    def add_license(self):

        licenseDir = "licenseFile"
        configInfo = {"License": None}

        self.license = LicenseClass.License(licenseDir, configInfo)
        licensePayload = self.license.getPayload()
        # print(licensePayload)

        self.license.config(self.cfsession, licensePayload)
        # print(license)
        print("License added successfully")

    def map_license(self, camera_details):

        # x = {'Features': ['Crowd Detection'], "cameraid": 744,
        #      "Name": "Tripwire_33", "siteId": 119}
        # print(camera_details)
        licenseID = self.license.mapLicense(self.cfsession, camera_details)

        # print(licenseID)

    def getheader(self):
        headers = {
            'Authorization': f'Bearer {self.cfsession.jwtToken}'
        }
        return headers

    def upload_congiguration(self, file_path, channel_id_field):
        try:
            # print(file_path)
            # print(channel_id_field)
            with open(file_path, 'rb') as file:
                # Prepare the multipart form data
                files = {'importFile': file}
                data = {'channelIdField': json.dumps(channel_id_field)}
                base_url = f"http://{self.ip_address}:{self.port}"
                url = base_url + "/api/v1/config/channel"
                # print(url)
                headers = self.getheader()
                # print(headers)
                response = self.cfsession.session.put(url,
                                                      files=files,
                                                      data=data,
                                                      headers=headers)

                if response.status_code == 200:
                    print("Configuration uploaded successfully.")
                else:
                    print(
                        f"Failed to upload file. Status code: {response.status_code}")

        except Exception as e:
            print(f"An error occurred during file upload: {str(e)}")

    def start_analytics_in_separate_thread(self, runanalyticsinfo, site_id, duration):
        self.cfsession.run_analytics(runanalyticsinfo, site_id)
        sleep(duration)
        self.cfsession.stop_analytics(runanalyticsinfo, site_id)

    def get_site_id(self):

        try:
            config = self.load_db_config()
            connection = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database='allgovision',
                port=config['port']
            )
            cursor = connection.cursor()
            sql_query = "SELECT enterpriseId FROM centraluser where userId=%s"
            cursor.execute(sql_query, (self.username,))
            rows = cursor.fetchall()
            enterprise_id = rows[0][0]
            sql_query = "SELECT id FROM site where enterpriseId=%s"
            cursor.execute(sql_query, (enterprise_id,))
            rows = cursor.fetchall()
            self.site_id = rows[0][0]
            cursor.close()

        except Exception as e:
            print(f"Error fetching data from the site table: {e}")
            self.site_id = 0

    def add_camera(self):
        list_of_cameras = self.read_testcase_table()
        # print(list_of_cameras)
        cursor = self.connection.cursor()
        # SQL query to retrieve channels from the testcase table
        query = "SELECT testcaselist FROM test_suit where test_suit_id=%s"
        cursor.execute(query, (self.test_suit_name,))

        # Fetch all rows from the query
        results = cursor.fetchall()
        print(results)

        # Initialize an empty list to store all names
        all_names = []

        # Loop through each tuple in the list
        for tup in results:
            # Loop through each string in the tuple
            for item in tup:
                # Split the string by comma and extend the all_names list
                all_names.extend(item.split(','))
        print(all_names)
        
        threads = []
        for camera in list_of_cameras:
            if camera[1] in all_names:
                camera_info = {
                    "model": "video file",
                    "ip": "video file",
                    "analyticUrl": camera[2],
                    "minorUrl": camera[2],
                    "majorUrl": camera[2],
                    "transport": "file",
                    "name": camera[1],
                    "username": "user",
                    "password": "pass",
                    "port": "80",
                    "siteId": self.site_id
                }
                # print(camera_info)
                camera_id = self.cfsession.add_file_as_camera(camera_info)
                # print(camera_id)
                feature_name = [camera[6]]
                name = camera[1]
                site_id = self.site_id
                camera_details = {}
                camera_details['Features'] = feature_name
                camera_details['cameraid'] = camera_id
                camera_details['Name'] = name
                camera_details['siteId'] = self.site_id
                self.map_license(camera_details)
                self.upload_congiguration(camera[5], camera_id)
                runanalyticsinfo = {
                    "channelid": camera_id,
                }
                video_lenth = camera[3]
                # Create a thread for each camera with its duration
                thread = threading.Thread(target=self.start_analytics_in_separate_thread, args=(
                    runanalyticsinfo, self.site_id, video_lenth))
                threads.append(thread)
                thread.start()
        print("All cameras started successfully.")
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        print("All cameras stopped successfully.")


config_object = ConfigureChannel('Automation_details.xlsx', 'config.json')
config_object.connect_to_database()
config_object.read_login_details()
config_object.get_list_of_test_suit_name()
config_object.select_testcase_list_from_test_suit_table()
config_object.insert_into_test_suit()
config_object.list_of_channels_from_testrun_table()
config_object.insert_into_test_run()
# config_object.read_login_details()
config_object.get_site_id()
config_object.login_to_config_service()
config_object.add_license()
config_object.add_camera()


# calling the insert_in_testrun_output.py
output_database_object = OutputDatabase('config.json')
output_database_object.connect_to_alarm_system_database()
output_database_object.connect_to_allgovision_database()
output_database_object.clear_test_run_output_table()
output_database_object.fetch_test_run_test_case_list(
    output_database_object.alarm_system_connection)
output_database_object.read_alarms_from_allgovision()


# calling the comparison.py
validator = AlarmSystemValidator('config.json')
validator.run()
