SELECT
    investor_id,
    company_id,
    shares,
    RANK() OVER (PARTITION BY company_id ORDER BY shares DESC) AS rank_in_company
FROM Portfolio;
