SELECT 
  article_id,
  FORMAT_DATE('%Y-%m', event_date) AS year_month,
  SUM(unique_session_count) AS page_view_count
FROM `elife-data-pipeline.prod.ga4_metrics_event_counts_by_date` 
WHERE article_id IS NOT NULL
  AND event_name = 'page_view'
  AND event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
GROUP BY FORMAT_DATE('%Y-%m', event_date), article_id
