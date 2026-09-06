-- Claude Vision returns structured lists instead of a single treatment string.
-- Existing text treatments are preserved by wrapping them into a 1-element array.

alter table public.detection_reports
  add column if not exists symptoms jsonb not null default '[]'::jsonb,
  add column if not exists prevention jsonb not null default '[]'::jsonb,
  add column if not exists explanation text,
  add column if not exists needs_expert_confirmation boolean not null default true;

-- Convert treatment: text -> jsonb array, keeping any existing advice.
alter table public.detection_reports
  alter column treatment drop default;

alter table public.detection_reports
  alter column treatment type jsonb
  using case
    when treatment is null or btrim(treatment) = '' then '[]'::jsonb
    else jsonb_build_array(treatment)
  end;

alter table public.detection_reports
  alter column treatment set default '[]'::jsonb,
  alter column treatment set not null;

comment on column public.detection_reports.treatment is 'Claude Vision treatment steps (JSON array of strings).';
comment on column public.detection_reports.symptoms is 'Visible symptoms observed by Claude Vision (JSON array).';
comment on column public.detection_reports.prevention is 'Preventive measures from Claude Vision (JSON array).';
