CREATE OR REPLACE VIEW v_stock_prices_latest AS
SELECT
    sp.price_id,
    c.name AS company_name,
    c.ticker,
    sp.trade_date,
    sp.open_price,
    sp.high_price,
    sp.low_price,
    sp.close_price,
    sp.volume,
    sp.currency,
    sp.close_price_pln
FROM
    StockPrice sp
JOIN
    Company c ON sp.company_id = c.company_id
WHERE
    (sp.company_id, sp.trade_date) IN (
        SELECT company_id, MAX(trade_date)
        FROM StockPrice
        GROUP BY company_id
    );
