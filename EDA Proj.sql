-- Exploratory Data Analysis

select *
from layoffs_staging2;

select max(total_laid_off), max(percentage_laid_off)
from layoffs_staging2;


select *
from layoffs_staging2
where percentage_laid_off=1
order by funds_raised_millions desc;

select company, sum(total_laid_off)
from layoffs_staging2
group by company
order by 2 desc; -- which company took the hit

select min(`date`), max(`date`)
from layoffs_staging2;

select industry, sum(total_laid_off)
from layoffs_staging2
group by industry
order by 2 desc; -- which industry took the hit

select country, sum(total_laid_off)
from layoffs_staging2
group by country
order by 2 desc; -- which country took the hit

select YEAR(`date`), sum(total_laid_off)
from layoffs_staging2
group by YEAR(`date`)
order by 1 DESC; -- which year most effect

select stage, sum(total_laid_off)
from layoffs_staging2
group by stage
order by 2 DESC; -- stage of company

-- rolling total for month
select substring(`date`,1,7) as `month`, sum(total_laid_off)
from layoffs_staging2
where substring(`date`,1,7) is not null
group by `month`
order by 1 asc; -- simple query for total for each month/year

with rolling_total as
(
select substring(`date`,1,7) as `month`, sum(total_laid_off) as total_off
from layoffs_staging2
where substring(`date`,1,7) is not null
group by `month`
order by 1 asc
)
select `month`, total_off,
sum(total_off) over(order by `month`) as roll_total
from rolling_total; -- adds up all layoffs, and at the end gives grand total

-- do the same for company

select company, year(`date`),sum(total_laid_off)
from layoffs_staging2
group by company, year(`date`)
order by 3 desc; 

-- rank, highest layoff count gets #1

with company_year(company, years, total_laid_off) as
(
select company, year(`date`),sum(total_laid_off)
from layoffs_staging2
group by company, year(`date`)
order by 3 desc
), company_year_rank as
(
select *, dense_rank() over (partition by years order by total_laid_off desc) as ranking
from company_year
where years is not null

)
select * from company_year_rank
where ranking <=5;
