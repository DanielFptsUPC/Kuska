-- Pegar en Supabase: Project -> SQL Editor -> New query -> Run

create table if not exists incidents (
  id uuid primary key default gen_random_uuid(),
  client_id text unique not null,
  description text,
  photo_urls text[] default '{}',
  video_url text,
  lat double precision not null,
  lon double precision not null,
  status text default 'processing',
  gemma_result jsonb,
  created_at timestamptz default now(),
  created_at_client timestamptz,
  synced_at timestamptz
);

-- MVP sin auth compleja: RLS desactivado, el backend (service_role key) controla el acceso.
alter table incidents disable row level security;
