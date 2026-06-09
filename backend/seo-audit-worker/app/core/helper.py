def print_seo_result(result: dict):
    print("\n" + "=" * 60)
    print("SEO ANALYSIS")
    print("=" * 60)

    print(f"Title            : {result['title']['value']}")
    print(f"HTTPS            : {result['metadata']['https']}")
    print(f"Canonical        : {result['metadata']['canonical']}")
    print(f"Canonical Count  : {result['metadata']['canonical_count']}")
    print(f"Canonical Absolute : {result['metadata']['canonical_absolute']}")
    print(f"Robots           : {result['metadata']['robots']}")

    print("\nSITEMAP")
    print(f"Exists           : {result['sitemap']['exists']}")
    print(f"Sitemaps Parsed  : {result['sitemap'].get('sitemaps_parsed', [])}")
    print(f"Total URL Count  : {result['sitemap'].get('url_count', 0)}")

    print("\nHEADINGS")
    print(f"  H1             : {result['heading']['h1_count']}")
    print(f"  H2             : {result['heading']['h2_count']} (Empty: {result['heading'].get('h2_empty_count', 0)})")
    print(f"  H3             : {result['heading']['h3_count']} (Empty: {result['heading'].get('h3_empty_count', 0)})")

    print("\nIMAGES")
    print(f"  Total          : {result['images']['total_images']}")
    print(f"  Missing ALT    : {result['images']['missing_alt_count']}")

    print("\nLINKS")
    print(f"  Internal       : {result['internal_links']['count']}")
    print(f"  External       : {result['external_links']['count']}")
    print(f"  Broken Links   : {result.get('broken_links', {}).get('broken_count', 0)}")
    if result.get('broken_links', {}).get('broken_links'):
        for link in result['broken_links']['broken_links']:
            print(f"    - {link['url']} (Status: {link['status_code']} | Error: {link.get('error', 'None')})")

    print("\nSCHEMA")
    print(f"  Count          : {result['schema']['count']}")
    print(f"  Types          : {', '.join(result['schema']['types'])}")

    print("\nWEB VITALS")
    print(f"  Performance    : {result['web_vitals']['performance_score']}")
    print(f"  LCP            : {result['web_vitals']['field_data']['lcp_ms']} ms")
    print(f"  INP            : {result['web_vitals']['field_data']['inp_ms']} ms")
    print(f"  CLS            : {result['web_vitals']['field_data']['cls']} ms")

    print("\nLANGUAGE")
    print(f"  HTML Lang      : {result['languages']['html_lang']}")
    print(f"  Warnings       : {len(result['languages']['warning'])}")

    print("=" * 60)