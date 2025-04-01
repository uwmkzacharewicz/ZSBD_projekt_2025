CREATE OR REPLACE FUNCTION count_transactions (
    p_investor_id IN NUMBER,
    p_company_id  IN NUMBER DEFAULT NULL
) RETURN NUMBER IS
    v_count NUMBER;
BEGIN
    IF p_company_id IS NULL THEN
        SELECT COUNT(*) INTO v_count
        FROM Transaction
        WHERE investor_id = p_investor_id;
    ELSE
        SELECT COUNT(*) INTO v_count
        FROM Transaction
        WHERE investor_id = p_investor_id AND company_id = p_company_id;
    END IF;

    RETURN v_count;
END;
/


-- Test the function
-- SELECT count_transactions(1) FROM dual;
-- SELECT count_transactions(1, 2) FROM dual;