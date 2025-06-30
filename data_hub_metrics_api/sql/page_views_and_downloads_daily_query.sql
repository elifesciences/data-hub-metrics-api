SELECT 
  article_id,
  event_date,
  SUM(IF(event_name = 'page_view', unique_session_count, 0)) AS page_view_count,
  SUM(IF(event_name = 'file_download', unique_session_count, 0)) AS download_count
FROM `elife-data-pipeline.prod.ga4_metrics_event_counts_by_date` 
WHERE article_id IS NOT NULL
  AND event_name IN ('page_view', 'file_download')
  AND event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL {number_of_days} DAY)
GROUP BY event_date, article_id
