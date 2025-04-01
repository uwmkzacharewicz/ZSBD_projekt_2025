create or replace TRIGGER trg_validate_investor
BEFORE INSERT OR UPDATE ON Investor
FOR EACH ROW
DECLARE
    invalid_email EXCEPTION;
    invalid_phone EXCEPTION;
    invalid_nid   EXCEPTION;
BEGIN
    -- Walidacja e-maila
    IF NOT REGEXP_LIKE(:NEW.email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') THEN
        RAISE invalid_email;
    END IF;

    -- Walidacja numeru telefonu (9 cyfr lub zaczynający się od +XX)
    IF :NEW.phone IS NOT NULL AND NOT REGEXP_LIKE(:NEW.phone, '^\+?\d{9,15}$') THEN
        RAISE invalid_phone;
    END IF;

    -- Walidacja PESEL (11 cyfr + kontrola długości)
    IF :NEW.national_id IS NOT NULL AND NOT REGEXP_LIKE(:NEW.national_id, '^\d{11}$') THEN
        RAISE invalid_nid;
    END IF;

EXCEPTION
    WHEN invalid_email THEN
        RAISE_APPLICATION_ERROR(-20001, 'Niepoprawny adres e-mail');
    WHEN invalid_phone THEN
        RAISE_APPLICATION_ERROR(-20002, 'Niepoprawny numer telefonu');
    WHEN invalid_nid THEN
        RAISE_APPLICATION_ERROR(-20003, 'Niepoprawny numer identyfikacyjny (PESEL)');
END;
