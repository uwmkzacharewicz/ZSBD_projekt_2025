CREATE OR REPLACE PROCEDURE add_company (
    p_name     IN VARCHAR2,
    p_ticker   IN VARCHAR2,
    p_sector   IN VARCHAR2,
    p_country  IN VARCHAR2,
    p_website  IN VARCHAR2
) AS
    v_err_msg  VARCHAR2(4000); 
BEGIN
    INSERT INTO Company (name, ticker, sector, country, website)
    VALUES (p_name, p_ticker, p_sector, p_country, p_website);

EXCEPTION
    WHEN OTHERS THEN
        v_err_msg := SQLERRM;  
        INSERT INTO ImportLog (operation, user_name, table_name, message)
        VALUES (
            'INSERT',
            SYS_CONTEXT('USERENV', 'SESSION_USER'),
            'COMPANY',
            TO_CLOB(v_err_msg)  
        );        
        RAISE_APPLICATION_ERROR(-20001, 'Błąd podczas dodawania firmy: ' || v_err_msg);
END;