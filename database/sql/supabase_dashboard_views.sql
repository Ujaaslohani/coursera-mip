-- 1. Most frequently requested topics
create or replace view public.dashboard_popular_topics
with (security_invoker = true)
as
select
    normalized_topic,
    count(*) as query_count,
    count(distinct conversation_id) as conversation_count,
    max(created_at) as last_requested_at
from public.user_queries
where normalized_topic is not null
  and length(trim(normalized_topic)) > 0
group by normalized_topic;


-- 2. Evidence types most frequently used by RAG
create or replace view public.dashboard_evidence_usage
with (security_invoker = true)
as
select
    content_type,
    count(*) as evidence_usage_count,
    count(distinct qdrant_record_id) as unique_records_used,
    round(avg(similarity_score)::numeric, 4) as average_similarity_score
from public.retrieval_evidence
group by content_type;


-- 3. Lectures most frequently used as evidence
create or replace view public.dashboard_lecture_usage
with (security_invoker = true)
as
select
    lecture_id,
    count(*) as evidence_usage_count,
    count(distinct qdrant_record_id) as unique_records_used,
    round(avg(similarity_score)::numeric, 4) as average_similarity_score
from public.retrieval_evidence
where lecture_id is not null
group by lecture_id;


-- 4. Recommendation and feedback performance
create or replace view public.dashboard_feedback_summary
with (security_invoker = true)
as
select
    count(*) as total_feedback_records,
    count(*) filter (where is_helpful = true) as helpful_count,
    count(*) filter (where is_helpful = false) as not_helpful_count,
    count(*) filter (where approval = 'approved') as approved_count,
    count(*) filter (where approval = 'rejected') as rejected_count,
    round(avg(rating)::numeric, 2) as average_rating
from public.user_feedback;


-- 5. Overall application activity
create or replace view public.dashboard_activity_summary
with (security_invoker = true)
as
select
    (select count(*) from public.conversations) as total_conversations,
    (select count(*) from public.user_queries) as total_queries,
    (select count(*) from public.generated_responses) as total_responses,
    (select count(*) from public.retrieval_evidence) as total_evidence_records,
    (select count(*) from public.recommendations) as total_recommendations,
    (select count(*) from public.user_feedback) as total_feedback_records;