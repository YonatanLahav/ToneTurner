create table rephrase_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  input_text text not null,
  source_language text not null default 'english',
  translation text,
  professional text not null,
  friendly text not null,
  direct text not null,
  creative text not null,
  created_at timestamptz not null default now()
);

alter table rephrase_history enable row level security;

create policy "Users can manage their own history"
  on rephrase_history
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create index on rephrase_history (user_id, created_at desc);
