import mysql.connector
from mysql.connector import Error
import json
from datetime import timedelta


class AlarmSystemValidator:
    def __init__(self, config_path):
        self.config_path = config_path
        self.connection = None
        self.list = []  # list of ids which are already matched with groundtruth
        self.threshold = None

    def load_config(self):
        with open(self.config_path, 'r') as file:
            config = json.load(file)
            self.threshold = config['threshold']
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

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Closed connection to database")

    def fetch_data_from_table(self, table_name, name):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = f"SELECT time_of_alarm, name_of_alarm, alarm_id FROM {table_name} WHERE test_case_name = %s"
            cursor.execute(query, (name,))
            data = cursor.fetchall()
            return data
        except Error as e:
            print(f"Error fetching data from {table_name}:", e)
            return None

    def compare_alarm_times(self, groundtruth_data, test_output_data):
        true_alarms = 0
        missed_alarms = 0
        false_alarms = 0
        true_alarm_list = []
        false_alarm_list = []
        missed_alarm_list = []
        # print(groundtruth_data)
        # print(test_output_data)
        test_output_ids = {alarm['alarm_id']
                           for alarm in test_output_data}

        groundtruth_times = {alarm['time_of_alarm']
                             for alarm in groundtruth_data}
        test_output_times = {alarm['time_of_alarm']
                             for alarm in test_output_data}

        for gt_alarm in groundtruth_data:
            gt_time = gt_alarm['time_of_alarm']
            matched = False
            if (matched == False):
                matched_alarm = next(
                    (alarm for alarm in test_output_data if alarm['time_of_alarm'] == gt_time), None)
                if matched_alarm != None and matched_alarm['alarm_id'] not in self.list:
                    true_alarms += 1
                    matched = True

                    test_alarm_id = matched_alarm['alarm_id']

                    true_alarm_list.append({
                        'Groundtruth_alarm_id': gt_alarm['alarm_id'],
                        'Test_alarm_id': test_alarm_id
                    })
                    self.list.append(test_alarm_id)
                if (matched == False):
                    gt_time = gt_time - timedelta(seconds=self.threshold)

                    matched_alarm = next(
                        (alarm for alarm in test_output_data if alarm['time_of_alarm'] == gt_time), None)

                    if matched_alarm != None and matched_alarm['alarm_id'] not in self.list:
                        true_alarms += 1
                        matched = True

                        test_alarm_id = matched_alarm['alarm_id']

                        true_alarm_list.append({
                            'Groundtruth_alarm_id': gt_alarm['alarm_id'],
                            'Test_alarm_id': test_alarm_id
                        })
                        self.list.append(test_alarm_id)

                if (matched == False):
                    gt_time = gt_time + timedelta(seconds=self.threshold)
                    matched = False
                    matched_alarm = next(
                        (alarm for alarm in test_output_data if alarm['time_of_alarm'] == gt_time), None)

                    if matched_alarm != None and matched_alarm['alarm_id'] not in self.list:
                        true_alarms += 1
                        matched = True

                        test_alarm_id = matched_alarm['alarm_id']

                        true_alarm_list.append({
                            'Groundtruth_alarm_id': gt_alarm['alarm_id'],
                            'Test_alarm_id': test_alarm_id
                        })
                        self.list.append(test_alarm_id)

            if matched == False:
                missed_alarms += 1
                missed_alarm_list.append(gt_alarm['alarm_id'])

        for id in test_output_ids:
            if id not in self.list:
                false_alarms += 1
                false_alarm_list.append(id)

        return true_alarms, missed_alarms, false_alarms, true_alarm_list, false_alarm_list, missed_alarm_list

    def compare_alarm_times_old(self, groundtruth_data, test_output_data):
        true_alarms = 0
        missed_alarms = 0
        false_alarms = 0
        true_alarm_list = []
        false_alarm_list = []
        missed_alarm_list = []
        # print(groundtruth_data)
        # print(test_output_data)

        groundtruth_times = {alarm['time_of_alarm']
                             for alarm in groundtruth_data}
        test_output_times = {alarm['time_of_alarm']
                             for alarm in test_output_data}

        for gt_alarm in groundtruth_data:
            gt_time = gt_alarm['time_of_alarm']
            if gt_time in test_output_times:
                true_alarms += 1
                test_alarm_id = None
                for test_alarm in test_output_data:
                    if test_alarm['time_of_alarm'] == gt_time:
                        test_alarm_id = test_alarm['alarm_id']
                true_alarm_list.append({
                    'Groundtruth_alarm_id': gt_alarm['alarm_id'],
                    'Test_alarm_id': test_alarm_id
                })
            else:
                missed_alarms += 1
                missed_alarm_list.append(gt_alarm['alarm_id'])

        for test_alarm in test_output_data:
            test_time = test_alarm['time_of_alarm']
            if test_time not in groundtruth_times:
                false_alarms += 1
                false_alarm_list.append(test_alarm['alarm_id'])

        return true_alarms, missed_alarms, false_alarms, true_alarm_list, false_alarm_list, missed_alarm_list

    def update_validation_summary(self, test_run_id, test_case_name, true_alarms, false_alarms, missed_alarms, true_alarm_list, false_alarm_list, missed_alarm_list):
        try:
            cursor = self.connection.cursor()
            true_alarm_list_json = json.dumps(true_alarm_list)
            false_alarm_list_json = json.dumps(false_alarm_list)
            missed_alarm_list_json = json.dumps(missed_alarm_list)

            update_query = """
                INSERT INTO validationsummary (
                    Test_run_id, test_case_name, NumTrueAlarms, NumFalseAlarms, NumMissedAlarms,
                    TrueAlarmList, FalseAlarmList, MissedAlarmList
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    NumTrueAlarms = VALUES(NumTrueAlarms),
                    NumFalseAlarms = VALUES(NumFalseAlarms),
                    NumMissedAlarms = VALUES(NumMissedAlarms),
                    TrueAlarmList = VALUES(TrueAlarmList),
                    FalseAlarmList = VALUES(FalseAlarmList),
                    MissedAlarmList = VALUES(MissedAlarmList)
            """
            data = (test_run_id, test_case_name, true_alarms, false_alarms, missed_alarms,
                    true_alarm_list_json, false_alarm_list_json, missed_alarm_list_json)
            cursor.execute(update_query, data)
            self.connection.commit()
            print("Validation summary updated successfully.")
        except Error as e:
            print("Error updating validation summary:", e)

    def fetch_test_run_test_case_list(self):
        try:
            cursor = self.connection.cursor()
            query = "SELECT test_run_id, TestCaseList FROM test_run"
            cursor.execute(query)
            result = cursor.fetchall()
            return [(row[0], row[1].split(',')) for row in result] if result else []
        except Error as e:
            print("Error fetching TestCaseList from test_run:", e)
            return []

    def run(self):
        self.connect_to_database()
        if not self.connection or not self.connection.is_connected():
            return

        test_case_lists = self.fetch_test_run_test_case_list()
        for run_id, test_case_names in test_case_lists:
            for name in test_case_names:
                try:
                    groundtruth_data = self.fetch_data_from_table(
                        'groundtruth', name)
                    if groundtruth_data is None:
                        print("Error: Could not fetch data from groundtruth table")
                        continue

                    test_output_data = self.fetch_data_from_table(
                        'test_run_output', name)
                    if test_output_data is None:
                        print(
                            "Error: Could not fetch data from test_run_output table")
                        continue

                    true_alarms, missed_alarms, false_alarms, true_alarm_list, false_alarm_list, missed_alarm_list = self.compare_alarm_times(
                        groundtruth_data, test_output_data)

                    self.update_validation_summary(run_id, name,
                                                   true_alarms, false_alarms, missed_alarms,
                                                   true_alarm_list, false_alarm_list, missed_alarm_list)
                except Exception as e:
                    print("Error:", e)
        self.close_connection()


# validator = AlarmSystemValidator('config.json')
# validator.run()
