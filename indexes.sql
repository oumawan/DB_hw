CREATE INDEX idx_myapp_vehicle_vtype ON myapp_vehicle (vtype);

CREATE INDEX idx_myapp_leave_uid_id ON myapp_leave (uid_id);
CREATE INDEX idx_myapp_leave_tbegin_tend ON myapp_leave (tbegin, tend);

CREATE INDEX idx_myapp_schedule_uid_id ON myapp_schedule (uid_id);
CREATE INDEX idx_myapp_schedule_vid_id ON myapp_schedule (vid_id);
CREATE INDEX idx_myapp_schedule_lineNo_id ON myapp_schedule (lineNo_id);
CREATE INDEX idx_myapp_schedule_dtime_atime ON myapp_schedule (dtime, atime);

CREATE INDEX idx_myapp_transfer_vid_id ON myapp_transfer (vid_id);
CREATE INDEX idx_myapp_transfer_date ON myapp_transfer (date);