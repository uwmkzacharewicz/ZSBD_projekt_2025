CREATE OR REPLACE VIEW v_company_stock AS
SELECT
    c.company_id,
    c.name AS company_name,
    c.ticker,
    sp.trade_date,
    sp.open_price,
    sp.high_price,
    sp.low_price,
    sp.close_price,
    sp.volume,
    sp.currency,
    sp.close_price_pln,
    sp.source
FROM
    Company c
JOIN
    StockPrice sp ON c.company_id = sp.company_id;
