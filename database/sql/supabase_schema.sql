----------------------------------------------------
-- COURSE ERA ALMAX APPLICATION database
-- QDRANT IS COURSE_CONTENT VECTOR database
-- HUGGING FACE IS THE VISUAL-FILE stored
-- SUPABASE STORES APPLICATION ACTIVITY AND ANALYTICS
----------------------------------------------------

-- 1. CONVERATION table
-- A single user can have mulitiple conversation
-- nullable user_id, so anonymous testing is possible

create table public.conversations (
  conversation_id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  title text,
  session_id text,
  started_at timestamptz not null default now(),
  last_activity_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb

);

--2. USER QURIES
-- STORES EVERY QUESTION/QUERY SUBMITTED BY THE user
create table public.user_queries (
  query_id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null
      references public.conversations(conversation_id)
      on delete cascade,
  
  query_text text not null,
  normalized_topic text,
  detected_intent text,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,

  constraint user_queries_text_not_empty
      check (length(trim(query_text))>0)
);


-- 3. GENERATED RESPONSES
-- Stores the final RAG/LLM answer for a query

create table public.generated_responses (
  response_id uuid primary key default gen_random_uuid(),
  query_id uuid not null
      references public.user_queries(query_id)
      on delete cascade,
  
  generated_answer text not null,
  model_name text,
  model_provider text,
  prompt_version text,
  response_status text not null default 'completed',
  latency_ms integer,
  input_token_count integer,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,

  constraint generated_response_status_check
      check(
        response_status in ('pending','completed','failed','blocked')
      ),
  
  constraint generated_response_latency_check
      check (latency_ms is null or latency_ms >=0 )
);


-- 4. RETRIEVAL EVIDENCE
-- USES THE EXACT QDRANT RECORDS USED BY THE RAG SYSTEM AS A references
-- NO VECTOR DUPLICATION

create table public.retrieval_evidence (
  evidence_id uuid primary key default gen_random_uuid(),
  response_id uuid not null
      references public.generated_responses(response_id)
      on delete cascade,
  
  qdrant_record_id text not null,
  content_type text not null,
  lecture_id text,
  module_id text,
  similarity_score double precision,
  retrieval_rank integer,
  evidence_text text,
  asset_path text,
  timestamp_seconds double precision,
  created_At timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,

  constraint retrieval_evidence_content_type_check
      check (
        content_type in (
          'caption','slide','frame','transcript','quiz','discussion'
        )
      ),
  
  constraint retrieval_evidence_rank_check
      check (retrieval_rank is null or retrieval_rank > 0),
  
  constraint retrieval_evidence_unique_record
      unique (response_id, qdrant_record_id)
);

-- 5. RECOMMENDATIONS
-- STORES THE INDIVIDUAL RECOMMENDATIONS EXTRACTED FROM THE LLM RESPONSE
---------------------------------------------------------------------------
create table public.recommendations (
  recommendation_id uuid primary key default gen_random_uuid(),
  response_id uuid not null
      references public.generated_responses(response_id)
      on delete cascade,
  
  recommendation_type text,
  recommendation_text text not null,
  target_record_id text,
  priority integer,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,

  constraint recommendations_text_not_empty
      check (length(trim(recommendation_text))>0),
  
  constraint recommendations_priority_check
      check (priority is null or priority >0)
);


-- 6. USER FEEDBACK
-- STORES THE FEEBACK FOR A GENERATED RESPONSE
--------------------------------------------------------------------
create table public.user_feedback (
  feedback_id uuid primary key default gen_random_uuid(),
  response_id uuid not null
      references public.generated_responses(response_id)
      on delete cascade,

  user_id uuid references auth.users(id) on delete set null,
  rating smallint,
  is_helpful boolean,
  approval text,
  feedback_text text,
  created_at timestamptz not null default now(),

  constraint user_feedback_rating_check
      check (rating is null or rating between 1 and 5),

  constraint user_feedback_approval_check
      check (approval is null or approval in ('pending', 'approved', 'rejected')),
  
  constraint one_feedback_per_user_response
      unique (response_id, user_id)
);


-- ====================================================================
-- INDEXES
-- THESE SUPPORT CONVERSATION HISTORY, EVIDENCE INSPECTION
-- DASHBOARD STATISTICS AND FREQUENTLY ASKED TOPIC ANALYSIS
-- ====================================================================

create index conversations_user_id_idx
    on public.conversations(user_id);

create index conversations_started_at_idx
    on public.conversations(started_at desc);

create index user_queries_conversation_id_idx
    on public.user_queries(created_at desc);

create index user_queries_created_at_idx
    on public.user_queries(created_at desc);
  
create index user_queries_normalized_topic_idx
    on public.user_queries(normalized_topic);

create index generated_responses_query_id_idx
    on public.generated_responses(query_id);

create index generated_responses_created_at_idx
    on public.generated_responses(created_at desc);

create index retrieval_evidence_responses_id_idx
    on public.retrieval_evidence(response_id);

create index retrieval_evidence_qdrant_record_id_idx
    on public.retrieval_evidence(qdrant_record_id);

create index retrieval_evidence_content_type_idx
    on public.retrieval_evidence(content_type);

create index recommendations_response_id_idx
    on public.recommendations(response_id);

create index user_feedback_response_id_idx
    on public.user_feedback(response_id);




