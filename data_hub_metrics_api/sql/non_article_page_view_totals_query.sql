SELECT 
  content_type,
  content_id,
  SUM(unique_session_count) AS page_view_count
FROM (
  SELECT
    REGEXP_EXTRACT(page_location, r'/(?:inside-elife)/([a-z0-9]+)/') AS content_id,
    CASE
      WHEN top_level_page_path = '/inside-elife' THEN 'blog-article'
    END AS content_type,
    unique_session_count
  FROM `elife-data-pipeline.prod.ga4_metrics_event_counts_by_date`
  WHERE event_name = 'page_view'
    AND event_date >= '2023-03-20'
)
WHERE content_id IS NOT NULL
GROUP BY content_type, content_id
