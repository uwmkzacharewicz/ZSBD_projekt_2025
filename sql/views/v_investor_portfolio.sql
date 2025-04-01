CREATE OR REPLACE VIEW v_investor_portfolio AS
SELECT
    i.investor_id,
    i.name AS investor_name,
    i.client_code,
    i.email,
    c.company_id,
    c.name AS company_name,
    c.ticker,
    p.shares,
    p.avg_price,
    (p.shares * p.avg_price) AS total_value,
    p.last_updated
FROM
    Investor i
JOIN
    Portfolio p ON i.investor_id = p.investor_id
JOIN
    Company c ON p.company_id = c.company_id;


SELECT * FROM v_investor_portfolio