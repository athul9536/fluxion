-- Pincode is recorded only for diseased crops, so outbreaks can be grouped by
-- area later. Healthy scans intentionally leave it null.
alter table public.detection_reports
  add column if not exists pincode varchar(12);

comment on column public.detection_reports.pincode is
  'Farmer-entered postal code. Saved only when a disease is detected; null for healthy or undetermined scans.';

create index if not exists detection_reports_pincode_idx
  on public.detection_reports (pincode)
  where pincode is not null;
