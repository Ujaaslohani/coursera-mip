import os
from typing import Any
from dotenv import load_dotenv
from supabase import Client, create_client
import datetime
from datetime import timezone

load_dotenv()

##creating classes to store application data genrated by the backend and RAG pipeline

class SupabaseApplicationDB:

#------------------------------------------------------------------------------
    ##bacsic intialization
#------------------------------------------------------------------------------
    def __init__(self) -> None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_secret_key = os.getenv("SUPABASE_SECRET_KEY")

        if not supabase_url or not supabase_secret_key:
            raise ValueError("Supabase credentials are missing from .env")

        ##creating a supabase client
        self.client: Client = create_client(
            supabase_url,
            supabase_secret_key,
        )

#------------------------------------------------------------------------------
# ##creating a conversation
#------------------------------------------------------------------------------
    def create_converstion(self,
                           session_id: str,
                           title: str | None = None,
                           user_id: str | None = None,
                           metadata: dict | None = None) -> str:

        record = {
            "session_id": session_id,
            "title": title,
            "user_id": user_id,
            "metadata": metadata
        }

        result = (
            self.client.table("conversations")
            .insert(record)
            .execute()
        )

        return result.data[0]["conversation_id"]


    #------------------------------------------------------------------------------
    #saving the rag interaction
    #------------------------------------------------------------------------------
    def save_rag_interaction(self,
                             *,
                             conversation_id: str,
                             query_text: str,
                             generated_answer: str,
                             normalized_topic: str| None = None,
                             detected_intent: str | None = None,
                             model_name: str | None = None,
                             model_provider: str | None = None,
                             prompt_version: str | None = None,
                             latency_ms: int | None = None,
                             evidence:list[dict[str,Any]]|None = None,
                             recommendations:list[dict[str,Any]]|None = None,
                             metadata: dict[str] | None = None,) -> dict[str,Any]:

        '''HERE YOU SAVE ONE QUERY,
        GENERATED RESPONSE, QDRANT EVIDENCE AND RECOMMENDATIONS,
        
        IF AN ERROR OCCURS AFTER CREATING THE WUERY, THE QUERY WILL BE DELETED
        CASCADE DELETION REMOVES ANY PARTIALLY CREATED RESPONSE/EVIDENCE'''

        query_id : str | None = None

        try:

            ## inserting the query into the user_queries table
            query_result = (
                self.client.table("user_queries")
                .insert(
                    {
                        "conversation_id": conversation_id,
                        "query_text": query_text,
                        "normalized_topic": normalized_topic,
                        "detected_intent": detected_intent,
                        "metadata": metadata or {},}).execute()
            )

            query_id = query_result.data[0]["query_id"]


            ##inserting the generated response into the generated_responses table
            response_result = (
                self.client.table("generated_responses")
                .insert(
                    {

                        "query_id": query_id,
                        "generated_answer": generated_answer,
                        "model_name": model_name,
                        "model_provider": model_provider,
                        "prompt_version": prompt_version,
                        "response_status": "completed",
                        "latency_ms": latency_ms,
                        "metadata": metadata or {},
                    }
            ).execute()
            )


            response_id = response_result.data[0]["response_id"]

            ##inserting the qdrant evidence into the retrieval_evidence table

            evidence_records=[]

            for item in evidence or []:

                evidence_records.append(
                    {

                        "response_id": response_id,
                        "qdrant_record_id": item["qdrant_record_id"],
                        "content_type": item["content_type"],
                        "lecture_id": item["lecture_id"],
                        "module_id": item["module_id"],
                        "similarity_score": item["similarity_score"],
                        "retrieval_rank": item["retrieval_rank"],
                        "evidence_text": item["evidence_text"],
                        "asset_path": item["asset_path"],
                        "timestamp_seconds": item["timestamp_seconds"],
                        "metadata": item["metadata"] or {},
                    }
                )

            if evidence_records:
                    (
                        self.client.table("retrieval_evidence")
                        .insert(evidence_records)
                        .execute()
                    )

            ##inserting the recommendations into the recommendations table
            recommendation_records=[]

            for item in recommendations or []:

                    recommendation_records.append(
                        {
                                "response_id": response_id,
                                "recommendation_type": item["recommendation_type"],
                                "recommendation_text": item["recommendation_text"],
                                "target_record_id": item["target_record_id"],
                                "priority": item["priority"],
                                "metadata": item["metadata"] or {},
                        }
                    )

            if recommendation_records:
                    (
                        self.client.table("recommendations")
                        .insert(recommendation_records)
                        .execute()
                    )

            (
                    self.client.table('conversations')
                    .update({'last_activity_at': datetime.now(timezone.utc).isoformat()})
                    .eq('conversation_id', conversation_id)
                    .execute()
            )

            return {
                    "conversation_id": conversation_id,
                    "query_id": query_id,
                    "response_id": response_id,
                    "evidence_cotun": len(evidence_records),
                    "recommendation_count": len(recommendation_records)
            }

        except Exception:
            if query_id:
                  (
                       self.client.table("user_queries").delete()
                       .eq("query_id", query_id)
                       .execute()
                  )
            raise

    #------------------------------------------------------------------------------
    # saving feedback into the user_feedback table
    #------------------------------------------------------------------------------
    def save_feedback(self,
                      *,
                      response_id: str,
                      user_id: str | None = None,
                      rating: int | None = None,
                      is_helpful: bool | None = None,
                      approval: str = 'pending',
                      feedback_text: str | None = None,) -> str:

        result = (
             self.client.table("user_feedback").insert({
                    "response_id": response_id,
                    "user_id": user_id,
                    "rating": rating,
                    "is_helpful": is_helpful,
                    "approval": approval,
                    "feedback_text": feedback_text,
             }).execute()
        )
        return result.data[0]["feedback_id"]

    ##-----------------------------------------------------------------------------
    ## DASHBOARD SUMMARY VIEWS
    ##-----------------------------------------------------------------------------

    def get_dashboard_summary(self) -> dict[str,Any]:

         result = (
              self.client.table("dashboard_activity_summary")
              .select("*")
              .single()
              .execute()
         )

         return result.data


            
            



