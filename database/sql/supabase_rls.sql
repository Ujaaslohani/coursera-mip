--ENABLING ROW LEVEL SECURITY

alter table public.conversations enable row level security;
alter table public.user_queries enable row level security;
alter table public.generated_responses enable row level security;
alter table public.retrieval_evidence enable row level security;
alter table public.recommendations enable row level security;
alter table public.user_feedback enable row level security;


-- USERS/EDUCATOR CAN ACCESS ONLY THEIR OWN CONVERSATIONS
--============================================================================
create policy "user can insert their conversations"
on public.conversations
for insert
to authenticated
with check (user_id = auth.uid());

-- acessing conversations
create policy "users can view their conversations"
on public.conversations
for select
to authenticated
using (user_id = auth.uid());


-- user updating the conversations
create policy "users can update their conversations"
on public.conversations
for update
to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

-- user deleting their own conversations
create policy "users can delete their conversations"
on public.conversations
for delete
to authenticated
using (user_id = auth.uid());

-- user viewing quries from their conversations
create policy "users can view queries from their conversations"
on public.user_queries
for select
to authenticated
using(
  exists(
    select 1
    from public.conversations as c
    where c.conversation_id = user_queries.conversation_id and c.user_id = auth.uid()
  )
);

--- user viewing the generated response
create policy "users can view their generated responses"
on public.generated_responses
for select
to authenticated
using (
  exists(
    select 1
    from public.user_queries as q
    join public.conversations as c
      on c.conversation_id=q.conversation_id
    where q.query_id = generated_responses.query_id
      and c.user_id = auth.uid()
  )
);


-- user viewing retrieved evidence
create policy "users can view evidence for their responses"
on public.retrieval_evidence
for select
to authenticated
using (
  exists (
    select 1
    from public.generated_responses as r
    join public.user_queries as q
      on q.query_id = r.query_id
    join public.conversations as c
      on c.conversation_id = q.conversation_id
    where r.response_id= retrieval_evidence.response_id
      and c.user_id = auth.uid()
  )
);


--- user viewing recommendations
create policy "users can view their recommendations"
on public.recommendations
for select
to authenticated
using (
  exists (
    select 1
    from public.generated_responses as r
    join public.user_queries as q
      on q.query_id = r.query_id
    join public.conversations as c
      on c.conversation_id = q.conversation_id
    where r.response_id = recommendations.response_id
      and c.user_id = auth.uid()
  )
);

-- user can insert their feedback
create policy "users can insert their feedback"
on public.user_feedback
for insert
to authenticated
with check (user_id = auth.uid());

-- users viewing the feedback
create policy "users can view their feedback"
on public.user_feedback
for select
to authenticated
using (user_id = auth.uid());

-- user updating feedback
create policy "user can update their feedback"
on public.user_feedback
for update
to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());