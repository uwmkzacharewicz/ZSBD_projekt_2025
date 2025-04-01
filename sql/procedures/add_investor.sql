CREATE OR REPLACE PROCEDURE add_investor (
    p_name        IN VARCHAR2,
    p_email       IN VARCHAR2,
    p_phone       IN VARCHAR2 DEFAULT NULL,
    p_national_id IN VARCHAR2 DEFAULT NULL
) AS
    v_err_msg VARCHAR2(4000);
    PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
    INSERT INTO Investor (name, email, phone, national_id)
    VALUES (p_name, p_email, p_phone, p_national_id);

    -- dodaj log (sukces)
    INSERT INTO Log (operation, user_name, table_name, action_detail, message, success)
    VALUES ('INSERT', SYS_CONTEXT('USERENV', 'SESSION_USER'), 'INVESTOR', 'add_investor', 'Dodano inwestora: ' || p_name, 'Y');

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        v_err_msg := SQLERRM;

        -- dodaj log (błąd)
        BEGIN
            INSERT INTO Log (operation, user_name, table_name, action_detail, message, success)
            VALUES ('INSERT', SYS_CONTEXT('USERENV', 'SESSION_USER'), 'INVESTOR', 'add_investor', TO_CLOB(v_err_msg), 'N');
            COMMIT;
        EXCEPTION
            WHEN OTHERS THEN
                NULL; -- zabezpieczenie przed błędami przy logowaniu błędu
        END;

        RAISE_APPLICATION_ERROR(-20002, 'Błąd podczas dodawania inwestora: ' || v_err_msg);
END;