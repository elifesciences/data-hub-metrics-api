SELECT
  COALESCE(ga4.content_type, ua.content_type) AS content_type,
  COALESCE(ga4.content_id, ua.content_id) AS content_id,
  COALESCE(ga4.page_view_count, 0) + COALESCE(ua.total_ua_views, 0) AS page_view_count,
FROM (
  SELECT 
    content_type,
    content_id,
    SUM(unique_session_count) AS page_view_count
  FROM (
    SELECT
      REGEXP_EXTRACT(
        REGEXP_EXTRACT(page_location, r'://(?:[^/]+)(/[^?]*)'),  -- page path
        r'^/(?:inside-elife|labs|collections|digests|events|interviews|for-the-press)/([a-z0-9]+)/'
      ) AS content_id,
      CASE
        WHEN top_level_page_path = '/inside-elife' THEN 'blog-article'
        WHEN top_level_page_path = '/labs' THEN 'labs-post'
        WHEN top_level_page_path = '/collections' THEN 'collection'
        WHEN top_level_page_path = '/digests' THEN 'digest'
        WHEN top_level_page_path = '/events' THEN 'event'
        WHEN top_level_page_path = '/interviews' THEN 'interview'
        WHEN top_level_page_path = '/for-the-press' THEN 'press-package'
      END AS content_type,
      unique_session_count
    FROM `elife-data-pipeline.prod.ga4_metrics_event_counts_by_date`
    WHERE event_name = 'page_view'
      AND event_date >= '2023-03-20'
  )
  WHERE content_id IS NOT NULL
  GROUP BY content_type, content_id
) AS ga4
FULL OUTER JOIN (
  SELECT *
  FROM `elife-data-pipeline.elife_metrics_dump.mv_elife_metrics_non_article_total_ua_views`
) AS ua
  ON ga4.content_id = ua.content_id
  AND ga4.content_type = ua.content_type