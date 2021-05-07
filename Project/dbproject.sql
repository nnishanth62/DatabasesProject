-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 07, 2021 at 11:05 PM
-- Server version: 10.4.17-MariaDB
-- PHP Version: 7.3.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dbproject`
--

-- --------------------------------------------------------

--
-- Table structure for table `airline`
--

CREATE TABLE `airline` (
  `name` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `airline`
--

INSERT INTO `airline` (`name`) VALUES
('American Airlines'),
('Delta'),
('Nidhin Air'),
('NYU Airline'),
('Turkish Airlines');

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff`
--

CREATE TABLE `airline_staff` (
  `username` varchar(20) NOT NULL,
  `first_name` varchar(20) DEFAULT NULL,
  `last_name` varchar(20) DEFAULT NULL,
  `staff_password` varchar(32) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `airline_name` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `airline_staff`
--

INSERT INTO `airline_staff` (`username`, `first_name`, `last_name`, `staff_password`, `date_of_birth`, `airline_name`) VALUES
('blobert3', 'Frederick', 'Dukes', 'm@gn3t0', '1963-11-15', 'Turkish Airlines'),
('emarks123', 'Earnest', 'Marks', 'p@p3rb0y!', '1983-09-25', 'NYU Airline'),
('jeeb', 'Darth', 'Maul', '098f6bcd4621d373cade4e832627b4f6', '1998-06-09', 'Delta'),
('lcarter', 'Lee', 'Carter', 'v1p3r', '1979-08-27', 'American Airlines'),
('nnishanth2000', 'Nidhin', 'Nishanth', 'C0mpsc1guy', '2000-03-30', 'Nidhin Air'),
('test', 'test', 'test', '098f6bcd4621d373cade4e832627b4f6', '2001-01-01', 'Nidhin Air');

-- --------------------------------------------------------

--
-- Table structure for table `airplane`
--

CREATE TABLE `airplane` (
  `ID` char(5) NOT NULL,
  `airline_name` varchar(20) NOT NULL,
  `seats` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `airplane`
--

INSERT INTO `airplane` (`ID`, `airline_name`, `seats`) VALUES
('12345', 'Nidhin Air', 160),
('12345', 'Turkish Airlines', 150),
('22222', 'Delta', 200),
('22222', 'Nidhin Air', 190),
('6CSwH', 'Nidhin Air', 220),
('98765', 'American Airlines', 230);

-- --------------------------------------------------------

--
-- Table structure for table `airport`
--

CREATE TABLE `airport` (
  `name` char(3) NOT NULL,
  `city` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `airport`
--

INSERT INTO `airport` (`name`, `city`) VALUES
('DFW', 'Dallas/Fort Worth'),
('EWR', 'Newark'),
('JFK', 'New York City'),
('LAG', 'New York City'),
('LAX', 'Los Angeles');

-- --------------------------------------------------------

--
-- Table structure for table `booking_agent`
--

CREATE TABLE `booking_agent` (
  `email` varchar(30) NOT NULL,
  `booking_agent_id` char(6) DEFAULT NULL,
  `agent_password` varchar(32) DEFAULT NULL,
  `commission` decimal(11,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `booking_agent`
--

INSERT INTO `booking_agent` (`email`, `booking_agent_id`, `agent_password`, `commission`) VALUES
('carlislec@forks.com', '191319', 'tw1l1ghtr0x', '255.00'),
('grog@gmail.com', 'grog12', '098f6bcd4621d373cade4e832627b4f6', '0.00'),
('jhowlett@gmail.com', '333666', 'w0lv3r1n3', '610.00'),
('nsussex@gmail.com', '123456', 's!n1st3r', '230.00'),
('test@gmail.com', 'test12', '098f6bcd4621d373cade4e832627b4f6', '210.00');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `email` varchar(30) NOT NULL,
  `first_name` varchar(20) DEFAULT NULL,
  `last_name` varchar(20) DEFAULT NULL,
  `cust_password` varchar(32) DEFAULT NULL,
  `phone_number` varchar(13) DEFAULT NULL,
  `address_building_number` int(11) DEFAULT NULL,
  `address_street` varchar(20) DEFAULT NULL,
  `address_city` varchar(20) DEFAULT NULL,
  `address_state` varchar(20) DEFAULT NULL,
  `passport_number` char(9) DEFAULT NULL,
  `passport_country` varchar(20) DEFAULT NULL,
  `passport_expiration` date DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`email`, `first_name`, `last_name`, `cust_password`, `phone_number`, `address_building_number`, `address_street`, `address_city`, `address_state`, `passport_number`, `passport_country`, `passport_expiration`, `date_of_birth`) VALUES
('coolguy@whitehouse.gov', 'Cory', 'Baxter', 'flavortown3', '12223334444', 1900, 'Pennsylvania Avenue', 'Washington', 'DC', '112233445', 'United States', '2028-05-20', '1993-08-28'),
('jayclue@hotmail.net', 'Benjamin', 'Boston', 'weezerfan!@', '2123334445555', 1, 'Cool Guy Street', 'Detroit', 'Michigan', '555554444', 'United States', '2028-04-25', '2021-03-24'),
('jdahhan@gmail.com', 'Johnlouis', 'Dahhan', 'databases12#', '19173334444', 123, 'University Square', 'New York City', 'New York', '123456789', 'United States', '2026-04-25', '2000-01-19'),
('jeff@hotmail.net', 'Jeff', 'Goldblum', '098f6bcd4621d373cade4e832627b4f6', '1234561234', 349, 'w 16 st', 'Manhattan', 'New York', '123456789', 'US', '2021-05-11', '2021-04-28'),
('pogchimp@quickmail.com', 'Frank', 'McGuire', 'iloveSQL!', '19876543216', 245, 'Sesame Street', 'Portland', 'Oregon', '999999999', 'United States', '2026-01-20', '2000-12-26'),
('test@gmail.com', 'test', 'test', '098f6bcd4621d373cade4e832627b4f6', '1231241243', 123, 'street', 'street', 'street', '159159159', 'usa', '2021-04-26', '2021-05-03');

-- --------------------------------------------------------

--
-- Table structure for table `flight`
--

CREATE TABLE `flight` (
  `flight_num` char(6) NOT NULL,
  `airline_name` varchar(20) NOT NULL,
  `airplane_id` char(5) DEFAULT NULL,
  `departure_time` time NOT NULL,
  `departure_date` date NOT NULL,
  `departure_airport_name` char(3) DEFAULT NULL,
  `arrival_time` time DEFAULT NULL,
  `arrival_date` date DEFAULT NULL,
  `arrival_airport_name` char(3) DEFAULT NULL,
  `price` decimal(7,2) DEFAULT NULL,
  `flight_status` varchar(10) DEFAULT NULL,
  `tickets_sold` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `flight`
--

INSERT INTO `flight` (`flight_num`, `airline_name`, `airplane_id`, `departure_time`, `departure_date`, `departure_airport_name`, `arrival_time`, `arrival_date`, `arrival_airport_name`, `price`, `flight_status`, `tickets_sold`) VALUES
('123456', 'Nidhin Air', '12345', '13:30:00', '2020-10-31', 'JFK', '16:30:00', '2020-10-31', 'EWR', '200.00', 'on-time', 1),
('123456', 'Turkish Airlines', '12345', '23:00:00', '2021-08-31', 'LAX', '01:20:00', '2021-09-01', 'JFK', '1200.00', 'on-time', 2),
('333444', 'Nidhin Air', '22222', '09:30:00', '2021-05-20', 'EWR', '15:00:00', '2021-05-20', 'LAX', '1100.00', 'delayed', 1),
('a2z6io', 'Nidhin Air', '12345', '00:26:00', '2021-05-06', 'LAX', '00:25:00', '2021-05-12', 'EWR', '1000.00', 'on-time', 0),
('m2V3Qz', 'Nidhin Air', '12345', '04:02:00', '2021-05-08', 'LAX', '03:35:00', '2021-05-09', 'DFW', '500.00', 'on-time', 2);

-- --------------------------------------------------------

--
-- Stand-in structure for view `purchasable_tickets`
-- (See below for the actual view)
--
CREATE TABLE `purchasable_tickets` (
`airline_name` varchar(20)
,`flight_num` char(6)
,`departure_date` date
,`departure_time` time
,`arrival_date` date
,`arrival_time` time
,`departure_airport_name` char(3)
,`departure_city` varchar(20)
,`arrival_airport_name` char(3)
,`arrival_city` varchar(20)
,`tickets_sold` int(11)
,`capacity` int(11)
,`price` decimal(7,2)
);

-- --------------------------------------------------------

--
-- Table structure for table `purchase`
--

CREATE TABLE `purchase` (
  `ticket_id` char(5) NOT NULL,
  `customer_email` varchar(30) NOT NULL,
  `booking_agent_email` varchar(30) DEFAULT NULL,
  `purchase_date` date DEFAULT NULL,
  `purchase_time` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `purchase`
--

INSERT INTO `purchase` (`ticket_id`, `customer_email`, `booking_agent_email`, `purchase_date`, `purchase_time`) VALUES
('11188', 'jayclue@hotmail.net', 'carlislec@forks.com', '2021-08-29', '12:10:00'),
('18568', 'test@gmail.com', 'test@gmail.com', '2021-04-05', '11:41:48'),
('32165', 'coolguy@whitehouse.gov', 'nsussex@gmail.com', '2020-10-25', '15:35:00'),
('33344', 'pogchimp@quickmail.com', NULL, '2020-09-24', '14:20:00'),
('99999', 'jdahhan@gmail.com', 'jhowlett@gmail.com', '2021-07-29', '17:40:00'),
('ADOwF', 'test@gmail.com', NULL, '2021-02-07', '14:39:46'),
('fbRx2', 'test@gmail.com', NULL, '2021-05-05', '20:57:28'),
('ffGCZ', 'coolguy@whitehouse.gov', 'test@gmail.com', '2021-05-05', '21:46:17'),
('N7Rlw', 'jayclue@hotmail.net', 'test@gmail.com', '2021-05-07', '13:36:37'),
('OqfeA', 'test@gmail.com', NULL, '2021-05-07', '15:31:56');

-- --------------------------------------------------------

--
-- Table structure for table `ratings`
--

CREATE TABLE `ratings` (
  `email` varchar(30) NOT NULL,
  `flight_num` char(6) NOT NULL,
  `airline_name` varchar(20) NOT NULL,
  `comments` varchar(300) NOT NULL,
  `rating` tinyint(4) NOT NULL CHECK (`rating` > 0 and `rating` < 6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `ratings`
--

INSERT INTO `ratings` (`email`, `flight_num`, `airline_name`, `comments`, `rating`) VALUES
('coolguy@whitehouse.gov', '123456', 'Nidhin Air', 'Sucked, whole plane stank like doodoo ass', 2),
('jayclue@hotmail.net', '123456', 'Nidhin Air', 'whoa... where am i?', 4),
('test@gmail.com', '123456', 'Nidhin Air', 'predy goob', 4),
('jdahhan@gmail.com', 'a2z6io', 'Nidhin Air', 'awesome, whole plane semeleled poopy doopy', 3);

-- --------------------------------------------------------

--
-- Table structure for table `staff_phone_numbers`
--

CREATE TABLE `staff_phone_numbers` (
  `username` varchar(20) NOT NULL,
  `phone_number` varchar(13) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `staff_phone_numbers`
--

INSERT INTO `staff_phone_numbers` (`username`, `phone_number`) VALUES
('emarks123', '13475552222'),
('emarks123', '17188887777'),
('lcarter', '12121234567'),
('nnishanth2000', '0123456789');

-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` char(5) NOT NULL,
  `flight_airline_name` varchar(20) DEFAULT NULL,
  `flight_num` char(6) DEFAULT NULL,
  `sold_price` decimal(7,2) DEFAULT NULL,
  `customer_email` varchar(30) DEFAULT NULL,
  `payment_card_type` varchar(6) DEFAULT NULL,
  `payment_card_num` varchar(19) DEFAULT NULL,
  `payment_cardholder` varchar(30) DEFAULT NULL,
  `payment_card_expdate` date DEFAULT NULL
) ;

--
-- Dumping data for table `ticket`
--

INSERT INTO `ticket` (`ticket_id`, `flight_airline_name`, `flight_num`, `sold_price`, `customer_email`, `payment_card_type`, `payment_card_num`, `payment_cardholder`, `payment_card_expdate`) VALUES
('11188', 'Turkish Airlines', '123456', '1200.00', 'jayclue@hotmail.net', 'credit', '0000111122223333444', 'Brian Boston', '2028-06-01'),
('18568', 'Nidhin Air', '123456', '900.00', 'test@gmail.com', 'debit', '1234098765837492', 'Greg Gorg', '2023-07-30'),
('32165', 'Turkish Airlines', '123456', '1190.00', 'coolguy@whitehouse.gov', 'credit', '12341234123412345', 'Cory Baxter', '2028-06-01'),
('33344', 'Nidhin Air', '123456', '200.00', 'pogchimp@quickmail.com', 'debit', '0000000000000000', 'Morpheus Dorpheus', '2024-10-01'),
('99999', 'Nidhin Air', '123456', '190.00', 'jdahhan@gmail.com', 'debit', '1234567890123456', 'Johnlouis Dahhan', '2027-04-01'),
('ADOwF', 'Nidhin Air', 'm2V3Qz', '500.00', 'test@gmail.com', 'credit', '12344567987536215', 'greg gorg', '2023-05-09'),
('fbRx2', 'Turkish Airlines', '123456', '1200.00', 'test@gmail.com', 'credit', '12345678912345678', 'Jeff Bezos', '2021-05-14'),
('ffGCZ', 'Turkish Airlines', '123456', '1100.00', 'coolguy@whitehouse.gov', 'credit', '12345678912345678', 'Jeff Bezos', '0005-05-05'),
('N7Rlw', 'Nidhin Air', '333444', '1000.00', 'jayclue@hotmail.net', 'credit', '1234685748951237', 'jay clue', '2027-05-19'),
('OqfeA', 'Nidhin Air', 'm2V3Qz', '500.00', 'test@gmail.com', 'credit', '7676767676767676', 'jeff bezos', '2027-05-20');

-- --------------------------------------------------------

--
-- Structure for view `purchasable_tickets`
--
DROP TABLE IF EXISTS `purchasable_tickets`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `purchasable_tickets`  AS SELECT `flight`.`airline_name` AS `airline_name`, `flight`.`flight_num` AS `flight_num`, `flight`.`departure_date` AS `departure_date`, `flight`.`departure_time` AS `departure_time`, `flight`.`arrival_date` AS `arrival_date`, `flight`.`arrival_time` AS `arrival_time`, `flight`.`departure_airport_name` AS `departure_airport_name`, `dep_port`.`city` AS `departure_city`, `flight`.`arrival_airport_name` AS `arrival_airport_name`, `ar_port`.`city` AS `arrival_city`, `flight`.`tickets_sold` AS `tickets_sold`, `airplane`.`seats` AS `capacity`, `flight`.`price` AS `price` FROM (((`flight` join `airport` `dep_port`) join `airport` `ar_port`) join `airplane` on(`flight`.`airline_name` = `airplane`.`airline_name`)) WHERE `flight`.`tickets_sold` < `airplane`.`seats` AND `dep_port`.`name` = `flight`.`departure_airport_name` AND `ar_port`.`name` = `flight`.`arrival_airport_name` AND `airplane`.`ID` = `flight`.`airplane_id` AND `flight`.`departure_date` > curdate() ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `airline`
--
ALTER TABLE `airline`
  ADD PRIMARY KEY (`name`);

--
-- Indexes for table `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD PRIMARY KEY (`username`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `airplane`
--
ALTER TABLE `airplane`
  ADD PRIMARY KEY (`ID`,`airline_name`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `airport`
--
ALTER TABLE `airport`
  ADD PRIMARY KEY (`name`);

--
-- Indexes for table `booking_agent`
--
ALTER TABLE `booking_agent`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `flight`
--
ALTER TABLE `flight`
  ADD PRIMARY KEY (`flight_num`,`airline_name`,`departure_time`,`departure_date`),
  ADD KEY `arrival_airport_name` (`arrival_airport_name`),
  ADD KEY `departure_airport_name` (`departure_airport_name`),
  ADD KEY `airplane_id` (`airplane_id`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `purchase`
--
ALTER TABLE `purchase`
  ADD PRIMARY KEY (`ticket_id`,`customer_email`),
  ADD KEY `customer_email` (`customer_email`),
  ADD KEY `booking_agent_email` (`booking_agent_email`);

--
-- Indexes for table `ratings`
--
ALTER TABLE `ratings`
  ADD PRIMARY KEY (`flight_num`,`airline_name`,`email`),
  ADD KEY `email` (`email`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `staff_phone_numbers`
--
ALTER TABLE `staff_phone_numbers`
  ADD PRIMARY KEY (`username`,`phone_number`);

--
-- Indexes for table `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`ticket_id`),
  ADD KEY `flight_airline_name` (`flight_airline_name`),
  ADD KEY `flight_num` (`flight_num`),
  ADD KEY `customer_email` (`customer_email`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD CONSTRAINT `airline_staff_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`name`);

--
-- Constraints for table `airplane`
--
ALTER TABLE `airplane`
  ADD CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`name`);

--
-- Constraints for table `flight`
--
ALTER TABLE `flight`
  ADD CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`arrival_airport_name`) REFERENCES `airport` (`name`),
  ADD CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`departure_airport_name`) REFERENCES `airport` (`name`),
  ADD CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`airplane_id`) REFERENCES `airplane` (`ID`),
  ADD CONSTRAINT `flight_ibfk_4` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`name`);

--
-- Constraints for table `purchase`
--
ALTER TABLE `purchase`
  ADD CONSTRAINT `purchase_ibfk_1` FOREIGN KEY (`ticket_id`) REFERENCES `ticket` (`ticket_id`),
  ADD CONSTRAINT `purchase_ibfk_2` FOREIGN KEY (`customer_email`) REFERENCES `customer` (`email`),
  ADD CONSTRAINT `purchase_ibfk_3` FOREIGN KEY (`booking_agent_email`) REFERENCES `booking_agent` (`email`);

--
-- Constraints for table `ratings`
--
ALTER TABLE `ratings`
  ADD CONSTRAINT `ratings_ibfk_1` FOREIGN KEY (`flight_num`) REFERENCES `flight` (`flight_num`),
  ADD CONSTRAINT `ratings_ibfk_2` FOREIGN KEY (`email`) REFERENCES `customer` (`email`),
  ADD CONSTRAINT `ratings_ibfk_3` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`name`);

--
-- Constraints for table `staff_phone_numbers`
--
ALTER TABLE `staff_phone_numbers`
  ADD CONSTRAINT `staff_phone_numbers_ibfk_1` FOREIGN KEY (`username`) REFERENCES `airline_staff` (`username`);

--
-- Constraints for table `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`flight_airline_name`) REFERENCES `airline` (`name`),
  ADD CONSTRAINT `ticket_ibfk_2` FOREIGN KEY (`flight_num`) REFERENCES `flight` (`flight_num`),
  ADD CONSTRAINT `ticket_ibfk_3` FOREIGN KEY (`customer_email`) REFERENCES `customer` (`email`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
