# NCSBE Wake County current voter file

- Source: [NCSBE voter registration data](https://www.ncsbe.gov/results-data/voter-registration-data), direct file `https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter92.zip`.
- County: Wake County (NCSBE county file number 92).
- Retrieved: 2026-10-14; S3 `Last-Modified`: 2026-10-12.
- Downloaded ZIP size: 62,637,808 bytes. It contains one tab-delimited file, `ncvoter92.txt` (503,510,375 bytes uncompressed).
- Local file: `ncvoter92.zip`; SHA-256: `c955b751a05c8d12b59ab5a16218932ddcb3d84520341f50e9b2ca453d77e362`.
- Schema: [NCSBE layout file](https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt). The current file has status/reason fields and registration, address, demographic, and district data. Birth date, SSN, and driver's license number are excluded; some address/contact data remains identifiable.

## Why this file was selected

The project already contains the HPI prepared sample based on the 2018-11-06 NC snapshot. It has 1,728 Wake rows representing 1,402 distinct NCIDs. This current county file lets us compare a bounded historical sample with the current roll without pulling the 1.3 GB statewide archives. The aggregate continuity audit is in `reports/wake_cross_snapshot_audit.md`.

This is real voter data. Keep the ZIP local, do not commit or redistribute the records, and do not include them in a public demo. NCSBE describes the files as weekly current point-in-time records and notes that removed registrations whose most recent vote was more than ten years ago are omitted. An older NCID not present in this one county file may have moved, been removed, or otherwise changed; it is not a verified wrongful-removal label.
