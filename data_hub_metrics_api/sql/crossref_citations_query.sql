SELECT
  article_id,
  version_number,
  SUM(citation_count) AS citation_count
FROM (
  SELECT 
    is_referenced_by_count AS citation_count,
    REGEXP_EXTRACT(LOWER(DOI), r'10\.7554\/elife\.(\d{5,6})') AS article_id,
    REGEXP_EXTRACT(DOI, r'\.(\d{1,2})$') AS version_number
  FROM `elife-data-pipeline.prod.v_latest_crossref_metadata_api_response`
  WHERE STARTS_WITH(DOI, '10.7554/')
    AND DOI NOT LIKE '%.sa%'
    AND COALESCE(is_referenced_by_count, 0) > 0
)
WHERE article_id IS NOT NULL
GROUP BY article_id, version_number
