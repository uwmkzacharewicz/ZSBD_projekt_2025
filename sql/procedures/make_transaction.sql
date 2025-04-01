CREATE OR REPLACE PROCEDURE make_transaction (
    p_investor_id      IN NUMBER,
    p_company_id       IN NUMBER,
    p_operation        IN VARCHAR2,  -- 'BUY' lub 'SELL'
    p_shares           IN NUMBER,
    p_price_per_share  IN NUMBER,
    p_commission_pct   IN NUMBER DEFAULT 0
) AS
    v_total_value   NUMBER(12, 2);
    v_err_msg       VARCHAR2(4000);
    v_existing_shares NUMBER;
    PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
    -- Oblicz wartość transakcji z uwzględnieniem prowizji
    v_total_value := p_shares * p_price_per_share * (1 + p_commission_pct / 100);

    IF p_operation = 'SELL' THEN
        -- Sprawdź czy inwestor ma wystarczającą liczbę akcji
        SELECT NVL(shares, 0) INTO v_existing_shares
        FROM Portfolio
        WHERE investor_id = p_investor_id AND company_id = p_company_id;

        IF v_existing_shares < p_shares THEN
            RAISE_APPLICATION_ERROR(-20005, 'Nie można sprzedać więcej akcji niż posiadanych.');
        END IF;

        -- Zmniejsz stan posiadania
        UPDATE Portfolio
        SET shares = shares - p_shares,
            avg_price = CASE WHEN shares - p_shares > 0 THEN avg_price ELSE NULL END,
            last_updated = CURRENT_TIMESTAMP
        WHERE investor_id = p_investor_id AND company_id = p_company_id;

    ELSIF p_operation = 'BUY' THEN
        -- Jeśli istnieje rekord, aktualizuj; jeśli nie, dodaj
        BEGIN
            SELECT shares INTO v_existing_shares
            FROM Portfolio
            WHERE investor_id = p_investor_id AND company_id = p_company_id;

            UPDATE Portfolio
            SET
                shares = shares + p_shares,
                avg_price = ROUND(((avg_price * shares) + (p_price_per_share * p_shares)) / (shares + p_shares), 2),
                last_updated = CURRENT_TIMESTAMP
            WHERE investor_id = p_investor_id AND company_id = p_company_id;

        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                INSERT INTO Portfolio (investor_id, company_id, shares, avg_price)
                VALUES (p_investor_id, p_company_id, p_shares, p_price_per_share);
        END;
    ELSE
        RAISE_APPLICATION_ERROR(-20006, 'Nieznana operacja. Dozwolone: BUY lub SELL.');
    END IF;

    -- Dodaj wpis transakcji
    INSERT INTO Transaction (
        investor_id, company_id, operation, shares,
        price_per_share, total_value, transaction_date
    ) VALUES (
        p_investor_id, p_company_id, p_operation, p_shares,
        p_price_per_share, v_total_value, SYSDATE
    );

    -- Dodaj log
    INSERT INTO Log (status, operation, user_name, table_name, action_detail, message)
    VALUES ('OK', 'INSERT', SYS_CONTEXT('USERENV', 'SESSION_USER'), 'TRANSACTION',
            'make_transaction', 'Transakcja: ' || p_operation || ' ' || p_shares || ' akcji');

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        v_err_msg := SQLERRM;
        BEGIN
            INSERT INTO Log (status, operation, user_name, table_name, action_detail, message)
            VALUES ('ERROR', 'INSERT', SYS_CONTEXT('USERENV', 'SESSION_USER'), 'TRANSACTION',
                    'make_transaction', TO_CLOB(v_err_msg));
            COMMIT;
        EXCEPTION
            WHEN OTHERS THEN NULL;
        END;
        RAISE_APPLICATION_ERROR(-20010, 'Błąd transakcji: ' || v_err_msg);
END;
