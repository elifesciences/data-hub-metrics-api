SELECT
  COALESCE(ga4.article_id, ua.article_id) AS article_id,
  COALESCE(ga4.page_view_count, 0) + COALESCE(ua.page_view_count, 0) AS page_view_count
FROM (
  SELECT 
    article_id,
    SUM(unique_session_count) AS page_view_count
  FROM `elife-data-pipeline.prod.ga4_metrics_event_counts_by_date`
  WHERE article_id IS NOT NULL
    AND event_name = 'page_view'
    AND event_date >= '2023-03-20'
  GROUP BY article_id
) ga4
FULL OUTER JOIN (
  SELECT 
    article_id,
    total_ua_views AS page_view_count
  FROM `elife-data-pipeline.elife_metrics_dump.mv_elife_metrics_total_ua_views_and_downloads`
) ua
  ON ua.article_id = ga4.article_id
