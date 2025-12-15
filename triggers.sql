
CREATE TRIGGER after_line_delete
AFTER DELETE ON myapp_line
FOR EACH ROW
BEGIN
    DELETE FROM myapp_schedule WHERE lineNo_id = OLD.lineNo;
END;

CREATE TRIGGER after_vehicle_delete
AFTER DELETE ON myapp_vehicle
FOR EACH ROW
BEGIN
    DELETE FROM myapp_schedule WHERE vid_id = OLD.vid;
    DELETE FROM myapp_transfer WHERE vid_id = OLD.vid;
END;

CREATE TRIGGER after_transfer_insert
AFTER INSERT ON myapp_transfer
FOR EACH ROW
BEGIN
    UPDATE myapp_vehicle
    SET depotID = NEW.toDepot
    WHERE vid = NEW.vid_id;
END;

