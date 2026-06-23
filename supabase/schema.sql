-- Jalankan file ini di Supabase SQL Editor.
-- Tabel ini dipakai untuk menyimpan histori hasil perhitungan DSS/SPK metode SAW.

create extension if not exists pgcrypto;

create table if not exists public.dss_history (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  metode text not null default 'SAW',
  dataset_name text,
  criteria jsonb not null,
  weights jsonb not null,
  result jsonb not null,
  best_alternative text,
  best_score numeric
);

alter table public.dss_history enable row level security;

-- Policy demo UAS: aplikasi publik boleh insert dan read histori.
-- Untuk produksi asli, policy harus dibuat lebih ketat memakai auth user.
drop policy if exists "dss history demo select" on public.dss_history;
drop policy if exists "dss history demo insert" on public.dss_history;

create policy "dss history demo select"
on public.dss_history
for select
to anon
using (true);

create policy "dss history demo insert"
on public.dss_history
for insert
to anon
with check (true);
