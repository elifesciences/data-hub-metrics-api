SELECT 
  article_id,
  SUM(unique_session_count) AS page_view_count
FROM `elife-data-pipeline.prod.ga4_metrics_event_counts_by_date` 
WHERE article_id IS NOT NULL
  AND event_name = 'page_view'
GROUP BY article_id