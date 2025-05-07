from openpyxl import load_workbook
import mysql.connector
from mysql.connector import Error
import json
import datetime


class OutputDatabase:
    def __init__(self, config_path):
        self.config_path = config_path
        self.connection = None
        self.alarm_system_connection = None
        self.test_case_lists = []
        self.test_suit_name = None

    def read_login_details(self):
        with open('login_details.json', 'r') as file:
            data = json.load(file)

            self.test_suit_name = data['test_suit_name']

        return data

    def load_config(self):
        with open(self.config_path, 'r') as file:
            config = json.load(file)
        return config

    def connect_to_alarm_system_database(self):
        config = self.load_config()
        try:
            self.alarm_system_connection = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                port=config['port']
            )
            if self.alarm_system_connection.is_connected():
                print(f"Connected to {config['database']} database")
        except Error as e:
            print(f"Error connecting to {config['database']} database:", e)

    def fetch_test_run_test_case_list(self, connection):
        try:
            cursor = connection.cursor()

            # Query to get the last inserted row
            query = "SELECT test_run_id, TestCaseList FROM test_run ORDER BY test_run_id DESC LIMIT 1"
            cursor.execute(query)

            # Fetch the last inserted row
            result = cursor.fetchall()

            print(result)
            if result:
                # Fetching and parsing JSON data

                self.test_case_lists = [(row[0], row[1].split(','))
                                        for row in result]
            else:
                self.test_case_lists = []

        except Error as e:
            print("Error fetching TestCaseList from test_run:", e)
            self.test_case_lists = []

    def get_starting_time_from_allgovision(self, channel_name):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT streamingConfig
                FROM channel
                WHERE name = %s
            """
            cursor.execute(query, (channel_name,))
            result = cursor.fetchone()
            if result:
                streaming_time_str = result['streamingConfig']
                # Assume streaming_time_str is in 'HH:MM:SS' format
                current_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
                starting_time_str = f"{current_date_str} {streaming_time_str}"
                starting_time = datetime.datetime.strptime(
                    starting_time_str, '%Y-%m-%d %H:%M:%S')
                return starting_time
            else:
                print(
                    f"No starting time found for channelName='{channel_name}'")
                return None
        except Error as e:
            print("Error querying starting time:", e)
            return None

    def get_video_length(self, channel_name):
        try:
            cursor = self.alarm_system_connection.cursor()
            query = "SELECT video_length_in_seconds FROM testcase where test_case_name = %s"
            cursor.execute(query, (channel_name,))
            result = cursor.fetchall()
            if result:
                return result[0][0]
            else:
                return 0

        except Error as e:
            print("Error fetching TestCaseList from test_run:", e)
            return 0

    def query_alarms_from_allgovision(self, start_time, end_time, channel_name):
        try:
            # print(start_time)
            # print(end_time)
            # print(channel_name)
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT TimeStamp, AlarmName
                FROM alarm
                WHERE TimeStamp BETWEEN %s AND %s AND camName = %s
            """
            cursor.execute(query, (start_time, end_time, channel_name))
            alarms_data = cursor.fetchall()
            return alarms_data
        except Error as e:
            print("Error querying alarms:", e)
            return None

    def insert_into_test_run_output(self, data):
        try:
            cursor = self.alarm_system_connection.cursor()
            insert_query = """
                INSERT INTO test_run_output (
                    test_run_id,test_case_name,
                    time_of_alarm, name_of_alarm
                ) VALUES (%s,%s,%s, %s)
            """
            cursor.executemany(insert_query, data)
            self.alarm_system_connection.commit()
            # print(cursor.rowcount,
            #       "Record(s) inserted successfully into test_run_output table")
        except Error as e:
            print("Error inserting into test_run_output:", e)

    # clear test_run output table
    def clear_test_run_output_table(self):
        try:
            cursor = self.alarm_system_connection.cursor()
            query = "DELETE FROM test_run_output"
            cursor.execute(query)
            self.alarm_system_connection.commit()
            # print("Data deleted successfully from test_run_output table")
        except Error as e:
            print("Error deleting from test_run_output")

    def read_alarms_from_allgovision(self):

        test_run_id_channel_name_list = []
        for run_id, test_case_name in self.test_case_lists:
            for name in test_case_name:

                # print(name)
                test_run_id_channel_name_list.append(
                    (run_id, name)
                )

        # Print the list of tuples containing test_run_id, id, and channel_name
        # print("List of tuples (test_run_id, id, channel_name):")
        # for item in test_run_id_channel_name_list:
        #     print(item)

        for item in test_run_id_channel_name_list:
            run_id, channel_name = item

            start_time = self.get_starting_time_from_allgovision(
                channel_name)
            if not start_time:
                continue

            duration = self.get_video_length(channel_name)

            end_time = start_time + datetime.timedelta(seconds=duration)

            # Convert start_time and end_time to string for SQL query
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            # print(start_time_str)
            end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
            # print(channel_name)

            # Query alarms from allgovision database within the specified time range
            alarms_data = self.query_alarms_from_allgovision(
                start_time_str, end_time_str, channel_name)
            # print("Alarms data:", alarms_data)

            if alarms_data:
                # Prepare data for insertion into test_run_output table
                data_to_insert = []
                for alarm in alarms_data:
                    alarm_timestamp = alarm['TimeStamp']
                    relative_time = (alarm_timestamp -
                                     start_time).total_seconds()
                    relative_time_str = str(
                        datetime.timedelta(seconds=relative_time))
                    data_to_insert.append(
                        (run_id, channel_name, relative_time_str, alarm['AlarmName']))

                # Insert data into test_run_output table
                self.insert_into_test_run_output(data_to_insert)
        print("Inserted successfully into test_run_output table")

    def connect_to_allgovision_database(self):
        config = self.load_config()
        try:
            self.connection = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database='allgovision',
                port=config['port']
            )
            if self.connection.is_connected():
                print(f"Connected to {config['database']} database")
        except Error as e:
            print(f"Error connecting to {config['database']} database:", e)


# output_database_object = OutputDatabase('config.json')
# output_database_object.connect_to_alarm_system_database()
# output_database_object.connect_to_allgovision_database()
# output_database_object.fetch_test_run_test_case_list(
#     output_database_object.alarm_system_connection)
# output_database_object.read_alarms_from_allgovision()
