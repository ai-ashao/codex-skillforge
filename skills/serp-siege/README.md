# SERP Siege

SERP Siege is a post-decision execution-planning orchestrator for tool-site SEO. Given a user-selected website, competitor domain, keyword, or combination, it produces competitor and keyword maps, feature and SERP coverage matrices, an SEO page map, a bounded First Batch, and an MVP/P1/P2 roadmap.

The user decides whether to pursue the project. SERP Siege improves how to execute it. It does not score the opportunity, output GO/NO_GO, choose site architecture, build or publish the site, generate bulk SEO copy, submit pages for indexing, or monitor rankings.

## Optional upstream context

SERP Siege has no opportunity-analysis dependency. If the user already has an opportunity or architecture report, it may be supplied as `opportunity_context`; SERP Siege consumes the chosen destination and constraints without rerunning or challenging the upstream decision.

## Example

```text
Use $serp-siege with:

target:
  keyword: image compressor
market:
  country: US
  language: en
business:
  monetization: adsense
  maintenance_preference: low
execution:
  destination: independent_site
```

## Validation

```bash
python3 -B skills/serp-siege/scripts/validate_output.py path/to/report.md
python3 -B -m unittest discover -s skills/serp-siege/tests -v
```

Validation confirms execution-report structure and page/cluster invariants. Live SERP accuracy and evidence truthfulness still require review.
