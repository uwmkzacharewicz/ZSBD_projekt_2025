create or replace PROCEDURE add_company (
    p_name     IN VARCHAR2,
    p_ticker   IN VARCHAR2,
    p_sector   IN VARCHAR2,
    p_country  IN VARCHAR2,
    p_website  IN VARCHAR2
) AS
    v_err_msg  VARCHAR2(4000);
    PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
    INSERT INTO Company (name, ticker, sector, country, website)
    VALUES (p_name, p_ticker, p_sector, p_country, p_website);

    -- log sukcesu
    INSERT INTO Log (status, operation, user_name, table_name, action_detail, message)
    VALUES ('OK','INSERT', SYS_CONTEXT('USERENV', 'SESSION_USER'), 'COMPANY', 'add_company', 'Dodano firmę: ' || p_name);

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        v_err_msg := SQLERRM;

        -- log błędu
        BEGIN
            INSERT INTO Log (status, operation, user_name, table_name, action_detail, message)
            VALUES ('ERROR','INSERT', SYS_CONTEXT('USERENV', 'SESSION_USER'), 'COMPANY', 'add_company', TO_CLOB(v_err_msg));
            COMMIT;
        EXCEPTION
            WHEN OTHERS THEN
                NULL;
        END;

        RAISE_APPLICATION_ERROR(-20001, 'Błąd podczas dodawania firmy: ' || v_err_msg);
END;