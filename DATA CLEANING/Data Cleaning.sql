-- Data Cleaning

Select *
from layoffs;

-- 1. Remove Duplicates

-- 2. Standardize the Data

-- 3. Null Values or blank values

-- 4. Remove Any Columns not relevant

CREATE TABLE layoffs_staging
LIKE layoffs;

SELECT *
FROM layoffs_staging;

INSERT layoffs_staging
SELECT *
FROM layoffs;

-- (1) REMOVING DUPLICATES

WITH duplicate_cte AS
(
SELECT *,
ROW_NUMBER() OVER(
PARTITION BY company, location, industry, total_laid_off, percentage_laid_off,`date`, stage, country, funds_raised_millions) as row_num
from layoffs_staging
)
SELECT *
FROM duplicate_cte
WHERE row_num>1 ;

SELECT * 
FROM layoffs_staging
WHERE company = 'Casper'; -- DUPLICATES EXIST


CREATE TABLE `layoffs_staging2` (
  `company` text,
  `location` text,
  `industry` text,
  `total_laid_off` text,
  `percentage_laid_off` text,
  `date` text,
  `stage` text,
  `country` text,
  `funds_raised_millions` text,
  `row_num` int
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


SELECT *
from layoffs_staging2;

insert into layoffs_staging2
SELECT *,
ROW_NUMBER() OVER(
PARTITION BY company, location, industry, total_laid_off, percentage_laid_off,`date`, stage, country, funds_raised_millions) as row_num
from layoffs_staging;

SET SQL_SAFE_UPDATES = 0;


DELETE
FROM layoffs_staging2
WHERE row_num>1 ;

SELECT * 
FROM layoffs_staging2
WHERE company = 'Casper'; -- NO DUPLICATES exist NOW

SELECT * 
FROM layoffs_staging2;


-- (2) STANDARDIZING DATA

UPDATE layoffs_staging2
SET company= TRIM(company); -- removed spaces from company values

SELECT DISTINCT industry
FROM layoffs_staging2
ORDER BY 1; -- crypto, crypto currency, cryptocurrency is same SO EDIT

SELECT *
FROM layoffs_staging2
WHERE industry like 'Crypto%';

update layoffs_staging2
SET INDUSTRY='Crypto'
where industry like 'Crypto%'; -- fixed

SELECT DISTINCT location
FROM layoffs_staging2
ORDER BY 1; -- correct

SELECT DISTINCT country
FROM layoffs_staging2
ORDER BY 1; -- problem in united states

SELECT DISTINCT country, TRIM(TRAILING '.' from country)
FROM layoffs_staging2
ORDER BY 1; 

update layoffs_staging2
set country=TRIM(TRAILING '.' from country)
WHERE COUNTRY LIKE 'United States%'; -- fixed

SELECT * 
FROM layoffs_staging2; -- date is in text format not 'date'


select `date` from layoffs_staging2;

select `date`,
str_to_date(`date`,'%m/%d/%Y')
from layoffs_staging2;

update layoffs_staging2
set `date`= str_to_date(`date`,'%m/%d/%Y')
where `date`!='NULL';


ALTER TABLE layoffs_staging2
MODIFY COLUMN `date` DATE; -- TEXT TO DATE FORMAT

select *
from layoffs_staging2;

-- funds, total laid off, percentage laid off in text

UPDATE layoffs_staging2
SET funds_raised_millions = NULL
WHERE TRIM(funds_raised_millions) = 'NULL';
ALTER TABLE layoffs_staging2
MODIFY COLUMN funds_raised_millions DECIMAL(10,2);



UPDATE layoffs_staging2
SET total_laid_off = NULL
WHERE TRIM(total_laid_off) = 'NULL';
ALTER TABLE layoffs_staging2
MODIFY COLUMN total_laid_off INT;


UPDATE layoffs_staging2
SET percentage_laid_off = NULL
WHERE TRIM(percentage_laid_off) = 'NULL';
ALTER TABLE layoffs_staging2
MODIFY COLUMN percentage_laid_off DECIMAL(5,2);





-- (3) Deal with NULL/BLANK Values

UPDATE layoffs_staging2
SET
	funds_raised_millions=NULLIF(TRIM(UPPER(funds_raised_millions)), 'NULL'),
    total_laid_off = NULLIF(TRIM(UPPER(total_laid_off)), 'NULL'),
    percentage_laid_off = NULLIF(TRIM(UPPER(percentage_laid_off)), 'NULL')
WHERE
   TRIM(UPPER(funds_raised_millions)) = 'NULL' OR
   TRIM(UPPER(total_laid_off)) = 'NULL'
    OR TRIM(UPPER(percentage_laid_off)) = 'NULL'; -- converts string 'NULL' values to actual NULL values
    
UPDATE layoffs_staging2
SET industry=NULL
WHERE industry='';

select *
from layoffs_staging2
where total_laid_off is NULL AND percentage_laid_off is NULL;

select *
from layoffs_staging2
where industry is NULL OR industry=''; 

-- check if a value can be populated
select *
from layoffs_staging2
where company='Airbnb'; -- yes it has two values, one null other Travel


select t1.industry, t2.industry
from layoffs_staging2 t1
JOIN layoffs_staging2 t2
	ON t1.company=t2.company
    AND t1.location=t2.location
WHERE (t1.industry is NULL)
AND t2.industry is NOT NULL;

UPDATE layoffs_staging2 t1
JOIN layoffs_staging2 t2
	ON t1.company=t2.company
SET t1.industry=t2.industry
WHERE (t1.industry is NULL)
AND t2.industry is NOT NULL;

select *
from layoffs_staging2;

-- (4) Remove Any Columns not relevant

select *
from layoffs_staging2
where total_laid_off is NULL AND percentage_laid_off is NULL;
-- this data is not needed

DELETE
from layoffs_staging2
where total_laid_off is NULL AND percentage_laid_off is NULL;

alter table layoffs_staging2
drop COLUMN row_num;

select *
from layoffs_staging2;


