-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 28, 2021 at 10:20 PM
-- Server version: 10.4.22-MariaDB
-- PHP Version: 8.0.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `evidencija_studenata`
--

-- --------------------------------------------------------

--
-- Table structure for table `korisnici`
--

CREATE TABLE `korisnici` (
  `id` int(11) NOT NULL,
  `ime` varchar(100) CHARACTER SET utf8 NOT NULL,
  `prezime` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `lozinka` varchar(200) NOT NULL,
  `rola` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `korisnici`
--

INSERT INTO `korisnici` (`id`, `ime`, `prezime`, `email`, `lozinka`, `rola`) VALUES
(5, 'admin', 'admin', 'admin@admin.com', 'pbkdf2:sha256:260000$u37mRIiIcoSvkuu4$a71987f698f6403e2b9a1d0f0af76b932ad46d3bc4a74812c19013444429204d', 'administrator');

-- --------------------------------------------------------

--
-- Table structure for table `ocene`
--

CREATE TABLE `ocene` (
  `ocena_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `predmet_id` int(11) NOT NULL,
  `ocena` smallint(6) NOT NULL,
  `datum` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `ocene`
--

INSERT INTO `ocene` (`ocena_id`, `student_id`, `predmet_id`, `ocena`, `datum`) VALUES
(23, 19, 5, 8, '2000-12-25'),
(24, 19, 6, 9, '2000-01-02'),
(25, 19, 7, 10, '2021-01-12'),
(26, 18, 8, 7, '2021-12-28'),
(27, 18, 9, 8, '2021-12-26'),
(28, 17, 5, 8, '2021-12-16'),
(29, 17, 6, 6, '2021-12-04'),
(30, 17, 9, 9, '2021-12-19'),
(31, 20, 10, 9, '2021-12-19'),
(32, 20, 9, 10, '2021-12-08');

-- --------------------------------------------------------

--
-- Table structure for table `predmeti`
--

CREATE TABLE `predmeti` (
  `id` int(11) NOT NULL,
  `sifra` varchar(30) NOT NULL,
  `naziv` varchar(50) NOT NULL,
  `godina_studija` smallint(6) NOT NULL,
  `espb` int(11) NOT NULL,
  `obavezni_izborni` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `predmeti`
--

INSERT INTO `predmeti` (`id`, `sifra`, `naziv`, `godina_studija`, `espb`, `obavezni_izborni`) VALUES
(5, 'MAT1', 'Matematika 1', 1, 8, 'Obavezan'),
(6, 'MAT2', 'Matematika 2', 2, 8, 'Obavezan'),
(7, 'IT', 'Internet Tehnologije', 2, 7, 'Izborni'),
(8, 'TEN', 'Tehnicki Engleski 1', 2, 6, 'Izborni'),
(9, 'TEN2', 'Tehnicki Engleski 2', 3, 6, 'Obavezan'),
(10, 'WEB', 'Web programiranje', 3, 6, 'Izborni');

-- --------------------------------------------------------

--
-- Table structure for table `studenti`
--

CREATE TABLE `studenti` (
  `id` int(11) NOT NULL,
  `ime` varchar(100) NOT NULL,
  `ime_roditelja` varchar(100) NOT NULL,
  `prezime` varchar(100) NOT NULL,
  `broj_indeksa` varchar(10) NOT NULL,
  `godina_studija` smallint(6) NOT NULL,
  `jmbg` bigint(20) NOT NULL,
  `datum_rodjenja` date NOT NULL,
  `espb` int(11) NOT NULL,
  `prosek_ocena` float NOT NULL,
  `broj_telefona` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `slika` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `studenti`
--

INSERT INTO `studenti` (`id`, `ime`, `ime_roditelja`, `prezime`, `broj_indeksa`, `godina_studija`, `jmbg`, `datum_rodjenja`, `espb`, `prosek_ocena`, `broj_telefona`, `email`, `slika`) VALUES
(17, 'Petar', 'Milos', 'Petrovic', 'RER 2219', 1, 123456789, '2000-01-01', 22, 7.6667, '0654778965', 'petar.petrovic@gmail.com', ''),
(18, 'MIlos', 'Dejan', 'MIlic', 'RER 0118', 1, 156219851985, '2000-05-03', 12, 7.5, '0621487459', 'milos.milic@gmail.com', ''),
(19, 'Dejan', 'Zoki', 'Dekic', 'SEK 1615', 2, 1234958126, '2001-12-25', 23, 9, '06487895132', 'dejan.dekic@hotmail.com', ''),
(20, 'Zoran', 'Petar', 'Zokic', 'REr 0220', 3, 46878941235, '1998-12-15', 12, 9.5, '069875456321', 'zoran.zokic@yahoo.com', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `korisnici`
--
ALTER TABLE `korisnici`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ocene`
--
ALTER TABLE `ocene`
  ADD PRIMARY KEY (`ocena_id`),
  ADD KEY `ocene_predmet` (`predmet_id`),
  ADD KEY `ocene_student` (`student_id`);

--
-- Indexes for table `predmeti`
--
ALTER TABLE `predmeti`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `studenti`
--
ALTER TABLE `studenti`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `korisnici`
--
ALTER TABLE `korisnici`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `ocene`
--
ALTER TABLE `ocene`
  MODIFY `ocena_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `predmeti`
--
ALTER TABLE `predmeti`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `studenti`
--
ALTER TABLE `studenti`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ocene`
--
ALTER TABLE `ocene`
  ADD CONSTRAINT `ocene_predmet` FOREIGN KEY (`predmet_id`) REFERENCES `predmeti` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `ocene_student` FOREIGN KEY (`student_id`) REFERENCES `studenti` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
