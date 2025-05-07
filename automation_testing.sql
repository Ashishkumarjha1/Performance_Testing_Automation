-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.5.8-MariaDB - Source distribution
-- Server OS:                    Linux
-- HeidiSQL Version:             12.5.0.6677
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for alarm_system
CREATE DATABASE IF NOT EXISTS `alarm_system` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `alarm_system`;

-- Dumping structure for table alarm_system.alarmname
CREATE TABLE IF NOT EXISTS `alarmname` (
  `id` int(11) NOT NULL,
  `name` varchar(128) NOT NULL,
  `displayname` varchar(128) NOT NULL,
  `category` varchar(128) DEFAULT NULL,
  `color` varchar(128) DEFAULT 'rgb(255,255,255,0)',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Dumping data for table alarm_system.alarmname: ~0 rows (approximately)

-- Dumping structure for table alarm_system.groundtruth
CREATE TABLE IF NOT EXISTS `groundtruth` (
  `test_case_name` varchar(50) DEFAULT NULL COMMENT 'Test Case Id (Unique for every test case)',
  `alarm_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identity of the Alarm for the testcase (unique for a test case)',
  `time_of_alarm` time DEFAULT NULL COMMENT 'Time of Alarm (Relative to start of test video)',
  `name_of_alarm` varchar(255) DEFAULT NULL COMMENT 'Alarm / Event Type name',
  `alarm_metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Metadata specific to Alarm (stored as key value paris)' CHECK (json_valid(`alarm_metadata`)),
  `object_metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Metadata related to object that triggered the alarm' CHECK (json_valid(`object_metadata`)),
  `alarm_image` varchar(255) DEFAULT NULL COMMENT 'URL to the Image of the Alarm',
  `object_crop` varchar(255) DEFAULT NULL COMMENT 'URL of the Object Crop',
  PRIMARY KEY (`alarm_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=142 DEFAULT CHARSET=utf8;

-- Dumping data for table alarm_system.groundtruth: ~0 rows (approximately)

-- Dumping structure for table alarm_system.testcase
CREATE TABLE IF NOT EXISTS `testcase` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identity of the Test Case (Shoudl be unique across all test cases)',
  `test_case_name` varchar(255) DEFAULT NULL COMMENT 'Identity of the Test Case (Shoudl be unique across all test cases)',
  `video_path` varchar(255) DEFAULT NULL COMMENT 'URL to the video / VLC RTSP stream that is needed for the testcase',
  `video_length_in_seconds` int(11) DEFAULT NULL COMMENT 'Length of the test video in seconds',
  `Description` text DEFAULT NULL COMMENT 'Describes what the test case is testing',
  `configInfoPath` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'URL to the folder which has information specific to test case',
  `feature_name` varchar(255) DEFAULT NULL,
  `test_suit_name` varchar(255) DEFAULT NULL COMMENT 'Name of the Test Suit associated with the Test Case',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8;

-- Dumping data for table alarm_system.testcase: ~0 rows (approximately)

-- Dumping structure for table alarm_system.test_run
CREATE TABLE IF NOT EXISTS `test_run` (
  `test_run_id` int(11) NOT NULL AUTO_INCREMENT,
  `Description` text DEFAULT NULL,
  `TestRunName` text DEFAULT NULL COMMENT 'Name of the Test Run',
  `software_version` varchar(50) DEFAULT NULL,
  `TestCaseList` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'List of TestCase IDs, that are part of the Test Run',
  `test_date` date DEFAULT NULL,
  `tester_name` varchar(255) DEFAULT NULL,
  `TestRunBaseURL` varchar(255) DEFAULT NULL COMMENT 'Base URL used for storing all the test results',
  PRIMARY KEY (`test_run_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- Dumping data for table alarm_system.test_run: ~0 rows (approximately)

-- Dumping structure for table alarm_system.test_run_output
CREATE TABLE IF NOT EXISTS `test_run_output` (
  `test_run_id` int(11) DEFAULT NULL COMMENT 'Test Run ID',
  `test_case_name` varchar(50) DEFAULT NULL,
  `alarm_id` int(11) NOT NULL AUTO_INCREMENT,
  `time_of_alarm` time DEFAULT NULL,
  `name_of_alarm` varchar(255) DEFAULT NULL,
  `alarm_metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`alarm_metadata`)),
  `object_metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`object_metadata`)),
  `alarm_image` varchar(255) DEFAULT NULL,
  `ObjectCrop` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`alarm_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- Dumping data for table alarm_system.test_run_output: ~0 rows (approximately)

-- Dumping structure for table alarm_system.test_suit
CREATE TABLE IF NOT EXISTS `test_suit` (
  `test_suit_id` VARCHAR(255) NOT NULL,
  `Description` text DEFAULT NULL,
  `testcaselist` longtext DEFAULT NULL,
  PRIMARY KEY (`test_suit_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Dumping data for table alarm_system.test_suit: ~0 rows (approximately)

-- Dumping structure for table alarm_system.validationsummary
CREATE TABLE IF NOT EXISTS `validationsummary` (
  `Test_run_id` int(11) DEFAULT NULL,
  `test_case_name` varchar(50) DEFAULT NULL,
  `NumTrueAlarms` int(11) DEFAULT NULL,
  `NumFalseAlarms` int(11) DEFAULT NULL,
  `NumMissedAlarms` int(11) DEFAULT NULL,
  `TrueAlarmList` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'A list of key value pairs, where the key is the Alarm ID int he Test_run_output and the correspondig Alarm Id in the Groundtruth table' CHECK (json_valid(`TrueAlarmList`)),
  `FalseAlarmList` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Array of Alarms ID in the test_run_output table, which are False Alarms' CHECK (json_valid(`FalseAlarmList`)),
  `MissedAlarmList` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Array of Alarms in the Ground Truth Table which were missed' CHECK (json_valid(`MissedAlarmList`)),
  `Test Case Status` int(11) DEFAULT NULL COMMENT 'Test Case Pass or Fail',
  `Description` int(11) DEFAULT NULL COMMENT 'Describinng What Failed'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Contains the Validation summary for a Test Run';

-- Dumping data for table alarm_system.validationsummary: ~0 rows (approximately)

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
