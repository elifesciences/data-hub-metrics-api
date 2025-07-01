SELECT
  COALESCE(ga4.article_id, ua.article_id) AS article_id,
  COALESCE(ga4.page_view_count, 0) + COALESCE(ua.total_ua_views, 0) AS page_view_count,
  COALESCE(ga4.download_count, 0) + COALESCE(ua.total_ua_downloads, 0) AS download_count
FROM (
  SELECT 
    article_id,
    SUM(IF(event_name = 'page_view', unique_session_count, 0)) AS page_view_count,
    SUM(IF(event_name = 'file_download', unique_session_count, 0)) AS download_count
  FROM `elife-data-pipeline.prod.ga4_metrics_event_counts_by_date`
  WHERE article_id IS NOT NULL
    AND event_name IN ('page_view', 'file_download')
    AND event_date >= '2023-03-20'
  GROUP BY article_id
) ga4
FULL OUTER JOIN (
  SELECT *
  FROM `elife-data-pipeline.elife_metrics_dump.mv_elife_metrics_total_ua_views_and_downloads`
) ua
  ON ua.article_id = ga4.article_id
