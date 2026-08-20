# Demo Script

Walkthrough for the required demonstration video (doc §7.8, §10).

1. **Asset registration** — Open `/assets`, register the `a2-transcript-backprop`
   sample asset from `data/sample_assets/assets_manifest.json`. Show the
   returned `asset_id` and `job_id`.
2. **Processing status** — Open `/processing`, paste the `job_id`, show it
   moving from `uploaded` toward `indexed` as the pipeline runs.
3. **Unified query** — Open `/query`, ask:
   *"Why are learners struggling with the backpropagation concept?"*
   (from `data/sample_queries.json`). Show the cited evidence panel pulling
   from transcript, slide, quiz, and discussion sources simultaneously —
   this is the cross-modal proof point.
4. **Synthesis + citations** — Point out the generated answer includes a
   `confidence` score and every claim maps to a `segment_id` shown in the
   evidence panel underneath.
5. **Human review** — Open `/recommendations`, load the generated
   `insight_id`, and walk through accept/edit/reject/escalate — emphasize
   that nothing is "approved" until this step.
6. **Dashboards** — Open `/dashboard` and `/operations` to show
   pipeline health and review-outcome metrics pulled from `/api/metrics`.

Total run time target: 4-6 minutes.
