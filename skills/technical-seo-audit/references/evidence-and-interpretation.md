# Evidence and Interpretation

## Evidence labels

| Label | Meaning | Examples |
| --- | --- | --- |
| `OBSERVED` | Directly returned by a script or inspected response. | HTTP 200, `noindex`, canonical URL, JSON-LD parse error. |
| `REVIEW` | Needs context or a human/LLM decision. | Whether a canonical is intentional; whether page copy matches the target query. |
| `UNASSESSED` | Cannot be established from the available data. | Index coverage, GSC queries, rendered client state, field CWV. |

## Severity discipline

| Priority | Use only when | Example |
| --- | --- | --- |
| `P0` | A confirmed unintended blocker affects an in-scope production route. | Production page expected to rank sends `noindex`; robots blocks all target crawlers. |
| `P1` | Observable defect materially impairs discoverability or correct representation. | Broken final canonical, malformed required JSON-LD, inaccessible intended sitemap. |
| `P2` | A meaningful improvement needs product or content context. | Missing useful meta description; ambiguous internal-link path. |
| `P3` | Optional polish or a hypothesis. | Rewording an otherwise truthful title. |

Do not assign priority without stating the production expectation. A `noindex` page can be intentional; an absent sitemap can be acceptable for a small private or non-indexable site.

## Interpretation rules

- Treat `<title>` and meta-description character counts as display considerations, not ranking thresholds.
- Treat H1/heading counts as structure observations. HTML can validly contain multiple headings; judge clarity against the page task.
- Treat word count as a coverage observation. It does not establish thin content, helpfulness, or demand.
- Treat static HTML image-alt checks as incomplete when client rendering is detected. Empty `alt` can be correct for decorative images.
- Treat JSON-LD as a machine-readable representation, not a ranking guarantee. Distinguish declared/top-level types from nested entity types, and verify that all claims are truthful to the visible product.
- Treat `html lang` and hreflang syntax, canonical-aware self-reference, primary-language consistency, HTTP reachability, and reciprocal declarations as observable. Treat language-market mapping and `x-default` necessity as product/SEO review decisions.
- Treat a target URL missing from a bounded sitemap sample as review-only; the sitemap may be partitioned or intentionally exclude the route.
- Treat a valid but empty sitemap as review evidence, not a successful inventory signal.
- Treat HTTP delivery, meta robots, Googlebot meta, and only the applicable crawler scope of `X-Robots-Tag` together when assessing indexability intent.
- Treat static link counts as inventory only. They do not prove link health, crawl depth, anchor quality, or orphan status.
- Do not evaluate target-query alignment without a user-supplied query or independently gathered SERP/GSC evidence.
- Do not describe a public fetch as crawl/index verification.
